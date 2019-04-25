from django.apps import AppConfig


class ElearningConfig(AppConfig):
    name = 'eLearning'
    verbose_name = 'E-Learning'

    def ready(self):
        import eLearning.signals
