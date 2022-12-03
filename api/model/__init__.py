import enum

from werkzeug.exceptions import NotFound


class RestEnum(enum.IntEnum):
    """
    Tuple list compatibile with Restful argparse choices.
    """

    @classmethod
    def tuple(cls):
        return tuple(t.value for t in cls)


class BaseMixin(object):

    @classmethod
    def get_or_404(cls, id):
        m = cls.query.get(id)
        if m is None:
            raise NotFound(f"{cls.__tablename__} not exists")
        return m

    def update(self, **kw):
        for key, value in kw.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BoardPermission(enum.Enum):
    CARD_EDIT = "card.edit"
    CARD_COMMENT = "card.comment"
    CARD_DELETE = "card.delete"
    CARD_ASSIGN_MEMBER = "card.assign_member"
    CARD_DEASSIGN_MEMBER = "card.deassign_member"
    CARD_ADD_DATE = "card.add_date"
    CARD_EDIT_DATE = "card.edit_date"

    LIST_CREATE = "list.create"
    LIST_EDIT = "list.edit"
    LIST_DELETE = "list.delete"

    BOARD_UPDATE = "board.update"

    CHECKLIST_CREATE = "checklist.create"
    CHECKLIST_EDIT = "checklist.edit"
    CHECKLIST_ITEM_MARK = "checklist_item.mark"


class BoardActivityEvent(enum.Enum):
    BOARD_CREATE = "board.create"
    BOARD_ARCHIVE = "board.archive"
    BOARD_CHANGE_TITLE = "board.change_title"
    BOARD_CHANGE_OWNER = "board.change-owner"
    BOARD_REVERT = "board.revert"

    MEMBER_ADD = "member.add"
    MEMBER_ACCESS_REVOKE = "member.access_revoke"
    MEMBER_DELETE = "member.delete"
    MEMBER_REVERT = "member.revert"
    MEMBER_CHANGE_ROLE = "member.change_role"

    LIST_CREATE = "list.create"
    LIST_UPDATE = "list.update"
    LIST_ARCHIVE = "list.archive"
    LIST_REVERT = "list.revert"
    LIST_DELETE = "list.delete"


# TODO: ! Convert CardActivityEvent to enum, BE CAREFUL WE NEED SOME conversion on migration!
class CardActivityEvent(RestEnum):
    CARD_ASSIGN_TO_LIST = 1
    CARD_MOVE_TO_LIST = 2
    CARD_COMMENT = 3
    CHECKLIST_CREATE = 4
    CHECKLIST_UPDATE = 5
    CHECKLIST_DELETE = 6
    CHECKLIST_ITEM_MARKED = 7
    CHECKLIST_ITEM_DUE_DATE = 8
    CHECKLIST_ITEM_USER_ASSIGN = 9

    CARD_ASSIGN_MEMBER = 10
    CARD_DEASSIGN_MEMBER = 11
    CARD_ADD_DATE = 12
    CARD_EDIT_DATE = 13
    CARD_DELETE_DATE = 14
