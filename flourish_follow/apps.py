from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'flourish_follow'
    verbose_name = 'Flourish Follow'
    admin_site_name = 'flourish_follow_admin'
