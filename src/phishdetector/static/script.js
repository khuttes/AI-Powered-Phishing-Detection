// enable bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const data = {};
    for (let el of form.elements) {
        if (el.name) data[el.name] = el.value;
    }
    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const json = await res.json();
        let html = `<div class="alert alert-info">Phishing probability: <strong>${json.phishing_probability.toFixed(3)}</strong></div>`;
        if (json.features) {
            html += '<h5>Feature values</h5><table class="table table-sm"><thead><tr><th>Feature</th><th>Value</th></tr></thead><tbody>';
            for (const [k,v] of Object.entries(json.features)) {
                html += `<tr><td>${k}</td><td>${v}</td></tr>`;
            }
            html += '</tbody></table>';
        }
        document.getElementById('result').innerHTML = html;
        // update history and chart
        addHistory(json.phishing_probability);
    } catch (err) {
        document.getElementById('result').innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    }
});

// maintain a simple session history and render chart
let history = [];
let chart;

function addHistory(score) {
    history.push(score);
    renderHistory();
    updateChart();
}

function renderHistory() {
    const div = document.getElementById('history');
    if (history.length === 0) {
        div.innerHTML = '';
        return;
    }
    let html = '<h5 class="text-white">Recent Scores</h5><ul class="list-group">';
    history.slice(-5).reverse().forEach(s => {
        html += `<li class="list-group-item bg-dark text-white">${s.toFixed(3)}</li>`;
    });
    html += '</ul>';
    div.innerHTML = html;
}

function updateChart() {
    const ctx = document.getElementById('scoreChart').getContext('2d');
    if (!chart) {
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: history.map((_, i) => i+1),
                datasets: [{ label: 'Phishing score', data: history, borderColor: '#ff6384', tension: 0.4 }]
            },
            options: { scales: { y: { min:0, max:1 } } }
        });
    } else {
        chart.data.labels = history.map((_, i) => i+1);
        chart.data.datasets[0].data = history;
        chart.update();
    }
}

// batch form
const batchForm = document.getElementById('batchForm');
batchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(batchForm);
    try {
        const res = await fetch('/batch', { method: 'POST', body: formData });
        const json = await res.json();
        if (json.error) {
            document.getElementById('batchResult').innerHTML = `<div class="alert alert-danger">${json.error}</div>`;
        } else {
            document.getElementById('batchResult').innerHTML = `<div class="alert alert-success">Scored file written to: <code>${json.output}</code></div>`;
        }
    } catch (err) {
        document.getElementById('batchResult').innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    }
});
