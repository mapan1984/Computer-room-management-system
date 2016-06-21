#!/usr/bin/env python3
# encoding: utf-8
import os
from app import create_app, db
from app.models import User, Computer
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('default')

db.drop_all()
db.create_all()

admin_mapan = User(email='mapansky1984@163.com', username='mapan', is_admin=True)
admin_mapan.password = 'mapan'
user_other = User(email='2642896890@qq.com', username='other', is_admin=False)
user_other.password = 'other'

c1 = Computer(name='c1', user=admin_mapan)
c2 = Computer(name='c2', user=user_other)
c3 = Computer(name='c3', user=admin_mapan)
c4 = Computer(name='c4', user=admin_mapan)
c5 = Computer(name='c5', user=user_other)
c6 = Computer(name='c6', user=user_other)

# 通过db.session管理数据库的改动
db.session.add_all([c1, c2, admin_mapan, user_other])
db.session.commit()

print(c1.id)

'''
===================================
Python对象 ----> data.sqlite
--------------------------------------
修改行
>>> admin_role.name = 'Administrator'
>>> db.session.add(admin_role)
>>> ad.session.commit()

删除行
>>> db.session.delete(admin_role)
>>> db.session.commit()

查询行
>>> Computer.query.all()
[<Computer u'Admin'>, <Computer u'User'>]

>>> User.query.filter_by(role=user_role).all()
[<User u'other'>]

查看原生SQL查询语句
>>> str(User.query.filter_by(role=user_role))
'SELECT users.id AS users_id, users.username AS users_username,
users.role_id AS users_role_id FROM users WHERE :param_1 = users.role_id'


============================================================
data.sqlite ---------> Python对象
------------------------------------------------
加载名为User的用户角色(在shell中通过数据库查询)
>>> user_role = Computer.query.filter_by(name='User').first()
>>> user_role.all()
[<Computer 'User'>]


========================================================
Computer对象的users属性返回这个对象的
users = db.relationship('User', backref='role') # users属性返回与这个角色相关联的用户组成的列表
--------------------------------------------------------------------------------------
>>> users = user_role.users
>>> users
[<User u'other'>]
>>> users[0].role
<Computer u'User'>

添加lazy='dynamic'后，禁止自动查询
>>> user_role.users.order_by(User.username).all()
[<User u'david'>, <User u'susan'>]
>>> user_role.users.count()
2
'''
