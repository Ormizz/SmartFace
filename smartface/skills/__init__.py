"""
SmartFace Skills Package
Contains all skill modules for the assistant
"""

from .web_search import WebSearchSkill
from .reminder import ReminderSkill
from .smart_home import SmartHomeSkill

__all__ = ['WebSearchSkill', 'ReminderSkill', 'SmartHomeSkill']