# file: bot/states/onboarding.py
"""Onboarding FSM states (9-step profile creation)"""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """9-step profile creation"""
    language = State()        # Step 1
    name = State()            # Step 2
    age = State()             # Step 3
    gender = State()          # Step 4
    city = State()            # Step 5
    interests = State()       # Step 6
    purpose = State()         # Step 7
    bio = State()             # Step 8
    photo = State()           # Step 9
