from datetime import datetime
import typing
import json

from werkzeug.exceptions import Forbidden
import sqlalchemy as sqla
from marshmallow.exceptions import ValidationError

from api.app import db, socketio
from api.model.user import User

from api.model import BoardPermission, CardActivityEvent
from api.model.board import BoardAllowedUser
from api.model.card import CardActivity, Card
from api.model.checklist import CardChecklist, ChecklistItem


class ChecklistService:
    """
    Contains business logic for Checklist.
    """

    def post(self, current_user: User, card_id: int, data: dict) -> CardChecklist:
        """Creates Checklist."""
        card: Card = Card.get_or_404(card_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            card.board_id, current_user.id)

        if (current_member.has_permission(BoardPermission.CHECKLIST_CREATE)):
            # Create checklist
            checklist = CardChecklist(
                card_id=card.id,
                board_id=card.board_id,
                **data
            )

            # Card activity
            card.activities.append(
                CardActivity(
                    board_user_id=current_member.id,
                    event=CardActivityEvent.CHECKLIST_CREATE.value,
                    entity_id=card.id,
                    changes=json.dumps({
                        "to": {
                            "title": checklist.title
                        }
                    })
                )
            )
            db.session.add(checklist)
            db.session.commit()
            return checklist
        raise Forbidden()

    def patch(self, current_user: User, checklist_id: int, data: dict) -> CardChecklist:
        """Updates Checklist."""
        checklist: CardChecklist = CardChecklist.get_or_404(checklist_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            checklist.board_id, current_user.id)

        if current_member.has_permission(BoardPermission.CHECKLIST_EDIT):
            checklist.update(**data)
            db.session.commit()
            db.session.refresh(checklist)
            return checklist
        raise Forbidden()

    def delete(self, current_user: User, checklist_id: int):
        """Deletes Checklist"""
        checklist: CardChecklist = CardChecklist.get_or_404(checklist_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            checklist.board_id, current_user.id)

        if (current_member.has_permission(BoardPermission.CHECKLIST_EDIT)):
            db.session.delete(checklist)
            checklist.card.activities.append(
                CardActivity(
                    board_user_id=current_member.id,
                    event=CardActivityEvent.CHECKLIST_DELETE.value
                )
            )
            db.session.commit()
        else:
            raise Forbidden()


