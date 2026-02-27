# Stock Monitor 📈

> **Never miss a stock price target again!** 
> 
> Stock Monitor is an intelligent web application that automatically tracks stock prices and sends you email notifications when your target prices are reached. Perfect for investors who want to monitor multiple stocks without constantly checking the market.

## 🌟 What Can You Do?

- ✅ Monitor multiple stocks simultaneously
- ✅ Set price targets with flexible conditions (above/below)
- ✅ Receive automated email alerts when targets are hit
- ✅ Schedule checks on weekdays, weekends, or every day
- ✅ Toggle monitoring on/off without deleting your watchlist
- ✅ View real-time market status for major exchanges (Taiwan, US, Japan)
- ✅ Track stocks across different markets and currencies

**Currently tracking:** Taiwan Stock Exchange (TWSE), US Stock Exchange (NYSE), Japan Stock Exchange (TSE)

## 🎯 Quick Example

**Scenario:** You want to buy Apple stock when it drops below $180
1. Add AAPL with target price ≤ $180
2. Set daily check at 09:15 AM
3. When AAPL hits $180 or below → Get an email alert immediately! 📧

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

## ⚡ Quick Start (5 Minutes)

1. **Complete the installation steps above** (takes ~2 minutes)

2. **Add your first stock:**
   - Open dashboard at `http://localhost:8000`
   - Enter stock symbol (e.g., `AAPL` or `2330.TW`)
   - Set target price and condition (≥ or ≤)
   - Click "OK"

3. **Set up a schedule:**
   - Click "⏰ My Schedule" section
   - Choose time (e.g., 09:15)
   - Select frequency (Weekday/Weekend/Everyday)
   - Click "Add"

4. **Wait for the magic:**
   - Scheduler checks every 15 minutes (00, 15, 30, 45)
   - When your stock hits the target → Email alert! 🎉

**That's it!** You now have automated stock monitoring running 24/7

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

## How It Works 🔄

Here's the complete flow when a price target is hit:

```
[Scheduler Check at 09:15]
    ↓
[Match Time & Frequency]
    ├─ Check if time = 09:15 ✅
    ├─ Check if day type matches (weekday/weekend/everyday) ✅
    └─ If both match → Continue
    ↓
[Load Watchlist]
    ├─ Get all active stocks for user ✅
    └─ Prepare symbols for price check
    ↓
[Fetch Live Prices]
    ├─ Query Yahoo Finance API for latest prices ✅
    └─ Get AAPL: $180.50, GOOGL: $140.25, etc.
    ↓
[Check Conditions]
    ├─ AAPL $180.50 >= $180.00? ✅ HIT!
    ├─ GOOGL $140.25 <= $135.00? ❌ No Hit
    └─ Collect all hits
    ↓
[Send Email] 📧
    ├─ Group hits by user
    └─ Send summary email with table of triggers
    
    Email Preview:
    ┌─────────────────────────────────┐
    │  🔔 Stock Monitor: 2 Alerts Hit  │
    │  ─────────────────────────────  │
    │  AAPL    | $180.50 | ≥ $180.00  │
    │  2330.TW | $450.00 | ≤ $450.00  │
    └─────────────────────────────────┘
```

## Models 🗄️

The application uses 4 main data models:

### **User** 👤
Who is monitoring stocks (currently defaults to demo user)
```python
- id: int (primary key)
- email: str (unique) - Where alerts are sent
- password: str - Authentication (MVP simplified)
```

### **Watchlist** 👁️
Individual stocks you want to monitor with your target rules
```python
- id: int (primary key)
- user_id: int - Which user owns this watchlist
- symbol: str - Stock ticker (AAPL, 2330.TW, etc.)
- target_price: float - Your price target
- condition: str - "gte" (≥) or "lte" (≤)
- is_active: bool - ON/OFF toggle (true = monitoring active)
```

### **UserSchedule** ⏰
When you want the scheduler to check your watchlist
```python
- id: int (primary key)
- user_id: int - Which user has this schedule
- check_time: str - Time to check (HH:MM format, e.g., "09:15")
- frequency: str - "weekday", "weekend", or "everyday"
```

