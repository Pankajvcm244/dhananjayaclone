# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt
import erpnext
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
)
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
import frappe.utils
from .templates import prepare_email_body
from dhananjaya.dhananjaya.doctype.pg_upload_batch.pg_upload_batch import (
    refresh_pg_upload_batch,
)
from .validations import (
    validate_kind_donation,
    validate_donation_account,
    validate_modes_account,
    validate_atg_required,
    validate_donor,
    validate_yatra_required,
    validate_govt_laws,
    validate_cheque_details,
    validate_cheque_screenshot,
    validate_reference_number,
)

from .notifications import (
    notify_mobile_app_users,
)

from dhananjaya.dhananjaya.utils import (
    get_best_contact_address,
    get_company_defaults,
    get_pdf_dr,
    get_preacher_users,
    get_preachers,
    is_donor_kyc_available,
    is_donor_request_kyc_available,
)
import frappe
from frappe import _, sendmail
from frappe.model.naming import getseries
from frappe.utils import money_in_words, today, unique, get_link_to_form
from frappe.model.naming import make_autoname

# from erpnext.controllers.accounts_controller import AccountsController
from datetime import datetime
from frappe.model.document import Document
from frappe.utils.data import getdate
from .constants import (
    CASH_PAYMENT_MODE,
    TDS_PAYMENT_MODE,
    PAYMENT_GATWEWAY_MODE,
    CHEQUE_MODE,
    CONSUMABLE,
)


