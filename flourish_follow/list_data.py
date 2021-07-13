from edc_constants.constants import OTHER, DWTA

from edc_list_data import PreloadData

list_data = {
    'flourish_follow.reasonsunwilling': [
        ('not_interested', 'Caregiver not interested in participating'),
        ('busy', 'Busy during the suggested times'),
        ('away', 'Out of town during the suggested times'),
        ('unavailable', 'Not available during the suggested times'),
        (DWTA, 'Caregiver prefer not to say why I am unwilling.'),
        ('busy_dwtp', 'Caregiver is busy and does not want to participate'),
        ('doesnt_live_in_area', 'Caregiver does not live in study area'),
        ('wont_disclose_status_to_child',
         'Caregiver is not willing to disclose status to their child'),
        ('child_not_lwh',
         'Caregiver feels that child is not living with HIV and does not see '
         'a need to join the study'),
        ('doesnt_want_to_join', 'Caregiver does not want to join another study'),
        ('work_constraints', 'Caregiver has work constraints'),
        ('fears_joining', 'Caregiver has fears of joining study/traveling during COVID'),
        ('partner_refused', 'Caregiver’s partner does not want/allow them to participate '),
        ('other_appts', 'Caregiver has many other doctor appointments'),
        ('fears_stigma', 'Caregiver fears stigmatization'),
        ('child_busy', 'Child is busy and does not want to participate'),
        ('child_not_interested', 'Child is not interested in joining study'),
        ('child_doesnt_live_in_area', 'Child does not live in study area'),
        ('child_fears_joining', 'Child has fears of joining study/traveling during COVID'),
        ('child_other_appts', 'Child has many other doctor appointments'),
        ('child_fears_stigma', 'Child fears stigmatization'),
        ('child_dead', 'Child is late (has passed away)'),
        ('caregiver_unwilling',
         'Biological mother is late (has passed away), and caregiver is unwilling'),
        ('child_is_unwilling', 'Child is unwilling and prefers not to say why'),
        (OTHER, 'Other reason ...'),
    ],
}

preload_data = PreloadData(
    list_data=list_data)
