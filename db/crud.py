from db import SessionLocal
from db.models import User

def add_user_if_not_exists(telegram_id: int):
    session = SessionLocal()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        new_user = User(telegram_id=telegram_id)
        session.add(new_user)
        session.commit()
    session.close()
