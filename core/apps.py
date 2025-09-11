from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

# Configure default auto field outside the class to satisfy type checkers
setattr(CoreConfig, "default_auto_field", "django.db.models.BigAutoField")
