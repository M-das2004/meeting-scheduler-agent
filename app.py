import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
from scheduler_agent import MeetingSchedulerAgent
from calendar_manager import CalendarManager

# Initialize session state
if 'calendar_manager' not in st.session_state:
    st.session_state.calendar_manager = CalendarManager()

if 'preferences' not in st.session_state:
    st.session_state.preferences = {
        'timezone': 'UTC',
        'work_hours_start': 9,
        'work_hours_end': 17,
        'preferred_meeting_duration': 30,
        'buffer_time': 15,
        'max_meetings_per_day': 5
    }

# Page config
st.set_page_config(
    page_title="Meeting Scheduler Agent",
    page_icon="📅",
    layout="wide"
)

st.title("📅 Meeting Scheduler Agent")
st.caption("AI-powered intelligent scheduling with data compression")

# Sidebar - Preferences
with st.sidebar:
    st.header("⚙️ Scheduling Preferences")
    
    timezone = st.selectbox(
        "Timezone",
        ["UTC", "EST", "PST", "CST", "MST", "IST"],
        index=0
    )
    
    col1, col2 = st.columns(2)
    with col1:
        work_start = st.number_input("Work Start (Hour)", 0, 23, 9)
    with col2:
        work_end = st.number_input("Work End (Hour)", 0, 23, 17)
    
    preferred_duration = st.selectbox(
        "Preferred Meeting Duration (min)",
        [15, 30, 45, 60, 90],
        index=1
    )
    
    buffer_time = st.number_input("Buffer Between Meetings (min)", 0, 60, 15, 5)
    max_meetings = st.number_input("Max Meetings Per Day", 1, 20, 5)
    
    if st.button("💾 Save Preferences"):
        st.session_state.preferences = {
            'timezone': timezone,
            'work_hours_start': work_start,
            'work_hours_end': work_end,
            'preferred_meeting_duration': preferred_duration,
            'buffer_time': buffer_time,
            'max_meetings_per_day': max_meetings
        }
        st.success("Preferences saved!")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📅 Calendar", "➕ Add Meeting", "🤖 AI Scheduler", "📊 Analytics"])

# Tab 1: View Calendar
with tab1:
    st.header("Your Calendar")
    
    meetings = st.session_state.calendar_manager.get_all_meetings()
    
    if meetings:
        # Convert to DataFrame for display
        df = pd.DataFrame(meetings)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df = df.sort_values('start_time')
        
        # Display upcoming meetings
        st.subheader("Upcoming Meetings")
        now = datetime.now()
        upcoming = df[df['start_time'] >= now]
        
        if not upcoming.empty:
            for _, meeting in upcoming.iterrows():
                with st.expander(f"📌 {meeting['title']} - {meeting['start_time'].strftime('%b %d, %I:%M %p')}"):
                    st.write(f"**Time:** {meeting['start_time'].strftime('%I:%M %p')} - {meeting['end_time'].strftime('%I:%M %p')}")
                    st.write(f"**Duration:** {meeting['duration']} minutes")
                    st.write(f"**Attendees:** {meeting['attendees']}")
                    if meeting.get('description'):
                        st.write(f"**Description:** {meeting['description']}")
                    
                    if st.button(f"🗑️ Delete", key=f"del_{meeting['id']}"):
                        st.session_state.calendar_manager.delete_meeting(meeting['id'])
                        st.rerun()
        else:
            st.info("No upcoming meetings scheduled")
        
        # Display calendar view
        st.subheader("Calendar View")
        st.dataframe(
            df[['title', 'start_time', 'end_time', 'attendees', 'duration']],
            use_container_width=True
        )
    else:
        st.info("No meetings scheduled. Add your first meeting!")

# Tab 2: Add Meeting
with tab2:
    st.header("Schedule New Meeting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Meeting Title*", placeholder="Weekly Team Sync")
        attendees = st.text_input("Attendees (comma-separated)", placeholder="john@email.com, sarah@email.com")
        
    with col2:
        meeting_date = st.date_input("Date*", datetime.now().date())
        meeting_time = st.time_input("Start Time*", datetime.now().time())
    
    duration = st.selectbox(
        "Duration (minutes)*",
        [15, 30, 45, 60, 90, 120],
        index=1
    )
    
    description = st.text_area("Description (optional)", placeholder="Meeting agenda and notes...")
    
    if st.button("➕ Add Meeting"):
        if title and meeting_date and meeting_time:
            # Combine date and time
            start_datetime = datetime.combine(meeting_date, meeting_time)
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Check for conflicts
            conflicts = st.session_state.calendar_manager.check_conflicts(
                start_datetime,
                end_datetime
            )
            
            if conflicts:
                st.warning("⚠️ Conflict detected with existing meetings:")
                for conflict in conflicts:
                    st.write(f"- {conflict['title']} ({conflict['start_time']} - {conflict['end_time']})")
                
                if st.button("Schedule Anyway"):
                    meeting_id = st.session_state.calendar_manager.add_meeting(
                        title, start_datetime, end_datetime, attendees, description, duration
                    )
                    st.success(f"✅ Meeting '{title}' added!")
                    st.rerun()
            else:
                meeting_id = st.session_state.calendar_manager.add_meeting(
                    title, start_datetime, end_datetime, attendees, description, duration
                )
                st.success(f"✅ Meeting '{title}' scheduled successfully!")
                st.rerun()
        else:
            st.error("Please fill in all required fields (*)")

