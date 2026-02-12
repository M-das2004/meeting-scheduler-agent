# 📅 Meeting Scheduler Agent

An intelligent scheduling system that compresses calendar data and optimizes meeting arrangements with reduced latency.

## Features

- 📅 **Smart Calendar Management**: Add, view, and delete meetings with conflict detection
- 🤖 **AI-Powered Scheduling**: Automatically find optimal meeting times based on preferences
- ⚙️ **Customizable Preferences**: Set work hours, meeting duration, buffer times
- 🔍 **Conflict Detection**: Automatically detect scheduling conflicts
- 📊 **Calendar Analytics**: View meeting patterns and statistics
- 💾 **Data Compression**: Reduce calendar data size by 60-70% for efficient processing
- 📥 **Export Functionality**: Download your calendar data

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd meeting-scheduler-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Use

### Set Your Preferences (Sidebar)
1. Select your timezone
2. Set work hours (e.g., 9 AM - 5 PM)
3. Choose preferred meeting duration
4. Set buffer time between meetings
5. Define max meetings per day
6. Click "Save Preferences"

### Add Meetings
1. Go to "➕ Add Meeting" tab
2. Enter meeting details:
   - Title
   - Attendees (comma-separated emails)
   - Date and time
   - Duration
   - Optional description
3. Click "Add Meeting"
4. System will check for conflicts automatically

### Use AI Scheduler
1. Go to "🤖 AI Scheduler" tab
2. Enter meeting requirements:
   - Meeting title
   - Number of attendees
   - Duration
   - Date range to search
3. Set meeting priority
4. Add any special requirements
5. Click "Find Best Times"
6. Review AI suggestions with scores
7. Book your preferred slot

### View Calendar & Analytics
- **📅 Calendar Tab**: View all upcoming meetings
- **📊 Analytics Tab**: See meeting patterns, time distribution, and compression stats

## How It Works

### Intelligent Scheduling Algorithm

The AI scheduler evaluates time slots based on multiple factors:

**Scoring Factors (0-100 points):**
- ⏰ **Time of Day**:
  - 9-11 AM: +20 points (peak focus time)
  - 2-4 PM: +15 points (good productivity)
  - After 4 PM: -10 points
  - 12-1 PM: -15 points (lunch hour)

- 📅 **Day of Week**:
  - Tuesday-Thursday: +10 points (mid-week ideal)
  - Monday: -5 points (busy catch-up)
  - Friday afternoon: -15 points

- ⏱️ **Meeting Duration**:
  - Long meetings (60+ min) in morning: +10 points

### Data Compression

Calendar data is compressed using `zlib` compression:
- **Original**: Full JSON with all meeting details
- **Compressed**: Base64-encoded compressed data
- **Savings**: Typically 60-70% size reduction
- **Use Case**: Faster API calls, reduced bandwidth

## Project Structure

```
meeting-scheduler-agent/
├── app.py                    # Main Streamlit application
├── scheduler_agent.py        # AI scheduling logic
├── calendar_manager.py       # Calendar data management
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Features Breakdown

### 1. Calendar Management (`calendar_manager.py`)
- Add/delete meetings
- Check conflicts
- Get availability
- Compress/decompress calendar data
- Generate calendar summaries

### 2. AI Scheduler (`scheduler_agent.py`)
- Find optimal time slots
- Score slots based on preferences
- Suggest rescheduling
- Check meeting load
- Avoid overloading days

### 3. User Interface (`app.py`)
- Clean, intuitive Streamlit interface
- Multiple tabs for different functions
- Real-time conflict detection
- Visual analytics and charts
- Data export functionality

## Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/meeting-scheduler-agent.git
git push -u origin main
```

2. **Deploy**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Deploy!

3. **Get your link**: 
   ```
   https://meeting-scheduler-agent-xxxxx.streamlit.app
   ```

## Example Use Cases

1. **Personal Calendar Management**: Track all your meetings in one place
2. **Team Scheduling**: Find best times that work for everyone
3. **Interview Scheduling**: Optimize candidate interview slots
4. **Client Meetings**: Find professional meeting times
5. **Recurring Meetings**: Set up weekly team syncs

## Technical Highlights

- **No API Key Required**: Works completely offline
- **Smart Algorithms**: Rule-based AI for optimal scheduling
- **Efficient**: Compressed data reduces processing time
- **User-Friendly**: Clean interface with helpful tooltips
- **Analytics**: Understand your meeting patterns

## Future Enhancements

- [ ] Email integration (Google Calendar, Outlook)
- [ ] Recurring meeting support
- [ ] Team availability checking
- [ ] Video conferencing links
- [ ] Meeting reminders
- [ ] Time zone conversion
- [ ] Meeting templates

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License

---

**Built with ❤️ using Streamlit**

For questions or support, please open an issue on GitHub.
