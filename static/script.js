document.addEventListener('DOMContentLoaded', function () {
    // Demo financial dataset setup (matching screenshot trends)
    const dataset = [
        { Date: '01-06-2025', Revenue: 3100, Expenses: 6500, Status: 'Profit', Confidential: 'No' },
        { Date: '02-06-2025', Revenue: 3000, Expenses: 2800, Status: 'Profit', Confidential: 'No' },
        { Date: '03-06-2025', Revenue: 3600, Expenses: 2800, Status: 'Profit', Confidential: 'No' },
        { Date: '04-06-2025', Revenue: 3600, Expenses: 3400, Status: 'Profit', Confidential: 'Yes' },
        { Date: '05-06-2025', Revenue: 2300, Expenses: 3400, Status: 'Loss', Confidential: 'Yes' },
        { Date: '06-06-2025', Revenue: 2300, Expenses: 2500, Status: 'Loss', Confidential: 'No' },
        { Date: '07-06-2025', Revenue: 4000, Expenses: 2500, Status: 'Profit', Confidential: 'No' },
        { Date: '08-06-2025', Revenue: 4100, Expenses: 4400, Status: 'Loss', Confidential: 'Yes' },
        { Date: '09-06-2025', Revenue: 2400, Expenses: 4400, Status: 'Loss', Confidential: 'No' },
        { Date: '10-06-2025', Revenue: 2400, Expenses: 3200, Status: 'Loss', Confidential: 'Yes' },
        { Date: '11-06-2025', Revenue: 3800, Expenses: 3200, Status: 'Profit', Confidential: 'No' },
        { Date: '12-06-2025', Revenue: 3800, Expenses: 4300, Status: 'Loss', Confidential: 'Yes' },
        { Date: '13-06-2025', Revenue: 3100, Expenses: 4300, Status: 'Loss', Confidential: 'No' }
    ];

    // Load initial views
    populateDateDropdown(dataset);
    renderTrendChart(dataset);
    updateDailyBarChart(dataset[0]); // Load first date by default

    // Dropdown change listener
    const dateDropdown = document.getElementById('dateDropdown');
    if (dateDropdown) {
        dateDropdown.addEventListener('change', function (e) {
            const selectedDate = e.target.value;
            const record = dataset.find(r => r.Date === selectedDate);
            if (record) {
                updateDailyBarChart(record);
            }
        });
    }

    // Chat Form Listener
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (message) {
                handleChatMessage(message);
                input.value = '';
            }
        });
    }

    // File Upload Listener
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
});

// Populate dropdown options
function populateDateDropdown(records) {
    const dropdown = document.getElementById('dateDropdown');
    if (!dropdown) return;
    dropdown.innerHTML = '';
    records.forEach(r => {
        const option = document.createElement('option');
        option.value = r.Date;
        option.textContent = r.Date;
        dropdown.appendChild(option);
    });
}

// Render Daily Bar Chart (Total Expenses, Profit, Loss)
function updateDailyBarChart(record) {
    const profit = record.Revenue > record.Expenses ? (record.Revenue - record.Expenses) : 0;
    const loss = record.Expenses > record.Revenue ? (record.Expenses - record.Revenue) : 0;

    const data = [{
        type: 'bar',
        x: [record.Expenses, profit, loss],
        y: ['Total Daily Expenses', 'Profit', 'Loss'],
        orientation: 'h',
        marker: {
            color: ['#80CBC4', '#66BB6A', '#EF5350']
        }
    }];

    const layout = {
        margin: { l: 130, r: 20, t: 10, b: 30 },
        xaxis: { range: [0, 8000] },
        autosize: true
    };

    Plotly.newPlot('dailyBarChart', data, layout, { responsive: true });
}

// Render Profit & Loss Line Trend Chart
function renderTrendChart(records) {
    const dates = records.map(r => r.Date);
    const profitTrend = records.map(r => r.Revenue > r.Expenses ? r.Revenue : r.Expenses);
    const lossTrend = records.map(r => r.Expenses);

    const traceProfit = {
        x: dates,
        y: profitTrend,
        mode: 'lines+markers',
        name: 'Profit',
        line: { color: '#2E7D32', width: 3, shape: 'spline' }
    };

    const traceLoss = {
        x: dates,
        y: lossTrend,
        mode: 'lines+markers',
        name: 'Loss',
        line: { color: '#C62828', width: 3, shape: 'spline' }
    };

    const layout = {
        margin: { l: 40, r: 20, t: 20, b: 60 },
        yaxis: { title: 'Amount' },
        xaxis: { tickangle: -45 },
        autosize: true
    };

    Plotly.newPlot('trendLineChart', [traceProfit, traceLoss], layout, { responsive: true });
}

// Chatbot Handling
async function handleChatMessage(message) {
    const chatMessages = document.getElementById('chatMessages');

    const userDiv = document.createElement('div');
    userDiv.className = 'user-message';
    userDiv.style.textAlign = 'right';
    userDiv.style.margin = '8px 0';
    userDiv.innerHTML = `<div style="display:inline-block; background:#4F46E5; color:#fff; padding:8px 12px; border-radius:12px;"><p style="margin:0;">${message}</p></div>`;
    chatMessages.appendChild(userDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: message })
        });

        const data = await response.json();

        const botDiv = document.createElement('div');
        botDiv.className = 'bot-message';
        botDiv.innerHTML = `<span class="bot-avatar">✦</span><div><small>FinSight Assistant</small><p>${data.response}</p></div>`;
        chatMessages.appendChild(botDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

    } catch (err) {
        console.error("Chat error:", err);
    }
}

// File Upload Handler
async function handleFileUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const fileMessage = document.getElementById('fileMessage');
    fileMessage.textContent = `Processing ${file.name}...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.data) {
            fileMessage.textContent = `Successfully processed ${file.name}!`;
            populateDateDropdown(data.data);
            renderTrendChart(data.data);
            updateDailyBarChart(data.data[0]);
        }
    } catch (err) {
        fileMessage.textContent = 'Server error during file upload.';
    }
}