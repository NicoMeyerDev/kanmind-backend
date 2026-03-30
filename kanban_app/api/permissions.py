from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Task

#Nur der Admin darf löschen und bearbeiten    
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # GET jeder eingeloggte User darf lesen
        if request.method in SAFE_METHODS:
            return True
        # DELETE nur Superuser (Admin) darf löschen
        elif request.method =="DELETE":
            return bool(request.user and request.user.is_superuser)
        # PATCH nur Staff darf bearbeiten
        elif request.method =="PATCH":
            return bool(request.user and request.user.is_staff)
        else:
            return bool(request.user and request.user.is_superuser) 

class IsBoardMemberOrOwner(BasePermission):
    def has_permission(self, request, view):
        # Ist der User überhaupt eingeloggt?
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Ist der User der Owner?
        if obj.owner == request.user:
            return True
        # Ist der User ein Member?
        if request.user in obj.members.all():
            return True
        # Sonst 403
        return False         
    
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