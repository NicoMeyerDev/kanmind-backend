from django.urls import path, include
from .views import BoardView, BoardSingleView, TaskView, TaskSingleView


urlpatterns = [
    path("board/",BoardView.as_view()),
    path("board/<int:pk>/", BoardSingleView.as_view(),name="board-detail"),

    path("task/",TaskView.as_view()),
    path("task/<int:pk>/", TaskSingleView.as_view(),name="task-detail"),
    
]    