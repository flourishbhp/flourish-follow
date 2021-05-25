from edc_identifier.simple_identifier import SimpleUniqueIdentifier


class ExportIdentifier(SimpleUniqueIdentifier):

    random_string_length = 5
    identifier_type = 'export_identifier'
    template = 'E{device_id}{random_string}'
