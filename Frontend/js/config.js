const CONFIG = {
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://127.0.0.1:8000'
        : 'https://cryptosim-backend.onrender.com', // TODO: user should replace this with their actual Render URL
    WS_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'ws://127.0.0.1:8000'
        : 'wss://cryptosim-backend.onrender.com', // TODO: user should replace this with their actual Render URL
};

// Export for use in other scripts if needed, 
// though for simple static sites, global variable is often easiest.
window.APP_CONFIG = CONFIG;