class DonationReceipt(AccountsController):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        additional_charges: DF.Currency
        address: DF.Data | None
        amended_from: DF.Link | None
        amount: DF.Currency
        asset_item: DF.Link | None
        asset_location: DF.Link | None
        atg_required: DF.Check
        auto_generated: DF.Check
        bank_account: DF.Link | None
        bank_name: DF.Data | None
        bank_transaction: DF.Link | None
        bank_transaction_description: DF.SmallText | None
        bounce_transaction: DF.Link | None
        cash_account: DF.Link | None
        cash_received_date: DF.Date | None
        cheque_branch: DF.Data | None
        cheque_date: DF.Date | None
        cheque_number: DF.Data | None
        company: DF.Link
        company_abbreviation: DF.Data | None
        contact: DF.Data | None
        cost_center: DF.Link | None
        donation_account: DF.Link | None
        donor: DF.Link | None
        donor_creation_request: DF.Link | None
        donor_creation_request_name: DF.Data | None
        ecs_rejection_reason: DF.Data | None
        ecs_transaction_id: DF.Data | None
        email: DF.Data | None
        full_name: DF.Data | None
        gateway_expense_account: DF.Link | None
        ifsc_code: DF.Data | None
        is_csr: DF.Check
        is_ecs: DF.Check
        kind_type: DF.Literal["", "Consumable", "Asset"]
        old_ar_date: DF.Date | None
        old_ar_no: DF.Data | None
        old_dr_no: DF.Data | None
        old_ins_account_number: DF.Data | None
        old_ins_bank: DF.Data | None
        old_ins_date: DF.Date | None
        old_ins_number: DF.Data | None
        old_receipt_date: DF.Date | None
        patron: DF.Link | None
        patron_name: DF.Data | None
        payment_gateway_document: DF.Link | None
        payment_method: DF.Link
        payment_screenshot: DF.AttachImage | None
        preacher: DF.Link | None
        print_remarks_on_receipt: DF.Check
        project: DF.Link | None
        receipt_date: DF.Date | None
        receipt_series: DF.Data | None
        reference_no: DF.Data | None
        remarks: DF.Text | None
        seva_subtype: DF.Link | None
        seva_type: DF.Link
        sevak_name: DF.Data | None
        stock_expense_account: DF.Link | None
        tds_account: DF.Link | None
        user_remarks: DF.Text | None
        yatra_registration: DF.Link | None

    # end: auto-generated types
    def autoname(self):

        self.company_abbreviation = frappe.get_cached_value(
            "Company", self.company, "abbr"
        )

        if self.name:
            return
        elif self.receipt_series:
            self.name = make_autoname(self.receipt_series, "", self)
        else:
            year = datetime.now().strftime("%y")
            month = datetime.now().strftime("%m")
            prefix = f"{self.company_abbreviation}-DR{year}{month}-"
            self.name = prefix + getseries(prefix, 4)

    def validate(self):
        self.flags.is_new_doc = self.is_new()
        self.flags.kyc_available = self.is_kyc_available()
        validate_donor(self)
        validate_atg_required(self)
        validate_govt_laws(self)
        validate_yatra_required(self)
        validate_cheque_details(self)
        # Hundi Donations are to be separately managed by accounts
        # validate_cheque_screenshot(self) # Need to change in API before uncommenting this as screenshot is uploaded post creation
        # validate_reference_number(self)
        return

    def is_kyc_available(self):
        kyc_available = False
        if self.donor:
            kyc_available = is_donor_kyc_available(self.donor)
        elif self.donor_creation_request:
            kyc_available = is_donor_request_kyc_available(self.donor_creation_request)
        return kyc_available

    def is_kind_donation(self):
        return frappe.get_cached_value(
            "DJ Mode of Payment", self.payment_method, "kind"
        )

    ###### ON CHANGE TRIGGERS ON EVERY CHANGE ON SAVE, SUBMIT & AFTER SUBMIT ALSO ######
    ###### UPDATE JOURNAL ENTRY & GL ENTRIES ON SEVA TYPE CHANGE #######################
    ###### UPDATE PAYMENT GATEWAY TRANSACTION ALSO TO HAVE SAME DONOR & SEVA TYPE ######
    def on_change(self):
        if self.has_value_changed("workflow_state"):
            notify_mobile_app_users(self)
        if self.docstatus == 1:
            # Update the same Donor in Payment Gateway Transaction also, if changed.
            if self.has_value_changed("donor"):
                frappe.db.set_value(
                    "Payment Gateway Transaction",
                    self.payment_gateway_document,
                    "donor",
                    self.donor,
                )
            ####
            # if self.has_value_changed("seva_type"):
            #     self.on_change_seva_type()  # Use Only in Emergency Cases.
            ## TODO First check the impact of both GL Entry & Payment Ledger Entry
            ###
            if self.has_value_changed("is_csr"):
                settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
                if settings_doc.separate_accounting_for_csr:
                    frappe.throw(
                        "Not allowed to change CSR after submission as there is accounting based on it."
                    )
        return

    #######################################################

    # Update Accounts in Journal Entry & General Ledger, if changed.
    ## What is updated:
    ## > Journal Entry
    ## 1. Journal Entry Account
    ## 2. GL Entry
    ## 3. User Remarks
    ## 4. Title
    ## > Donation Receipt
    ## 1. Seva Type
    ## 2. Donation Account
    ## > Payment Gateway Transaction
    ## 1. Seva Type

    def on_change_seva_type(self):
        frappe.db.set_value(
            "Payment Gateway Transaction",
            self.payment_gateway_document,
            "seva_type",
            self.seva_type,
        )

        company_detail = get_company_defaults(self.company)
        if company_detail.auto_create_journal_entries:
            seva_doc = frappe.get_cached_doc("Seva Type", self.seva_type)

        if not seva_doc.account:
            frappe.throw(("No Account associated with this Seva Type."))

        old_doc = self.get_doc_before_save()
        if not old_doc:
            return
        old_seva_type, old_account = old_doc.seva_type, old_doc.donation_account
        new_seva_type, new_account = self.seva_type, seva_doc.account
        frappe.db.sql(
            f"UPDATE `tabDonation Receipt` SET donation_account = '{new_account}' WHERE name = '{self.name}'"
        )

        jes = frappe.get_all(
            "Journal Entry", filters={"donation_receipt": self.name}, pluck="name"
        )

        if jes:
            jes_str = ",".join(jes)
            frappe.db.sql(
                f"""
                        UPDATE `tabJournal Entry Account`
                        SET account = '{new_account}'
                        WHERE 
                            account = '{old_account}'
                            AND parent IN ('{jes_str}')
                        """
            )
            frappe.db.sql(
                f"""
                        UPDATE `tabGL Entry`
                        SET account = '{new_account}'
                        WHERE voucher_no IN ('{jes_str}') AND account = '{old_account}'
                        """
            )
            for je in jes:
                remarks = frappe.get_value("Journal Entry", je, "user_remark")
                if remarks:
                    frappe.db.set_value(
                        "Journal Entry",
                        je,
                        {
                            "title": new_account,
                            "user_remark": remarks.replace(
                                old_seva_type, new_seva_type
                            ),
                        },
                    )
        frappe.db.commit()

    ################################################################
    ###### BEFORE SAVE : SETTINGS DEFAULT ACCOUNTS OF COMPANY ######

    def before_save(self):
        validate_yatra_required(self)
        self.set_receipt_date()
        self.amount_in_words = money_in_words(self.amount, main_currency="Rupees")
        company_detail = get_company_defaults(self.company)
        # Check for Preacher Change
        if (
            not self.flags.is_new_doc
            and self.has_value_changed("preacher")
            and "DCC Manager" not in frappe.get_roles()
        ):
            frappe.throw(
                "Only DCC Manager is allowed to change the Preacher of a Donor."
            )

        if (not self.contact) or (not self.address):
            address, contact, email = get_best_contact_address(self.donor)
            self.contact = "" if contact is None else contact
            self.address = "" if address is None else address
        ## Setting Default Accounts in Receipt

        if not self.donation_account:
            separate_accounting_for_csr = frappe.db.get_single_value(
                "Dhananjaya Settings", "separate_accounting_for_csr"
            )
            if separate_accounting_for_csr and self.is_csr:
                account = frappe.db.get_value(
                    "Seva Type", self.seva_type, "csr_account"
                )
                if not account:
                    frappe.throw(
                        f"There is no CSR Account setup for Seva Type {self.seva_type}."
                    )
            else:
                account = frappe.db.get_value("Seva Type", self.seva_type, "account")

            if account is None:
                self.donation_account = company_detail.donation_account
            else:
                self.donation_account = account

        if not self.bank_account:
            self.bank_account = company_detail.bank_account
        if self.payment_method == CASH_PAYMENT_MODE and not self.cash_account:
            cash_account = frappe.db.get_value(
                "Seva Type", self.seva_type, "cash_account"
            )
            if cash_account:
                self.cash_account = cash_account
            else:
                self.cash_account = company_detail.cash_account
        if (
            self.payment_method == PAYMENT_GATWEWAY_MODE
            and not self.gateway_expense_account
        ):
            self.gateway_expense_account = company_detail.gateway_expense_account

        ## Setting Cost Center:
        self.update_accounting_dimensions()
        # if not self.cost_center:
        #     if self.seva_subtype:
        #         seva_subtype_doc = frappe.get_cached_doc(
        #             "Seva Subtype", self.seva_subtype
        #         )
        #         for c in seva_subtype_doc.cost_centers:
        #             if c.company == self.company:
        #                 self.cost_center = c.cost_center
        #                 break

    def set_receipt_date(self):
        """
        1. No Need to update if Receipt Date is already set
        2. Use today for CASH, KIND Donations
        3. For GATEWAY Payments
            -> This will be used only while making receipts manually. So the date will be updated later based on below priorities:
            a.  Auto Reconcillation from PG Upload Batch
            b.  From Bank Transaction
        4. For NEFT/RTGS/UPI Payments
            -> Initially it will be today but on realisation will be updated to Bank Transaction Date
        ##TODO : Insert these logics on Realization Workflow
        """
        if self.payment_method == CHEQUE_MODE:
            self.receipt_date = self.cheque_date
        elif not self.receipt_date:
            self.receipt_date = today()

    def refactor_receipt_date(self):
        "Method required to correct the receipt date based on the bank transaction date."

        if (
            self.payment_method in [CASH_PAYMENT_MODE, TDS_PAYMENT_MODE]
            or self.is_kind_donation()
        ):
            return
        else:
            bank_tx_date = frappe.get_value(
                "Bank Transaction", self.bank_transaction, "date"
            )
            if bank_tx_date:
                if self.payment_method == CHEQUE_MODE:
                    self.receipt_date = self.cheque_date
                    if self.receipt_date > bank_tx_date:
                        frappe.throw(
                            "Receipt Date cannot be greater than Bank Transaction Date in case of Cheque."
                        )
                elif self.payment_method == PAYMENT_GATWEWAY_MODE:
                    if not self.payment_gateway_document:
                        self.receipt_date = bank_tx_date
                else:
                    self.receipt_date = bank_tx_date

        return

    ###### UPDATE WORKFLOW STATE FROM 'SUSPENSE' TO 'REALIZED' ON ENTERING THE RIGHT DONOR ######
    # _saving_flag = False

    # def on_update_after_submit(self):
    #     if not self._saving_flag:
    #         self._saving_flag = True
    #         if self.donor:
    #             self.db_set("workflow_state", "Realized", update_modified=True)
    #         self.save()
    #         self._saving_flag = False

    ###### BEFORE SUBMIT : CHECK WHETHER REQUIRED ACCOUNTS ARE SET ######

    def before_submit(self):
        self.refactor_receipt_date()
        self.cost_center = (
            self.cost_center or erpnext.get_default_cost_center(self.company),
        )
        validate_kind_donation(self)
        company_detail = get_company_defaults(self.company)
        if not company_detail.auto_create_journal_entries:
            return
        validate_donation_account(self)
        validate_modes_account(self)
        validate_yatra_required(self)
        return

    ###### ON INSERT : AUTO CREATE JOURNAL ENTRY CHECK ######

    def on_submit(self):
        company_detail = get_company_defaults(self.company)
        settings_doc = frappe.get_cached_doc("Dhananjaya Settings")
        is_kind_mode = self.is_kind_donation()
        if company_detail.auto_create_journal_entries:
            # je_doc = self.create_journal_entry()
            self.make_gl_entries()
            if self.payment_method not in (CASH_PAYMENT_MODE, TDS_PAYMENT_MODE) and (
                not is_kind_mode
            ):
                self.reconcile_bank_transaction()

            if (
                self.payment_method == PAYMENT_GATWEWAY_MODE
                and self.payment_gateway_document
            ):
                self.reconcile_gateway_transaction()

        if is_kind_mode and self.asset_item:
            asset_name = self.make_asset()
            asset_link = get_link_to_form("Asset", asset_name)
            frappe.msgprint(f"Asset Created : {asset_link}", alert=True)
        # frappe.errprint(self.receipt_date)
        # frappe.errprint(self.receipt_date)
        # frappe.throw("ERROR")

    #
    def make_asset(self, is_grouped_asset=False):
        item_doc = frappe.get_doc("Item", self.asset_item)
        if not self.asset_location:
            frappe.throw("Enter location for the asset")
        asset = frappe.get_doc(
            {
                "doctype": "Asset",
                "item_code": self.asset_item,
                "asset_name": item_doc.item_name,
                "naming_series": item_doc.asset_naming_series or "AST",
                "asset_category": item_doc.asset_category,
                "location": self.asset_location,
                "company": self.company,
                "donation_receipt": self.name,
                "calculate_depreciation": 0,
                "is_existing_asset": 1,
                "gross_purchase_amount": self.amount,
                "purchase_date": self.receipt_date,
                "available_for_use_date": self.receipt_date,
            }
        )

        asset.flags.ignore_validate = True
        asset.flags.ignore_mandatory = True
        asset.set_missing_values()
        asset.insert()
        return asset.name

    def get_cost_center(self):
        COST_CENTER = None
        if self.seva_subtype:
            subseva_doc = frappe.get_doc("Seva Subtype", self.seva_subtype)
            for c in subseva_doc.cost_centers:
                if c.company == self.company:
                    COST_CENTER = c.cost_center
        if not COST_CENTER:
            COST_CENTER = frappe.db.get_value("Company", self.company, "cost_center")
        return COST_CENTER

    def before_cancel(self):
        frappe.only_for("DCC Manager")

        if self.payment_method == CASH_PAYMENT_MODE:
            frappe.only_for("System Manager")
        super().before_cancel()

    def on_cancel(self):
        self.ignore_linked_doctypes = [
            "GL Entry",
        ]
        super().on_cancel()
        if frappe.db.exists("GL Entry", {"voucher_no": self.name}):
            self.make_gl_entries(cancel=True)
        if self.payment_gateway_document:
            self.unset_payment_gateway()
        if self.asset_item:
            self.cancel_asset()
        self.db_set("workflow_state", "Cancelled")

    def unset_payment_gateway(self):
        frappe.db.set_value(
            "Payment Gateway Transaction",
            self.payment_gateway_document,
            {"receipt_created": 0, "donor": None, "seva_type": None},
        )
        pg_batch = frappe.db.get_value(
            "Payment Gateway Transaction", self.payment_gateway_document, "batch"
        )
        refresh_pg_upload_batch(pg_batch)

    def cancel_asset(self):
        assets = frappe.db.get_all(
            "Asset",
            filters={"donation_receipt": self.name, "docstatus": 1},
            pluck="name",
        )
        if len(assets) > 0:
            asset = assets[0]
            asset_doc = frappe.get_doc("Asset", asset)
            asset_doc.cancel()

    def make_gl_entries(self, cancel=False):
        gl_entries = self.get_gl_entries()
        make_gl_entries(gl_entries, cancel=cancel, merge_entries=False)

    def get_gl_entries(self):
        is_kind_mode = self.is_kind_donation()
        seva_type_doc = frappe.get_cached_doc("Seva Type", self.seva_type)
        company_detail = get_company_defaults(self.company)
        if (not seva_type_doc) or (not seva_type_doc.account):
            frappe.throw(
                _(
                    "Either Seva Type not set or Account is not connected. It is required."
                )
            )

        default_cost_center = self.get_cost_center()

        ## TODO : Below can be eliminated since we don't need donor_name
        if not self.donor:
            if not self.donor_creation_request:
                frappe.throw(
                    "At least one of Donor or Donation Creation Request document is must to process."
                )
            donor_name = frappe.get_value(
                "Donor Creation Request", self.donor_creation_request, "full_name"
            )
        else:
            donor_name = self.full_name

        if self.amount <= 0:
            frappe.throw("Amount can not be Zero.")

        gl_base_entries = []

        if is_kind_mode:
            from erpnext.assets.doctype.asset.asset import (
                is_cwip_accounting_enabled,
            )
            from erpnext.assets.doctype.asset_category.asset_category import (
                get_asset_category_account,
            )

            kind_debit_account = None
            if self.kind_type == CONSUMABLE:
                kind_debit_account = self.stock_expense_account
            else:
                asset_category = frappe.db.get_value(
                    "Item", self.asset_item, "asset_category"
                )
                account_type = (
                    "capital_work_in_progress_account"
                    if is_cwip_accounting_enabled(asset_category)
                    else "fixed_asset_account"
                )
                asset_category_account = get_asset_category_account(
                    account_type, item=self.asset_item, company=self.company
                )
                if not asset_category_account:
                    form_link = get_link_to_form("Asset Category", asset_category)
                    frappe.throw(
                        _("Please set Fixed Asset Account in {} against {}.").format(
                            form_link, self.company
                        ),
                        title=_("Missing Account"),
                    )
                kind_debit_account = asset_category_account

            gl_base_entries.extend(
                [
                    frappe._dict(
                        posting_date=self.receipt_date,
                        account=self.donation_account,
                        credit=self.amount,
                        party_type="Donor",
                        party=self.donor,
                    ),
                    frappe._dict(
                        posting_date=self.receipt_date,
                        account=kind_debit_account,
                        debit=self.amount,
                    ),
                ]
            )
        elif self.payment_method == CASH_PAYMENT_MODE:
            if self.cash_received_date:
                cashier_received_date = self.cash_received_date
            else:
                cashier_received_date = today()

            gl_base_entries.extend(
                [
                    frappe._dict(
                        posting_date=self.receipt_date,
                        account=self.donation_account,
                        credit=self.amount,
                        party_type="Donor",
                        party=self.donor,
                    ),
                    frappe._dict(
                        posting_date=cashier_received_date,
                        account=self.cash_account,
                        debit=self.amount,
                    ),
                ]
            )

            ## Bring in Temporary Ledgers

            if str(self.receipt_date) != str(cashier_received_date):
                gl_base_entries.extend(
                    [
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=company_detail.temporary_cash_account,
                            debit=self.amount,
                        ),
                        frappe._dict(
                            posting_date=cashier_received_date,
                            account=company_detail.temporary_cash_account,
                            credit=self.amount,
                        ),
                    ]
                )
        elif self.payment_method == TDS_PAYMENT_MODE:
            # Jounrnal Entry date should be the receipt date only.

            gl_base_entries.extend(
                [
                    frappe._dict(
                        posting_date=self.receipt_date,
                        account=self.donation_account,
                        credit=self.amount,
                        party_type="Donor",
                        party=self.donor,
                    ),
                    frappe._dict(
                        posting_date=self.receipt_date,
                        account=self.tds_account,
                        debit=self.amount,
                    ),
                ]
            )
        else:
            bank_account_ledger = frappe.get_cached_doc(
                "Bank Account", self.bank_account
            )
            transaction = None
            if self.bank_transaction:
                transaction = frappe.get_doc("Bank Transaction", self.bank_transaction)

            if self.payment_method == CHEQUE_MODE:
                "Temporary Entries will always exist."
                gl_base_entries.extend(
                    [
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=self.donation_account,
                            credit=self.amount,
                            party_type="Donor",
                            party=self.donor,
                        ),
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=company_detail.temporary_cheque_account,
                            debit=self.amount,
                        ),
                        frappe._dict(
                            posting_date=(
                                self.receipt_date
                                if not transaction
                                else transaction.date
                            ),
                            account=company_detail.temporary_cheque_account,
                            credit=self.amount,
                        ),
                        frappe._dict(
                            posting_date=(
                                self.receipt_date
                                if not transaction
                                else transaction.date
                            ),
                            account=bank_account_ledger.account,
                            debit=self.amount,
                        ),
                    ]
                )

            elif self.payment_method == PAYMENT_GATWEWAY_MODE:
                gl_base_entries.extend(
                    [
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=self.donation_account,
                            credit=self.amount,
                            party_type="Donor",
                            party=self.donor,
                        ),
                        frappe._dict(
                            posting_date=(
                                self.receipt_date
                                if not transaction
                                else transaction.date
                            ),
                            account=bank_account_ledger.account,
                            debit=self.amount - self.additional_charges,
                        ),
                    ]
                )
                if self.additional_charges:
                    gl_base_entries.append(
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=self.gateway_expense_account,
                            debit=self.additional_charges,
                        ),
                    )
                ## Bring in Temporary Ledgers
                if transaction and self.receipt_date != transaction.date:
                    gl_base_entries.extend(
                        [
                            frappe._dict(
                                posting_date=self.receipt_date,
                                account=company_detail.temporary_gateway_account,
                                debit=self.amount - self.additional_charges,
                            ),
                            frappe._dict(
                                posting_date=transaction.date,
                                account=company_detail.temporary_gateway_account,
                                credit=self.amount - self.additional_charges,
                            ),
                        ]
                    )
            else:
                gl_base_entries.extend(
                    [
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=self.donation_account,
                            credit=self.amount,
                            party_type="Donor",
                            party=self.donor,
                        ),
                        frappe._dict(
                            posting_date=self.receipt_date,
                            account=bank_account_ledger.account,
                            debit=self.amount,
                        ),
                    ]
                )

        gl_entries = []

        for gb in gl_base_entries:
            gl_entries.append(
                self.get_gl_dict(
                    {
                        **gb,
                        **{"cost_center": self.cost_center, "project": self.project},
                    },
                    item=self,
                )
            )
        return gl_entries

    ###### BANK RECONCILLATION AUTOMATION ######

    ###### Reconciles Bank Transaction with Journal Entry and also updates the Clearance Date in Journal Entry
    def reconcile_bank_transaction(self):
        voucher = {
            "payment_doctype": self.doctype,
            "payment_name": self.name,
            "amount": self.amount
            - (0 if not self.additional_charges else self.additional_charges),
        }
        tx_doc = frappe.get_doc("Bank Transaction", self.bank_transaction)
        add_payment_entry(tx_doc, voucher)

    ###### BANK RECONCILLATION AUTOMATION ######

    # Reconciles Bank Transaction with Journal Entry and also updates the Clearance Date in Journal Entry
    def reconcile_gateway_transaction(self):
        gateway_doc = frappe.get_doc(
            "Payment Gateway Transaction", self.payment_gateway_document
        )
        gateway_doc.donor = self.donor
        gateway_doc.seva_type = self.seva_type
        gateway_doc.receipt_created = 1
        gateway_doc.save()

    def update_accounting_dimensions(self):
        DEFAULTS = None
        if self.seva_subtype:
            DEFAULTS = frappe.get_doc("Seva Subtype", self.seva_subtype).get(
                "cost_centers"
            )
            DEFAULTS = next((c for c in DEFAULTS if c.company == self.company), None)
        if DEFAULTS:
            dimensions = ["cost_center", "project"] + get_accounting_dimensions()
            for dimension in dimensions:
                self.update({dimension: DEFAULTS.get(dimension)})

    # TODO Update Onchnage
    # COST_CENTER = None
    # if self.seva_subtype:
    #     subseva_doc = frappe.get_doc("Seva Subtype", self.seva_subtype)
    #     for c in subseva_doc.cost_centers:
    #         if c.company == self.company:
    #             COST_CENTER = c.cost_center
    # if not COST_CENTER:
    #     COST_CENTER = frappe.db.get_value("Company", self.company, "cost_center")
    # return COST_CENTER
    ###


