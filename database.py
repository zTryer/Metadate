from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

DATABASE_URL = "sqlite:///bot.db"  # Локальная база данных SQLite
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, nullable=False)
    usage_count = Column(Integer, default=0)  # Количество использований
    is_paid = Column(Boolean, default=False)  # Пользователь оплатил подписку?
    access_granted = Column(Boolean, default=False)  # Доступ к боту активен?
    subscription_end_date = Column(DateTime, nullable=True)  # Дата окончания подписки
    auto_renew = Column(Boolean, default=True)  # Подписка продлевается автоматически?

# Инициализация базы
def init_db():
    Base.metadata.create_all(bind=engine)

# Создание/получение пользователя
def get_or_create_user(db, telegram_id):
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if not user:
        user = User(telegram_id=str(telegram_id))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Увеличение счётчика использования
def increment_usage(db, telegram_id):
    user = get_or_create_user(db, telegram_id)
    user.usage_count += 1
    db.commit()
    return user

# Установка подписки
def set_subscription(db, telegram_id, days=29):
    user = get_or_create_user(db, telegram_id)
    user.is_paid = True
    user.access_granted = True
    user.subscription_end_date = datetime.now() + timedelta(days=days)
    db.commit()
    return user

# Проверка активной подписки
def is_subscription_active(db, telegram_id):
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if user and user.access_granted and user.subscription_end_date:
        return user.subscription_end_date >= datetime.now()
    return False

# Отключение авто-продления
def disable_auto_renew(db, telegram_id):
    user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if user:
        user.auto_renew = False
        db.commit()
    return user
