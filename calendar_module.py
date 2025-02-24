import datetime
import sqlite3
from discord.ext import tasks

DB_FILE = "events.db"

class CalendarEvent:
    """Class representing a calendar event."""
    def __init__(self, event_name, event_date_time, user_id, description="", reminder_time=0, repeat=None, max_repeats=None, repeat_count=0, reminded=False):
        self.event_name = event_name  # Event name
        self.event_date_time = event_date_time  # Event date and time (datetime object)
        self.user_id = user_id  # User ID associated with the event
        self.description = description  # Event description
        self.reminder_time = reminder_time  # Reminder time in minutes before the event
        self.repeat = repeat  # Repeat interval (timedelta object)
        self.max_repeats = max_repeats  # Maximum number of repetitions
        self.repeat_count = repeat_count  # Current repeat count
        self.reminded = reminded  # Whether the user has been reminded

def initialize_db():
    """Initialize the database and ensure the events table exists."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_name TEXT,
            event_date_time TEXT,
            user_id INTEGER,
            description TEXT,
            reminder_time INTEGER,
            repeat_interval INTEGER,
            max_repeats INTEGER,
            repeat_count INTEGER DEFAULT 0,
            reminded BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_event(event):
    """Add a new event to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (event_name, event_date_time, user_id, description, reminder_time, repeat_interval, max_repeats, repeat_count, reminded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event.event_name, event.event_date_time.strftime("%Y-%m-%d %H:%M"), event.user_id, event.description, event.reminder_time, event.repeat.total_seconds() if event.repeat else None, event.max_repeats, event.repeat_count, event.reminded))
    conn.commit()
    conn.close()

def remove_event(event_name, user_id):
    """Remove a specific event from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE event_name = ? AND user_id = ?", (event_name, user_id))
    conn.commit()
    conn.close()

def get_user_events(user_id):
    """Retrieve all events for a specific user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT event_name, event_date_time, description FROM events WHERE user_id = ?", (user_id,))
    events = cursor.fetchall()
    conn.close()
    
    return [CalendarEvent(event_name, datetime.datetime.strptime(event_date_time, "%Y-%m-%d %H:%M"), user_id, description) for event_name, event_date_time, description in events]

@tasks.loop(seconds=60)
async def check_events(bot):
    """Check if any events need to be triggered or reminded."""
    current_time = datetime.datetime.now(datetime.timezone.utc)  # ✅ Ensure UTC timezone
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()

    for row in events:
        event_name, event_date_time, user_id, description, reminder_time, repeat_interval, max_repeats, repeat_count, reminded = row

        # ✅ Convert event_time to UTC
        event_time = datetime.datetime.strptime(event_date_time, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)
        reminder_time = event_time - datetime.timedelta(minutes=reminder_time)

        # ✅ Reminder logic
        if reminder_time <= current_time and not reminded:
            user = bot.get_user(user_id) or await bot.fetch_user(user_id)
            if user:
                await user.send(f"🔔 Reminder: Your event `{event_name}` is about to start!")
            cursor.execute("UPDATE events SET reminded = 1 WHERE event_name = ? AND user_id = ?", (event_name, user_id))

        # ✅ Handle expired events
        if event_time <= current_time:
            if repeat_interval and (max_repeats is None or repeat_count < max_repeats):
                next_time = event_time + datetime.timedelta(seconds=repeat_interval)
                cursor.execute("UPDATE events SET event_date_time = ?, repeat_count = ?, reminded = 0 WHERE event_name = ? AND user_id = ?", 
                               (next_time.strftime("%Y-%m-%d %H:%M"), repeat_count + 1, event_name, user_id))
            else:
                cursor.execute("DELETE FROM events WHERE event_name = ? AND user_id = ?", (event_name, user_id))

    conn.commit()
    conn.close()

initialize_db()  # Ensure the database exists
