from sqlalchemy.orm import Session
from src.entity.models import User, RoleEnum
from security import hash_password  

def create_user(db: Session, username: str, email: str, password: str):
    # Перевірка кількості користувачів
    user_count = db.query(User).count()
    role = RoleEnum.ADMIN if user_count == 0 else RoleEnum.USER

    user = User(
        username=username,
        email=email,
        password=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
