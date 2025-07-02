frappe.pages['sensor-charts-hourly'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Hourly Sensor Charts',
		single_column: true
	});
	
const container = $(`
  <div style="
    height: 100vh; 
    display: flex; 
    justify-content: center; 
    align-items: center;
    background: var(--background-color);
  ">
    <a class="dashboard-link"
       href="/insights/dashboards/17csorcj3v"
       target="_blank"
       style="
         text-decoration: none;
         padding: 12px 24px;
         border-radius: 10rem;
         font-weight: 500;
         font-size: 16px;
         background: var(--btn-bg);
         color: var(--btn-text-color);
         border: 1px solid var(--border-color);
         transition: background 0.3s, color 0.3s;
       ">
       View Hourly Sensor Dashboard
    </a>
  </div>
`);

$(wrapper).append(container);

// Add hover style
$(`<style>
  .dashboard-link:hover {
    background: var(--primary);
    color: white;
    cursor: pointer;
  }
</style>`).appendTo("head");


	page.main.append(container);
};
