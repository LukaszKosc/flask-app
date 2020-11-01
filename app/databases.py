from app import routes
from flask import request


class Database(routes.FlaskView):
    route_base = '/db'

    @routes.route('/connect')
    def connect(self):
        return f"Connecting to db"





#
# @fapp.route('/db')
# def db_index():
#     return "Hello, DB"
