import frappe
import mysql.connector

def run_query(query):
	settings = frappe.get_cached_doc("Dhananjaya Import Settings")
	mydb = mysql.connector.connect(
		host=settings.host,
		user=settings.mysql_user,
		password=settings.mysql_password,
		database=settings.database_name
	)
	cursor = mydb.cursor(dictionary=True)
	cursor.execute(query)
	data = cursor.fetchall()
	return data