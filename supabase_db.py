"""
Supabase Database Helper Functions
Handles all cloud database operations for Angel's Flow
"""

from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
USE_CLOUD = bool(SUPABASE_URL and SUPABASE_KEY)

if USE_CLOUD:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase error: {e}")
        USE_CLOUD = False

# Task Operations
def get_user_tasks(user_id):
    """Get all tasks for a user from cloud"""
    if not USE_CLOUD:
        return []

    try:
        response = supabase.table('tasks').select('*').eq('user_id', user_id).execute()
        tasks = []
        for row in response.data:
            task = {
                'id': str(row['id']),
                'description': row['description'],
                'priority': row['priority'],
                'category': row['category'],
                'due_date': row['due_date'],
                'created_at': row['created_at'],
                'completed': row['completed'],
                'completed_at': row['completed_at'],
                'recurring': row.get('recurring', False),
                'recurring_freq': row.get('recurring_freq')
            }
            tasks.append(task)
        return tasks
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def save_task(user_id, task):
    """Save a single task to cloud"""
    if not USE_CLOUD:
        return False

    try:
        data = {
            'user_id': user_id,
            'description': task['description'],
            'priority': task['priority'],
            'category': task['category'],
            'due_date': task.get('due_date'),
            'created_at': task.get('created_at', datetime.now().isoformat()),
            'completed': task.get('completed', False),
            'completed_at': task.get('completed_at'),
            'recurring': task.get('recurring', False),
            'recurring_freq': task.get('recurring_freq')
        }

        # Check if task exists (by checking if we have an id that's a UUID)
        if 'id' in task and len(str(task['id'])) > 30:  # UUID format
            # Update existing
            supabase.table('tasks').update(data).eq('id', task['id']).execute()
        else:
            # Insert new
            supabase.table('tasks').insert(data).execute()

        return True
    except Exception as e:
        print(f"Error saving task: {e}")
        return False

def delete_task_from_cloud(user_id, task_id):
    """Delete a task from cloud"""
    if not USE_CLOUD:
        return False

    try:
        supabase.table('tasks').delete().eq('id', task_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

# Trash Operations
def get_user_trash(user_id):
    """Get all trash items for a user"""
    if not USE_CLOUD:
        return []

    try:
        response = supabase.table('trash').select('*').eq('user_id', user_id).execute()
        return response.data or []
    except Exception as e:
        print(f"Error fetching trash: {e}")
        return []

def save_to_trash(user_id, task):
    """Save a task to trash"""
    if not USE_CLOUD:
        return False

    try:
        data = {
            'user_id': user_id,
            'task_id': task.get('id'),
            'description': task['description'],
            'priority': task['priority'],
            'category': task['category'],
            'due_date': task.get('due_date'),
            'created_at': task.get('created_at'),
            'completed': task.get('completed', False),
            'recurring': task.get('recurring', False),
            'recurring_freq': task.get('recurring_freq'),
            'deleted_at': datetime.now().isoformat()
        }
        supabase.table('trash').insert(data).execute()
        return True
    except Exception as e:
        print(f"Error saving to trash: {e}")
        return False

def delete_from_trash(user_id, trash_id):
    """Permanently delete from trash"""
    if not USE_CLOUD:
        return False

    try:
        supabase.table('trash').delete().eq('id', trash_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting from trash: {e}")
        return False

# User Stats
def get_user_stats(user_id):
    """Get user statistics"""
    if not USE_CLOUD:
        return {'streak': 0, 'theme': 'light'}

    try:
        response = supabase.table('user_stats').select('*').eq('user_id', user_id).execute()
        if response.data:
            return {
                'streak': response.data[0].get('streak', 0),
                'theme': response.data[0].get('theme', 'light')
            }
        else:
            # Create default stats
            default_stats = {'user_id': user_id, 'streak': 0, 'theme': 'light'}
            supabase.table('user_stats').insert(default_stats).execute()
            return {'streak': 0, 'theme': 'light'}
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {'streak': 0, 'theme': 'light'}

def update_user_stats(user_id, streak=None, theme=None):
    """Update user statistics"""
    if not USE_CLOUD:
        return False

    try:
        data = {'updated_at': datetime.now().isoformat()}
        if streak is not None:
            data['streak'] = streak
        if theme is not None:
            data['theme'] = theme

        # Upsert (update or insert)
        supabase.table('user_stats').upsert({
            'user_id': user_id,
            **data
        }).execute()
        return True
    except Exception as e:
        print(f"Error updating stats: {e}")
        return False

# Sync Helper - merge localStorage with cloud on first login
def sync_local_to_cloud(user_id, local_tasks):
    """Upload local tasks to cloud on first sync"""
    if not USE_CLOUD or not local_tasks:
        return

    try:
        for task in local_tasks:
            save_task(user_id, task)
        print(f"✅ Synced {len(local_tasks)} local tasks to cloud")
    except Exception as e:
        print(f"Error syncing local to cloud: {e}")
