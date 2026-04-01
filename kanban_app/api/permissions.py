from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Task

#Task Permission (Board)
class IsTaskBoardMemberOrBoardOwner(BasePermission):
    #Prüft Zugriff auf einzelne Task
    def has_object_permission(self, request, view, obj):
        board = obj.board

        #GET/HEAD/OPTIONS immer erlaubt
        if request.method in SAFE_METHODS:
            return True

        #PATCH Owner oder Member darf bearbeiten
        if request.method == "PATCH":
            return (
                board.owner == request.user or
                board.members.filter(id=request.user.id).exists()
            )

        #DELETE nur Owner darf löschen
        if request.method == "DELETE":
            return board.owner == request.user

        return False

#Board Permission
class IsBoardMemberOrOwner(BasePermission):

    #User muss eingeloggt sein
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    #Objektbasierte Prüfung
    def has_object_permission(self, request, view, obj):

        #GET Owner oder Member darf sehen
        if request.method == "GET":
            return obj.owner == request.user or request.user in obj.members.all()

        #PATCH nur Owner darf ändern
        if request.method == "PATCH":
            return obj.owner == request.user

        #DELETE nur Owner darf löschen
        if request.method == "DELETE":
            return obj.owner == request.user

#Task Permission über task_id
class IsTaskBoardMember(BasePermission):
    """
    Zugriff auf Task über URL (task_id)
    """

    def has_permission(self, request, view):

        #User muss eingeloggt sein
        if not request.user or not request.user.is_authenticated:
            return False

        #task_id aus URL holen
        task_id = view.kwargs.get("task_id")

        #Task laden inkl. Board
        try:
            task = Task.objects.select_related("board").get(id=task_id)
        except Task.DoesNotExist:
            return False

        board = task.board

        #Owner oder Member darf zugreifen
        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )

#Comment Permission
class IsCommentAuthor(BasePermission):

    # Nur Autor darf Kommentar löschen
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.author == request.user

        return False