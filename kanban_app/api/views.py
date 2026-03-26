from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdminForDeleteOrPatchAndReadOnly

from kanban_app.models import Board , Task, Comment
from kanban_app.api.serializers import BoardSerializer, TaskSerializer, CommentSerializer

#Liste aller Boards
class BoardView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all boards or create a new boad.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

#Einzelansicht von einem Board
class BoardSingleView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView,):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated,IsAdminForDeleteOrPatchAndReadOnly]


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    

class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all tasks or create a new task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

#Einzelansicht eines Task
class TaskSingleView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated,IsAdminForDeleteOrPatchAndReadOnly]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)    

#alle Tasks die dem aktuell eingeloggten User zugewiesen sind    
class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer   

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)
    
#es werden alle Tasks angezeigt,bei den man als Reviewer eingetragen ist
class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(reviewers=self.request.user)
    

class CommentView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all comments or create a new comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    #Filter nach Task
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])
    
    #legt fest, wer den Kommentar geschrieben hat
    def perform_create(self, serializer):
        serializer.save(author=self.request.user, task_id=self.kwargs["task_id"])

class CommentSingleView(mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAdminForDeleteOrPatchAndReadOnly]
    lookup_url_kwarg = "comment_id"

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        return Comment.objects.filter(task_id=self.kwargs["task_id"])


class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        email = request.query_params.get("email")
        

        if not email:
            return Response({"error": "Email ist erforderlich"},status=status.HTTP_400_BAD_REQUEST)
        exists = User.objects.filter(email=email).exists()

        return Response(
            {"exists": exists},
            status=status.HTTP_200_OK
        )



    

    
        




    
    