##TODO: Check if this is needed
def add_payment_entry(tx_doc, voucher):
    "Add the vouchers with zero allocation. Save() will perform the allocations and clearance"
    if voucher["amount"] > tx_doc.unallocated_amount:
        frappe.throw(
            frappe._(
                f"Donation amount is more than Bank Transaction {tx_doc.name}'s unallocated amount ({tx_doc.unallocated_amount})."
            )
        )

    found = False
    for pe in tx_doc.payment_entries:
        if (
            pe.payment_document == voucher["payment_doctype"]
            and pe.payment_entry == voucher["payment_name"]
        ):
            found = True

    if not found:
        pe = {
            "payment_document": voucher["payment_doctype"],
            "payment_entry": voucher["payment_name"],
            "allocated_amount": voucher["amount"],
        }
        tx_doc.append("payment_entries", pe)
    tx_doc.save()


# DONOR SEARCH IN DONATION RECEIPT #
############# BEGIN ################


def get_fields(doctype, fields=None):
    if fields is None:
        fields = []
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and not meta.title_field.strip() in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)


# To Search the Donors based on their name and contact numbers.
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_donor(doctype, txt, searchfield, start, page_len, filters):
    fields = ["name", "full_name", "last_donation"]
    join_stmt = ""
    cond = ""
    if txt.isdigit():
        join_stmt = " left join `tabDonor Contact` dc on dc.parent = donor.name"
        fields.append("dc.contact_no as contact")
        cond += " or dc.contact_no LIKE %(txt)s"
    fields = get_fields(doctype, fields)
    fields[0] = "donor." + fields[0]
    # fields[1] = "CONCAT(IF(donor.is_patron=1,'🅿','')," + fields[1] + ")"
    preachers = get_preachers()
    if preachers:
        cond += (
            " and donor.llp_preacher IN ("
            + (",".join([f"'{p}'" for p in preachers]))
            + ")"
        )
    return frappe.db.sql(
        """
        select {fields} 
        from `tabDonor` donor
        {join_stmt}
        where full_name LIKE %(txt)s
        {cond}
        order by last_donation desc,full_name limit %(page_len)s offset %(start)s
        """.format(
            **{"fields": ", ".join(fields), "cond": cond, "join_stmt": join_stmt}
        ),
        {"txt": "%" + txt + "%", "start": start, "page_len": 40},
    )


