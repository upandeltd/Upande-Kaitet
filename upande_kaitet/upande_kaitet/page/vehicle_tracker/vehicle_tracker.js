frappe.pages['vehicle-tracker'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Vehicle Tracker',
        single_column: true
    });

    // UI Filters
	$(page.body).append(`
		<div class="position-sticky top-0" style="z-index: 1000; background: var(--bg-color); padding-top: 1rem;">
			<div class="frappe-card p-4 mb-4">
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
						<select id="vehicle-select" class="form-select">
						</select>
					</div>
					<div class="col-md-1 d-grid">
						<button class="btn btn-primary btn-sm" id="apply-filters">Apply</button>
					</div>
				</div>
			</div>
		</div>

		<div class="frappe-card p-2" style="height: 600px; border-radius: 8px; overflow: hidden;">
			<div id="vehicle-map" style="height: 100%; width: 100%; border-radius: 8px;"></div>
		</div>
	`);

    // Set default date range (last 24h)
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    $("#start-date").val(yesterday.toISOString().split('T')[0]);
    $("#end-date").val(today.toISOString().split('T')[0]);

    function load_leaflet(callback) {
        if (typeof L === 'undefined') {
            frappe.require([
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
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
                limit_page_length: 100
            },
            callback: function (r) {
                const select = $("#vehicle-select");
                select.append(`<option value="">All Vehicles</option>`);
                (r.message || []).forEach(vehicle => {
                    select.append(`<option value="${vehicle.name}">${vehicle.name}</option>`);
                });
            }
        });
    }

	function render_map(data) {
		if (window.vehicleMap) {
			window.vehicleMap.remove();  // Destroys previous map instance
		}

		$("#vehicle-map").empty();  // Reset DOM container just in case

		const map = L.map('vehicle-map', {
			center: [-0.0236, 37.9062],  // Kenya approximate center
			zoom: 7,
			minZoom: 6,
			maxBounds: [
				[-5, 33], // Southwest Kenya
				[5, 42]   // Northeast Kenya
			],
			maxBoundsViscosity: 1.0
		});

		window.vehicleMap = map;

		// Base Layers
		const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; OpenStreetMap contributors'
		});

		const satellite = L.tileLayer(
			'https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
				subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
				attribution: '&copy; Google Maps',
				maxZoom: 20
			}
		);

		osm.addTo(map);  // Default

		const baseLayers = {
			"OpenStreetMap": osm,
			"Satellite": satellite
		};

		L.control.layers(baseLayers).addTo(map);  // Add toggle

		// Plot vehicle trails
		data.forEach(vehicle => {
			const points = vehicle.trail.map(p => [p.latitude, p.longitude]);
			if (!points.length) return;

			const polyline = L.polyline(points, { color: 'blue' }).addTo(map);
			polyline.bindPopup(`${vehicle.name} - ${vehicle.imei}`);

			const latest = points[points.length - 1];
			const marker = L.marker(latest).addTo(map);

			marker.bindPopup(`${vehicle.name}<br>Last seen: ${vehicle.timestamp}`);

			marker.bindTooltip(`
				<strong>${vehicle.name}</strong><br>
				IMEI: ${vehicle.imei}<br>
				Last Seen: ${vehicle.timestamp}
			`, {
				direction: 'top',
				offset: [0, -10],
				permanent: false,
				sticky: true,
				opacity: 0.9
			});
		});
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
                vehicle
            },
            callback: function (r) {
                render_map(r.message || []);
            }
        });
    }

    $("#apply-filters").on("click", function () {
        load_leaflet(fetch_data);
    });

    // Initial load
    populate_vehicle_dropdown();
    load_leaflet(fetch_data);
};
