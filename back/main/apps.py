from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Django app config for main.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        # подключаю сигналы
        import main.signals
