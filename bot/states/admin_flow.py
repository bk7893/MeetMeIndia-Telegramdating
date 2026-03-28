# file: bot/states/admin_flow.py
"""Admin panel FSM states"""

from aiogram.fsm.state import State, StatesGroup


class AdminFlowStates(StatesGroup):
    """Admin actions"""
    broadcasting = State()
    user_action = State()
    payment_action = State()
