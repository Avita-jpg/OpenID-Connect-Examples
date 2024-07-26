from django.apps import AppConfig
from constance.apps import ConstanceConfig
from constance.signals import config_updated

# change label for Constance configuration view in admin page
class CustomConstance(ConstanceConfig):
    verbose_name = "Open ID Connect"

class AuthappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'

    


  