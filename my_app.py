from app import fapp, db
from app.models import User, Post, Role


@fapp.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post, 'Role': Role}
