from aiogram.fsm.state import StatesGroup, State


class StateVacancy(StatesGroup):
    CATALOG = State()
    SUBCATALOG = State()
    NAME = State()
    DESCRIPTION = State()
    EXPERIENCE = State()
    LANGUAGE = State()
    DISABILITY = State()
    PRICE = State()
    REGION = State()
    CITY = State()
