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


class BoardView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return all boards where the current user is either
        the owner or a member.
        """
        user = self.request.user
        return (Board.objects.filter(owner=user) | Board.objects.filter(members=user)).distinct()

    def get(self, request, *args, **kwargs):
        """
        Return the list of boards accessible to the current user.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new board for the current user.
        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create the board with the current user as owner
        and automatically add the owner as a board member.
        """
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)


class BoardSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get(self, request, *args, **kwargs):
        """
        Return the details of a single board.
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Partially update a single board.
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete a single board.
        """
        return self.destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Use a dedicated serializer for partial board updates.
        """
        if self.request.method == "PATCH":
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TaskView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return the task list.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new task after validating the target board
        and the user's membership.
        """
        board_id = request.data.get("board")

        try:
            board = Board.objects.get(id=int(board_id))
        except (TypeError, ValueError, Board.DoesNotExist):
            raise ValidationError({"board": "Invalid board id."})

        if not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
            raise PermissionDenied("Not a board member.")

        return self.create(request, *args, **kwargs)


class TaskSingleView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrBoardOwner]

    def get(self, request, *args, **kwargs):
        """
        Return a single task.
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Partially update a single task.
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete a single task.
        """
        return self.destroy(request, *args, **kwargs)


class AssignedToMeView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Return all tasks assigned to the current user.
        """
        return Task.objects.filter(assignee=self.request.user)


class ReviewingView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Return all tasks where the current user is assigned
        as reviewer.
        """
        return Task.objects.filter(reviewers=self.request.user)


class CommentView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return all comments for the requested task.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Create a new comment for the requested task if the user
        has access to the related board.
        """
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        board = task.board

        if not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
            raise PermissionDenied("Kein Zugriff")

        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return all comments for the requested task in chronological order
        and ensure that the user has access to the related board.
        """
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        board = task.board

        if not (board.owner == self.request.user or board.members.filter(id=self.request.user.id).exists()):
            raise PermissionDenied("Kein Zugriff")

        return Comment.objects.filter(task_id=task.id).order_by("created_at")

    def perform_create(self, serializer):
        """
        Attach the current user as author and the requested task
        to the new comment.
        """
        task = get_object_or_404(Task, id=self.kwargs["task_id"])
        serializer.save(author=self.request.user, task=task)


class CommentSingleView(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = "comment_id"

    def delete(self, request, *args, **kwargs):
        """
        Delete a single comment.
        """
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Restrict the queryset to the requested comment and ensure
        that it belongs to the given task.
        """
        task_id = self.kwargs["task_id"]
        comment_id = self.kwargs["comment_id"]

        comment = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        return Comment.objects.filter(id=comment.id)


class EmailCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Return basic user information for the provided email address
        if a matching account exists.
        """
        email = request.query_params.get("email")

        if not email:
            return Response({"error": "Email fehlt"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Nicht gefunden"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.username
        }, status=status.HTTP_200_OK)