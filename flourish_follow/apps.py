from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'flourish_follow'
    admin_site_name = 'flourish_follow_admin'
