from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Task


class IsTaskBoardMemberOrBoardOwner(BasePermission):
    """
    Allow read access to all authenticated users.
    Allow updates for board members or owner.
    Allow deletion only for the board owner.
    """

    def has_object_permission(self, request, view, obj):
        board = obj.board

        if request.method in SAFE_METHODS:
            return True

        if request.method == "PATCH":
            return (
                board.owner == request.user or
                board.members.filter(id=request.user.id).exists()
            )

        if request.method == "DELETE":
            return board.owner == request.user

        return False


class IsBoardMemberOrOwner(BasePermission):
    """
    Allow access to board members and owner for read operations.
    Restrict update and delete operations to the board owner only.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):

        if request.method == "GET":
            return obj.owner == request.user or obj.members.filter(id=request.user.id).exists()

        if request.method == "PATCH":
            return obj.owner == request.user

        if request.method == "DELETE":
            return obj.owner == request.user


class IsTaskBoardMember(BasePermission):
    """
    Allow access only if the user is a member or owner
    of the board associated with the given task_id.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        task_id = view.kwargs.get("task_id")

        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            return False

        board = task.board

        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )


class IsCommentAuthor(BasePermission):
    """
    Allow deletion of a comment only if the requesting user
    is the author of that comment.
    """

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.author == request.user

        return False