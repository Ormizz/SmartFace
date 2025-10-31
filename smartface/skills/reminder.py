import json
import os
from datetime import datetime, timedelta
from smartface.config import REMINDERS_FILE


class ReminderSkill:
    """
    Reminder management skill
    Stores reminders in JSON file
    """
    
    def __init__(self):
        print("🔧 Initializing Reminder skill...")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
        
        # Load existing reminders
        self.reminders = self._load_reminders()
        
        print(f"✅ Reminder skill ready ({len(self.reminders)} reminders loaded)")
    
    def _load_reminders(self):
        """Load reminders from file"""
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading reminders: {e}")
                return []
        return []
    
    def _save_reminders(self):
        """Save reminders to file"""
        try:
            with open(REMINDERS_FILE, 'w') as f:
                json.dump(self.reminders, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving reminders: {e}")
            return False
    
    def add_reminder(self, text, time_str=None):
        """
        Add a new reminder
        
        Args:
            text: Reminder text
            time_str: Optional time string (not implemented yet)
            
        Returns:
            str: Confirmation message
        """
        if not text or not text.strip():
            return "I need to know what to remind you about."
        
        reminder = {
            'id': len(self.reminders) + 1,
            'text': text.strip(),
            'created': datetime.now().isoformat(),
            'completed': False
        }
        
        self.reminders.append(reminder)
        
        if self._save_reminders():
            return f"Got it! I've added a reminder: {text}"
        else:
            return "I had trouble saving that reminder. Please try again."
    
    def list_reminders(self):
        """
        List all active reminders
        
        Returns:
            str: List of reminders
        """
        active_reminders = [r for r in self.reminders if not r.get('completed', False)]
        
        if not active_reminders:
            return "You don't have any reminders right now."
        
        if len(active_reminders) == 1:
            return f"You have 1 reminder: {active_reminders[0]['text']}"
        
        response = f"You have {len(active_reminders)} reminders:\n"
        for i, reminder in enumerate(active_reminders, 1):
            response += f"{i}. {reminder['text']}\n"
        
        return response.strip()
    
    def complete_reminder(self, reminder_id):
        """
        Mark a reminder as completed
        
        Args:
            reminder_id: ID of reminder to complete
            
        Returns:
            str: Confirmation message
        """
        for reminder in self.reminders:
            if reminder['id'] == reminder_id:
                reminder['completed'] = True
                if self._save_reminders():
                    return f"Marked reminder as complete: {reminder['text']}"
                else:
                    return "I had trouble updating that reminder."
        
        return f"I couldn't find reminder #{reminder_id}"
    
    def delete_reminder(self, reminder_id):
        """
        Delete a reminder
        
        Args:
            reminder_id: ID of reminder to delete
            
        Returns:
            str: Confirmation message
        """
        for i, reminder in enumerate(self.reminders):
            if reminder['id'] == reminder_id:
                deleted_text = reminder['text']
                self.reminders.pop(i)
                if self._save_reminders():
                    return f"Deleted reminder: {deleted_text}"
                else:
                    return "I had trouble deleting that reminder."
        
        return f"I couldn't find reminder #{reminder_id}"
    
    def clear_completed(self):
        """
        Clear all completed reminders
        
        Returns:
            str: Confirmation message
        """
        before_count = len(self.reminders)
        self.reminders = [r for r in self.reminders if not r.get('completed', False)]
        after_count = len(self.reminders)
        
        deleted_count = before_count - after_count
        
        if deleted_count == 0:
            return "No completed reminders to clear."
        
        if self._save_reminders():
            return f"Cleared {deleted_count} completed reminder{'s' if deleted_count > 1 else ''}."
        else:
            return "I had trouble clearing reminders."
    
    def count_reminders(self):
        """
        Get count of active reminders
        
        Returns:
            int: Number of active reminders
        """
        return len([r for r in self.reminders if not r.get('completed', False)])