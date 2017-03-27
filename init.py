import os
from flask_script import Shell, Manager
from app import create_app, db
from app.models import Operator, OpRole

manager = Manager(create_app('development'))

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def init_db():
    admin_role = OpRole('Admin')
    user_role = OpRole('User')
    admin_user = Operator('admin', 'admin', 'Administrator')

    db.session.add_all([admin_role, user_role, admin_user])
    db.session.commit()
    admin_user.role_id = admin_role.id
    db.session.add(admin_user)
    db.session.commit()

if __name__ == '__main__':
    manager.run()
