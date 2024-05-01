from django.apps import AppConfig


class WebappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webapp'

    # for upload user pic in profile
    
    def ready(self):
        import webapp.signals