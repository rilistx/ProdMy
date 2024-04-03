from aiogram.fsm.state import StatesGroup, State


class StateRegistration(StatesGroup):
    LANGUAGE = State()
    PHONE = State()
