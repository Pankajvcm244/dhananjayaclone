from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': False,
		'fieldname': 'llp_preacher',
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Donor','Patron']
			}
		]
	}

