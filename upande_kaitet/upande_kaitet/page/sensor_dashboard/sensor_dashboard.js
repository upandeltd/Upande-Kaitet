frappe.pages['sensor-dashboard'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Sensor Dashboard",
		single_column: true,
	});

	$(page.body).html(`
		<!-- Temperature Chart Section -->
		<div id="tph-section" class="mb-4">
			<div class="row d-flex flex-wrap align-items-end justify-content-center" style="gap: 10px;">
				<div class="col-auto">
					<label for="sensor-name">Sensor Name</label>
					<select class="form-control" id="sensor-name"></select>
				</div>

				<div class="col-auto">
					<label for="date-from">Select Date</label>
					<input type="date" class="form-control" id="date-from">
				</div>

				<div class="col-auto">
					<label for="timespan">Timespan</label>
					<select class="form-control" id="timespan">
						<option value="">Select Timespan</option>
						<option value="last_24h" selected>Last 24 Hours</option>
						<option value="last_week">Last Week</option>
						<option value="last_month">Last Month</option>
						<option value="last_quarter">Last Quarter</option>
						<option value="last_year">Last Year</option>
					</select>
					</select>
				</div>

				<div class="col-auto">
					<label for="time-interval">Time Interval</label>
					<select class="form-control" id="time-interval">
						<option value="hourly" selected>Hourly</option>
					</select>
				</div>

				<div class="col-auto">
					<button class="btn btn-primary" id="refresh-chart" style="margin-top: 25px;">Refresh</button>
				</div>
			</div>

			<div style="margin-top: 10px; width: 100%; border:1px solid grey;">
				<div id="chart-area">
					<div id="chart-wrapper" style="min-width: 100%;"></div>
				</div>
			</div>
		</div>
	`);

	loadCombinedScripts(() => {
		initAllCharts(() => {
			// Auto-select Cold Room and refresh after short delay
			setTimeout(() => {
				$('#sensor-name').val('kaitet_greenhouse1');
				$('#refresh-chart').trigger('click');
			}, 300);
		});
	});
};

// Load external chart libraries
function loadCombinedScripts(callback) {
	const jscMain = document.createElement('script');
	jscMain.src = 'https://code.jscharting.com/latest/jscharting.js';
	jscMain.onload = () => {
		const jscWidgets = document.createElement('script');
		jscWidgets.src = 'https://code.jscharting.com/latest/jscharting-widgets.js';
		jscWidgets.onload = callback;
		document.head.appendChild(jscWidgets);
	};
	document.head.appendChild(jscMain);
}

