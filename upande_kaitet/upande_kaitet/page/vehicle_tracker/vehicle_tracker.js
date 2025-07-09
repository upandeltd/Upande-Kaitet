frappe.pages["vehicle-tracker"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Vehicle Tracker",
		single_column: true,
	});

	$(page.body).append(`
		<style>
			#vehicle-filter-bar {
				position: sticky;
				top: 0;
				z-index: 10;
				background: var(--bg-color);
				padding: 1rem 2rem;
				border-bottom: 1px solid var(--gray-200);
				margin-bottom: 1rem;
				border-radius: 8px;
			}
			#vehicle-map-container {
				height: 600px;
				overflow: hidden;
			}
			#vehicle-map {
				height: 100%;
				width: 100%;
				border-radius: 8px;
			}
			@media (max-width: 768px) {
				#vehicle-filter-bar {
					padding: 1rem;
				}
			}
		</style>

		<div id="vehicle-filter-bar" class="frappe-card">
			<div class="container">
				<div class="row g-3 align-items-end">
					<div class="col-md-3">
						<label for="start-date" class="form-label">Select Date</label>
						<input type="date" id="start-date" class="form-control">
					</div>
					<div class="col-md-3">
						<label for="vehicle-select" class="form-label">Vehicle</label>
						<select id="vehicle-select" class="form-select"></select>
					</div>
				</div>
			</div>
		</div>

		<div id="vehicle-map-container" class="frappe-card p-2">
			<div id="vehicle-map"></div>
		</div>
	`);

	// Set today's date on load
	const today = new Date();
	$("#start-date").val(today.toISOString().split("T")[0]);

	function load_leaflet(callback) {
		if (typeof L === "undefined") {
			frappe.require([
				"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
				"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
			], callback);
		} else {
			callback();
		}
	}

	function populate_vehicle_dropdown() {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Vehicle",
				fields: ["name"],
				limit_page_length: 100,
			},
			callback: function (r) {
				const select = $("#vehicle-select");
				select.append(`<option value="">All Vehicles</option>`);
				(r.message || []).forEach((vehicle) => {
					select.append(`<option value="${vehicle.name}">${vehicle.name}</option>`);
				});
			},
		});
	}
