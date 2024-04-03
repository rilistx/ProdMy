from sqlalchemy import ForeignKey, String, Text, Integer, BigInteger,  Numeric, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Language(Base):
    __tablename__ = 'language'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Informer(Base):
    __tablename__ = 'informer'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Catalog(Base):
    __tablename__ = 'catalog'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


class Subcatalog(Base):
    __tablename__ = 'subcatalog'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'), nullable=False)

    catalog: Mapped['Catalog'] = relationship(backref='subcatalog')


class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    have: Mapped[bool] = mapped_column(Boolean, default=True)


class Region(Base):
    __tablename__ = 'region'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    have: Mapped[bool] = mapped_column(Boolean, default=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)

    country: Mapped['Country'] = relationship(backref='region')


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    have: Mapped[bool] = mapped_column(Boolean, default=True)
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'), nullable=False)

    region: Mapped['Region'] = relationship(backref='city')


class Currency(Base):
    __tablename__ = 'currency'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    rate: Mapped[str] = mapped_column(Numeric(10, 2), default=0)


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    language_id: Mapped[int] = mapped_column(ForeignKey('language.id', ondelete='CASCADE'), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)

    language: Mapped['Language'] = relationship(backref='user')
    country: Mapped['Country'] = relationship(backref='user')


class Vacancy(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    disability: Mapped[bool] = mapped_column(Boolean, nullable=False)
    language: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[str] = mapped_column(BigInteger, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=True)
    view: Mapped[int] = mapped_column(Integer, default=0)
    complaint: Mapped[int] = mapped_column(Integer, default=0)
    subcatalog_id: Mapped[int] = mapped_column(ForeignKey('subcatalog.id', ondelete='CASCADE'), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey('currency.id', ondelete='CASCADE'), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'), nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id', ondelete='CASCADE'), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    subcatalog: Mapped['Subcatalog'] = relationship(backref='vacancy')
    currency: Mapped['Currency'] = relationship(backref='vacancy')
    country: Mapped['Country'] = relationship(backref='vacancy')
    region: Mapped['Region'] = relationship(backref='vacancy')
    city: Mapped['City'] = relationship(backref='vacancy')
    user: Mapped['User'] = relationship(backref='vacancy')


class Schedule(Base):
    __tablename__ = 'schedule'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    complete: Mapped[bool] = mapped_column(Boolean, default=False)
    incomplete: Mapped[bool] = mapped_column(Boolean, default=False)
    shift: Mapped[bool] = mapped_column(Boolean, default=False)
    rotating: Mapped[bool] = mapped_column(Boolean, default=False)
    flexible: Mapped[bool] = mapped_column(Boolean, default=False)
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    vacancy: Mapped['Vacancy'] = relationship(backref='schedule')


class Employment(Base):
    __tablename__ = 'employment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full: Mapped[bool] = mapped_column(Boolean, default=False)
    seasonal: Mapped[bool] = mapped_column(Boolean, default=False)
    partial: Mapped[bool] = mapped_column(Boolean, default=False)
    internship: Mapped[bool] = mapped_column(Boolean, default=False)
    part_time: Mapped[bool] = mapped_column(Boolean, default=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    vacancy: Mapped['Vacancy'] = relationship(backref='employment')


class Expertise(Base):
    __tablename__ = 'expertise'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inexperienced: Mapped[bool] = mapped_column(Boolean, default=False)
    from_one: Mapped[bool] = mapped_column(Boolean, default=False)
    one_to_three: Mapped[bool] = mapped_column(Boolean, default=False)
    three_to_six: Mapped[bool] = mapped_column(Boolean, default=False)
    from_six: Mapped[bool] = mapped_column(Boolean, default=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    vacancy: Mapped['Vacancy'] = relationship(backref='expertise')


class Liked(Base):
    __tablename__ = 'liked'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.uuid', ondelete='CASCADE'), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='liked')
    vacancy: Mapped['Vacancy'] = relationship(backref='liked')
