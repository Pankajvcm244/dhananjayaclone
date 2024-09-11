from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': False,
		'fieldname': 'donor_creation_request',
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Donor','Donation Receipt']
			}
		]
	}
