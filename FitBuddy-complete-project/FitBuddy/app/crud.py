from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User
def get_user(db:Session,user_id:str): 
    return db.scalar(
        select(User).where(User.user_id==user_id))
def get_all_users(db:Session): 
    return db.scalars(
        select(User).order_by(User.created_at.desc())).all()
def create_user(db:Session,**data):
    u=User(**data);
    db.add(u); 
    db.commit(); 
    db.refresh(u); 
    return u
def update_user_plan(db:Session,user:User,updated_plan:str,feedback:str):
    user.updated_plan=updated_plan; user.last_feedback=feedback
    db.add(user); db.commit(); db.refresh(user); return user
