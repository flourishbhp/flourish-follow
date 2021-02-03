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
    ('subject_work_place', 'Name and location of workplace'),
    ('indirect_contact_physical_address', 'Indirect contact address'),
)

LOCATION_SUCCESS = (
    ('physical_address', 'Physical Address with detailed description'),
    ('subject_work_place', 'Name and location of workplace'),
    ('indirect_contact_physical_address', 'Indirect contact address '),
    ('none_of_the_above', 'None of the above'),
)

MAY_CALL = (
    (YES, 'Yes, we may continue to contact the participant.'),
    (NO, 'No, participant has asked NOT to be contacted again.'),
    (NOT_APPLICABLE, 'Not Applicable')
)

UNSUCCESSFUL_VISIT = (
    ('no_one_was_home', 'No one was home'),
    ('location_no_longer_used', 'Previous BHP participant no longer uses this location'),
    (NOT_APPLICABLE, 'Not Applicable'),
    (OTHER, 'Other'),
)

HOME_VISIT = (
    (NOT_APPLICABLE, 'Not Applicable'),
    ('never_answer', 'Decide to do home visit because the phone is never answered'),
    ('requested_home_visit', 'Participants prefers/requested a home visit'),
    (OTHER, 'Other reason ...'),
)

PHONE_SUCCESS = (
    ('subject_cell', 'subject_cell'),
    ('subject_cell_alt', 'subject_cell_alt'),
    ('subject_phone', 'subject_phone'),
    ('subject_phone_alt', 'subject_phone_alt'),
    ('subject_work_phone', 'subject_work_phone'),
    ('indirect_contact_cell', 'indirect_contact_cell'),
    ('indirect_contact_phone', 'indirect_contact_phone'),
    ('caretaker_cell',  'caretaker_cell'),
    ('caretaker_tel', 'caretaker_tel'),
    ('none_of_the_above', 'None of the above'),
)


PHONE_USED = (
    ('subject_cell', 'subject_cell'),
    ('subject_cell_alt', 'subject_cell_alt'),
    ('subject_phone', 'subject_phone'),
    ('subject_phone_alt', 'subject_phone_alt'),
    ('subject_work_phone', 'subject_work_phone'),
    ('indirect_contact_cell', 'indirect_contact_cell'),
    ('indirect_contact_phone', 'indirect_contact_phone'),
    ('caretaker_cell',  'caretaker_cell'),
    ('caretaker_tel', 'caretaker_tel'),
)
