from rest_framework import serializers
from django.contrib.auth.models import User

from kanban_app.models import Board, Task, Comment


#User-Serializer:
#Wird genutzt, um User-Daten sauber als Objekt in Responses zurückzugeben.
class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    #Gibt den vollständigen Namen zurück, falls vorhanden.
    #Falls nicht, wird der Username genutzt.
    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username


#Board-Liste / Board-Erstellung:
#Für GET /boards/ und POST /boards/
class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board
        fields = ["id","title","members","member_count","ticket_count","tasks_to_do_count","tasks_high_prio_count","owner_id",]
        read_only_fields = ["owner_id"]
        extra_kwargs = {
            "members": {"write_only": True}
        }

    #Titel darf nicht leer sein
    def validate_title(self, title):
        title = title.strip()
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title

    #Anzahl der Board-Mitglieder
    def get_member_count(self, obj):
        return obj.members.count()

    #Anzahl aller Tasks im Board
    def get_ticket_count(self, obj):
        return obj.tasks.count()

    #Anzahl der Tasks mit Status "to-do"
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    #Anzahl der Tasks mit hoher Priorität
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()


#Board-Detail:
#Für GET /boards/{id}/
class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    #Gibt alle Tasks des Boards mit Detaildaten zurück
    def get_tasks(self, obj):
        return TaskDetailSerializer(obj.tasks.all(), many=True).data


#Board-Update:
#Für PATCH /boards/{id}/
class BoardUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]
        extra_kwargs = {
            "members": {"write_only": True}
        }


#Task-Serializer:
#Für GET /tasks/, POST /tasks/ und PATCH /tasks/{id}/
class TaskSerializer(serializers.ModelSerializer):
    # Response-Felder
    assignee = UserSerializer(read_only=True)
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    #Request-Felder
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="assignee",
        write_only=True,
        required=False,
        allow_null=True
    )
    reviewer_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = ["id""board","title","description","status","priority","assignee","assignee_id","reviewer","reviewer_id","due_date","comments_count",]

    #Erstellt eine neue Task und setzt optional den Reviewer
    def create(self, validated_data):
        reviewer_id = validated_data.pop("reviewer_id", None)
        task = Task.objects.create(**validated_data)

        if reviewer_id:
            task.reviewers.set([reviewer_id])

        return task

    #ktualisiert eine Task und setzt optional den Reviewer neu
    def update(self, instance, validated_data):
        reviewer_id = validated_data.pop("reviewer_id", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if reviewer_id is not None:
            instance.reviewers.set([reviewer_id])

        return instance

    #Titel darf nicht leer sein
    def validate_title(self, title):
        title = title.strip()
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title

    #Status muss einem erlaubten Wert entsprechen
    def validate_status(self, value):
        allowed = ["to-do", "in-progress", "review", "done"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültiger Status")
        return value

    #Priority muss einem erlaubten Wert entsprechen
    def validate_priority(self, value):
        allowed = ["low", "medium", "high"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültige Priorität")
        return value

    #Gibt die Anzahl der Kommentare zurück
    def get_comments_count(self, obj):
        return obj.comments.count()

    #Gibt den ersten Reviewer als User-Objekt zurück
    def get_reviewer(self, obj):
        first_reviewer = obj.reviewers.first()
        if first_reviewer:
            return UserSerializer(first_reviewer).data
        return None


#Task-Detail im Board-Detail-Endpoint
class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id","title","description","status","priority","assignee","reviewer","due_date","comments_count",]

    #Gibt den ersten Reviewer als User-Objekt zurück
    def get_reviewer(self, obj):
        first_reviewer = obj.reviewers.first()
        if first_reviewer:
            return UserSerializer(first_reviewer).data
        return None

    #Gibt die Anzahl der Kommentare zurück
    def get_comments_count(self, obj):
        return obj.comments.count()


#Comment-Serializer:
#Für GET /comments/ und POST /comments/
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["task", "author", "created_at"]

    #Kommentartext darf nicht leer sein
    def validate_content(self, content):
        content = content.strip()
        if not content:
            raise serializers.ValidationError("content darf nicht leer sein")
        return content

    #Gibt den Autor als Namen zurück
    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username