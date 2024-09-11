// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Donor Creation Request", {
  onload: function (frm) {
    frm.events.get_similar_donors(frm);
  },
  refresh: function (frm) {
    if (frm.doc.status == "Open") {
      frm.add_custom_button("Create Donor", function () {
        frappe.call({
          freeze: true,
          method:
            "dhananjaya.dhananjaya.doctype.donor_creation_request.donor_creation_request.get_donor_from_request",
          args: {
            request: frm.doc.name,
          },
          callback: function (r) {
            if (!r.exc) {
              var doc = frappe.model.sync(r.message);
              frappe.set_route("Form", doc[0].doctype, doc[0].name);
            }
          },
        });
      });
      frm.add_custom_button("Update Donor", function () {
        frappe.prompt(
          {
            label: "Donor",
            fieldname: "donor",
            fieldtype: "Link",
            options: "Donor",
          },
          (values) => {
            console.log(values.donor);
            frappe.call({
              freeze: true,
              method:
                "dhananjaya.dhananjaya.doctype.donor_creation_request.donor_creation_request.update_donor",
              args: {
                donor: values.donor,
                request: frm.doc.name,
              },
            });
          }
        );
      });
    }
  },

  donor_set() {
    frappe.msgprint("dddd");
  },

  get_similar_donors(frm) {
    frappe.call({
      method:
        "dhananjaya.dhananjaya.doctype.donor_creation_request.donor_creation_request.get_similar_donors",
      args: {
        request: frm.doc.name,
      },
      callback: function (r) {
        if (!r.exc) {
          console.log(r.message);
          var html = frm.events.get_html_data(frm, r.message);
          frm.set_df_property("similar_donors_view", "options", html);
        }
      },
    });
  },
  get_html_data(frm, data) {
    // var data = JSON.parse(data);
    var data_html = "";
    console.log(typeof data);
    for (let key in data) {
      var section_data = "";
      for (let d_key in data[key]) {
        let donor_data = data[key][d_key];
        section_data += `
                          <tr>
                            <td>${d_key}</td>
                            <td>${donor_data["donor_name"]}</td>
                            <td>${donor_data["contact"]}</td>
                            <td>${donor_data["address"]}</td>
                            <td><a style = "text-decoration:none;" href = "/app/donor/${d_key}"> 🔗 </a></td>
                          </tr>
                          `;
      }

      data_html += `
                      <h4>${key.toUpperCase()}</h4>
                      <table>
                        <tr>
                          <td>Donor ID</td>
                          <td>Donor Name</td>
                          <td>Donor Contact</td>
                          <td>Donor Address</td>
                          <td>Link</td>
                        <tr>
                        ${section_data}
                      </table>
                      <br><br>`;
    }
    return (
      `
            <style>
              table, th, td {
                border: 1px solid black;
                padding: 5px;
              }
            </style>
            ` + data_html
    );
  },
});