### **StockMeta** 📊
Stock metadata (name, currency) fetched from Yahoo Finance
```python
- symbol: str (primary key) - Stock ticker
- name: str - Company name
- currency: str - Currency (USD, TWD, etc.)
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

### ❌ Email not being sent?

**Check these steps:**

1. **Verify `.env` file exists** in the project root
   ```bash
   cat .env  # Should show SMTP_USER and SMTP_PASSWORD
   ```

2. **Verify SMTP credentials** are correct
   - For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833), NOT your regular password
   - Enable "Less secure app access" if not using App Password

3. **Check application is running**
   ```bash
   # In terminal, you should see:
   # INFO:     Uvicorn running on http://127.0.0.1:8000
   ```

4. **Look for error messages** in the terminal output
   ```
   ❌ Email failed: [SSL: CERTIFICATE_VERIFY_FAILED]
   ```

### ⏰ Scheduler not running or not triggering?

1. **Confirm scheduler started** when you launched the app
   - Look for: `INFO:     Application startup complete`

2. **Check your schedule time format**
   - Must be HH:MM with 15-minute intervals: `00, 15, 30, 45`
   - Example: ✅ `09:15`, ❌ `09:10`

3. **Verify stocks are marked as ACTIVE**
   - Go to dashboard and check if "ON" button is showing
   - Click toggle to turn monitoring ON

4. **Monitor the terminal output** for scheduler logs
   - Every 15 mins you should see: `🚀 SCHEDULER WOKE UP AT: HH:MM`

5. **Test with a manual price check**
   - Add a stock with current price as target
   - Wait until scheduler runs
   - You should see a "HIT!" message in terminal

### 🗄️ Database errors?

1. **Reset the database completely**
   ```bash
   rm stock_monitor.db
   ```

2. **Restart the application**
   - Stop: Press `Ctrl+C` in terminal
   - Start: `uvicorn main:app --reload`
   - This auto-creates a fresh database

3. **Check database connection**
   ```bash
   # Verify the DATABASE_URL in .env is correct
   cat .env | grep DATABASE_URL
   ```

### 🔍 Still not working? Enable Debug Mode

Check the terminal output for detailed messages:

```
--- 🚀 SCHEDULER WOKE UP AT: 09:15 ---
👀 DB Dump (All Schedules): [('09:15', 'weekday', 1)]
✅ PASS: Found matching schedules for User IDs: [1]
✅ PASS: Found 3 active watchlists. Fetching prices now...
```

Each emoji tells you where the flow stopped:
- 🚀 = Scheduler started
- 👀 = Showing database content
- ✅ = Step passed successfully  
- 🛑 = Process aborted
- ❌ = Error occurred

If you see `🛑 ABORT:` messages, that's your issue!

## License 📄

This project is provided as-is for personal use.

## Contributing 🤝

Want to improve Stock Monitor? Contributions are welcome!

**Areas we need help with:**
- User authentication system
- Support for more markets (Hong Kong, Singapore, etc.)
- Database migrations & schema improvements
- UI/UX enhancements
- Additional notification methods (SMS, LINE, Telegram)
- Performance optimizations

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support 💬

**Having issues?**
- Check the [Troubleshooting](#troubleshooting-) section above
- Review [Terminal Output & Debugging](#terminal-output--debugging-) for detailed logs
- Open an issue on GitHub with:
  - What you expected to happen
  - What actually happened
  - Terminal output/error messages
  - Your OS and Python version

**Questions or suggestions?**
- Open a GitHub Discussion
- Check existing issues to see if someone asked the same thing

## Roadmap 🗺️

See [Future Enhancements](#future-enhancements-) for planned features.

**Current Status:** MVP (Minimum Viable Product)
- Core functionality: ✅ Working
- Production-ready: ⚠️ Not yet (auth system needed)
- Actively maintained: ✅ Yes

## Contact 💬

For questions or feedback, please reach out through:
- GitHub Issues
- GitHub Discussions
- Direct message on GitHub

---

**Happy stock monitoring! 📊** If Stock Monitor helped you, please star ⭐ the repository!
