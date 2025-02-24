# bot-module

This is a calling module made according to someone's request

## Language？

python

## How to use
First, navigate to your bot project.

Next, at the top of your bot file, use the `from import` statement with these function imports:
```python
from calendar_module import add_event, remove_event, get_user_events, check_events, CalendarEvent
```

Then, in your bot project, add the following commands:
```python
@bot.slash_command(name="event_add", description="Add a new event to the calendar")
async def event_add(
    ctx: discord.ApplicationContext,
    event_name: str,
    event_time: str,
    description: str = "",
    reminder_time: int = 10,
    repeat: int = 0
):
    """ Add a new event. Time format: YYYY-MM-DD HH:MM """
    try:
        event_date_time = datetime.strptime(event_time, "%Y-%m-%d %H:%M")
        repeat_delta = timedelta(minutes=repeat) if repeat > 0 else None

        new_event = CalendarEvent(
            event_name=event_name,
            event_date_time=event_date_time,
            user_id=ctx.author.id,
            description=description,
            reminder_time=reminder_time,
            repeat=repeat_delta
        )

        add_event(new_event)
        await ctx.respond(f"✅ Event `{event_name}` has been added for {event_time}!")
    except ValueError:
        await ctx.respond("⚠ Invalid time format. Please use `YYYY-MM-DD HH:MM`!")

@bot.slash_command(name="event_remove", description="Remove an event by name")
async def event_remove(ctx: discord.ApplicationContext, event_name: str):
    """ Remove a specific event """
    remove_event(event_name, ctx.author.id)
    await ctx.respond(f"🗑 Event `{event_name}` has been removed!")

@bot.slash_command(name="event_list", description="View all your events")
async def event_list(ctx: discord.ApplicationContext):
    """ List all user events """
    user_events = get_user_events(ctx.author.id)

    if not user_events:
        await ctx.respond("📭 You currently have no events!")
        return

    event_messages = []
    for event in user_events:
        event_messages.append(f"📅 **{event.event_name}** - {event.event_date_time.strftime('%Y-%m-%d %H:%M')}\n📌 {event.description}")

    response = "\n\n".join(event_messages)
    await ctx.respond(f"**Your event list:**\n{response}")
```

Finally, enter these commands into your bot project.
- Note: The commands I use are built with Pycord, not discord.py.
- Make sure you have Pycord installed.

## Version？

V1.4

### Acknowledgment
Created by Shiroko253 (Deprecated Features)

Adapted by Miya253

### License
MIT
