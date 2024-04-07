from aiogram.fsm.state import StatesGroup, State


class StateVacancy(StatesGroup):
    CATALOG = State()
    SUBCATALOG = State()
    NAME = State()
    DESCRIPTION = State()
    REMOTE = State()
    DISABILITY = State()
    LANGUAGE = State()
    PRICE = State()
    REGION = State()
    CITY = State()
