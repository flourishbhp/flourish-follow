from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

flourish_follow = Navbar(name='flourish_follow')
no_url_namespace = True if settings.APP_NAME == 'flourish_follow' else False

flourish_follow.append_item(
    NavbarItem(name='assignments',
               label='Assignements',
               fa_icon='fa-cogs',
               url_name='flourish_follow:home_url'))

flourish_follow.append_item(
    NavbarItem(
        name='worklist',
        title='Worklist',
        label='Worklist',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'flourish_follow_listboard_url'],
        no_url_namespace=no_url_namespace))

flourish_follow.append_item(
    NavbarItem(
        name='appointments',
        title='appointments',
        label='appointments',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'flourish_follow_appt_listboard_url'],
        no_url_namespace=no_url_namespace))

site_navbars.register(flourish_follow)
