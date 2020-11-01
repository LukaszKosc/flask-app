from app import fapp, db
from app.models import User, Post


@fapp.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}


