from flask import Flask, render_template, redirect, flash, url_for
from flask_login._compat import unicode
from flask_wtf import Form
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from wtforms import StringField, PasswordField, BooleanField
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@49.235.167.8/Conf'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = "12345678"
app.jinja_env.auto_reload = True
login_manger = LoginManager(app)
login_manger.login_view = 'login'
db = SQLAlchemy(app)


class LoginForm(Form):
    name = StringField()
    password = PasswordField()
    remember_me = BooleanField()


class UserAdmin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    icon_path = db.Column(db.String(128), nullable=False, default='assets/images/profile.png')
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


users = db.Table('users',
                 db.Column('conf_id',db.Integer,db.ForeignKey('conf.id')),
                db.Column('user_id',db.Integer,db.ForeignKey('user.id'))
                 )



class Conf(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), primary_key=True, nullable=False)
    icon_path = db.Column(db.String(128), nullable=False)
    detail = db.Column(db.String(1024), nullable=True)
    identify = db.Column(db.String(128), nullable=False)
    compere_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    compere = db.relationship('User', backref='conf')
    users_id = db.relationship('User',secondary=users,backref=db.backref('users',lazy='dynamic'))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    icon_path = db.Column(db.String(128), nullable=False, default='assets/images/profile.png')
    password = db.Column(db.String(128), nullable=False)
    inf = db.Column(db.String(1024))
    units = db.Column(db.String(128))
    id_card = db.Column(db.String(32))
    tel = db.Column(db.String(16))
    join_time = db.Column(db.DateTime)
    sex = db.Column(db.String(4))
    room = db.Column(db.String(4))

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


@login_manger.user_loader
def load_user(user_id):
    return UserAdmin.query.get(int(user_id)) or User.query.get(int(user_id))


def get_name(id):
    user = User.query.filter(User.id == id).first()
    if user:
        return user.name
    return id


app.add_template_filter(get_name, 'get_name')


@app.route('/')
def hello_world():
    if current_user:
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/index')
@login_required
def index():
    conf_list = Conf.query.all()
    return render_template('index.html', conf_list=conf_list, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserAdmin.query.filter(UserAdmin.name == form.name.data).first() or User.query.filter(
            User.name == form.name.data).first()
        print(user)
        if user:
            if form.password.data == user.password:
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('index'))
            else:
                flash('密码错误！')
            return redirect(url_for('login'))
        else:
            flash('用户名不存在')
            return redirect(url_for('login'))

    else:
        return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/regist', methods=['POSE', 'GET'])
def regist():
    return render_template('signin.html')


@app.route('/<conf_id>')
def conf_detail(conf_id):
    conf = Conf.query.filter(Conf.id == conf_id).first()
    return render_template('conf_detail.html', conf=conf,current_user=current_user)


if __name__ == '__main__':
    app.run(debug=True)