# Tab 3: AI Scheduler
with tab3:
    st.header("🤖 AI Meeting Scheduler")
    
    st.write("Let AI find the best time for your meeting based on your calendar and preferences.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ai_title = st.text_input("Meeting Title", placeholder="Client Presentation")
        ai_attendees = st.text_input("Number of Attendees", value="3")
        ai_duration = st.selectbox("Duration (minutes)", [15, 30, 45, 60, 90], index=1)
    
    with col2:
        ai_date_range_start = st.date_input("Search From", datetime.now().date())
        ai_date_range_end = st.date_input("Search Until", (datetime.now() + timedelta(days=7)).date())
    
    ai_priority = st.select_slider(
        "Meeting Priority",
        options=["Low", "Medium", "High", "Urgent"],
        value="Medium"
    )
    
    ai_preferences_text = st.text_area(
        "Special Requirements (optional)",
        placeholder="Prefer morning meetings, need a conference room, etc."
    )
    
    if st.button("🔍 Find Best Times"):
        with st.spinner("Analyzing your calendar and finding optimal slots..."):
            agent = MeetingSchedulerAgent(st.session_state.preferences)
            
            # Get calendar data
            calendar_data = st.session_state.calendar_manager.get_calendar_summary(
                ai_date_range_start,
                ai_date_range_end
            )
            
            # Find available slots
            suggestions = agent.find_optimal_slots(
                start_date=ai_date_range_start,
                end_date=ai_date_range_end,
                duration=ai_duration,
                existing_meetings=st.session_state.calendar_manager.get_all_meetings(),
                preferences=st.session_state.preferences
            )
            
            if suggestions:
                st.success(f"Found {len(suggestions)} optimal time slots!")
                
                for i, slot in enumerate(suggestions[:5], 1):
                    with st.expander(f"Option {i}: {slot['start'].strftime('%b %d, %I:%M %p')} ⭐ Score: {slot['score']}/100"):
                        st.write(f"**Start:** {slot['start'].strftime('%A, %B %d at %I:%M %p')}")
                        st.write(f"**End:** {slot['end'].strftime('%I:%M %p')}")
                        st.write(f"**Duration:** {ai_duration} minutes")
                        st.write(f"**Reason:** {slot['reason']}")
                        
                        if st.button(f"📅 Book This Slot", key=f"book_{i}"):
                            meeting_id = st.session_state.calendar_manager.add_meeting(
                                ai_title,
                                slot['start'],
                                slot['end'],
                                ai_attendees,
                                ai_preferences_text,
                                ai_duration
                            )
                            st.success(f"✅ Meeting booked for {slot['start'].strftime('%b %d at %I:%M %p')}!")
                            st.rerun()
            else:
                st.warning("No suitable time slots found. Try adjusting your date range or preferences.")

# Tab 4: Analytics
with tab4:
    st.header("📊 Calendar Analytics")
    
    meetings = st.session_state.calendar_manager.get_all_meetings()
    
    if meetings:
        df = pd.DataFrame(meetings)
        df['start_time'] = pd.to_datetime(df['start_time'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Meetings", len(df))
        
        with col2:
            total_duration = df['duration'].sum()
            st.metric("Total Hours", f"{total_duration / 60:.1f}")
        
        with col3:
            avg_duration = df['duration'].mean()
            st.metric("Avg Duration", f"{avg_duration:.0f} min")
        
        # Meetings by day of week
        st.subheader("Meetings by Day of Week")
        df['day_of_week'] = df['start_time'].dt.day_name()
        day_counts = df['day_of_week'].value_counts()
        st.bar_chart(day_counts)
        
        # Meeting time distribution
        st.subheader("Meeting Time Distribution")
        df['hour'] = df['start_time'].dt.hour
        hour_counts = df['hour'].value_counts().sort_index()
        st.line_chart(hour_counts)
        
        # Compression stats
        st.subheader("Data Compression Stats")
        original_size = len(json.dumps(meetings))
        compressed_data = st.session_state.calendar_manager.compress_calendar_data()
        compressed_size = len(compressed_data)
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Size", f"{original_size} bytes")
        with col2:
            st.metric("Compressed Size", f"{compressed_size} bytes")
        with col3:
            st.metric("Compression Ratio", f"{compression_ratio:.1f}%")
    else:
        st.info("No data available for analytics. Schedule some meetings first!")

# Export functionality
st.sidebar.markdown("---")
if st.session_state.calendar_manager.get_all_meetings():
    st.sidebar.subheader("📥 Export Data")
    
    export_data = {
        'meetings': st.session_state.calendar_manager.get_all_meetings(),
        'preferences': st.session_state.preferences
    }
    
    st.sidebar.download_button(
        "Download Calendar Data",
        data=json.dumps(export_data, indent=2, default=str),
        file_name=f"calendar_export_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )