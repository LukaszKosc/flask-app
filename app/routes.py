import os
import imghdr
from app import fapp
from datetime import datetime
from flask import request, flash, redirect, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.models import User, Post, db
from flask import render_template
from app.forms import LoginForm, RegistrationForm, \
    EditProfileForm, EmptyForm, PostForm, SearchPostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email


MAX_LENGTH = 100


@fapp.route('/')
@fapp.route('/index')
def index():
    if current_user.is_authenticated:
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
        return redirect(url_for('index'))
    return render_template('login.html', title='Login page', form=form)


@fapp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@fapp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    m = db.inspect(Post)
    # all orm attributes
    fields = [{'field': column} for column in list(m.all_orm_descriptors.keys()) if column != 'user_id']
    # columns
    # list(m.columns.keys())
    form = SearchPostForm()
    if form.validate_on_submit():
        field = form.field.data
        value = form.value.data
        posts = Post.query.filter_by(**{field: value}).all()
        return render_template('items.html', title='Search results', posts=posts, search_results=True)
    posts = None
    return render_template('search.html', title='Search', user=current_user, fields=fields,
                           form=form, posts=posts, search_results=False)


@fapp.route('/items')
def items():
    posts = Post.query.filter_by(user_id=current_user.id)
    return render_template('items.html', title='Items', posts=posts)


@fapp.route('/members')
@login_required
def members():
    users = User.query.all()
    return render_template('members.html', title='Members', users=users)


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


@fapp.route('/user/<username>')
@login_required
def user(username):
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': current_user, 'body': 'Test post #1'},
        {'author': current_user, 'body': 'Test post #2'}
    ]
    # if username == current_user.username:
    #     # user = User.query.filter_by(username=username).first_or_404()
    #     posts = [
    #         {'author': current_user, 'body': 'Test post #1'},
    #         {'author': current_user, 'body': 'Test post #2'}
    #     ]
    # else:
    #     flash(f'Invalid operation - Current user "{current_user.username}" cannot see posts of other user')
    #     return redirect(url_for('user', username=current_user.username))
    return render_template('user.html', user=user, posts=posts, form=form)


@fapp.route('/submit_post', methods=['GET', 'POST'])
@login_required
def submit_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Congratulations, you have added new post!')

        return redirect(url_for('items'))
    return render_template('submit_post.html', title='Write new post!', form=form)


@fapp.route('/user/<username>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    form = EditProfileForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        f = form.filename.data
        if f:
            secured_fname = secure_filename(f.filename)
            if imghdr.what(f.stream) in fapp.config['ALLOWED_IMG_EXTENSIONS']:
                dst_dir = os.path.join(user.get_avatar_dir(), secured_fname)
                f.save(dst_dir)
                flash(f'Successfully uploaded file "{secured_fname}", saved in {dst_dir}!')
            else:
                flash(f'Selected file "{secured_fname}" was not valid image type!')
        about_me = form.about_me.data
        if about_me:
            user.about_me = about_me
            db.session.commit()
        return redirect(url_for('user', username=user.username))
    return render_template('edit_profile.html', form=form)


@fapp.route('/admin')
@login_required
def admin():
    if current_user.is_authenticated:
        user = User.query.filter_by(username=current_user.username).first_or_404()
        return render_template('admin.html', user=user) \
            if current_user.is_admin \
            else redirect(url_for('user', username=current_user.username))


@fapp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@fapp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@fapp.route('/reset_password_request', methods=['POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@fapp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@fapp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

