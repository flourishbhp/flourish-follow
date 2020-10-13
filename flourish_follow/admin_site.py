from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = 'Flourish Follow'
    site_header = 'Flourish Follow'
    index_title = 'Flourish Follow'
    site_url = '/flourish_follow/list/'


flourish_follow_admin = AdminSite(name='flourish_follow_admin')
