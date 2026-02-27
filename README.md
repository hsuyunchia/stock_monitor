# Stock Monitor 📈

A FastAPI-based stock price monitoring application that tracks stock prices and sends email notifications when target prices are reached.

## Features ✨

- **Stock Price Monitoring**: Add stocks to your watchlist with target prices
- **Conditional Alerts**: Set alerts for when prices go above (GTE) or below (LTE) your target
- **Email Notifications**: Receive email summaries when alerts are triggered
- **Flexible Scheduling**: Configure monitoring frequency (weekdays, weekends, or everyday)
- **Web Dashboard**: User-friendly dashboard to manage your watchlist and schedules
- **Persistent Storage**: SQLite database to store users, stocks, and monitoring rules
- **Duplicate Prevention**: Prevents duplicate watchlist entries and schedules
- **Toggle Monitoring**: Turn stocks on/off without deleting them
- **Timezone Support**: Asia/Taipei timezone for accurate scheduling
- **Debug Logging**: Comprehensive terminal output for debugging and monitoring
- **Sorted Schedules**: Schedules displayed in chronological order on dashboard

## Tech Stack 🛠️

- **Backend**: FastAPI, Uvicorn
- **Database**: SQLModel, SQLite
- **Task Scheduling**: APScheduler (background job scheduler)
- **Stock Data**: yfinance (fetches real-time stock prices)
- **Frontend**: Jinja2 templates, HTML/CSS
- **Email**: SMTP (Gmail or other providers)
- **Environment Management**: python-dotenv

## Project Structure 📁

```
stock_monitor/
├── main.py                 # FastAPI app setup & dashboard route
├── models.py              # SQLModel definitions (User, Watchlist, etc.)
├── config.py              # Configuration & environment variables
├── database.py            # Database initialization & session management
├── requirements.txt       # Python dependencies
│
├── routers/               # API route handlers
│   ├── stocks.py         # Stock add/delete endpoints
│   └── schedules.py      # Schedule management endpoints
│
├── services/             # Business logic
│   ├── fetcher.py        # yfinance stock data fetching
│   ├── notifier.py       # Email notification service
│   └── scheduler.py      # Background task scheduling & notifications
│
├── templates/            # Frontend templates
│   └── dashboard.html    # Web UI for managing stocks
│
└── stock_monitor.db      # SQLite database (auto-created)
```

## Installation 🚀

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock_monitor
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   DATABASE_URL=sqlite:///./stock_monitor.db
   ```
   
   **Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:8000`

## Usage 📝

### Adding a Stock to Monitor

1. Go to the dashboard (`http://localhost:8000`)
2. Fill in the stock form:
   - **Symbol**: Stock ticker (e.g., AAPL, GOOGL)
   - **Target Price**: The price threshold
   - **Condition**: Choose "≥" (GTE) or "≤" (LTE)
3. Click "Add Stock"

### Setting Up Schedules

Configure when you want price checks to run:
- **Check Time**: Time of day (e.g., 09:15)
- **Frequency**: Weekdays, weekends, or everyday

The scheduler runs in the background and checks active watchlist items at specified times.

### How Notifications Work

1. At your configured check time, the scheduler fetches current stock prices
2. Compares prices against your target prices and conditions
3. Sends an email summary if any alerts are triggered
4. Email contains stock names, current prices, and your target prices

## Models 🗄️

### User
```python
- id: int (primary key)
- email: str (unique)
- password: str
```

### Watchlist
```python
- id: int (primary key)
- user_id: int (foreign key)
- symbol: str (stock ticker)
- target_price: float
- condition: str ("gte" or "lte")
- is_active: bool
```

### UserSchedule
```python
- id: int (primary key)
- user_id: int (foreign key)
- check_time: str (e.g., "09:15")
- frequency: str ("weekday", "weekend", "everyday")
```

### StockMeta
```python
- symbol: str (primary key)
- name: str (company name)
- currency: str
```

## API Endpoints 🔌

### Stock Management
- `POST /stocks/add` - Add a stock to watchlist (with duplicate prevention)
- `POST /stocks/delete/{item_id}` - Remove a stock from watchlist
- `POST /stocks/toggle/{item_id}` - Toggle stock monitoring on/off

### Schedule Management
- `POST /schedules/add` - Add monitoring schedule (with duplicate prevention)
- `POST /schedules/delete/{sched_id}` - Remove a schedule

