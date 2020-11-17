from flask import render_template
from app import fapp, db


@fapp.errorhandler(404)
def not_found_error(error):
    print(error)
    return render_template('404.html'), 404


@fapp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    print(error)
    return render_template('500.html'), 500