############# CLOSE ################
# DONOR SEARCH IN DONATION RECEIPT #


##### PAYMENT GATEWAY PROCESS ####
############ BEGIN ###############


# Process all gateway payments received in a Batch.
@frappe.whitelist()
def process_batch_gateway_payments(batch):
    batch_doc = frappe.get_doc("PG Upload Batch", batch)
    if not (batch_doc.remaining_amount == batch_doc.bank_amount):
        frappe.throw("This Batch processing is not eligible due to amount mismatch.")
    bank_tx_doc = frappe.get_doc("Bank Transaction", batch_doc.bank_transaction)
    payment_txs = frappe.db.get_all(
        "Payment Gateway Transaction",
        filters={
            "batch": batch,
            "receipt_created": 0,
            "seva_type": ["is", "set"],
            "donor": ["is", "set"],
        },
        fields=("*"),
    )
    # # Check if Seva Types are set!
    # for tx in payment_txs:
    #     if not tx["seva_type"]:
    #         frappe.throw("Set Seva Types in all the batch gateway payments.")

    # # Check if Donors & Seva Types are set!
    # for tx in payment_txs:
    #     if not tx["donor"]:
    #         frappe.throw("Set Donor compulsorily in all batch gateway payments.")

    for tx in payment_txs:
        # Best Address Contact
        address, contact, email = get_best_contact_address(tx["donor"])

        seva_doc = frappe.get_cached_doc("Seva Type", tx["seva_type"])
        dr = {
            "doctype": "Donation Receipt",
            "company": batch_doc.company,
            "payment_gateway_document": tx["name"],
            # States as per Donor
            "docstatus": 0,
            "workflow_state": "Draft",
            "donor": tx["donor"],
            # Rest of Data
            "contact": contact,
            "address": address,
            "seva_type": tx["seva_type"],
            "donation_account": seva_doc.account,
            "receipt_date": bank_tx_doc.date,  ##TODO: Actual Date of Payment Gateway Tx to be brought in
            "payment_method": PAYMENT_GATWEWAY_MODE,
            "amount": tx["amount"],
            "additional_charges": tx["fee"],
            "gateway_expense_account": batch_doc.gateway_expense_account,
            "bank_account": batch_doc.bank_account,
            "bank_transaction": batch_doc.bank_transaction,
        }
        dr_doc = frappe.get_doc(dr)
        dr_doc.submit()
        # If Suspense
        if tx["donor"]:
            dr_doc.db_set("workflow_state", "Realized")
        else:
            dr_doc.db_set("workflow_state", "Suspense")
        frappe.db.set_value(
            "Payment Gateway Transaction", tx["name"], "receipt_created", 1
        )

    refresh_pg_upload_batch(batch_doc.name)


