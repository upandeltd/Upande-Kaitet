frappe.pages['sensor-dashboard'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Sensor Dashboard",
		single_column: true,
	});

	$(page.body).html(`
		<!-- Temperature Chart Section -->
		<div class="mb-4">
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

			<div style="margin-top: 10px; width: 100%; border:1px solid gray;">
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
			}, 200);
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
			if (timespan === 'last_year') options = ['yearly', 'quarterly', 'monthly','weekly'];
			else if (timespan === 'last_quarter') options = ['monthly', 'weekly'];
			else if (timespan === 'last_month') options = ['weekly', 'daily'];
			else if (timespan === 'last_week') options = ['daily','hourly'];
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
			if (typeof cb === 'function') cb();
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
		method: "upande_kaitet.api.sensor_charts.get_all_sensor_names",
		callback: function (r) {
			const select = $("#sensor-name");
			select.empty().append(`<option value="">Select Sensor</option>`);
			let seen = new Set();

			if (r.message && r.message.length > 0) {
				r.message.forEach(sensor => {
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
		}
	});
}

function setup_timespan_filter_handler() {
	const interval_map = {
		last_year: ["yearly","quarterly", "monthly",'weekly'],
		last_quarter: ["monthly", "weekly"],
		last_month: ["weekly", "daily"],
		last_week: ["daily",'hourly'],
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
            sensor_name: $("#sensor-name").val() || "kaitet_greenhouse1",
            date_from: $("#date-from").val(),
            timespan: $("#timespan").val(),
            time_interval: $("#time-interval").val()
        };

        if (!filters.sensor_name) {
            frappe.msgprint("Please select a sensor before loading the chart.");
            return;
        }

        const sensorMetadata = {
            "kaitet_greenhouse1": { label: "Cold Room", chartTitle: "Cold Room Temperature", unit: "°C", chartType: "cspline" },
            "kaitet_greenhouse2": { label: "GreenHouse", chartTitle: "GreenHouse Temperature", unit: "°C", chartType: "spline" },
            "energy": { label: "Energy", chartTitle: "Energy Consumption", unit: "kWh", chartType: "column" },
            "precipitation": { label: "Precipitation", chartTitle: "Rainfall", unit: "mm", chartType: "column" },
            "level": { label: "Tank Level", chartTitle: "Tank Level", unit: "cm", chartType: "column" },
            "ec": { label: "EC Sensor", chartTitle: "EC", unit: "µS/cm", chartType: "spline" },
            "main": { label: "Flow Rate", chartTitle: "Water Flow Rate", unit: "L/min", chartType: "spline" },
            "ph": { label: "PH Sensor", chartTitle: "pH Level", unit: "pH", chartType: "spline" }
        };

        const metadata = sensorMetadata[filters.sensor_name] || {};
        const chartTitle = metadata.chartTitle || "Sensor Chart";
        const unit = metadata.unit || "";
        const chartType = metadata.chartType || "column";

        $("#chart-area").html(`<div id="chart-wrapper" style="min-width: 100%;"><p>Loading chart...</p></div>`);
        $("#custom-chart-title, #x-axis-date-label").remove();

		//Chart height and responsive
		function getResponsiveChartHeight() {
			const width = document.getElementById("chart-wrapper")?.offsetWidth || 800;

			if (width < 500) return 280;
			if (width < 800) return 320;
			return 350;
		}

		frappe.call({
			method: "upande_kaitet.api.sensor_charts.get_sensor_chart_data",
			args: filters,
			callback: function (r) {
				let labels = Array.isArray(r.message.labels) ? r.message.labels : [];
				let values = Array.isArray(r.message.values) ? r.message.values : [];
				const hasRealData = labels.length && values.length && values.some(v => v !== null && v !== 0);

				$("#chart-wrapper").before(`
					<div id="custom-chart-title" style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;">
						${chartTitle} (${unit})
					</div>
				`);

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

				document.querySelector("#chart-wrapper").innerHTML = "";

				const points = labels.map((label, i) => {
					const yVal = values[i];
					const isHot = filters.sensor_name === "kaitet_greenhouse1" && yVal > 7;
					return {
						x: label,
						y: yVal,
						name: label,
						color: isHot ? "red" : "#5e64ff",
						marker: isHot
							? { visible: true, size: 6, fill: "red", outline: { color: "red" } }
							: { visible: false },
						attributes: { unit: unit }
					};
				});

				const showSparseLabels = filters.timespan === "last_week" && filters.time_interval === "hourly";
				const xAxisTicks = labels.map((label, index) => ({
					value: label,
					label: {
						text: showSparseLabels ? (index % 4 === 0 ? label : "") : label,
						style: { fontSize: '10px' },
						rotation: -45
					}
				}));

				// Min and max with 1 decimal precision
				const validValues = values.filter(v => v !== null && !isNaN(v));
				const minVal = validValues.length ? (Math.min(...validValues)).toFixed(1) : "-";
				const maxVal = validValues.length ? (Math.max(...validValues)).toFixed(1) : "-";

				JSC.chart("chart-wrapper", {
					type: chartType,
					height: getResponsiveChartHeight(),
					series: [{
						name: chartTitle,
						points: points
					}],
					xAxis: {
						label_text: `Time | Min: ${minVal} ${unit} | Max: ${maxVal} ${unit}`,
						scale_type: "category",
						crosshair_enabled: true,
						defaultTick: {
							enabled: true,
							label: {
								rotation: -45,
								style: { fontSize: '10px' },
								text: function (val, i) {
									if (filters.timespan === 'last_week' && filters.time_interval === 'hourly') {
										return i % 4 === 0 ? val : "";
									}
									return val;
								}
							},
							gridLine_visible: !(filters.timespan === 'last_week' && filters.time_interval === 'hourly')
						},
						customTicks: xAxisTicks
					},
					yAxis: {
						label_text: unit,
						formatString: 'n1'
					},
					defaultSeries: {
						tooltip: {
							template: function (point) {
								if (!point || !point.x) return "No data";
								let [datePart, timePart] = point.x.split(" ");
								let [year, month, day] = datePart.split("-");
								let months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
								let formattedDate = `${day} ${months[parseInt(month) - 1]} ${year}`;
								return `Date: ${formattedDate}, ${timePart}<br>Value: ${Number(point.y).toFixed(1)} ${unit}`;
							}
						}
					},
					legend_visible: false
				});
			}
		});
    });
}
