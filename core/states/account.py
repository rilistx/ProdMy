from aiogram.fsm.state import StatesGroup, State


class StateAccount(StatesGroup):
    NAME = State()

    change = None
