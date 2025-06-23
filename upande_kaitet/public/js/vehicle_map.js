frappe.pages['vehicle-map'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Vehicle Map View',
		single_column: true
	});

	// Load Leaflet CSS
	const leafletCSS = document.createElement('link');
	leafletCSS.rel = 'stylesheet';
	leafletCSS.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
	document.head.appendChild(leafletCSS);

	// Add map container
	$(wrapper).find('.layout-main-section').html(`<div id="vehicle-map" style="height: 600px;"></div>`);

	// Load JS
	frappe.require(["https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"], function () {
		render_vehicle_map();
	});
};

function render_vehicle_map() {
	const map = L.map('vehicle-map').setView([-1.2921, 36.8219], 6); // Nairobi default

	L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '© OpenStreetMap contributors',
		maxZoom: 18,
	}).addTo(map);

	frappe.call({
		method: 'upande_kaitet.api.get_all_vehicle_locations',
		callback: function (r) {
			if (!r.message || r.message.length === 0) {
				frappe.msgprint("No vehicle locations found.");
				return;
			}

			let bounds = [];

			r.message.forEach(vehicle => {
				let lat = parseFloat(vehicle.latitude);
				let lon = parseFloat(vehicle.longitude);

				if (!isNaN(lat) && !isNaN(lon)) {
					const latlng = [lat, lon];
					const marker = L.marker(latlng).addTo(map);

					marker.bindTooltip(
						`<strong>Plates:</strong> ${vehicle.plates}<br><strong>Make:</strong> ${vehicle.make}`,
						{
							direction: 'top',
							offset: [0, -10],
							opacity: 0.9,
							sticky: true
						}
					);

					bounds.push(latlng);
				}
			});

			if (bounds.length) {
				map.fitBounds(bounds);
			}
		}
	});
}
