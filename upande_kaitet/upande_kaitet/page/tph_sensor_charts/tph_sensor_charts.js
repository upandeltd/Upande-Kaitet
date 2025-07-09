frappe.pages["tph-sensor-charts"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "TPH Sensor Charts",
		single_column: true,
	});

	$(page.body).html(`
		<div class="row d-flex flex-wrap align-items-end justify-content-center" style="gap: 10px; margin-bottom: 15px; margin-top:10px;">
			<div class="col-auto">
				<label for="sensor-name">Sensor Name</label>
				<select class="form-control" id="sensor-name">
					<option value="">Loading sensors...</option>
				</select>
			</div>

			<div class="col-auto">
				<label for="date-from">Select Date</label>
				<input type="date" class="form-control" id="date-from">
			</div>

			<div class="col-auto">
				<label for="timespan">Timespan</label>
				<select class="form-control" id="timespan">
					<option value="">Select Timespan</option>
					<option value="last_year">Last Year</option>
					<option value="last_quarter">Last Quarter</option>
					<option value="last_month">Last Month</option>
					<option value="last_week">Last Week</option>
					<option value="last_24h" selected>Last 24 Hours</option>
				</select>
			</div>

			<div class="col-auto">
				<label for="time-interval">Time Interval</label>
				<select class="form-control" id="time-interval">
					<option value="hourly" selected>Hourly</option>
				</select>
			</div>

			<div class="col-auto">
				<button class="btn btn-primary" id="refresh-chart" style="margin-top: 25px;">Refresh Chart</button>
			</div>
		</div>

		<div style="margin-top: 0px; padding-top: 0px; width: 100%;">
			<div id="chart-area" style="padding-top: 40px; width: 100%; overflow-x: auto; scrollbar-width: none; -ms-overflow-style: none;">
				<div id="chart-wrapper" style="min-width: 100%;"></div>
			</div>
		</div>
	`);

	load_sensor_names(() => {
		setup_timespan_filter_handler();
		setup_date_filter_handler();
		setup_auto_refresh_on_filter_change();
		setup_refresh_handler();

		// Set initial defaults
		$("#timespan").val("last_24h").trigger("change");
		setTimeout(() => {
			$("#time-interval").val("hourly");
			$("#sensor-name").val("kaitet_greenhouse1");
			$("#date-from").val("");
		}, 200);
	});
};

function load_sensor_names(callback) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Sensor Reading",
			fields: ["sensor_name"],
			distinct: true,
			limit_page_length: 100,
		},
		callback: function (r) {
			const select = $("#sensor-name");
			select.empty().append(`<option value="">Select Sensor</option>`);
			let defaultSensorSet = false;

			if (r.message && r.message.length > 0) {
				let seen = new Set();
				r.message.forEach((row) => {
					const sensor = row.sensor_name;
					if (sensor && !seen.has(sensor)) {
						seen.add(sensor);

						let label;
						if (sensor === "kaitet_greenhouse1") {
							label = "Cold Room";
						} else if (sensor === "kaitet_greenhouse2") {
							label = "GreenHouse";
						} else {
							label = sensor.replace("kaitet_", "").replace("_", " ").toUpperCase();
						}

						const selected = sensor === "kaitet_greenhouse1" ? "selected" : "";
						select.append(`<option value="${sensor}" ${selected}>${label}</option>`);

						if (sensor === "kaitet_greenhouse1") {
							defaultSensorSet = true;
						}
					}
				});
			} else {
				select.append(`<option value="">No sensors found</option>`);
			}

			if (!defaultSensorSet && r.message.length > 0) {
				select.val(r.message[0].sensor_name);
			}

			if (callback) callback();
			$("#refresh-chart").click();
		},
	});
}

function setup_timespan_filter_handler() {
	const interval_map = {
		last_year: ["quarterly", "monthly"],
		last_quarter: ["monthly", "weekly"],
		last_month: ["weekly", "daily"],
		last_week: ["daily"],
		last_24h: ["hourly"],
	};

	$("#timespan").on("change", function () {
		const selected = $(this).val();
		const intervalSelect = $("#time-interval");
		intervalSelect.empty().append(`<option value="">Select Interval</option>`);

		if (selected) {
			$("#date-from").val("");
		}

		if (interval_map[selected]) {
			interval_map[selected].forEach((interval, index) => {
				const label = interval.charAt(0).toUpperCase() + interval.slice(1);
				const selectedAttr = index === 0 ? "selected" : "";
				intervalSelect.append(
					`<option value="${interval}" ${selectedAttr}>${label}</option>`
				);
			});
		}
	});
}

function setup_date_filter_handler() {
	$("#date-from").on("change", function () {
		const date = $(this).val();
		if (date) {
			$("#timespan").val("");
			$("#time-interval").html(`<option value="hourly" selected>Hourly</option>`);
			$("#refresh-chart").click();
		}
	});
}

function setup_auto_refresh_on_filter_change() {
	$("#sensor-name, #timespan, #time-interval").on("change", function () {
		$("#refresh-chart").click();
	});
}

function setup_refresh_handler() {
	$("#refresh-chart").on("click", function () {
		const filters = {
			sensor_name: $("#sensor-name").val(),
			date_from: $("#date-from").val(),
			timespan: $("#timespan").val(),
			time_interval: $("#time-interval").val(),
		};

		if (!filters.sensor_name) {
			frappe.msgprint("Please select a sensor before loading the chart.");
			return;
		}

		let chartTitle = "TPH Sensor Chart";
		if (filters.sensor_name === "kaitet_greenhouse1") {
			chartTitle = "Cold Room Temperature Chart";
		} else if (filters.sensor_name === "kaitet_greenhouse2") {
			chartTitle = "GreenHouse Temperature Chart";
		}

		$("#chart-area").html(
			"<div id='chart-wrapper' style='min-width: 100%;'><p>Loading chart...</p></div>"
		);

		frappe.call({
			method: "upande_kaitet.api.tph_sensor_charts.get_sensor_chart_data",
			args: filters,
			callback: function (r) {
				const labels = r.message.labels || [];
				const values = r.message.values || [];

				const chartData = {
					labels: labels.length ? labels : [""],
					datasets: [
						{
							name: chartTitle,
							values: values.length ? values : [0],
						},
					],
				};

				// Remove previous custom title and axis date label
				$("#custom-chart-title").remove();
				$("#x-axis-date-label").remove();
				$("#chart-wrapper").empty();

				// Insert styled chart title above the chart
				$("#chart-wrapper").before(`
					<div id="custom-chart-title" style="
						text-align: center;
						font-size: 26px;
						font-weight: bold;
						margin-bottom: 15px;
						color: #2c3e50;
					">
						${chartTitle}
					</div>
				`);

				// Append selected date label below chart (if any)
				const selectedDate = $("#date-from").val();
				if (selectedDate) {
					const readableDate = new Date(selectedDate).toLocaleDateString("en-KE", {
						year: "numeric",
						month: "long",
						day: "numeric",
					});

					$("#chart-wrapper").after(`
						<div id="x-axis-date-label" style="
							text-align: center;
							font-size: 14px;
							color: #666;
							margin-top: 10px;
						">
							Sensor data for ${readableDate}
						</div>
					`);
				}

				// Render the chart
				new frappe.Chart("#chart-wrapper", {
					data: chartData,
					type: "bar",
					height: 300,
					colors: ["#5e64ff"],
					barOptions: {
						spaceRatio: 0.1,
						barWidth: 0.5,
					},
					axisOptions: {
						xAxisMode: "tick",
						yAxisMode: "tick",
						xIsSeries: true,
					},
				});
			},
		});
	});
}