function initAllCharts(callback) {
	const site_name = 'kaitet';

	// ---------- Interval Options ----------
	function updateIntervalOptions(timespan, isDateSelected) {
		const $interval = $('#ec-interval');
		$interval.empty();

		let options = [];
		if (isDateSelected) options = ['hourly'];
		else {
			if (timespan === 'last_year') options = ['yearly', 'quarterly', 'monthly'];
			else if (timespan === 'last_quarter') options = ['monthly', 'weekly'];
			else if (timespan === 'last_month') options = ['weekly', 'daily'];
			else if (timespan === 'last_week') options = ['daily'];
			else options = ['hourly'];
		}

		options.forEach(val => {
			$interval.append(`<option value="${val}">${val.charAt(0).toUpperCase() + val.slice(1)}</option>`);
		});
	}

	// ---------- Date Range ----------
	function computeRange() {
		const now = new Date();
		let start = new Date(now);
		let end = new Date(now);

		const selectedDate = $('#ec-date').val();
		const timespan = $('#ec-timespan').val();

		if (selectedDate) {
			const date = new Date(selectedDate);
			start = new Date(date.setHours(0, 0, 0, 0));
			end = new Date(date.setHours(23, 59, 59, 999));
		} else {
			switch (timespan) {
				case 'last_year': start.setFullYear(now.getFullYear() - 1); break;
				case 'last_quarter': start.setMonth(now.getMonth() - 3); break;
				case 'last_month': start.setMonth(now.getMonth() - 1); break;
				case 'last_week': start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break;
				default: start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
			}
		}

		return { start, end };
	}

	// ---------- Load EC Data ----------
	function loadEcData() {
		const { start, end } = computeRange();
		const interval = $('#ec-interval').val() || 'hourly';

		frappe.call({
			method: "upande_sensors.upande_sensors.doctype.sensor_chart_data.sensor_chart_data.get_combined_sensor_data",
			args: {
				site_name,
				start_datetime: start.toISOString(),
				end_datetime: end.toISOString(),
			},
		}).then((res) => {
			const ec_data = res.message[1].ec_data || [];
			drawEcChart(ec_data, start.toISOString(), end.toISOString(), interval);
			drawEcGauge(ec_data);
		});
	}

	// ---------- Init Temperature Charts ----------
	function initTempCharts(cb) {
		load_sensor_names(() => {
			setup_timespan_filter_handler();
			setup_date_filter_handler();
			setup_auto_refresh_on_filter_change();
			setup_refresh_handler();
			if (typeof cb === 'function') cb(); // Call callback if provided
		});
	}

	// ---------- Set Up EC Events ----------
	$('#ec-date').on('change', function () {
		$('#ec-timespan').val('');
		updateIntervalOptions(null, true);
		loadEcData();
	});

	$('#ec-timespan').on('change', function () {
		$('#ec-date').val('');
		const selected = $(this).val();
		updateIntervalOptions(selected, false);
		loadEcData();
	});

	$('#ec-interval').on('change', loadEcData);

	// ---------- Init Both Sections ----------
	updateIntervalOptions('last_24h', false);
	loadEcData();

	// Init temperature charts and call callback after all is set
	initTempCharts(() => {
		if (typeof callback === 'function') callback();
	});
}

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
			let seen = new Set();

			if (r.message && r.message.length > 0) {
				r.message.forEach(row => {
					const sensor = row.sensor_name;
					if (sensor && !seen.has(sensor)) {
						seen.add(sensor);
						let label = sensor.replace("kaitet_", "").replace("_", " ").toUpperCase();

						if (sensor === "kaitet_greenhouse1") label = "Cold Room";
						if (sensor === "kaitet_greenhouse2") label = "GreenHouse";
						if (sensor === "energy") label = "Energy";
						if (sensor === "precipitation") label = "Precipitation";
						if (sensor === "level") label = "Tank Level";
						if (sensor === "ec") label = "EC Sensor";
						if (sensor === "main") label = "Flow Rate";
						if (sensor === "ph") label = "PH Sensor";

						select.append(`<option value="${sensor}">${label}</option>`);
					}
				});
			} else {
				select.append(`<option value="">No sensors found</option>`);
			}

			if (callback) callback();
			$("#refresh-chart").click();
		},

	});
}

