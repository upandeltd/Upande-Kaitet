frappe.pages["vehicle-tracker-test"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Vehicle Tracker",
		single_column: true,
	});

	// Add auto-refresh interval variable
	let refreshInterval;

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
				height: 400px;
				overflow: hidden;
				position: relative;
			}
			#vehicle-map {
				height: 100%;
				width: 100%;
				border-radius: 8px;
			}
			#map-error {
				position: absolute;
				top: 50%;
				left: 50%;
				transform: translate(-50%, -50%);
				background: rgba(255, 255, 255, 0.95);
				color: #b02a37;
				padding: 1rem 2rem;
				border-radius: 8px;
				font-weight: bold;
				font-size: 1.1rem;
				display: none;
				z-index: 999;
				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
			}
			@media (max-width: 768px) {
				#vehicle-filter-bar {
					padding: 1rem;
				}
			}
		</style>

		<div id="vehicle-filter-bar" class="frappe-card">
			<div class="container">
				<div class="row g-3 align-items-end justify-content-center text-center">
					<div class="col-md-3">
						<label for="start-date" class="form-label">Select Date</label>
						<input type="date" id="start-date" class="form-control">
					</div>
					<div class="col-md-3">
						<label for="vehicle-select" class="form-label">Vehicle</label>
						<select id="vehicle-select" class="form-select"></select>
					</div>
					<div class="col-md-3">
						<button id="refresh-map" class="btn btn-primary mt-4 w-100">Refresh</button>
					</div>
				</div>
			</div>
		</div>

		<div id="vehicle-map-container" class="frappe-card p-2">
			<div id="vehicle-map"></div>
			<div id="map-error">No vehicle data available for the selected filters.</div>
		</div>
	`);

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

	function render_map(data, showTrail = false) {
		if (window.vehicleMap) window.vehicleMap.remove();
		$("#vehicle-map").empty();
		$("#map-error").hide();

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
				attribution: "© Esri",
			}
		);
		osm.addTo(map);
		L.control.layers({ "OpenStreetMap": osm, "Satellite View": satellite }).addTo(map);

		const allLatLngs = [];

		if (!data.length) {
			$("#map-error").show();
			map.setView([-0.0236, 37.9062], 5);
			return;
		}

		data.forEach((vehicle) => {
			const rawTrail = (vehicle.raw_trail || []).map((p) => {
				const latlng = [p.latitude, p.longitude];
				allLatLngs.push(L.latLng(...latlng));
				return latlng;
			});

			if (!rawTrail.length) return;
			const last = rawTrail[rawTrail.length - 1];

			// Draw the full trail line
			if (showTrail && rawTrail.length > 1) {
				const polyline = L.polyline(rawTrail, {
					color: "blue",
					weight: 3,
					opacity: 0.8,
					lineJoin: "round",
				}).addTo(map);
				polyline.bindPopup(`${vehicle.name} - ${vehicle.imei || "No IMEI"}`);
			}

			// Hourly tooltip markers (only for specific vehicle)
			if (showTrail && Array.isArray(vehicle.trail)) {
				vehicle.trail.forEach((p) => {
					const marker = L.circleMarker([p.latitude, p.longitude], {
						radius: 4,
						color: "#0066ff",
						fillColor: "#0066ff",
						fillOpacity: 0.9,
					}).addTo(map);

					marker.bindTooltip(
						`Hour: ${p.timestamp}<br>Lat: ${p.latitude.toFixed(5)}<br>Lon: ${p.longitude.toFixed(5)}`,
						{ direction: "top", offset: [0, -6], opacity: 0.85 }
					);
				});
			}

			// Last seen marker - UPDATED to use latest_position.timestamp
			const displayTime = vehicle.latest_position?.timestamp || vehicle.timestamp;

			const marker = L.marker(last).addTo(map);
			marker.bindPopup(`${vehicle.name}<br>Last seen: ${displayTime}`);
			marker.bindTooltip(
				`<strong>${vehicle.name}</strong><br>IMEI: ${vehicle.imei || "N/A"}<br>Last Seen: ${displayTime}`,
				{ direction: "top", offset: [0, -10], sticky: true, opacity: 0.9 }
			);
		});

		// Fit to data or center on Kenya
		if (allLatLngs.length > 1) {
			map.fitBounds(L.latLngBounds(allLatLngs), {
				padding: [50, 50],
				maxZoom: 15,
			});
		} else if (allLatLngs.length === 1) {
			map.setView(allLatLngs[0], 15);
		} else {
			map.setView([-0.0236, 37.9062], 7);
		}

		// Add custom zoom-to-center control
		const zoomControl = L.control({ position: "topright" });
		zoomControl.onAdd = function () {
			const div = L.DomUtil.create("div", "leaflet-bar leaflet-control");
			const button = L.DomUtil.create("a", "", div);
			button.innerHTML = "🧭";
			button.href = "#";
			button.title = "Zoom to Center";
			button.style.cursor = "pointer";
			button.style.textDecoration = "none";

			L.DomEvent.on(button, "click", function (e) {
				e.preventDefault();
				e.stopPropagation();

				if (allLatLngs.length > 1) {
					map.fitBounds(L.latLngBounds(allLatLngs), {
						padding: [50, 50],
						maxZoom: 15,
					});
				} else if (allLatLngs.length === 1) {
					map.setView(allLatLngs[0], 15);
				} else {
					map.setView([-0.0236, 37.9062], 7);
				}
			});

			return div;
		};
		zoomControl.addTo(map);
	}

	function fetch_data() {
		const date = $("#start-date").val();
		const vehicle = $("#vehicle-select").val();
		const showTrail = !!vehicle;

		frappe.call({
			method: "upande_kaitet.api.vehicle_trails.get_all_vehicle_trails",
			args: {
				start_date: date,
				vehicle: vehicle,
			},
			callback: function (r) {
				render_map(r.message || [], showTrail);
			},
		});
	}

	function setupAutoRefresh() {
		clearInterval(refreshInterval); // Clear existing interval
		refreshInterval = setInterval(fetch_data, 3600000); // 1 hour refresh
	}

	// Event Listeners
	$("#start-date, #vehicle-select").on("change", () => {
		setupAutoRefresh();
		load_leaflet(fetch_data);
	});

	$("#refresh-map").on("click", () => {
		setupAutoRefresh();
		load_leaflet(fetch_data);
	});

	// Initialize
	populate_vehicle_dropdown();
	load_leaflet(fetch_data);
	setupAutoRefresh(); // Start auto-refresh
};