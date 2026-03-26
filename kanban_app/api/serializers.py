from rest_framework import serializers
from kanban_app.models import Board, Task, Comment

# Serializer für das Board-Modell
# Wandelt Board-Objekte in JSON um und umgekehrt
class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        # Felder, die in der API sichtbar
        fields = ["id", "owner", "members", "title", "description"]

    # Validierung für das Feld "title"
    def validate_title(self, title):
        title = title.strip()

        # Prüft, ob der Titel leer ist
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title


# Serializer für das Task-Modell
# Zuständig für Umwandlung zwischen DB und JSON
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # Felder für die API
        fields = ["id", "board", "title", "description", "assignee", "reviewers", "status", "priority"]

    # Validierung für das Feld "title"
    def validate_title(self, title):
        title = title.strip()    # Entfernt Leerzeichen

        # Prüft, ob der Titel leer ist
        if not title:
            raise serializers.ValidationError("Titel darf nicht leer sein")
        return title
    
    #Validierung für das Feld "status"
    def validate_status(self, value):
        allowed = ["Nicht_Begonnen", "Begonnen", "Erledigt"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültiger Status")
        return value
    #Validierung für das Feld "priority"
    def validate_priority(self, value):
        allowed = ["Niedrig", "Mittel", "Hoch"]
        if value not in allowed:
            raise serializers.ValidationError("Ungültige Priorität")
        return value



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # Felder für die API
        fields = ["id", "task", "author", "content", "created_at"]
        read_only_fields = ["task", "author", "created_at"]


    def validate_content(self, content):
        content = content.strip()    # Entfernt Leerzeichen    

     # Prüft, ob der Kommentar/content leer ist
        if not content:
            raise serializers.ValidationError("content darf nicht leer sein")
        return content
        