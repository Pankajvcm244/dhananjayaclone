// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on("Dhananjaya Receipts Export", {
  get_files(frm) {
    frappe.call({
      method:
        "dhananjaya.dhananjaya.doctype.dhananjaya_receipts_export.dhananjaya_receipts_export.get_backup_files",
      callback: function (r) {
        if (!r.exc) {
          console.log(r.message);
          var html = frm.events.get_html_data(frm, r.message);
          frm.set_df_property("files_html", "options", html);
        }
      },
    });
  },
  get_html_data(frm, files) {
    var files_html = "";
    for (let key in files) {
      let file_data = files[key];
      files_html += `
							  <tr>
								<td class="text-center">${parseInt(key) + 1}.</td>
								<td>${file_data["name"]}</td>
								<td><a class="btn btn-xs btn-default" href = "${
                  file_data["link"]
                }"> Download </a></td>
							  </tr>
							  `;
    }

    files_parent_html = `
						  <h4>Backup Files</h4>
						  <table>
							<tr>
							  <td>S.No.</td>
							  <td>File Name</td>
							  <td>File Link</td>
							<tr>
							${files_html}
						  </table>
						  <br><br>
						  `;

    return (
      `
				<style>
				  table, th, td {
					border: 1px solid black;
					padding: 10px;
				  }
				</style>
				` + files_parent_html
    );
  },

  onload: function (frm) {
    frm.trigger("get_files");
  },
  refresh: function (frm) {
    frm.add_custom_button(__("Prepare Zip"), function () {
      frappe.warn(
        "Are you sure you want to proceed?",
        "This action will take sometime. If you already have requested, please wait for that to complete.",
        () => {
          frappe.call({
            method:
              "dhananjaya.dhananjaya.doctype.dhananjaya_receipts_export.dhananjaya_receipts_export.generate_receipts",
            callback: function (r) {
              if (!r.exc) {
                frappe.msgprint(
                  "Task Queued. The links below will be updated on completion of download."
                );
              }
            },
          });
        },
        () => {}
      );
    });
  },
});
