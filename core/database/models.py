from sqlalchemy import func, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class Language(Base):
    __tablename__ = 'language'

    id: Mapped[int] = mapped_column(primary_key=True)
    abbreviation: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(unique=True)
    flag: Mapped[str] = mapped_column(unique=True)


class Currency(Base):
    __tablename__ = 'currency'

    id: Mapped[int] = mapped_column(primary_key=True)
    abbreviation: Mapped[str]
    rate: Mapped[float] = mapped_column(Numeric(10, 2), default=0)


class Catalog(Base):
    __tablename__ = 'catalog'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    logo: Mapped[str] = mapped_column(unique=True)


class Subcatalog(Base):
    __tablename__ = 'subcatalog'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'))

    catalog: Mapped['Catalog'] = relationship(backref='subcatalog')


class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    flag: Mapped[str] = mapped_column(unique=True)


class Region(Base):
    __tablename__ = 'region'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'))

    country: Mapped['Country'] = relationship(backref='region')


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'))

    region: Mapped['Region'] = relationship(backref='city')


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str | None]
    phone_number: Mapped[str] = mapped_column(unique=True)
    money: Mapped[int] = mapped_column(default=0)
    blocked: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    language_id: Mapped[int] = mapped_column(ForeignKey('language.id', ondelete='CASCADE'))
    currency_id: Mapped[int] = mapped_column(ForeignKey('currency.id', ondelete='CASCADE'))
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'))

    language: Mapped['Language'] = relationship(backref='user')
    currency: Mapped['Currency'] = relationship(backref='user')
    country: Mapped['Country'] = relationship(backref='user')


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[str]
    order_id: Mapped[str]
    purpose: Mapped[str]
    status: Mapped[bool | None]
    method: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship(backref='transaction')


class Vacancy(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[str]
    requirement: Mapped[str]
    employment: Mapped[bool]
    experience: Mapped[bool]
    schedule: Mapped[bool]
    remote: Mapped[bool]
    language: Mapped[bool]
    foreigner: Mapped[bool]
    disability: Mapped[bool]
    salary: Mapped[int]
    promotion: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
    channel_id: Mapped[int | None]
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'))
    subcatalog_id: Mapped[int] = mapped_column(ForeignKey('subcatalog.id', ondelete='CASCADE'))
    currency_id: Mapped[int] = mapped_column(ForeignKey('currency.id', ondelete='CASCADE'))
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'))
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'))
    city_id: Mapped[int | None] = mapped_column(ForeignKey('city.id', ondelete='CASCADE'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))

    catalog: Mapped[Catalog] = relationship(backref='vacancy')
    subcatalog: Mapped['Subcatalog'] = relationship(backref='vacancy')
    currency: Mapped['Currency'] = relationship(backref='vacancy')
    country: Mapped['Country'] = relationship(backref='vacancy')
    region: Mapped['Region'] = relationship(backref='vacancy')
    city: Mapped['City'] = relationship(backref='vacancy')
    user: Mapped['User'] = relationship(backref='vacancy')


class Preview(Base):
    __tablename__ = 'preview'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship(backref='preview')
    vacancy: Mapped['Vacancy'] = relationship(backref='preview')


class Complaint(Base):
    __tablename__ = 'complaint'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship(backref='complaint')
    vacancy: Mapped['Vacancy'] = relationship(backref='complaint')


class Liked(Base):
    __tablename__ = 'liked'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'))

    user: Mapped['User'] = relationship(backref='liked')
    vacancy: Mapped['Vacancy'] = relationship(backref='liked')
