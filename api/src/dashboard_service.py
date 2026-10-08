# Dashboard service

from database import db
from models import User

def user_dashBoard_logic(data):
    print(data)
    user = User.query.filter_by(id=data).first()
    return {"username":user.username},200
    
    