class ChecklistItemService:
    """
    Contains business logic for ChecklistItem.
    """

    def post(self, current_user: User, checklist_id: int, data: dict) -> ChecklistItem:
        """Creates ChecklistItem."""
        checklist: CardChecklist = CardChecklist.get_or_404(checklist_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            checklist.board_id, current_user.id)

        if current_member.has_permission(BoardPermission.CHECKLIST_EDIT):
            errors = {}
            assigned_user = None

            # Validate some SQL sutff if required.
            if data.get("marked_complete_board_user_id"):
                if not checklist.board.get_board_user(data["marked_complete_board_user_id"]):
                    errors["marked_complete_board_user_id"] = [
                        "User not exists or not member of board!"]

            if data.get("assigned_board_user_id"):
                assigned_user = checklist.board.get_board_user(
                    data["assigned_board_user_id"])

                if not assigned_user:
                    errors["assigned_board_user_id"] = [
                        "User not exists or not member of board!"]

            if len(errors.keys()) > 0:
                raise ValidationError(errors)

            item = ChecklistItem(
                board_id=checklist.board_id,
                **data
            )

            # Calculate position
            position_max = db.engine.execute(
                f"SELECT MAX(position) FROM card_checklist_item WHERE checklist_id={checklist.id}"
            ).fetchone()
            if position_max[0] is not None:
                item.position = position_max[0] + 1

            checklist.items.append(item)
            # TODO Send Email notification for assigned user
            db.session.commit()
            db.session.refresh(item)
            return item
        raise Forbidden()

    def checklist_item_process_changes(
        self,
        current_member: BoardAllowedUser, item: ChecklistItem, data: dict
    ):
        """Processes data changes of checklist item, creates card activities
        based on data changes.

        Args:
            current_member (User): Current logged in board member
            item (ChecklistItem): Checklist item to process
            data (dict): Data got from request
        """
        if (
            data.get("completed") is not None and
            data["completed"] != item.completed
        ):
            # Checklist item marked
            activity = CardActivity(
                board_user_id=current_member.id,
                event=CardActivityEvent.CHECKLIST_ITEM_MARKED,
                entity_id=item.id,
                changes=json.dumps(
                    {
                        "to": {
                            "title": item.title,
                            "completed": data["completed"]
                        }
                    }
                )
            )
            item.checklist.card.activities.append(activity)
            # Update details
            if data["completed"]:
                item.marked_complete_board_user_id = current_member.id
                item.marked_complete_on = datetime.utcnow()
            else:
                item.marked_complete_board_user_id = None
                item.marked_complete_on = None
        if (
            data.get("assigned_board_user_id") is not None and
            data["assigned_board_user_id"] != item.assigned_board_user_id
        ):
            activity = CardActivity(
                board_user_id=current_member.id,
                event=CardActivityEvent.CHECKLIST_ITEM_USER_ASSIGN,
                entity_id=item.id,
                changes=json.dumps(
                    {
                        "to": {
                            "board_user_id": data["assigned_board_user_id"]
                        }
                    }
                )
            )
            item.checklist.card.activities.append(activity)
        if (
            data.get("due_date") is not None and
            data["due_date"] != item.due_date
        ):
            activity = CardActivity(
                board_user_id=current_member.id,
                event=CardActivityEvent.CHECKLIST_ITEM_DUE_DATE,
                entity_id=item.id,
                changes=json.dumps(
                    {
                        "from": {
                            "due_date": item.due_date.strftime("%Y-%m-%d %H:%M:%S") if item.due_date else ""
                        },
                        "to": {
                            "due_date": data["due_date"].strftime("%Y-%m-%d %H:%M:%S")
                        }
                    }
                )
            )

    def patch(self, current_user: User, item_id: int, data: dict) -> ChecklistItem:
        """Updates ChecklistItem."""
        item: ChecklistItem = ChecklistItem.get_or_404(item_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            item.board_id, current_user.id)

        if current_member.has_permission(BoardPermission.CHECKLIST_EDIT):
            # User can update everything

            # SQL validation
            if data.get("marked_complete_board_user_id"):
                BoardAllowedUser.get_or_404(
                    data["marked_complete_board_user_id"])

            if data.get("assigned_board_user_id"):
                BoardAllowedUser.get_or_404(data["assigned_board_user_id"])

            self.checklist_item_process_changes(current_member, item, data)

            item.update(**data)

            db.session.commit()
            db.session.refresh(item)

            return item
        elif current_member.has_permission(BoardPermission.CHECKLIST_ITEM_MARK):
            # Only allow marking for member
            # TODO: raise forbidden if there's other fields on data
            self.checklist_item_process_changes(current_member, item, data)
            item.update(completed=data["completed"])

            db.session.commit()
            db.session.refresh(item)

            return item
        raise Forbidden()

    def delete(self, current_user: User, item_id: int):
        """Deletes ChecklistItem"""
        item: ChecklistItem = ChecklistItem.get_or_404(item_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            item.board_id, current_user.id)

        if current_member.has_permission(BoardPermission.CHECKLIST_EDIT):
            db.session.delete(item)
            db.session.commit()
        else:
            raise Forbidden()

    def update_items_position(
        self,
        current_user: User,
        checklist_id: int,
        data: typing.List[int]
    ):
        checklist: CardChecklist = CardChecklist.get_or_404(checklist_id)
        current_member = BoardAllowedUser.get_by_usr_or_403(
            checklist.board_id, current_user.id)

        if current_member.has_permission(BoardPermission.CHECKLIST_EDIT):
            for index, item in enumerate(data):
                db.session.query(ChecklistItem).filter(
                    sqla.and_(
                        ChecklistItem.id == item,
                        ChecklistItem.checklist_id == checklist.id
                    )
                ).update({"position": index})
                db.session.commit()


checklist_service = ChecklistService()
checklist_item_service = ChecklistItemService()
