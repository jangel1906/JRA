# Task Multiverse - A Sims-like Task Management App

A unique and engaging task management application where characters with distinct personalities walk around in multiple universes and remind you about your tasks based on priority.

## Features

### 🎭 5 Unique Characters

Each character has their own personality and reminder style:

- **Alex** (Energetic) - Enthusiastic reminders that pump you up
- **Maya** (Thoughtful) - Gentle, caring reminders
- **Leo** (Focused) - Direct, no-nonsense reminders
- **Zara** (Creative) - Inspiring, creative reminders
- **Sam** (Analytical) - Logical, data-driven reminders

### 🌌 4 Different Universes

Characters roam across themed universes:

- **Work Universe** - Professional tasks and productivity
- **Home Universe** - Personal and household tasks
- **Creative Universe** - Creative projects and hobbies
- **Zen Universe** - Wellness and mindfulness tasks

### 📊 5-Level Priority System

Tasks are organized by priority:

1. **Critical** (Red) - Reminders every 5 minutes
2. **High** (Orange) - Reminders every 15 minutes
3. **Medium** (Yellow) - Reminders every 30 minutes
4. **Low** (Green) - Reminders every 60 minutes
5. **Someday** (Blue) - Reminders every 2 hours

### ✨ Key Features

- **Animated Characters**: Characters move around their universes in real-time
- **Smart Reminders**: Get personalized reminders based on character personality and task priority
- **Task Assignment**: Assign tasks to specific characters
- **Universe Organization**: Organize tasks by different life areas
- **Real-time Updates**: See characters move and receive reminders while you work
- **Task Completion**: Mark tasks as complete when done

## How to Use

### Creating a Task

1. Enter your task description
2. Select a priority level (1-5)
3. Assign it to a character
4. Choose which universe it belongs to
5. Click "Create Task"

### Managing Tasks

- View all active tasks in the Task Control Center
- See task statistics by priority level
- Click "Complete" to mark tasks as done
- Watch as characters remind you based on priority

### Understanding Reminders

- Higher priority tasks get more frequent reminders
- Each character delivers reminders in their unique style
- Reminders appear in the Reminders panel on the right
- The most recent 10 reminders are always visible

## Running the Application

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python task_multiverse_app.py
```

The app will be available at `http://localhost:8051`

### Production Deployment

The app is configured for Cloud Run deployment:

```bash
# The Procfile contains the production configuration
gunicorn task_multiverse_app:server -w 1 --threads 8 --timeout 0
```

## Technical Details

### Built With

- **Dash** - Python web framework
- **Dash Bootstrap Components** - UI components
- **Python 3.11** - Runtime environment

### Architecture

- **Client-side State**: Uses Dash Store components for managing tasks, character positions, and reminders
- **Real-time Updates**: Interval components trigger character movement (every 2 seconds) and reminder checks (every 5 seconds)
- **Responsive Design**: Mobile-friendly interface using Bootstrap
- **Stateless Backend**: All state maintained client-side for scalability

### Data Models

**Task**:
```python
{
    "id": "uuid",
    "description": "Task description",
    "priority": 1-5,
    "character_id": "char1",
    "universe": "work",
    "created_at": "ISO timestamp",
    "status": "active|completed",
    "last_reminder": "ISO timestamp"
}
```

**Character**:
```python
{
    "id": "char1",
    "name": "Alex",
    "personality": "Energetic",
    "color": "#FF6B6B",
    "reminder_style": "enthusiastic",
    "emoji": "🏃"
}
```

**Universe**:
```python
{
    "id": "work",
    "name": "Work Universe",
    "color": "#667eea",
    "icon": "💼"
}
```

## Customization

### Adding New Characters

Edit the `CHARACTERS` list in `task_multiverse_app.py`:

```python
CHARACTERS.append({
    "id": "char6",
    "name": "Your Character",
    "personality": "Description",
    "color": "#HEX_COLOR",
    "reminder_style": "style_key",
    "emoji": "🎯"
})
```

Don't forget to add reminder messages in `get_reminder_message()`.

### Adding New Universes

Edit the `UNIVERSES` list:

```python
UNIVERSES.append({
    "id": "new_universe",
    "name": "New Universe",
    "color": "#HEX_COLOR",
    "icon": "🌟"
})
```

### Adjusting Reminder Frequencies

Edit the `PRIORITY_LEVELS` dictionary:

```python
PRIORITY_LEVELS = {
    1: {"name": "Critical", "color": "#FF4444", "reminder_interval": 5},
    # reminder_interval is in minutes
}
```

## Tips for Best Experience

1. **Assign tasks strategically**: Match task types to character personalities for the most enjoyable reminders
2. **Use priorities wisely**: Reserve level 1 (Critical) for truly urgent tasks to avoid notification fatigue
3. **Organize by universe**: Group related tasks in the same universe for better organization
4. **Complete tasks promptly**: Mark completed tasks to keep your workspace clean and reminders relevant
5. **Watch the multiverse**: Enjoy the animations as characters move between universes!

## Future Enhancements

Potential features for future versions:

- Task persistence (database integration)
- Task due dates and deadlines
- Character leveling and achievements
- Custom character creation
- Sound notifications
- Dark mode
- Mobile app version
- Task templates
- Recurring tasks
- Task dependencies
- Analytics and productivity insights

## License

This project is part of the JRA (Personal Goal & Task Management) suite.

## Support

For issues or questions, please create an issue in the repository.

---

Enjoy managing your tasks with your personal multiverse crew!
