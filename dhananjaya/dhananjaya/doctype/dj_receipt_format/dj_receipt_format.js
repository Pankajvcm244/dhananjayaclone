// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("DJ Receipt Format", {
    setup(frm) {
        frm.get_field("sample").html(SAMPLE_HTML);
    },
});

const SAMPLE_HTML = `<h3>Receipt Format Help</h3>
<p>Receipt format have 3 variables to use them in jinja scripting</p>
<ol>
  <li>Receipt Document (doc)</li>
  <li>Dhananjaya Settings (settings)</li>
  <li>Donor Data (donor)</li>
</ol>
<h6>Dhananjaya Settings (settings) Fields Sample</h6>
<pre><code>
{
    'owner': 'nrhd@hkm-group.org',
    'company': 'Hare Krishna Movement Jaipur',
    'preacher_allowed_receipt_creation': 1,
    'auto_create_journal_entries': 1,
    'donation_account': 'General Donation. - HKMJ',
    'cash_account': 'Cash From Donation - HKMJ',
    'bank_account': 'HKMJ - 1781220613087427 - AU Small Finance Bank',
    'gateway_expense_account': None,
    'credit_value': 100,
    'logo': '/files/logo hkmj.png',
    'seal': '/files/seal hkmj.png',
    'contact_address': 'C-6 to C-11, Mahal Yojna, Jagatpura, Jaipur - 302017',
    'contact_no': '8696139922',
    'contact_email': 'donorcare@hkmjaipur.org',
    'company_tagline': 'A non-profit charitable trust registered in Jaipur, India.&#x3C;br&#x3E; 24/09/21 &#x3C;br&#x3E;PAN No. : AAATH7322Q &#x3C;br&#x3E; CSR Registration No. : CSR00002414',
    'authority_name': 'Amitasana Dasa',
    'authority_position': 'President',
    'authority_signature': '/files/aap_signature.png',
    'atg_lines': 'Donations to this Institution is exempt u/s 80G vide&#x3C;br&#x3E;\nO:IT Com./Jai/II/IT Com/ Registration Date : 24/09/21&#x3C;br&#x3E;\nRegistration No : AAATH7322QF2021801&#x3C;br&#x3E;\nPAN : AAATH7322Q&#x3C;br&#x3E;',
    'thanks_note': ''}
</code></pre>

<h6>Donor Data (donor) Fields Sample</h6>
<pre><code>
{'full_name': 'Nitin Jain',
  'pan_no': 'AALDB0488Q',
  'aadhar_no': None,
  'address': '3/518, Shivanand Marg, Malviya Nagar, Jaipur, Jaipur, Rajasthan - 302017',
  'contact': '6375897613',
  'email': '',
  'money_in_words': 'Rupees Two Thousand, One Hundred only.',
  'reference_number': 'CMS/ NEFT PAYMENT INFIBEAM AVENUES LTD/ICICI BANK',
  'preacher_full_name': 'DMT',
  'preacher_mobile_no': None}
</code></pre>`;