############ CLOSE ###############
##### PAYMENT GATEWAY PROCESS ####


##### PAYMENT GATEWAY AUTO REALIZATION ####
############ BEGIN ###############


# Process all gateway payments received in a Batch.
@frappe.whitelist()
def auto_realize_batch_gateway_payments(batch):
    batch_doc = frappe.get_doc("PG Upload Batch", batch)

    if not (batch_doc.remaining_amount == batch_doc.bank_amount):
        frappe.throw("Auto Realization is not eligible due to amount mismatch.")

    if not batch_doc.gateway_expense_account:
        frappe.throw("Please set Gateway Expense Account first.")

    payment_txs = frappe.db.get_all(
        "Payment Gateway Transaction",
        filters={"batch": batch, "receipt_created": 0},
        fields=("*"),
    )

    for tx in payment_txs:
        receipts = frappe.db.sql(
            f"""
                    SELECT name
                    FROM `tabDonation Receipt`
                    WHERE REPLACE(remarks, ' ', '') = '{tx["name"]}'
                    AND workflow_state = 'Acknowledged'
                    AND amount = {tx["amount"]}
                    AND company = '{tx["company"]}'
                        """,
            pluck="name",
        )
        if len(receipts) > 0:
            receipt_doc = frappe.get_doc("Donation Receipt", receipts[0])
            receipt_doc.payment_method = PAYMENT_GATWEWAY_MODE
            receipt_doc.additional_charges = tx["fee"]
            receipt_doc.payment_gateway_document = tx["name"]
            receipt_doc.gateway_expense_account = batch_doc.gateway_expense_account
            receipt_doc.bank_account = batch_doc.bank_account
            receipt_doc.bank_transaction = batch_doc.bank_transaction
            receipt_doc.submit()
            receipt_doc.db_set("workflow_state", "Realized")
            frappe.db.set_value(
                "Payment Gateway Transaction",
                tx["name"],
                {
                    "receipt_created": 1,
                    "donor": receipt_doc.donor,
                    "seva_type": receipt_doc.seva_type,
                },
            )
    refresh_pg_upload_batch(batch_doc.name)


############ CLOSE ###############
##### PAYMENT GATEWAY AUTO REALIZATION ####

########## Send Receipt ##########


@frappe.whitelist()
def send_receipt(dr, recipients=[], send_to_donor=None):
    from frappe.core.doctype.communication.email import make

    dr_doc = frappe.get_doc("Donation Receipt", dr)
    if not recipients:
        recipients = get_preacher_users(dr_doc.preacher)
        if len(recipients) == 0:
            frappe.throw(
                _(
                    f"There is no ERP User set in LLP Preacher Profile of {dr_doc.preacher}"
                )
            )
    ext = ".pdf"
    content = get_pdf_dr(doctype=dr_doc.doctype, name=dr_doc.name, doc=dr_doc)
    out = {"fname": f"{dr_doc.name}" + ext, "fcontent": content}
    attachments = [out]

    sendmail(
        recipients=recipients,
        reference_doctype=dr_doc.doctype,
        reference_name=dr_doc.name,
        subject=f"Heartfelt Thanks for Your Support to {dr_doc.company_abbreviation}!",
        message=prepare_email_body(dr_doc),
        attachments=attachments,
    )
