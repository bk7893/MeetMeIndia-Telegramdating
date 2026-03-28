# file: bot/states/edit_profile.py
"""Profile editing FSM states"""

from aiogram.fsm.state import State, StatesGroup


class EditProfileStates(StatesGroup):
    """Edit profile fields"""
    choosing_field = State()
    editing_name = State()
    editing_age = State()
    editing_bio = State()
    editing_city = State()
    editing_interests = State()
    editing_photo = State()
