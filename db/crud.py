# db/crud.py
from sqlalchemy.orm import Session
# ایمپورت‌های صحیح از db.db و db.models
from db.db import SessionLocal # تغییر اینجا
from db.models import User, Task # تغییر اینجا
from config import ADMIN, STAFFS

# --- توابع مربوط به User (ادمین و نیرو) ---

def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int, name: str, role: str = "user", admin_id: int = None):
    db_user = User(telegram_id=telegram_id, name=name, role=role, admin_id=admin_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(db: Session, user: User, role: str):
    user.role = role
    db.commit()
    db.refresh(user)
    return user

def get_admin_user(db: Session):
    return db.query(User).filter(User.telegram_id == ADMIN["id"], User.role == "admin").first()

def get_staff_members_of_admin(db: Session, admin_id: int):
    return db.query(User).filter(User.admin_id == admin_id, User.role == "staff").all()


# --- توابع مربوط به Task ---

def create_task(db: Session, title: str, time_estimate: str, priority: str, expected_results: str, assigned_staff_id: int):
    db_task = Task(
        title=title,
        time_estimate=time_estimate,
        priority=priority,
        expected_results=expected_results,
        assigned_staff_id=assigned_staff_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_staff_id(db: Session, staff_id: int):
    return db.query(Task).filter(Task.assigned_staff_id == staff_id).all()

# --- توابع اولیه سازی دیتابیس ---

def init_users_and_staffs(db: Session):
    admin_db = get_user_by_telegram_id(db, ADMIN["id"])
    if not admin_db:
        admin_db = create_user(db, ADMIN["id"], ADMIN["name"], "admin")
        print(f"Admin '{ADMIN['name']}' created in DB.")
    elif admin_db.role != "admin":
        admin_db = update_user_role(db, admin_db, "admin")
        print(f"Admin '{ADMIN['name']}' role updated to admin.")
    else:
        print(f"Admin '{ADMIN['name']}' already exists in DB.")

    for staff_config in STAFFS:
        staff_db = get_user_by_telegram_id(db, staff_config["id"])
        if not staff_db:
            create_user(db, staff_config["id"], staff_config["name"], "staff", admin_db.id)
            print(f"Staff '{staff_config['name']}' created and assigned to admin.")
        elif staff_db.role != "staff" or staff_db.admin_id != admin_db.id:
            staff_db.role = "staff"
            staff_db.admin_id = admin_db.id
            db.commit()
            db.refresh(staff_db)
            print(f"Staff '{staff_config['name']}' role/admin_id updated.")
        else:
            print(f"Staff '{staff_config['name']}' already exists and assigned to admin.")