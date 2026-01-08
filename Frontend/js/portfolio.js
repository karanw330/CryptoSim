// Set Chart.js defaults for dark theme
Chart.defaults.color = '#ffffff';
Chart.defaults.borderColor = '#3a3a3a';

// Portfolio Donut Chart
const portfolioCtx = document.getElementById('portfolioChart').getContext('2d');
const portfolioChart = new Chart(portfolioCtx, {
    type: 'doughnut',
    data: {
        labels: ['Apple', 'Microsoft', 'Tesla', 'Google', 'Amazon', 'Netflix'],
        datasets: [{
            data: [28.5, 22.3, 15.8, 12.4, 11.2, 9.8],
            backgroundColor: [
                '#3b82f6',
                '#06b6d4',
                '#10b981',
                '#8b5cf6',
                '#f59e0b',
                '#ef4444'
            ],
            borderWidth: 0,
            cutout: '65%'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: '#2a2a2a',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: '#3a3a3a',
                borderWidth: 1,
                callbacks: {
                    label: function (context) {
                        return context.label + ': ' + context.parsed + '%';
                    }
                }
            }
        },
        elements: {
            arc: {
                borderWidth: 2,
                borderColor: '#2a2a2a'
            }
        }
    },
    plugins: [{
        beforeDraw: function (chart) {
            const width = chart.width,
                height = chart.height,
                ctx = chart.ctx;

            ctx.restore();
            const fontSize = (height / 114).toFixed(2);
            ctx.font = `bold ${fontSize}em sans-serif`;
            ctx.textBaseline = "middle";
            ctx.fillStyle = "#ffffff";

            const text = "63.2%",
                textX = Math.round((width - ctx.measureText(text).width) / 2),
                textY = height / 2 - 10;

            ctx.fillText(text, textX, textY);

            ctx.font = `${fontSize * 0.6}em sans-serif`;
            ctx.fillStyle = "#888888";
            const subText = "Allocation",
                subTextX = Math.round((width - ctx.measureText(subText).width) / 2),
                subTextY = height / 2 + 15;

            ctx.fillText(subText, subTextX, subTextY);
            ctx.save();
        }
    }]
});

// Tab switching function
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to clicked tab
    event.target.classList.add('active');

    // Show corresponding content
    document.getElementById(tabName).classList.add('active');
}

// Make chart responsive
window.addEventListener('resize', function () {
    portfolioChart.resize();
});