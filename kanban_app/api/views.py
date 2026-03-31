from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User

from .permissions import  IsTaskBoardMemberOrBoardOwner, IsBoardMemberOrOwner, IsTaskBoardMember, IsCommentAuthor

from django.shortcuts import get_object_or_404

from kanban_app.models import Board , Task, Comment
from kanban_app.api.serializers import BoardSerializer, BoardDetailSerializer, TaskSerializer, CommentSerializer, BoardUpdateSerializer 

#Liste aller Boards
class BoardView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all boards or create a new boad.
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

#Einzelansicht von einem Board
class BoardSingleView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView,):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated,IsBoardMemberOrOwner]


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer
    

class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all tasks or create a new task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

#Einzelansicht eines Task
class TaskSingleView(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrBoardOwner]

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
    permission_classes = [IsAuthenticated] 
    

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def get_queryset(self):
        get_object_or_404(Task, id=self.kwargs["task_id"])
        return Comment.objects.filter(task_id=self.kwargs["task_id"])
    
    #legt fest, wer den Kommentar geschrieben hat
    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        serializer.save(author=self.request.user, task_id=self.kwargs["task_id"])

class CommentSingleView(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        comment_id = self.kwargs["comment_id"]

        # Prüfen ob task_id zu comment_id passt
        if not Comment.objects.filter(id=comment_id, task_id=task_id).exists():
            raise ValidationError("Der Kommentar gehört nicht zur angegebenen Task.")
            

        return Comment.objects.filter(task_id=task_id)

class EmailCheckView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        email = request.query_params.get("email")


        if not email:
            return Response({"error": "Email ist erforderlich"},status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Email wurde nicht gefunden"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"id": user.id, "email": user.email, "fullname": user.username}, status=status.HTTP_200_OK)



    

    
        




    
    
