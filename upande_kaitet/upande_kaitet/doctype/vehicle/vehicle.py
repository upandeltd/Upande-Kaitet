import frappe
from frappe.model.document import Document
from pytz import UTC, timezone


class Vehicle(Document):
	def onload(self):
		if not self.imei:
			return

		# Get latest GPS Reading
		reading = frappe.get_all(
			"GPS Reading",
			filters={
				"imei": self.imei,
				"latitude": ["not in", [None, "", 0]],
				"longitude": ["not in", [None, "", 0]],
			},
			fields=["latitude", "longitude", "creation"],
			order_by="creation desc",
			limit=1,
		)

		if reading:
			r = reading[0]
			self.latitude = float(r["latitude"])
			self.longitude = float(r["longitude"])
			self.timestamp = r["creation"]
