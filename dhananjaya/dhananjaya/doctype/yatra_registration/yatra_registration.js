// Copyright (c) 2024, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Yatra Registration", {
  refresh(frm) {
    frm.set_query("seva_subtype", () => {
      return {
        filters: {
          is_a_yatra: 1,
          enabled: 1,
        },
      };
    });
    frm.set_query("donor_creation_request", () => {
      return {
        filters: {
          status: "Open",
        },
      };
    });
  },
});
