from django.apps import AppConfig


class MainConfig(AppConfig):
    """
    Django app config for main.
    """
    name = 'main'

    def ready(self):

        # подключаю сигналы
        import main.signals
