# db/crud.py
from sqlalchemy.orm import Session
from db.models import User, Task # مطمئن شوید Task هم ایمپورت شده
from datetime import datetime

# تابع کمکی برای دریافت کاربر بر اساس telegram_id
def get_user_by_telegram_id(db: Session, telegram_id: int):
    return db.query(User).filter(User.telegram_id == telegram_id).first()

# تابع کمکی برای دریافت کاربر بر اساس id داخلی دیتابیس
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# تابع برای دریافت یک کار بر اساس ID آن
def get_task_by_id(db: Session, task_id: int):
    """Retrieves a single task by its ID."""
    return db.query(Task).filter(Task.id == task_id).first()

# تابع برای ایجاد کاربر جدید
def create_user(db: Session, telegram_id: int, name: str, role: str = "user", admin_id: int = None):
    new_user = User(telegram_id=telegram_id, name=name, role=role, admin_id=admin_id)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# تابع برای ایجاد و یا به روزرسانی ادمین و نیروها در دیتابیس
def init_users_and_staffs(db: Session):
    from config import ADMIN, STAFFS # ایمپورت در داخل تابع برای جلوگیری از circular import

    # بررسی و ایجاد/به‌روزرسانی ادمین
    admin_db = get_user_by_telegram_id(db, ADMIN["id"])
    if not admin_db:
        admin_db = create_user(db, ADMIN["id"], ADMIN["name"], role="admin")
        print(f"Admin '{ADMIN['name']}' added to DB.")
    elif admin_db.role != "admin" or admin_db.name != ADMIN["name"]:
        admin_db.role = "admin"
        admin_db.name = ADMIN["name"]
        db.commit()
        db.refresh(admin_db)
        print(f"Admin '{ADMIN['name']}' updated in DB.")
    else:
        print(f"Admin '{ADMIN['name']}' already exists in DB.")

    # بررسی و ایجاد/به‌روزرسانی نیروها
    for staff_data in STAFFS:
        staff_db = get_user_by_telegram_id(db, staff_data["id"])
        if not staff_db:
            create_user(db, staff_data["id"], staff_data["name"], role="staff", admin_id=admin_db.id)
            print(f"Staff '{staff_data['name']}' added to DB.")
        elif staff_db.role != "staff" or staff_db.name != staff_data["name"] or staff_db.admin_id != admin_db.id:
            staff_db.role = "staff"
            staff_db.name = staff_data["name"]
            staff_db.admin_id = admin_db.id
            db.commit()
            db.refresh(staff_db)
            print(f"Staff '{staff_data['name']}' updated in DB.")
        else:
            print(f"Staff '{staff_data['name']}' already exists in DB.")

# تابع برای دریافت لیست نیروهای مرتبط با یک ادمین
def get_staff_members_of_admin(db: Session, admin_id: int):
    return db.query(User).filter(User.admin_id == admin_id, User.role == "staff").all()

# تابع برای ایجاد کار جدید
def create_task(db: Session, title: str, assigned_staff_id: int, time_estimate: str = None, priority: str = None, expected_results: str = None):
    new_task = Task(
        title=title,
        assigned_staff_id=assigned_staff_id,
        time_estimate=time_estimate,
        priority=priority,
        expected_results=expected_results,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# تابع برای دریافت کارهای تعریف شده برای یک نیرو
def get_tasks_by_staff_id(db: Session, staff_id: int):
    return db.query(Task).filter(Task.assigned_staff_id == staff_id).order_by(Task.created_at.desc()).all()