from rest_framework.permissions import BasePermission, SAFE_METHODS

#Nur der Admin darf löschen und bearbeiten    
class IsAdminForDeleteOrPatchAndReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        elif request.method =="DELETE":
            return bool(request.user and request.user.is_superuser)
        elif request.method =="PATCH":
            return bool(request.user and request.user.is_staff)
        else:
            return bool(request.user and request.user.is_superuser) 

         