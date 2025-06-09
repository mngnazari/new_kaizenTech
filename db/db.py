# db/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_PATH

# این خط را حذف کنید: import db.models
# زیرا باعث circular import می شود.

engine = create_engine(DB_PATH, echo=False)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # این خط را به اینجا منتقل کنید
    import db.models # <---- انتقال این خط به داخل تابع init_db()

    # این تابع جدول‌ها را بر اساس مدل‌های تعریف شده ایجاد می‌کند
    Base.metadata.create_all(bind=engine)
    print("Database tables created/checked.")