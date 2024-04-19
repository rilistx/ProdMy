from sqlalchemy import ForeignKey, String, Text, Integer, BigInteger,  Numeric, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Language(Base):
    __tablename__ = 'language'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    abbreviation: Mapped[str] = mapped_column(String(10), unique=True)
    title: Mapped[str] = mapped_column(Text, unique=True)
    flag: Mapped[str] = mapped_column(String(10), unique=True)


class Currency(Base):
    __tablename__ = 'currency'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    abbreviation: Mapped[str] = mapped_column(String(50), nullable=False)
    rate: Mapped[str] = mapped_column(Numeric(10, 2), default=0)


class Catalog(Base):
    __tablename__ = 'catalog'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    logo: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)


class Subcatalog(Base):
    __tablename__ = 'subcatalog'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'), nullable=False)

    catalog: Mapped['Catalog'] = relationship(backref='subcatalog')


class Country(Base):
    __tablename__ = 'country'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    flag: Mapped[str] = mapped_column(String(10), nullable=False)


class Region(Base):
    __tablename__ = 'region'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)

    country: Mapped['Country'] = relationship(backref='region')


class City(Base):
    __tablename__ = 'city'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'), nullable=False)

    region: Mapped['Region'] = relationship(backref='city')


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), unique=True)
    money: Mapped[int] = mapped_column(BigInteger, default=0)
    count_vacancy: Mapped[int] = mapped_column(BigInteger, default=0)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    language_id: Mapped[int] = mapped_column(ForeignKey('language.id', ondelete='CASCADE'), nullable=False)

    language: Mapped['Language'] = relationship(backref='user')


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    money: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='transaction')


class Vacancy(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    experience: Mapped[bool] = mapped_column(Boolean, nullable=False)
    language: Mapped[bool] = mapped_column(Boolean, nullable=False)
    disability: Mapped[bool] = mapped_column(Boolean, nullable=False)
    salary: Mapped[str] = mapped_column(BigInteger, nullable=False)
    view: Mapped[int] = mapped_column(Integer, default=0)
    count_complaint: Mapped[int] = mapped_column(Integer, default=0)
    promotion: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'), nullable=False)
    subcatalog_id: Mapped[int] = mapped_column(ForeignKey('subcatalog.id', ondelete='CASCADE'), nullable=False)
    currency_id: Mapped[int] = mapped_column(ForeignKey('currency.id', ondelete='CASCADE'), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'), nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id', ondelete='CASCADE'), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    catalog: Mapped['Catalog'] = relationship(backref='vacancy')
    subcatalog: Mapped['Subcatalog'] = relationship(backref='vacancy')
    currency: Mapped['Currency'] = relationship(backref='vacancy')
    country: Mapped['Country'] = relationship(backref='vacancy')
    region: Mapped['Region'] = relationship(backref='vacancy')
    city: Mapped['City'] = relationship(backref='vacancy')
    user: Mapped['User'] = relationship(backref='vacancy')


class Promote(Base):
    __tablename__ = 'promote'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    vacancy: Mapped['Vacancy'] = relationship(backref='promote')


class Complaint(Base):
    __tablename__ = 'complaint'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='complaint')
    vacancy: Mapped['Vacancy'] = relationship(backref='complaint')


class Separator(Base):
    __tablename__ = 'separator'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    experience: Mapped[bool] = mapped_column(Boolean, nullable=True)
    language: Mapped[bool] = mapped_column(Boolean, nullable=True)
    disability: Mapped[bool] = mapped_column(Boolean, nullable=True)
    salary_from: Mapped[str] = mapped_column(BigInteger, nullable=True)
    salary_to: Mapped[str] = mapped_column(BigInteger, nullable=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey('catalog.id', ondelete='CASCADE'), nullable=True)
    subcatalog_id: Mapped[int] = mapped_column(ForeignKey('subcatalog.id', ondelete='CASCADE'), nullable=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey('currency.id', ondelete='CASCADE'), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey('region.id', ondelete='CASCADE'), nullable=True)
    city_id: Mapped[int] = mapped_column(ForeignKey('city.id', ondelete='CASCADE'), nullable=True)

    catalog: Mapped['Catalog'] = relationship(backref='separator')
    subcatalog: Mapped['Subcatalog'] = relationship(backref='separator')
    currency: Mapped['Currency'] = relationship(backref='separator')
    country: Mapped['Country'] = relationship(backref='separator')
    region: Mapped['Region'] = relationship(backref='separator')
    city: Mapped['City'] = relationship(backref='separator')


class Liked(Base):
    __tablename__ = 'liked'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='liked')
    vacancy: Mapped['Vacancy'] = relationship(backref='liked')
