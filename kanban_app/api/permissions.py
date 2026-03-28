from rest_framework.permissions import BasePermission, SAFE_METHODS

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