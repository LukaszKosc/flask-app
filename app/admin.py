from app import routes
from flask import request, session, render_template
import json

class Admin(routes.FlaskView):
    route_base = '/admin'

    @routes.route('/')
    def connect(self):
        user=request.args.get('user')
        print('user', user)
        return render_template('admin.html', title='Admin page', user=user)





#
# @fapp.route('/db')
# def db_index():
#     return "Hello, DB"
