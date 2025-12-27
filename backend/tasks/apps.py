from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    
    def ready(self):
        """
        Initialize app. Import signals to register handlers.
        Called when Django app is ready.
        """
        from . import signals  # noqa: F401