/*
	function render_map(data, showTrail = false) {
		if (window.vehicleMap) window.vehicleMap.remove();
		$("#vehicle-map").empty();

		const map = L.map("vehicle-map", {
			zoom: 7,
			minZoom: 6,
			maxBounds: [[-5, 33], [5, 42]],
			maxBoundsViscosity: 1.0,
		});
		window.vehicleMap = map;

		const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution: "&copy; OpenStreetMap contributors",
		});

		const satellite = L.tileLayer(
			"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
			{
				attribution:
					"Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
			}
		);

		osm.addTo(map); // Default
		L.control.layers({ "OpenStreetMap": osm, "Satellite View": satellite }).addTo(map);

		const allLatLngs = [];

		data.forEach((vehicle) => {
			const points = vehicle.trail.map((p) => {
				const latlng = [p.latitude, p.longitude];
				allLatLngs.push(L.latLng(...latlng));
				return latlng;
			});

			if (!points.length) return;

			const last = points[points.length - 1];

			if (showTrail && points.length > 1) {
				const polyline = L.polyline(points, {
					color: "blue",
					weight: 3,
					opacity: 0.8,
					lineJoin: "round",
				}).addTo(map);
				polyline.bindPopup(`${vehicle.name} - ${vehicle.imei}`);

				const seenHours = new Set();
				vehicle.trail.forEach((p) => {
					const dateObj = new Date(p.timestamp);
					const hourKey = dateObj.getHours();

					if (!seenHours.has(hourKey)) {
						seenHours.add(hourKey);

						const marker = L.circleMarker([p.latitude, p.longitude], {
							radius: 4,
							color: "#0066ff",
							fillColor: "#0066ff",
							fillOpacity: 0.9,
						}).addTo(map);

						const timeStr = dateObj.toLocaleTimeString("en-KE", {
							hour: "2-digit",
							minute: "2-digit",
						});

						marker.bindTooltip(
							`Hour: ${timeStr}<br>Lat: ${p.latitude.toFixed(5)}<br>Lon: ${p.longitude.toFixed(5)}`,
							{ direction: "top", offset: [0, -6], opacity: 0.85 }
						);
					}
				});
			}

			const marker = L.marker(last).addTo(map);
			marker.bindPopup(`${vehicle.name}<br>Last seen: ${vehicle.timestamp}`);
			marker.bindTooltip(
				`<strong>${vehicle.name}</strong><br>IMEI: ${vehicle.imei}<br>Last Seen: ${vehicle.timestamp}`,
				{ direction: "top", offset: [0, -10], sticky: true, opacity: 0.9 }
			);
		});

		if (allLatLngs.length > 1) {
			map.fitBounds(L.latLngBounds(allLatLngs), {
				padding: [50, 50],
				maxZoom: 15,
			});
		} else if (allLatLngs.length === 1) {
			map.setView(allLatLngs[0], 15);
		} else {
			map.setView([-0.0236, 37.9062], 7); // Kenya fallback
		}
	}*/
	function render_map(data, showTrail = false) {
	if (window.vehicleMap) window.vehicleMap.remove();
	$("#vehicle-map").empty();

	const map = L.map("vehicle-map", {
		zoom: 7,
		minZoom: 6,
		maxBounds: [[-5, 33], [5, 42]],
		maxBoundsViscosity: 1.0,
	});
	window.vehicleMap = map;

	const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
		attribution: "&copy; OpenStreetMap contributors",
	});

	const satellite = L.tileLayer(
		"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
		{
			attribution:
				"Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
		}
	);

	osm.addTo(map); // Default
	L.control.layers({ "OpenStreetMap": osm, "Satellite View": satellite }).addTo(map);

	const allLatLngs = [];

	data.forEach((vehicle) => {
		const points = vehicle.trail.map((p) => {
			const latlng = [p.latitude, p.longitude];
			allLatLngs.push(L.latLng(...latlng));
			return latlng;
		});

		if (!points.length) return;

		const last = points[points.length - 1];

		if (showTrail && points.length > 1) {
			const polyline = L.polyline(points, {
				color: "blue",
				weight: 3,
				opacity: 0.8,
				lineJoin: "round",
			}).addTo(map);
			polyline.bindPopup(`${vehicle.name} - ${vehicle.imei}`);

			const seenHours = new Set();
			vehicle.trail.forEach((p) => {
				const dateObj = new Date(p.timestamp);
				const hourKey = dateObj.getHours();

				if (!seenHours.has(hourKey)) {
					seenHours.add(hourKey);

					const marker = L.circleMarker([p.latitude, p.longitude], {
						radius: 4,
						color: "#0066ff",
						fillColor: "#0066ff",
						fillOpacity: 0.9,
					}).addTo(map);

					const timeStr = dateObj.toLocaleTimeString("en-KE", {
						hour: "2-digit",
						minute: "2-digit",
					});

					marker.bindTooltip(
						`Hour: ${timeStr}<br>Lat: ${p.latitude.toFixed(5)}<br>Lon: ${p.longitude.toFixed(5)}`,
						{ direction: "top", offset: [0, -6], opacity: 0.85 }
					);
				}
			});
		}

		const marker = L.marker(last).addTo(map);
		marker.bindPopup(`${vehicle.name}<br>Last seen: ${vehicle.timestamp}`);
		marker.bindTooltip(
			`<strong>${vehicle.name}</strong><br>IMEI: ${vehicle.imei}<br>Last Seen: ${vehicle.timestamp}`,
			{ direction: "top", offset: [0, -10], sticky: true, opacity: 0.9 }
		);
	});

	// Initial fit
	if (allLatLngs.length > 1) {
		map.fitBounds(L.latLngBounds(allLatLngs), {
			padding: [50, 50],
			maxZoom: 15,
		});
	} else if (allLatLngs.length === 1) {
		map.setView(allLatLngs[0], 15);
	} else {
		map.setView([-0.0236, 37.9062], 7); // Kenya fallback
	}

	// --- Zoom to Center Button ---
	const zoomControl = L.control({ position: "topright" });

	zoomControl.onAdd = function () {
		const div = L.DomUtil.create("div", "leaflet-bar leaflet-control");
		const button = L.DomUtil.create("a", "", div);
		button.innerHTML = "⤢"; // or use 🧭 / 🔍 / 📍 as needed
		button.href = "#";
		button.title = "Zoom to Center";

		L.DomEvent.on(button, "click", function (e) {
			L.DomEvent.stopPropagation(e);
			L.DomEvent.preventDefault(e);

			if (allLatLngs.length > 1) {
				map.fitBounds(L.latLngBounds(allLatLngs), {
					padding: [50, 50],
					maxZoom: 15,
				});
			} else if (allLatLngs.length === 1) {
				map.setView(allLatLngs[0], 15);
			} else {
				map.setView([-0.0236, 37.9062], 7); // fallback
			}
		});

		return div;
	};

	zoomControl.addTo(map);
}


	function fetch_data() {
		const date = $("#start-date").val();
		const vehicle = $("#vehicle-select").val();
		const showTrail = vehicle && !$("#select-time").val(); // assuming `select-time` is optional

		frappe.call({
			method: "upande_kaitet.api.get_all_vehicle_trails",
			args: {
				start_date: date,
				time: $("#select-time").val(),
				vehicle: vehicle,
			},
			callback: function (r) {
				render_map(r.message || [], showTrail);
			},
		});
	}

	$("#start-date, #vehicle-select").on("change", () => {
		load_leaflet(fetch_data);
	});

	// Initial setup
	populate_vehicle_dropdown();
	load_leaflet(fetch_data);
};
