from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Task

#Nur der Admin darf löschen und bearbeiten    
class IsTaskBoardMemberOrBoardOwner(BasePermission):
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
    def has_permission(self, request, view):
        # Ist der User überhaupt eingeloggt?
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        #Owner oder Member
        if request.method == "GET":
            return obj.owner == request.user or request.user in obj.members.all()
        #nur Owner
        if request.method == "DELETE":
            return obj.owner == request.user
        #nur Owner
        if request.method == "PATCH":
            return obj.owner == request.user
    
class IsTaskBoardMember(BasePermission):
    """
    Prüft ob der User Mitglied oder Owner des Boards ist,
    zu dem die Task gehört.
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
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.author == request.user
        return False    