from django.urls import path 
from .views import BoardView, BoardSingleView, TaskView, TaskSingleView, AssignedToMeView, ReviewingView, CommentView, CommentSingleView, EmailCheckView


urlpatterns = [
    #urls Boards
    path("boards/",BoardView.as_view()),
    path("boards/<int:pk>/", BoardSingleView.as_view(),name="board-detail"),

    #urls Task
    path("tasks/",TaskView.as_view()),
    path("tasks/<int:pk>/", TaskSingleView.as_view(),name="task-detail"),
    path("tasks/assigned-to-me/", AssignedToMeView.as_view()),
    path("tasks/reviewing/", ReviewingView.as_view()),

    #urls Comment
    path("tasks/<int:task_id>/comments/",CommentView.as_view()),
    path("tasks/<int:task_id>/comments/<int:comment_id>/",CommentSingleView.as_view()),

    #url email
    path("email-check/",EmailCheckView.as_view(),name="email-check" )
]    