### Dashboard
- `GET /` - Main dashboard UI

## Environment Variables 🔐

| Variable | Description | Required |
|----------|-------------|----------|
| `SMTP_USER` | Email address for sending notifications | Yes |
| `SMTP_PASSWORD` | Email password or app password | Yes |
| `DATABASE_URL` | Database connection string | No (defaults to SQLite) |

## Terminal Output & Debugging 🖥️

The scheduler provides comprehensive logging in the terminal to help you understand what's happening:

### Successful Flow Example
```
--- 🚀 SCHEDULER WOKE UP AT: 09:15 ---
👀 DB Dump (All Schedules): [('09:15', 'weekday', 1), ('10:30', 'everyday', 1)]
✅ PASS: Found matching schedules for User IDs: [1]
✅ PASS: Found 3 active watchlists. Fetching prices now...
📈 API Result: {'AAPL': 180.50, 'GOOGL': 140.25, '2330.TW': 450.00}
🎯 HIT! AAPL current (180.50) vs target (>= 180.00)
💤 No Hit: GOOGL current (140.25) vs target (<= 135.00)
🎯 HIT! 2330.TW current (450.00) vs target (<= 450.00)
📧 Sending email to User 1 (demo@example.com)...
✅ Email sent to demo@example.com
```

### What Each Message Means

| Message | Status | Meaning |
|---------|--------|---------|
| `🚀 SCHEDULER WOKE UP AT: HH:MM` | ℹ️ Info | Scheduler is checking conditions |
| `👀 DB Dump (All Schedules): [...]` | 🔍 Debug | Shows all schedules in database |
| `✅ PASS: Found matching schedules` | ✅ Success | Time & frequency conditions matched |
| `✅ PASS: Found N active watchlists` | ✅ Success | Active stocks found to monitor |
| `📈 API Result: {...}` | 📊 Data | Stock prices fetched successfully |
| `🎯 HIT! SYMBOL current (X) vs target (OP Y)` | 🎯 Alert | Stock price met target condition |
| `💤 No Hit: SYMBOL...` | 💤 Info | Stock price didn't meet target |
| `📧 Sending email to User X...` | 📨 Action | Email is being sent |
| `✅ Email sent to user@example.com` | ✅ Success | Email sent successfully |
| `🛑 ABORT: No schedules matched` | ⚠️ Warning | No active schedules at this time |
| `⚠️ Missing price for SYMBOL` | ⚠️ Warning | Stock price couldn't be fetched |
| `❌ Email failed: <error>` | ❌ Error | SMTP error occurred |

## Notes 📌

- **MVP Version**: Currently uses a default user (id=1) for demonstration
- **Security**: Password storage is simplified for MVP; use bcrypt for production
- **Stock Data**: Real-time data sourced from Yahoo Finance via yfinance
- **Timezone**: Uses Asia/Taipei timezone for scheduler consistency
- **Duplicate Prevention**: Both watchlist items and schedules check for duplicates before adding
- **Toggle vs Delete**: Use toggle (ON/OFF button) to temporarily pause monitoring, delete to remove completely

## Future Enhancements 🎯

- [ ] User authentication & login system (replace hardcoded demo user)
- [ ] Multiple users with proper session management
- [ ] Support for stock symbols without `.TW` suffix (auto-detection)
- [ ] Display Chinese company names in dashboard & emails
- [ ] Prevent duplicate alert messages in the same email
- [ ] LINE notification support (in addition to email)
- [ ] Holiday/vacation mode - pause all monitoring for X days
- [ ] Portfolio tracking & performance analytics
- [ ] Stock price history & charts
- [ ] Advanced filtering & sorting options
- [ ] Rate limiting for API calls
- [ ] SMS notifications support

## Troubleshooting 🐛

**Email not being sent?**
- Verify SMTP credentials in `.env`
- Check that less secure app access is enabled (for Gmail)
- Ensure `.env` file exists in the project root

**Scheduler not running?**
- Check that the application is still running
- Verify check times are set correctly
- Look at console logs for APScheduler messages

**Database errors?**
- Delete `stock_monitor.db` to reset the database
- Restart the application to reinitialize tables

## License 📄

This project is provided as-is for personal use.

## Contact 💬

For issues or questions, please reach out or open an issue on the repository.
