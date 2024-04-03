from aiogram.fsm.state import StatesGroup, State


class StateRegistration(StatesGroup):
    PHONE = State()


class StateVacancy(StatesGroup):
    CATALOG = State()
    SUBCATALOG = State()
    NAME = State()
    DESCRIPTION = State()
    SCHEDULE = State()
    EMPLOYMENT = State()
    EXPERTISE = State()
    DISABILITY = State()
    LANGUAGE = State()
    PRICE = State()
    REGION = State()
    CITY = State()
