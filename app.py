from flask import Flask, render_template, request, redirect, flash, url_for
from flask_login._compat import unicode
from flask_wtf import Form
from flask_login import LoginManager, UserMixin, login_required, login_user,logout_user
from wtforms import StringField, PasswordField, SubmitField
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@49.235.167.8/Conference'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = "12345678"
app.jinja_env.auto_reload = True
login_manger = LoginManager(app)
login_manger.login_view = 'login'
db = SQLAlchemy(app)


class LoginForm(Form):
    name = StringField('name')
    password = PasswordField('password')
    submit = SubmitField('登录')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    inf = db.Column(db.String(1024))

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


class Conf(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), primary_key=True, nullable=False)
    detail = db.Column(db.String(1024), nullable=True)
    compere_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    compere = db.relationship('User', backref='conf')

    def __repr__(self):
        return '<Conf:(%s,%s)>' % (self.name, self.detail)


user1 = User(name='曾庶强', inf='dadadasfsfgfsf', password="123456")
user2 = User(name='叶琴', inf='啊书法大赛分隔符', password="123456")
confq = Conf(name="fsfefwf", detail='fewqgfgregrgtggwrgewrgewg', compere_id=21)
confv = Conf(name='dsaddsafefregertg', detail='gegtrghrthrthrh', compere_id=8987)


def Cover2Json(conf: Conf = '', user: User = ''):
    if conf is not None:
        return {
            'id': conf.id,
            'name': conf.name,
            'detail': conf.detail,
            'compere_id': conf.compere_id
        }
    else:
        return {
            'id': user.id,
            'name': user.name,
            'inf': user.inf
        }

@login_manger.user_loader
def load_user(id):
    return User.query.filter(User.id==id).first()

@app.route('/')
def hello_world():
    return render_template('sy5-3.html')


@app.route('/index')
def index():
    conf_list = [confq, confv]
    return render_template('index.html', conf_list=conf_list)


@app.route('/ss')
def getAll():
    return json.dumps(user1.Cover2Json())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.name == form.name.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('home'))
            flash('密码错误！')
            return redirect(url_for('login'))
        flash('用户名不错在！')
        return redirect(url_for('login'))
    else:
        return render_template('login.html', form=form)


@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
