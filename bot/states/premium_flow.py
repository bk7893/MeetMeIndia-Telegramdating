# file: bot/states/premium_flow.py
"""Premium subscription FSM states"""

from aiogram.fsm.state import State, StatesGroup


class PremiumFlowStates(StatesGroup):
    """Premium tier selection"""
    selecting_tier = State()
    confirming_purchase = State()
