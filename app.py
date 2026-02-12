import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date, time
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

    buffer_time  = st.number_input("Buffer Between Meetings (min)", 0, 60, 15, 5)
    max_meetings = st.number_input("Max Meetings Per Day", 1, 20, 5)

    if st.button("💾 Save Preferences"):
        st.session_state.preferences = {
            'timezone': timezone,
            'work_hours_start': int(work_start),
            'work_hours_end': int(work_end),
            'preferred_meeting_duration': preferred_duration,
            'buffer_time': int(buffer_time),
            'max_meetings_per_day': int(max_meetings)
        }
        st.success("Preferences saved!")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📅 Calendar", "➕ Add Meeting", "🤖 AI Scheduler", "📊 Analytics"])

# ─────────────────────────────────────────────
# Tab 1: View Calendar
# ─────────────────────────────────────────────
with tab1:
    st.header("Your Calendar")

    meetings = st.session_state.calendar_manager.get_all_meetings()

    if meetings:
        df = pd.DataFrame(meetings)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time']   = pd.to_datetime(df['end_time'])
        df = df.sort_values('start_time')

        st.subheader("All Scheduled Meetings")
        for _, meeting in df.iterrows():
            with st.expander(f"📌 {meeting['title']} — {meeting['start_time'].strftime('%b %d %Y, %I:%M %p')}"):
                st.write(f"**Time:** {meeting['start_time'].strftime('%I:%M %p')} – {meeting['end_time'].strftime('%I:%M %p')}")
                st.write(f"**Duration:** {meeting['duration']} minutes")
                st.write(f"**Attendees:** {meeting['attendees']}")
                if meeting.get('description'):
                    st.write(f"**Description:** {meeting['description']}")

                if st.button("🗑️ Delete", key=f"del_{meeting['id']}"):
                    st.session_state.calendar_manager.delete_meeting(meeting['id'])
                    st.rerun()

        st.subheader("Calendar Table")
        st.dataframe(
            df[['title', 'start_time', 'end_time', 'attendees', 'duration']],
            use_container_width=True
        )
    else:
        st.info("No meetings scheduled yet. Add your first meeting in the ➕ Add Meeting tab!")

# ─────────────────────────────────────────────
# Tab 2: Add Meeting — FREE date + time input
# ─────────────────────────────────────────────
with tab2:
    st.header("Schedule New Meeting")
    st.info("📝 Pick date and time for meeting.")

    col1, col2 = st.columns(2)

    with col1:
        title     = st.text_input("Meeting Title *", placeholder="Weekly Team Sync")
        attendees = st.text_input("Attendees (comma-separated)", placeholder="john@email.com, sarah@email.com")
        duration  = st.selectbox("Duration (minutes) *", [15, 30, 45, 60, 90, 120], index=1)

    with col2:
        # Date input — open range
        meeting_date = st.date_input(
            "Date *",
            value=date.today(),
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31)
        )

        # ✅ Use number inputs for hour/minute so user is NEVER locked to live time
        st.write("**Start Time ***")
        t1, t2 = st.columns(2)
        with t1:
            start_hour   = st.number_input("Hour (0–23)",   min_value=0, max_value=23, value=9,  step=1, key="add_hour")
        with t2:
            start_minute = st.number_input("Minute (0–59)", min_value=0, max_value=59, value=0, step=5, key="add_min")

    description = st.text_area("Description (optional)", placeholder="Meeting agenda and notes...")

    if st.button("➕ Add Meeting"):
        if title:
            start_dt = datetime.combine(meeting_date, time(int(start_hour), int(start_minute)))
            end_dt   = start_dt + timedelta(minutes=int(duration))

            conflicts = st.session_state.calendar_manager.check_conflicts(start_dt, end_dt)

            if conflicts:
                st.warning("⚠️ Conflict with existing meeting(s):")
                for c in conflicts:
                    st.write(f"- **{c['title']}** ({c['start_time']} – {c['end_time']})")
                st.error("Please choose a different time or delete the conflicting meeting.")
            else:
                st.session_state.calendar_manager.add_meeting(
                    title, start_dt, end_dt, attendees, description, int(duration)
                )
                st.success(f"✅ **'{title}'** scheduled for {start_dt.strftime('%b %d %Y at %I:%M %p')}!")
                st.rerun()
        else:
            st.error("Please enter a Meeting Title.")

