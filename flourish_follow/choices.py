from edc_constants.constants import NOT_APPLICABLE, YES, NO, DWTA, OTHER


APPT_GRADING = (
    ('firm', 'Firm appointment'),
    ('weak', 'Possible appointment'),
    ('guess', 'Estimated by RA'),
)

APPT_LOCATIONS = (
    ('home', 'At home'),
    ('work', 'At work'),
    ('telephone', 'By telephone'),
    ('clinic', 'At clinic'),
    ('OTHER', 'Other location'),
)

APPT_REASONS_UNWILLING = (
    ('not_interested', 'Not interested in participating'),
    ('busy', 'Busy during the suggested times'),
    ('away', 'Out of town during the suggested times'),
    ('unavailable', 'Not available during the suggested times'),
    (DWTA, 'Prefer not to say why I am unwilling.'),
    (OTHER, 'Other reason ...'),
)

CONTACT_FAIL_REASON = (
    ('no_response', 'Phone rang, no response but voicemail left'),
    ('no_response_vm_not_left', 'Phone rang no response and no option to leave voicemail'),
    ('disconnected', 'Phone did not ring/number disconnected'),
    ('number_changed', 'No longer the phone number of BHP participant'),
    (NOT_APPLICABLE, 'Not Applicable'),
)

LOCATION_FOR_CONTACT = (
    ('physical_address', 'Physical Address with detailed description'),
    ('workplace_location', 'Name and location of workplace'),
    ('contact_person', 'Full physical address '),
)

MAY_CALL = (
    (YES, 'Yes, we may continue to contact the participant.'),
    (NO, 'No, participant has asked NOT to be contacted again.'),
)

UNSUCCESSFUL_VISIT = (
    ('no_one_was_home', 'No one was home'),
    ('location_no_longer_used', 'Previous BHP participant no longer uses this location'),
    (OTHER, 'Other'),
)
