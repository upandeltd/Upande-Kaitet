frappe.pages['tph-sensor-charts'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'TPH Sensor Charts',
		single_column: true
	});

	$(page.body).html(`
		<div class="row">
			<div class="col-md-3">
				<label>Sensor Name</label>
				<select class="form-control" id="sensor-name">
					<option value="">Loading sensors...</option>
				</select>
			</div>
			<div class="col-md-3">
				<label>Date From</label>
				<input type="date" class="form-control" id="date-from">
			</div>
			<div class="col-md-3">
				<label>Date To</label>
				<input type="date" class="form-control" id="date-to">
			</div>
			<div class="col-md-3">
				<label>Timespan</label>
				<select class="form-control" id="timespan">
					<option value="">Select Timespan</option>
					<option value="last_year">Last Year</option>
					<option value="last_quarter">Last Quarter</option>
					<option value="last_month">Last Month</option>
					<option value="last_week">Last Week</option>
					<option value="last_24h" selected>Last 24 Hours</option>
				</select>
			</div>
		</div>

		<div class="row" style="margin-top: 15px;">
			<div class="col-md-3">
				<label>Time Interval</label>
				<select class="form-control" id="time-interval">
					<option value="hourly" selected>Hourly</option>
				</select>
			</div>

			<div class="col-md-3 align-self-end">
				<button class="btn btn-primary" id="refresh-chart">Refresh Chart</button>
			</div>
		</div>

		<div id="chart-area" style="margin-top: 40px;"></div>
	`);

	load_sensor_names(() => {
		setup_timespan_filter_handler();
		setup_refresh_handler();
	});
};

function load_sensor_names(callback) {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Sensor Reading',
			fields: ['sensor_name'],
			distinct: true,
			limit_page_length: 100
		},
		callback: function(r) {
			const select = $('#sensor-name');
			select.empty().append(`<option value="">Select Sensor</option>`);
			let defaultSensorSet = false;

			if (r.message && r.message.length > 0) {
				let seen = new Set();
				r.message.forEach(row => {
					if (row.sensor_name && !seen.has(row.sensor_name)) {
						seen.add(row.sensor_name);
						const label = row.sensor_name.replace('kaitet_', '').replace('_', ' ').toUpperCase();
						const selected = row.sensor_name === "kaitet_greenhouse1" ? 'selected' : '';
						select.append(`<option value="${row.sensor_name}" ${selected}>${label}</option>`);
						if (row.sensor_name === "kaitet_greenhouse1") {
							defaultSensorSet = true;
						}
					}
				});
			} else {
				select.append(`<option value="">No sensors found</option>`);
			}

			// Fallback to first sensor if greenhouse1 doesn't exist
			if (!defaultSensorSet && r.message.length > 0) {
				select.val(r.message[0].sensor_name);
			}

			if (callback) callback();

			// Auto load chart after dropdown is filled
			$('#refresh-chart').click();
		}
	});
}

function setup_timespan_filter_handler() {
	const interval_map = {
		last_year: ['quarterly', 'monthly'],
		last_quarter: ['monthly', 'weekly'],
		last_month: ['weekly', 'daily'],
		last_week: ['daily'],
		last_24h: ['hourly']
	};

	$('#timespan').on('change', function () {
		const selected = $(this).val();
		const intervalSelect = $('#time-interval');
		intervalSelect.empty().append(`<option value="">Select Interval</option>`);

		if (interval_map[selected]) {
			interval_map[selected].forEach(interval => {
				const label = interval.charAt(0).toUpperCase() + interval.slice(1);
				intervalSelect.append(`<option value="${interval}">${label}</option>`);
			});
		}
	});
}

function setup_refresh_handler() {
	$('#refresh-chart').on('click', function () {
		const filters = {
			sensor_name: $('#sensor-name').val(),
			date_from: $('#date-from').val(),
			date_to: $('#date-to').val(),
			timespan: $('#timespan').val(),
			time_interval: $('#time-interval').val()
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

		$("#chart-area").html("<p>Loading chart...</p>");

		frappe.call({
			method: 'upande_kaitet.api.tph_sensor_charts.get_sensor_chart_data',
			args: filters,
			callback: function (r) {
				const labels = r.message.labels || [];
				const values = r.message.values || [];

				const chartData = {
					labels: labels.length ? labels : [''],
					datasets: [{
						name: chartTitle,
						values: values.length ? values : [0]
					}]
				};

				$("#chart-area").empty();

				new frappe.Chart("#chart-area", {
					title: chartTitle,
					data: chartData,
					type: 'bar',
					height: 300,
					colors: ['#5e64ff'],
					axisOptions: {
						xAxisMode: 'tick',
						yAxisMode: 'tick'
					}
				});
			}
		});
	});
}
