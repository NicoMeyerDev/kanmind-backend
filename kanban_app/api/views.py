from rest_framework import mixins, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .permissions import IsTaskBoardMemberOrBoardOwner, IsBoardMemberOrOwner, IsTaskBoardMember, IsCommentAuthor
from kanban_app.models import Board, Task, Comment
from kanban_app.api.serializers import BoardSerializer, BoardDetailSerializer, TaskSerializer, CommentSerializer, BoardUpdateSerializer 


# Boards (Liste + Erstellen)
class BoardView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    #Nur Boards anzeigen, wo User Owner oder Mitglied ist
    def get_queryset(self):
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    #GET Liste
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    #POST Board erstellen
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    #Beim Erstellen User als Owner + Member setzen
    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


#Einzelnes Board
class BoardSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    #GET Board anzeigen
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    #PATCH Board updaten
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    #DELETE Board löschen
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    #Unterschiedlicher Serializer für PATCH
    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer

#Tasks Liste + Erstellen
class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    #GET Liste
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    #POST Task erstellen mit Validierung
    def post(self, request, *args, **kwargs):
        board = get_object_or_404(Board, id=request.data.get("board"))

        #User muss im Board sein
        if not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
            raise PermissionDenied("Nicht im Board")

        #Assignee prüfen
        assignee = request.data.get("assignee_id")
        if assignee and not board.members.filter(id=assignee).exists() and board.owner.id != int(assignee):
            raise ValidationError({"assignee_id": "Kein Board-Mitglied"})

        #Reviewer prüfen
        reviewer = request.data.get("reviewer_id")
        if reviewer and not board.members.filter(id=reviewer).exists() and board.owner.id != int(reviewer):
            raise ValidationError({"reviewer_id": "Kein Board-Mitglied"})

        return self.create(request, *args, **kwargs)

    #Reviewer nachträglich setzen (ManyToMany)
    def perform_create(self, serializer):
        task = serializer.save()

        reviewer_id = self.request.data.get("reviewer_id")
        if reviewer_id:
            task.reviewers.set([reviewer_id])

#Einzelner Task
class TaskSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrBoardOwner]

    #GET
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    #PATCH
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    #DELETE
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Tasks vom User
class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer

    #Alle Tasks, wo User Assignee ist
    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user)

#Tasks als Reviewer
class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer

    #Alle Tasks, wo User Reviewer ist
    def get_queryset(self):
        return Task.objects.filter(reviewers=self.request.user)



#Kommentare Liste + Erstellen
class CommentView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    #GET Kommentare einer Task
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    #POST Kommentar erstellen
    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        board = task.board

        #Zugriff prüfen
        if not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
            raise PermissionDenied("Kein Zugriff")

        return self.create(request, *args, **kwargs)

    #Nur Kommentare dieser Task + Zugriff prüfen
    def get_queryset(self):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        board = task.board

        if not (board.owner == self.request.user or board.members.filter(id=self.request.user.id).exists()):
            raise PermissionDenied("Kein Zugriff")

        return Comment.objects.filter(task_id=task.id).order_by("created_at")

    #Autor + Task automatisch setzen
    def perform_create(self, serializer):
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        serializer.save(author=self.request.user, task=task)

#Einzelner Kommentar löschen
class CommentSingleView(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    #DELETE
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    #Sicherstellen, dass Kommentar zur Task gehört
    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        comment_id = self.kwargs["comment_id"]

        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        return Comment.objects.filter(id=comment.id)

#Email Check
class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get("email")

        #Keine Email übergeben
        if not email:
            return Response({"error": "Email fehlt"}, status=status.HTTP_400_BAD_REQUEST)

        #User suchen
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Nicht gefunden"}, status=status.HTTP_404_NOT_FOUND)

        #Erfolg
        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.username
        }, status=status.HTTP_200_OK)