function setup_timespan_filter_handler() {
	const interval_map = {
		last_year: ["yearly","quarterly", "monthly"],
		last_quarter: ["monthly", "weekly"],
		last_month: ["weekly", "daily"],
		last_week: ["daily"],
		last_24h: ["hourly"],
	};

	$("#timespan").on("change", function () {
		const selected = $(this).val();
		const intervalSelect = $("#time-interval");
		intervalSelect.empty().append(`<option value="">Select Interval</option>`);

		if (selected) $("#date-from").val("");

		if (interval_map[selected]) {
			interval_map[selected].forEach((interval, index) => {
				const label = interval.charAt(0).toUpperCase() + interval.slice(1);
				const selectedAttr = index === 0 ? "selected" : "";
				intervalSelect.append(`<option value="${interval}" ${selectedAttr}>${label}</option>`);
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

		filters.sensor_name = filters.sensor_name || "kaitet_greenhouse1";
		if (!filters.sensor_name) {
			frappe.msgprint("Please select a sensor before loading the chart.");
			return;
		}

		let chartTitle = "Sensor Charts";
		let unit = "";

		const sensorMetadata = {
			"kaitet_greenhouse1": {
				label: "Cold Room",
				chartTitle: "Cold Room Temperature Chart (°C)",
				unit: "°C"
			},
			"kaitet_greenhouse2": {
				label: "GreenHouse",
				chartTitle: "GreenHouse Temperature Chart (°C)",
				unit: "°C"
			},
			"energy": {
				label: "Energy",
				chartTitle: "Energy Consumption Chart (kWh)",
				unit: "kWh"
			},
			"precipitation": {
				label: "Precipitation",
				chartTitle: "Rainfall Chart (mm)",
				unit: "mm"
			},
			"level": {
				label: "Tank Level",
				chartTitle: "Tank Level Chart (cm)",
				unit: "cm"
			},
			"ec": {
				label: "EC Sensor",
				chartTitle: "EC Chart (µS/cm)",
				unit: "µS/cm"
			},
			"main": {
				label: "Flow Rate",
				chartTitle: "Water Flow Rate Chart (L/min)",
				unit: "L/min"
			},
			"ph": {
				label: "PH Sensor",
				chartTitle: "pH Level Chart (pH)",
				unit: "pH"
			}
		};

		if (filters.sensor_name && sensorMetadata[filters.sensor_name]) {
			chartTitle = sensorMetadata[filters.sensor_name].chartTitle || "";
			unit = sensorMetadata[filters.sensor_name].unit || "";
		}

		$("#chart-area").html(`<div id="chart-wrapper" style="min-width: 100%;"><p>Loading chart...</p></div>`);
		$("#custom-chart-title, #x-axis-date-label").remove();

		frappe.call({
			method: "upande_kaitet.api.sensor_charts.get_sensor_chart_data",
			args: filters,
			callback: function (r) {
				const labels = Array.isArray(r.message.labels) ? r.message.labels : [];
				const values = Array.isArray(r.message.values) ? r.message.values : [];
				const labelFormat = r.message.label_format;

				const hasRealData = labels.length && values.length && values.some(v => v !== null && v !== 0);

				let chartData;

				if (hasRealData) {
					chartData = {
						labels,
						datasets: [{
							name: chartTitle,
							values,
						}],
					};
				} else {
					const interval = filters.time_interval || "hourly";
					const selectedDate = filters.date_from;

					let start, end;
					const now = new Date();
					end = new Date(now);
					start = new Date(now);

					if (selectedDate) {
						start = new Date(`${selectedDate}T00:00:00`);
						end = new Date(`${selectedDate}T23:59:59`);
					} else {
						switch (filters.timespan) {
							case "last_year": start.setFullYear(start.getFullYear() - 1); break;
							case "last_quarter": start.setMonth(start.getMonth() - 3); break;
							case "last_month": start.setMonth(start.getMonth() - 1); break;
							case "last_week": start.setDate(start.getDate() - 7); break;
							default: start.setHours(start.getHours() - 24);
						}
					}

					let emptyLabels = [], emptyValues = [], cursor = new Date(start);

					while (cursor <= end) {
						if (interval === "hourly") {
							emptyLabels.push(cursor.toLocaleTimeString("en-KE", { hour: "2-digit", minute: "2-digit" }));
							cursor.setHours(cursor.getHours() + 1);
						} else if (interval === "daily") {
							emptyLabels.push(cursor.toLocaleDateString("en-KE", { day: "numeric", month: "short" }));
							cursor.setDate(cursor.getDate() + 1);
						} else if (interval === "weekly") {
							emptyLabels.push(`Week ${getWeekNumber(cursor)}`);
							cursor.setDate(cursor.getDate() + 7);
						} else if (interval === "monthly") {
							emptyLabels.push(cursor.toLocaleDateString("en-KE", { month: "short", year: "numeric" }));
							cursor.setMonth(cursor.getMonth() + 1);
						}
						emptyValues.push(null);
					}

					chartData = {
						labels: emptyLabels.length ? emptyLabels : [""],
						datasets: [{
							name: "No Data Available",
							values: emptyValues.length ? emptyValues : [null],
						}],
					};
				}

				// Time-only label adjustment
				if (labelFormat === "time_only") {
					chartData.labels = chartData.labels.map(l => {
						const parts = l.split(" ");
						return parts.length === 2 ? parts[1] : l;
					});
				}

				// Chart Title
				$("#chart-wrapper").before(`
					<div id="custom-chart-title" style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;">
						${chartTitle}
					</div>
				`);

				// X-axis annotation
				if (filters.date_from) {
					const readableDate = new Date(filters.date_from).toLocaleDateString("en-KE", {
						year: "numeric", month: "long", day: "numeric"
					});
					$("#chart-wrapper").after(`
						<div id="x-axis-date-label" style="text-align: center; font-size: 14px; color: #666; margin-top: 10px;">
							Sensor data for ${readableDate}
						</div>
					`);
				}

				const sensorChartTypeMap = {
					"kaitet_greenhouse1": "bar",   // Temperature
					"kaitet_greenhouse2": "bar",   // Temperature
					"energy": "bar",                // Energy Consumption
					"precipitation": "bar",         // Rainfall
					"level": "line",                // Tank Level
					"ec": "line",                   // EC Sensor
					"main": "line",                 // Flow Rate
					"ph": "line"                    // pH Sensor
				};

				const chartType = sensorChartTypeMap[filters.sensor_name] || "bar";

				new frappe.Chart("#chart-wrapper", {
					data: chartData,
					type: chartType,
					height: 350,
					colors: ["#5e64ff"],
					barOptions: { spaceRatio: 0.3 },
					axisOptions: {
						xAxisMode: "tick",
						yAxisMode: "tick",
						xIsSeries: true
					},
					tooltipOptions: {
						formatTooltipX: d => {
							const parts = d.split(" ");
							return parts.length === 2 ? parts[1] : d;
						},
						formatTooltipY: val => (val !== null && val !== undefined ? `${val} ${unit}` : "No data")
					}
				});
			}
		});
	});
}