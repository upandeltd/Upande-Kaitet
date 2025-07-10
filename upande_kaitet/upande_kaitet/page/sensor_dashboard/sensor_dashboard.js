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
		initEcCharts();
		initTempCharts(() => {
			// Auto-select Cold Room and delay refresh slightly to allow DOM updates
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

// ==================== EC CHART SECTION ==================================
/*
function initEcCharts() {
	const site_name = 'kaitet';

	let end = new Date();
	let start = new Date(end.getTime() - 24 * 60 * 60 * 1000); // Default: Last 24 hours

	// Update interval options based on timespan or date
	function updateIntervalOptions(timespan, isDateSelected) {
		const $interval = $('#ec-interval');
		$interval.empty();

		let options = [];

		if (isDateSelected) {
			options = ['hourly'];
		} else {
			if (timespan === 'last_year') {
				options = ['yearly','quarterly', 'monthly'];
			} else if (timespan === 'last_quarter') {
				options = ['monthly', 'weekly'];
			} else if (timespan === 'last_month') {
				options = ['weekly', 'daily'];
			} else if (timespan === 'last_week') {
				options = ['daily'];
			} else {
				options = ['hourly'];
			}
		}

		options.forEach(val => {
			$interval.append(
				`<option value="${val}">${val.charAt(0).toUpperCase() + val.slice(1)}</option>`
			);
		});
	}

	// Calculate start/end datetime based on selection
	function computeRange() {
		const selectedDate = $('#ec-date').val();
		const timespan = $('#ec-timespan').val();
		end = new Date();

		if (selectedDate) {
			const date = new Date(selectedDate);
			start = new Date(date.setHours(0, 0, 0, 0));
			end = new Date(date.setHours(23, 59, 59, 999));
		} else {
			switch (timespan) {
				case 'last_year':
					start = new Date(end);
					start.setFullYear(end.getFullYear() - 1);
					break;
				case 'last_quarter':
					start = new Date(end);
					start.setMonth(end.getMonth() - 3);
					break;
				case 'last_month':
					start = new Date(end);
					start.setMonth(end.getMonth() - 1);
					break;
				case 'last_week':
					start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
					break;
				default:
					start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
			}
		}
	}

	// Load EC data
	function loadEcData() {
		computeRange();

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

	// Event handlers
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

	// Init
	updateIntervalOptions('last_24h', false);
	loadEcData();
}*/

function initEcCharts() {
	const site_name = 'kaitet';

	let end = new Date();
	let start = new Date(end.getTime() - 24 * 60 * 60 * 1000); // Default: Last 24 hours

	// Update interval dropdown options dynamically
	function updateIntervalOptions(timespan, isDateSelected) {
		const $interval = $('#ec-interval');
		$interval.empty();

		let options = [];

		if (isDateSelected) {
			options = ['hourly'];
		} else {
			switch (timespan) {
				case 'last_year':
					options = ['yearly', 'quarterly', 'monthly'];
					break;
				case 'last_quarter':
					options = ['monthly', 'weekly'];
					break;
				case 'last_month':
					options = ['weekly', 'daily'];
					break;
				case 'last_week':
					options = ['daily'];
					break;
				default:
					options = ['hourly'];
			}
		}

		options.forEach(val => {
			$interval.append(
				`<option value="${val}">${val.charAt(0).toUpperCase() + val.slice(1)}</option>`
			);
		});
	}

	// Compute start and end date range based on filters
	function computeRange() {
		const selectedDate = $('#ec-date').val();
		const timespan = $('#ec-timespan').val();
		end = new Date();

		if (selectedDate) {
			const date = new Date(selectedDate);
			start = new Date(date.setHours(0, 0, 0, 0));
			end = new Date(date.setHours(23, 59, 59, 999));
		} else {
			switch (timespan) {
				case 'last_year':
					start = new Date(end);
					start.setFullYear(end.getFullYear() - 1);
					break;
				case 'last_quarter':
					start = new Date(end);
					start.setMonth(end.getMonth() - 3);
					break;
				case 'last_month':
					start = new Date(end);
					start.setMonth(end.getMonth() - 1);
					break;
				case 'last_week':
					start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
					break;
				default: // last_24h or blank
					start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
			}
		}
	}

	// Load EC data and draw chart + gauge
	function loadEcData() {
		computeRange();
		const interval = $('#ec-interval').val() || 'hourly';

		frappe.call({
			method: "upande_sensors.upande_sensors.doctype.sensor_chart_data.sensor_chart_data.get_combined_sensor_data",
			args: {
				site_name,
				start_datetime: start.toISOString(),
				end_datetime: end.toISOString(),
				time_interval: interval, // ✅ now sent to backend
			},
		}).then((res) => {
			const ec_data = res.message[1].ec_data || [];
			drawEcChart(ec_data, start.toISOString(), end.toISOString(), interval);
			drawEcGauge(ec_data);
		});
	}

	// Event listeners for filters
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

	// Init chart on first load
	updateIntervalOptions('last_24h', false);
	loadEcData();
}



// ==================== TPH (Temperature) CHART SECTION ====================
function initTempCharts() {
	load_sensor_names(() => {
		setup_timespan_filter_handler();
		setup_date_filter_handler();
		setup_auto_refresh_on_filter_change();
		setup_refresh_handler();

		setTimeout(() => {
			$("#time-interval").val("hourly");
			$("#sensor-name").val("kaitet_greenhouse1");
			$("#date-from").val("");
		}, 200);
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
						else if (sensor === "kaitet_greenhouse2") label = "GreenHouse";
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

		let chartTitle = "TPH Sensor Chart";
		if (filters.sensor_name === "kaitet_greenhouse1") chartTitle = "Cold Room Temperature Chart";
		else if (filters.sensor_name === "kaitet_greenhouse2") chartTitle = "GreenHouse Temperature Chart";
		else if (filters.sensor_name === "ec") chartTitle = "EC Chart (µS/cm )";

		$("#chart-area").html(`<div id="chart-wrapper" style="min-width: 100%;"><p>Loading chart...</p></div>`);
		$("#custom-chart-title, #x-axis-date-label").remove();

		frappe.call({
			method: "upande_kaitet.api.tph_sensor_charts.get_sensor_chart_data",
			args: filters,
			callback: function (r) {
				const labels = Array.isArray(r.message.labels) ? r.message.labels : [];
				const values = Array.isArray(r.message.values) ? r.message.values : [];

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

					if (selectedDate) {
						start = new Date(`${selectedDate}T00:00:00`);
						end = new Date(`${selectedDate}T23:59:59`);
					} else {
						end = new Date();
						switch (filters.timespan) {
							case "last_year":
								start = new Date(end);
								start.setFullYear(end.getFullYear() - 1);
								break;
							case "last_quarter":
								start = new Date(end);
								start.setMonth(end.getMonth() - 3);
								break;
							case "last_month":
								start = new Date(end);
								start.setMonth(end.getMonth() - 1);
								break;
							case "last_week":
								start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
								break;
							default: // last_24h or blank
								start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
						}
					}

					let emptyLabels = [];
					let emptyValues = [];
					let cursor = new Date(start);

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

				// Display chart title
				$("#chart-wrapper").before(`
					<div id="custom-chart-title" style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;">
						${chartTitle}
					</div>
				`);

				// Date display below chart
				const selectedDate = filters.date_from;
				if (selectedDate) {
					const readableDate = new Date(selectedDate).toLocaleDateString("en-KE", {
						year: "numeric", month: "long", day: "numeric"
					});
					$("#chart-wrapper").after(`
						<div id="x-axis-date-label" style="text-align: center; font-size: 14px; color: #666; margin-top: 10px;">
							Sensor data for ${readableDate}
						</div>
					`);
				}

				const chartType = (filters.sensor_name === "ec") ? "line" : "bar";

				new frappe.Chart("#chart-wrapper", {
					data: chartData,
					type: chartType,
					height: 300,
					colors: ["#5e64ff"],
					barOptions: { spaceRatio: 0.3 },
					axisOptions: { xAxisMode: "tick", yAxisMode: "tick", xIsSeries: true },
				});
			},
		});
	});
}

// Helper function for weekly labels
function getWeekNumber(d) {
	d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
	const dayNum = d.getUTCDay() || 7;
	d.setUTCDate(d.getUTCDate() + 4 - dayNum);
	const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
	return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}


