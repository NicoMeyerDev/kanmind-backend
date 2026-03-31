from rest_framework import serializers
from kanban_app.models import Board, Task, Comment
from django.contrib.auth.models import User

# Serializer für das Board-Modell
# Wandelt Board-Objekte in JSON um und umgekehrt
class BoardSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = Board

        # Felder, die in der API sichtbar
        fields = ["id", "title","member_count", "ticket_count", "tasks_to_do_count", "tasks_high_prio_count", "owner_id"]
        read_only_fields = ["owner_id"]

    # Validierung der einzelnen Felder"
    def validate_title(self, title):
        title = title.strip()  # Leerzeichen am Anfang/Ende entfernen
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title
    
    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()  
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status="to-do").count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority="high").count()
    

    
# Serializer für User-Details in Responses
class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

    def get_fullname(self, obj):
        return obj.get_full_name() or obj.username


# Serializer für Board Update (PATCH)
class BoardUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserSerializer(source="owner", read_only=True)
    members_data = UserSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data", "members"]
        extra_kwargs = {
            "members": {"write_only": True}  # members nur im Request, nicht im Response
        }    


# Serializer für das Task-Modell
# Zuständig für Umwandlung zwischen DB und JSON
class TaskSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        # Felder für die API
        fields = ["id", "board", "title", "description", "assignee", "reviewer", "status", "priority", "due_date", "comments_count"]

    # Validierung für das Feld "title"
    def validate_title(self, title):
        title = title.strip()    # Entfernt Leerzeichen

        # Prüft, ob der Titel leer ist
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title
    
    #Validierung für das Feld "status"
    def validate_status(self, value):
        allowed = ["to-do", "in-progress", "done"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültiger Status")
        return value
    #Validierung für das Feld "priority"
    def validate_priority(self, value):
        allowed = ["low", "medium", "high"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültige Priorität")
        return value
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_reviewer(self, obj):
        first_reviewer = obj.reviewers.first()
        if first_reviewer:
            return UserSerializer(first_reviewer).data
        return None

class TaskDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id","title","description","status","priority","assignee","reviewer","due_date","comments_count",]

    def get_reviewer(self, obj):
        first_reviewer = obj.reviewers.first()
        if first_reviewer:
            return UserSerializer(first_reviewer).data
        return None

    def get_comments_count(self, obj):
        return obj.comments.count()



class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]
        

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        # Felder für die API
        fields = ["id", "author", "content", "created_at"]
        read_only_fields = ["task", "author", "created_at"]


    def validate_content(self, content):
        content = content.strip()    # Entfernt Leerzeichen    

     # Prüft, ob der Kommentar/content leer ist
        if not content:
            raise serializers.ValidationError("content darf nicht leer sein")
        return content

    def get_author(self, obj):
        return obj.author.get_full_name() or obj.author.username    