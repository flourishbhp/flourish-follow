from django.db.models.constants import LOOKUP_SEP


class WorkListQuerysetViewMixin:

    worklist_queryset_lookups = []

    @property
    def worklist_lookup_prefix(self):
        worklist_lookup_prefix = LOOKUP_SEP.join(self.worklist_queryset_lookups)
        return f'{worklist_lookup_prefix}__' if worklist_lookup_prefix else ''

    def add_username_filter_options(self, options=None, **kwargs):
        """Updates the filter options to limit the plots returned
        to those in the current username.
        """
        username = self.request.user.username
        options.update(
            {f'{self.worklist_lookup_prefix}assigned': username})
        return options

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        options = self.add_username_filter_options(
            options=options, **kwargs)
        return options
