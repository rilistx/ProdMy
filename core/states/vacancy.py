from aiogram.fsm.state import StatesGroup, State


class StateVacancy(StatesGroup):
    CATALOG = State()
    SUBCATALOG = State()
    NAME = State()
    DESCRIPTION = State()
    REQUIREMENT = State()
    EMPLOYMENT = State()
    EXPERIENCE = State()
    SCHEDULE = State()
    REMOTE = State()
    LANGUAGE = State()
    FOREIGNER = State()
    DISABILITY = State()
    SALARY = State()
    REGION = State()
    CITY = State()

    change = None
