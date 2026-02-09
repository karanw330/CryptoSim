# 📈 CryptoSim - Crypto Trading Simulator

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://cryp-sim.vercel.app/) [![Backend Status](https://img.shields.io/badge/Backend-Render-blue)](https://render.com/)

A real-time cryptocurrency trading simulation platform built with a FastAPI backend and a vanilla HTML/JS frontend. Experience trading with live market data, manage your portfolio, and track your performance without risking real money.

## 🚀 Live Demo

Check out the live application here: **[https://cryp-sim.vercel.app/](https://cryp-sim.vercel.app/)**

> [!NOTE]
> **Backend Limitations**: The backend is hosted on Render's Free Tier. This means the server spins down after 15 minutes of inactivity and there is no database persistence. **The first request may take 50+ seconds to respond while the server wakes up and your data may get wiped when the server goes to sleep.** Please be patient!

## ✨ Features

- **Real-Time Market Data**: Live cryptocurrency prices updated via WebSockets.
- **Trading Engine**: Buy and sell cryptocurrencies with instant execution.
- **User Authentication**: Secure signup and login using JWT (JSON Web Tokens).
- **Portfolio Management**: Track your holdings, trade history, and account balance in real-time.
- **Responsive Design**: Clean and intuitive interface optimized for desktop and mobile (work in progress).

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: SQLite
- **Authentication**: OAuth2 with JWT
- **Real-time**: WebSockets for live price updates

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **Hosting**: Vercel

## ⚙️ Configuration

Create a `.env` file in the root directory with the following variables:

```env
SECRET_KEY=your_secret_key_here
ALGORITHM=your algorithm here
FINNHUB_TOKEN= finnhub's api key for real time price stream
CRYP_SIM_KEY= Google Auth Client ID
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/CryptoSim.git
    cd CryptoSim
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    The database initializes automatically on the first run, or you can manually run:
    ```bash
    python -m app.db_init
    ```

### Running the Application

1.  **Start the Backend Server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

2.  **Run the Frontend:**
    You can simply open `Frontend/login_page.html` in your browser, or use a simple HTTP server for a better experience:
    ```bash
    # From the root directory
    python -m http.server 3000
    ```
    Then navigate to `http://localhost:3000/Frontend/login_page.html`.

## 📂 Project Structure

```
CryptoSim/
├── app/                 # Backend application logic
│   ├── login_back/      # Authentication routes and logic
│   ├── otp_verification/# OTP handling
│   ├── routes/          # API and WebSocket routes
│   └── order_book.py    # Trading engine logic
├── Frontend/            # Frontend static files
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript logic
│   └── *.html           # HTML pages
├── data/                # Database file (if created)
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
