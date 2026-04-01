from rest_framework import serializers
from django.contrib.auth.models import User

from kanban_app.models import Board, Task, Comment


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        """
        Return the user's full name if available.
        Fallback to the username if no full name is set.
        """
        return obj.get_full_name() or obj.username


class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "members",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]
        read_only_fields = ["owner_id"]
        extra_kwargs = {
            "members": {"write_only": True}
        }

    def validate_title(self, title):
        """
        Ensure that the board title is not empty after trimming whitespace.
        """
        title = title.strip()
        if not title:
            raise serializers.ValidationError("Title must not be empty.")
        return title

    def get_member_count(self, obj):
        """
        Return the total number of members assigned to the board.
        """
        return obj.members.count()

    def get_ticket_count(self, obj):
        """
        Return the total number of tasks assigned to the board.
        """
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        """
        Return the number of tasks with status 'to-do'.
        """
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        """
        Return the number of tasks with high priority.
        """
        return obj.tasks.filter(priority="high").count()


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        """
        Return all tasks of the board using the detailed task serializer.
        """
        return TaskDetailSerializer(obj.tasks.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]
        extra_kwargs = {
            "members": {"write_only": True}
        }


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True
    )

    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "assignee_id",
            "reviewer",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def create(self, validated_data):
        """
        Create a new task and optionally assign a reviewer.
        """
        reviewer = validated_data.pop("reviewer_id", None)
        task = Task.objects.create(**validated_data)

        if reviewer:
            task.reviewers.set([reviewer])

        return task

    def update(self, instance, validated_data):
        """
        Update the task fields and optionally replace the reviewer assignment.
        """
        reviewer = validated_data.pop("reviewer_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if reviewer is not None:
            instance.reviewers.set([reviewer])

        return instance

    def validate_title(self, title):
        """
        Ensure that the task title is not empty after trimming whitespace.
        """
        title = title.strip()
        if not title:
            raise serializers.ValidationError("Title must not be empty.")
        return title

    def validate_status(self, value):
        """
        Validate that the task status matches one of the allowed values.
        """
        allowed = ["to-do", "in-progress", "review", "done"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid status.")
        return value

    def validate_priority(self, value):
        """
        Validate that the task priority matches one of the allowed values.
        """
        allowed = ["low", "medium", "high"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid priority.")
        return value

    def get_comments_count(self, obj):
        """
        Return the number of comments assigned to the task.
        """
        return obj.comments.count()

    def get_reviewer(self, obj):
        """
        Return the first assigned reviewer serialized as user data.
        """
        reviewer = obj.reviewers.first()
        return UserSerializer(reviewer).data if reviewer else None


class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_reviewer(self, obj):
        """
        Return the first assigned reviewer serialized as user data.
        """
        first_reviewer = obj.reviewers.first()
        if first_reviewer:
            return UserSerializer(first_reviewer).data
        return None

    def get_comments_count(self, obj):
        """
        Return the number of comments assigned to the task.
        """
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["task", "author", "created_at"]

    def validate_content(self, content):
        """
        Ensure that the comment content is not empty after trimming whitespace.
        """
        content = content.strip()
        if not content:
            raise serializers.ValidationError("Content must not be empty.")
        return content

    def get_author(self, obj):
        """
        Return the display name of the comment author.
        Use the full name if available, otherwise the username.
        """
        return obj.author.get_full_name() or obj.author.username