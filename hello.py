import os
from threading import Thread

from flask import Flask, render_template, session, redirect, url_for
from flask.ext.script import Manager, Shell
# {{{ wtf
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField #字段对象
from wtforms.validators import Required      #验证函数
# end_wtf}}}
# {{{ sql alchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
# end sql}}}
from flask.ext.mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = '465'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SENDER'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_SUBJECT_PREFIX'] = '[COM_MAG]'
app.config['BEN_ADMIN'] =  os.environ.get('ben_admin')

app.config['MAIL_SUBJECT_PREFIX'] = '[COM ADMIN]'
app.config['MAIL_SENDER'] = 'COM Admin <mapansky1984@163.com>'

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

class NameForm(Form):
    name = StringField('用户名', validators=[Required()])         # type="text"的<input>
    password = PasswordField('输入密码', validators=[Required()]) # type="password的<input>"
    submit = SubmitField('登陆')                                  # type="submit"的<input>

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # users属性返回与这个角色相关联的用户组成的列表
    # 第一个参数User表示关联的模型
    # role向User模型中添加一个role属性
    # 这一属性可代替role_id访问Role模型，获取模型对象
    users = db.relationship('User', backref='role', lazy='dynamic') 

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) # 外键,值为表roles的id,类型为Integer

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None: # 用户第一次登陆
            user_role = Role.query.filter_by(name='User').first()
            user = User(username=form.name.data, password=form.password.data, role=user_role)
            db.session.add(user)
            session['known'] = False
            if app.config['BEN_ADMIN']:
                send_email(app.config['BEN_ADMIN'], 'New User',
                           'mail/new_user', user=user)
        else: #用户不是第一次登陆
            session['known'] = True
        session['name'] = form.name.data
        form.name.date = ''
        session['password'] = form.password.data
        return redirect(url_for('manage'))
    return render_template('index.html', form=form)


@app.route('/manage', methods=['get', 'post'])
def manage():
    return render_template('manage.html', name=session.get('name'), 
                           known=session.get('known'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    manager.run()