# ─────────────────────────────────────────────
# Tab 3: AI Scheduler — FREE date range search
# ─────────────────────────────────────────────
with tab3:
    st.header("🤖 AI Meeting Scheduler")
    st.write("Pick any date range and the AI will find the best available slots based on your preferences.")

    col1, col2 = st.columns(2)

    with col1:
        ai_title     = st.text_input("Meeting Title", placeholder="Client Presentation", key="ai_title")
        ai_attendees = st.text_input("Number of Attendees", value="3", key="ai_att")
        ai_duration  = st.selectbox("Duration (minutes)", [15, 30, 45, 60, 90], index=1, key="ai_dur")

    with col2:
        # ✅ Fully open date range — not clamped to today
        ai_start_date = st.date_input(
            "Search From",
            value=date.today(),
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="ai_start"
        )
        ai_end_date = st.date_input(
            "Search Until",
            value=date.today() + timedelta(days=7),
            min_value=date(2020, 1, 1),
            max_value=date(2030, 12, 31),
            key="ai_end"
        )

    ai_priority = st.select_slider(
        "Meeting Priority",
        options=["Low", "Medium", "High", "Urgent"],
        value="Medium"
    )

    ai_notes = st.text_area(
        "Special Requirements (optional)",
        placeholder="Prefer morning meetings, need a conference room, etc.",
        key="ai_notes"
    )

    if st.button("🔍 Find Best Times"):
        if ai_end_date < ai_start_date:
            st.error("'Search Until' must be after 'Search From'.")
        else:
            with st.spinner("Analysing calendar and finding optimal slots…"):
                agent = MeetingSchedulerAgent(st.session_state.preferences)

                suggestions = agent.find_optimal_slots(
                    start_date=ai_start_date,
                    end_date=ai_end_date,
                    duration=int(ai_duration),
                    existing_meetings=st.session_state.calendar_manager.get_all_meetings(),
                    preferences=st.session_state.preferences
                )

            if suggestions:
                st.success(f"✅ Found **{len(suggestions)}** available slots! Showing top 5:")

                for i, slot in enumerate(suggestions[:5], 1):
                    label = (
                        f"Option {i}: {slot['start'].strftime('%A, %b %d %Y')} "
                        f"at {slot['start'].strftime('%I:%M %p')}  "
                        f"⭐ Score: {slot['score']}/100"
                    )
                    with st.expander(label):
                        st.write(f"**Start   :** {slot['start'].strftime('%A, %B %d %Y at %I:%M %p')}")
                        st.write(f"**End     :** {slot['end'].strftime('%I:%M %p')}")
                        st.write(f"**Duration:** {ai_duration} minutes")
                        st.write(f"**Reason  :** {slot['reason']}")

                        if st.button(f"📅 Book Slot {i}", key=f"book_{i}"):
                            booked_title = ai_title if ai_title else "Untitled Meeting"
                            st.session_state.calendar_manager.add_meeting(
                                booked_title,
                                slot['start'],
                                slot['end'],
                                ai_attendees,
                                ai_notes,
                                int(ai_duration)
                            )
                            st.success(f"✅ **'{booked_title}'** booked for {slot['start'].strftime('%b %d at %I:%M %p')}!")
                            st.rerun()
            else:
                st.warning("No available slots found. Try a wider date range or adjust work-hour preferences.")

# ─────────────────────────────────────────────
# Tab 4: Analytics
# ─────────────────────────────────────────────
with tab4:
    st.header("📊 Calendar Analytics")

    meetings = st.session_state.calendar_manager.get_all_meetings()

    if meetings:
        df = pd.DataFrame(meetings)
        df['start_time'] = pd.to_datetime(df['start_time'])

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Meetings", len(df))
        c2.metric("Total Hours",    f"{df['duration'].sum() / 60:.1f}")
        c3.metric("Avg Duration",   f"{df['duration'].mean():.0f} min")

        st.subheader("Meetings by Day of Week")
        df['day_of_week'] = df['start_time'].dt.day_name()
        st.bar_chart(df['day_of_week'].value_counts())

        st.subheader("Meeting Start Hour Distribution")
        df['hour'] = df['start_time'].dt.hour
        st.line_chart(df['hour'].value_counts().sort_index())

        st.subheader("💾 Data Compression Stats")
        original_size   = len(json.dumps(meetings))
        compressed_data = st.session_state.calendar_manager.compress_calendar_data()
        compressed_size = len(compressed_data)
        ratio = (1 - compressed_size / original_size) * 100 if original_size else 0

        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Original Size",      f"{original_size} bytes")
        cc2.metric("Compressed Size",    f"{compressed_size} bytes")
        cc3.metric("Compression Saving", f"{ratio:.1f}%")
    else:
        st.info("No meeting data yet. Add some meetings to see analytics!")

# Sidebar export
st.sidebar.markdown("---")
if st.session_state.calendar_manager.get_all_meetings():
    st.sidebar.subheader("📥 Export")
    export_data = {
        'meetings':    st.session_state.calendar_manager.get_all_meetings(),
        'preferences': st.session_state.preferences
    }
    st.sidebar.download_button(
        "Download Calendar (JSON)",
        data=json.dumps(export_data, indent=2, default=str),
        file_name=f"calendar_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )
