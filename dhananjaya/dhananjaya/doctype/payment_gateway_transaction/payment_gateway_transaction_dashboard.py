from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'heatmap': False,
		'fieldname': 'payment_gateway_document',
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Donation Receipt']
			}
		]
	}
