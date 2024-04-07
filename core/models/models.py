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


class Informer(Base):
    __tablename__ = 'informer'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True)


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


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    warning: Mapped[bool] = mapped_column(Integer, default=0)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    language_id: Mapped[int] = mapped_column(ForeignKey('language.id', ondelete='CASCADE'), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id', ondelete='CASCADE'), nullable=True)

    language: Mapped['Language'] = relationship(backref='user')
    country: Mapped['Country'] = relationship(backref='user')


class Vacancy(Base):
    __tablename__ = 'vacancy'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    remote: Mapped[bool] = mapped_column(Boolean, nullable=False)
    disability: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[str] = mapped_column(BigInteger, nullable=False)
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


class Liked(Base):
    __tablename__ = 'liked'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.uuid', ondelete='CASCADE'), nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey('vacancy.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='liked')
    vacancy: Mapped['Vacancy'] = relationship(backref='liked')