// Set Chart.js defaults for dark theme
Chart.defaults.color = '#ffffff';
Chart.defaults.borderColor = '#3a3a3a';

// --- Shared Utilities (from RealTime.js) ---
async function getAccessToken() {
    let token = localStorage.getItem('access_token');
    if (!token) return null;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp - now < 60) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) return token;
            const res = await fetch('http://127.0.0.1:8000/refresh', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                return data.access_token;
            }
        }
    } catch (e) {
        console.error("Token error", e);
    }
    return token;
}

async function fetchWithAuth(url, options = {}) {
    const token = await getAccessToken();
    if (!token) {
        window.location.replace('./login_page.html');
        return;
    }
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    return fetch(url, options);
}

// Global data state
window.portfolioData = {
    balance: 0,
    holdings: [],
    prices: {},
    chart: null
};

window.profile = {
    'BINANCE:BTCUSDT': { "symbol": "BTC", "name": "Bitcoin", "color": "#3b82f6", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCBTC--big.svg" },
    'BINANCE:ETHUSDT': { "symbol": "ETH", "name": "Ethereum", "color": "#06b6d4", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCETH--big.svg" },
    'BINANCE:SOLUSDT': { "symbol": "SOL", "name": "Solana", "color": "#10b981", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCSOL--big.svg" },
    'BINANCE:BNBUSDT': { "symbol": "BNB", "name": "Binance Coin", "color": "#8b5cf6", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCBNB--big.svg" },
    'BINANCE:XRPUSDT': { "symbol": "XRP", "name": "Ripple", "color": "#f59e0b", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCXRP--big.svg" },
    'BINANCE:DOGEUSDT': { "symbol": "DOGE", "name": "Dogecoin", "color": "#ef4444", "logo": "https://s3-symbol-logo.tradingview.com/crypto/XTVCDOGE--big.svg" }
};

// --- Daily Movers Logic ---
let moversData = [];

function updateMovers() {
    const winnersList = document.getElementById('winners');
    const losersList = document.getElementById('losers');
    if (!winnersList || !losersList) return;

    // Filter out items without price data
    const validMovers = Object.keys(window.profile)
        .map(key => ({
            key,
            ...window.profile[key],
            price: window.portfolioData.prices[key]?.last_price || 0,
            perc: window.portfolioData.prices[key]?.perc_change || 0
        }))
        .filter(m => m.price > 0)
        .sort((a, b) => b.perc - a.perc);

    const winners = validMovers.filter(m => m.perc >= 0);
    const losers = validMovers.filter(m => m.perc < 0).reverse();

    const renderMover = (m) => `
        <div class="stock-item">
            <div class="stock-info">
                <div class="stock-icon" style="background: ${m.color};">${m.symbol}</div>
                <div class="stock-details">
                    <h4>${m.name}</h4>
                    <p>$${m.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
                </div>
            </div>
            <div class="stock-price">
                <div class="change ${m.perc >= 0 ? 'positive' : 'negative'}">${m.perc >= 0 ? '+' : ''}${m.perc.toFixed(2)}%</div>
            </div>
        </div>
    `;

    winnersList.innerHTML = winners.length ? winners.map(renderMover).join('') : '<p style="padding: 20px; color: #888;">No winners today</p>';
    losersList.innerHTML = losers.length ? losers.map(renderMover).join('') : '<p style="padding: 20px; color: #888;">No losers today</p>';
}

// --- Donut Chart ---
function initChart() {
    const ctx = document.getElementById('portfolioChart').getContext('2d');
    window.portfolioData.chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [],
                borderWidth: 0,
                cutout: '65%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#2a2a2a',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#3a3a3a',
                    borderWidth: 1,
                    callbacks: {
                        label: function (context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            },
            elements: { arc: { borderWidth: 2, borderColor: '#2a2a2a' } }
        },
        plugins: [{
            beforeDraw: function (chart) {
                const width = chart.width, height = chart.height, ctx = chart.ctx;
                ctx.restore();
                const fontSize = (height / 114).toFixed(2);
                ctx.font = `bold ${fontSize}em sans-serif`;
                ctx.textBaseline = "middle";
                ctx.fillStyle = "#ffffff";

                const text = window.portfolioData.allocationText || "0.0%",
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
}

function updateChart(holdings) {
    if (!window.portfolioData.chart) return;

    let totalVal = 0;
    const dataPoints = holdings.map(h => {
        const p = window.portfolioData.prices[h.item_id] || Object.values(window.portfolioData.prices).find(px => px.symbol.includes(h.item_id));
        const price = p ? p.last_price : 0;
        const val = h.amount * price;
        totalVal += val;
        return { label: h.item_id, value: val, color: window.profile[p?.symbol || Object.keys(window.profile).find(k => k.includes(h.item_id))]?.color || '#888' };
    }).filter(d => d.value > 0);

    if (dataPoints.length === 0) {
        window.portfolioData.allocationText = "0.0%";
        window.portfolioData.chart.data.labels = ['Empty'];
        window.portfolioData.chart.data.datasets[0].data = [100];
        window.portfolioData.chart.data.datasets[0].backgroundColor = ['#333333'];
    } else {
        window.portfolioData.chart.data.labels = dataPoints.map(d => d.label);
        window.portfolioData.chart.data.datasets[0].data = dataPoints.map(d => (d.value / totalVal) * 100);
        window.portfolioData.chart.data.datasets[0].backgroundColor = dataPoints.map(d => d.color);
        window.portfolioData.allocationText = "100%";
    }
    window.portfolioData.chart.update();
}

// --- Dashboard Sync ---
async function syncPortfolio() {
    try {
        // 1. Fetch User (Balance)
        const userRes = await fetchWithAuth('http://127.0.0.1:8000/users/me/');
        if (userRes && userRes.ok) {
            const userData = await userRes.json();
            window.portfolioData.balance = userData.balance_usd;
            document.getElementById('dashboard_cash_balance').textContent = `$${userData.balance_usd.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
            if (document.getElementById('stockUserMenu')) {
                document.getElementById('stockUserMenu').textContent = userData.username.substring(0, 2).toUpperCase();
            }
        }

        // 2. Fetch Holdings
        const portfolioRes = await fetchWithAuth('http://127.0.0.1:8000/users/me/items/');
        if (portfolioRes && portfolioRes.ok) {
            window.portfolioData.holdings = await portfolioRes.json();
            renderHoldings();
        }

        // 3. Update Global Stats
        updateStats();
    } catch (e) {
        console.error("Sync error:", e);
    }
}

function renderHoldings() {
    const list = document.getElementById('dashboard_holdings_list');
    if (!list) return;

    list.innerHTML = '';
    let totalHoldingsVal = 0;

    window.portfolioData.holdings.forEach(item => {
        const symbol = item.item_id;
        const amount = item.amount;
        // Match symbol from profile or prices
        const priceKey = Object.keys(window.profile).find(k => k.includes(symbol));
        const priceData = window.portfolioData.prices[priceKey];
        const currentPrice = priceData ? priceData.last_price : 0;
        const val = amount * currentPrice;
        totalHoldingsVal += val;

        const prof = window.profile[priceKey] || { name: symbol, logo: "" };

        list.insertAdjacentHTML('beforeend', `
            <div class="stock-item">
                <div class="stock-info">
                    <div class="stock-icon" style="background: rgba(255,255,255,0.05);"><img src="${prof.logo}" width="100%" height="100%" style="border-radius:50%"></div>
                    <div class="stock-details">
                        <h4>${prof.name}</h4>
                        <p>${symbol} • ${amount.toFixed(4)} units</p>
                    </div>
                </div>
                <div class="stock-price">
                    <div class="price">$${val.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                    <div class="change" style="color: #888;">@ $${currentPrice.toLocaleString()}</div>
                </div>
            </div>
        `);
    });

    if (window.portfolioData.holdings.length === 0) {
        list.innerHTML = '<div class="stock-item"><div class="stock-info"><p>No holdings found</p></div></div>';
    }

    window.portfolioData.totalHoldingsValue = totalHoldingsVal;
    updateChart(window.portfolioData.holdings);
}

function updateStats() {
    const totalValue = window.portfolioData.balance + (window.portfolioData.totalHoldingsValue || 0);
    const initialBalance = 100000;
    const totalProfit = totalValue - initialBalance;
    const profitPerc = (totalProfit / initialBalance) * 100;

    document.getElementById('dashboard_total_value').textContent = `$${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    const percEl = document.getElementById('dashboard_total_perc_change');
    percEl.textContent = `${profitPerc >= 0 ? '+' : ''}${profitPerc.toFixed(2)}%`;
    percEl.className = profitPerc >= 0 ? 'stats-change positive' : 'stats-change negative';

    const profitEl = document.getElementById('dashboard_total_profit');
    profitEl.textContent = `${totalProfit >= 0 ? '+' : '-'}$${Math.abs(totalProfit).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    profitEl.className = totalProfit >= 0 ? 'stats-value positive' : 'stats-value negative';

    // Update Performance Section (Today)
    const perfItems = document.querySelectorAll('.performance-item');
    if (perfItems.length > 0) {
        const todayValue = perfItems[0].querySelector('.performance-value');
        if (todayValue) {
            todayValue.textContent = `${profitPerc >= 0 ? '+' : ''}${profitPerc.toFixed(2)}%`;
            todayValue.className = `performance-value ${profitPerc >= 0 ? 'positive' : 'negative'}`;
        }
    }
}

// --- WebSocket Connection ---
function initWebSockets() {
    const socket = new WebSocket('ws://127.0.0.1:8000/ws/market');

    socket.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "send_stock_data") {
                window.portfolioData.prices[data.symbol] = data;

                // Throttle updates
                if (!window._last_ui_update || Date.now() - window._last_ui_update > 1000) {
                    renderHoldings();
                    updateStats();
                    updateMovers();
                    window._last_ui_update = Date.now();
                }
            }
        } catch (e) { }
    };

    socket.onclose = () => {
        setTimeout(initWebSockets, 5000);
    };
}

// Tab switching function
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    syncPortfolio();
    initWebSockets();
});

// Make chart responsive
window.addEventListener('resize', function () {
    if (window.portfolioData.chart) window.portfolioData.chart.resize();
});
