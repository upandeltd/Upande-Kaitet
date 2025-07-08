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
                    <label for="start-date" class="form-label">Start Date</label>
                    <input type="date" id="start-date" class="form-control">
                </div>
                <div class="col-md-3">
                    <label for="end-date" class="form-label">End Date</label>
                    <input type="date" id="end-date" class="form-control">
                </div>
                <div class="col-md-2">
                    <label for="interval" class="form-label">Interval</label>
                    <select id="interval" class="form-select">
                        <option value="hour">Hourly</option>
                        <option value="day">Daily</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label for="vehicle-select" class="form-label">Vehicle</label>
                    <select id="vehicle-select" class="form-select"></select>
                </div>
                <div class="col-md-1 d-grid">
                    <button class="btn btn-primary btn-sm" id="apply-filters">Apply</button>
                </div>
            </div>
        </div>
    </div>

    <div id="vehicle-map-container" class="frappe-card p-2">
        <div id="vehicle-map" style="height: 100%; width: 100%; border-radius: 8px;"></div>
    </div>
	`);

	const today = new Date();
	const yesterday = new Date(today);
	yesterday.setDate(today.getDate() - 1);
	$("#start-date").val(yesterday.toISOString().split("T")[0]);
	$("#end-date").val(today.toISOString().split("T")[0]);

	function load_leaflet(callback) {
		if (typeof L === "undefined") {
			frappe.require(
				[
					"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
					"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
				],
				callback
			);
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

	function render_map(data) {
		if (window.vehicleMap) {
			window.vehicleMap.remove();
		}

		$("#vehicle-map").empty();

		const map = L.map("vehicle-map", {
			zoom: 7,
			minZoom: 6,
			maxBounds: [
				[-5, 33],
				[5, 42],
			],
			maxBoundsViscosity: 1.0,
		});

		window.vehicleMap = map;

		const osm = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
			attribution: "&copy; OpenStreetMap contributors",
		});

		const satellite = L.tileLayer("https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", {
			subdomains: ["mt0", "mt1", "mt2", "mt3"],
			attribution: "&copy; Google Maps",
			maxZoom: 20,
		});

		osm.addTo(map);

		L.control
			.layers({
				OpenStreetMap: osm,
				Satellite: satellite,
			})
			.addTo(map);

		const allLatLngs = [];

		data.forEach((vehicle) => {
			const points = [];
			let prev = null;

			vehicle.trail.forEach((p) => {
				const curr = L.latLng(p.latitude, p.longitude);
				if (prev && curr.distanceTo(prev) < 5) return; // Filter jitter < 5m
				points.push([p.latitude, p.longitude]);
				allLatLngs.push(curr);
				prev = curr;
			});

			if (!points.length) return;

			const polyline = L.polyline(points, {
				color: "blue",
				weight: 3,
				opacity: 0.8,
				lineJoin: "round",
			}).addTo(map);

			polyline.bindPopup(`${vehicle.name} - ${vehicle.imei}`);

			const latest = points[points.length - 1];
			const marker = L.marker(latest).addTo(map);
			marker.bindPopup(`${vehicle.name}<br>Last seen: ${vehicle.timestamp}`);
			marker.bindTooltip(
				`
                <strong>${vehicle.name}</strong><br>
                IMEI: ${vehicle.imei}<br>
                Last Seen: ${vehicle.timestamp}
            `,
				{
					direction: "top",
					offset: [0, -10],
					permanent: false,
					sticky: true,
					opacity: 0.9,
				}
			);
		});

		if (allLatLngs.length) {
			map.fitBounds(allLatLngs, { padding: [50, 50] });
		} else {
			map.setView([-0.0236, 37.9062], 7); // fallback
		}
	}

	function fetch_data() {
		const start_date = $("#start-date").val();
		const end_date = $("#end-date").val();
		const interval = $("#interval").val();
		const vehicle = $("#vehicle-select").val();

		frappe.call({
			method: "upande_kaitet.api.get_all_vehicle_trails",
			args: {
				start_date,
				end_date,
				interval,
				vehicle,
			},
			callback: function (r) {
				render_map(r.message || []);
			},
		});
	}

	$("#apply-filters").on("click", function () {
		load_leaflet(fetch_data);
	});

	populate_vehicle_dropdown();
	load_leaflet(fetch_data);
};
