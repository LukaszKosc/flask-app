from app import fapp
from flask_classful import FlaskView, route
from flask import request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.models import User, Post, db
# from app.databases import Database
# from app.admin import Admin
from werkzeug.routing import BuildError
from flask import render_template
from app.forms import LoginForm, RegistrationForm


@fapp.errorhandler(404)
def page_not_found(aaaa):

    print('aaaa',aaaa)
    print('request',request)
    return 'URL: "" not found - 404'

# @fapp.route('/')  # , endpoint='simple_index')  # => url_for('simple_index')
# @fapp.route('/index')

# @fapp.route('/')
# @fapp.route('/index')
# def index():
# url_for('index_0'))  # => "/index"
# url_for('index_1'))  # => "/"

# @fapp.route('/index')
# @fapp.route('/')
# def index():
# url_for('index_0'))  # => "/"
# url_for('index_1'))  # => "/index"


@fapp.route('/')
@fapp.route('/index')
def index():
    if current_user.is_authenticated:
        print(current_user)
        posts = Post.query.all()
    else:
        posts = {}
    return render_template('index.html', title='Home', posts=posts)


@fapp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        print('Now user will be logged in')
        return redirect(url_for('index'))
    return render_template('login.html', title='Login page', form=form)


@fapp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@fapp.route('/search')
@login_required
def search():
    return render_template('search.html', title='Home', user=None)


@fapp.route('/results', methods=['POST'])
@login_required
def results():
    if request.method == 'POST':
        print('request.url', request.url)
        field = request.form.get('field', '')
        value = request.form.get('value', '')

        results = [{'field': field, 'value': value}]
        return render_template('results.html', title='Search', results=results)


@fapp.route('/items')
def items():
    results = [
        {'field': 123, 'value': 'asdasdasd'},
        {'field': 523, 'value': 'asdasasd324asddasd'},
    ]
    return render_template('items.html', title='Items', results=results)


@fapp.route('/contact')
def contact():
    body = '''
    <div>Hello on Contact page!</div>
    Address: Streetnaem</br>
    Number: 123
    '''
    return render_template('contact.html', title='Contact', body=body)


@fapp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# from app import fapp
#
#
# @fapp.route('/')
# @fapp.route('/index')
# def index():
#     return "Hello, World!"
#
