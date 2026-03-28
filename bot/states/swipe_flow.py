# file: bot/states/swipe_flow.py
"""Swiping flow FSM states"""

from aiogram.fsm.state import State, StatesGroup


class SwipeFlowStates(StatesGroup):
    """Swiping flow (mostly stateless)"""
    viewing_profile = State()
