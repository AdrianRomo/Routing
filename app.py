#!venv/bin/python
import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose
from wtforms import PasswordField
from connectR import crearU, modificarU, conectar, eliminarU, hacerPing

# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    router = db.Column(db.String(255))
    privileges = db.Column(db.Integer())
    IP = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


    def __str__(self):
        return self.email

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    can_edit = True
    edit_modal = False
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['privileges','IP','router','email', 'username','password']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    #form_overrides = {
    #    'password': PasswordField
    #}


class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')
# Flask views
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/user/edit/?id=<id>', methods=["GET", "POST"])
def routers():
    if request.method == 'POST':
        usuario = request.form['username']
        password = request.form['password']
        prv = request.form['privileges']
        
        print("usuario: ", usuario)
        print("password: ", password)
        print("privilegio: ", prv)
    
    if(b == "Crear"):
        crearU(usuario, password, prv)
    elif(b == "Eliminar"):
        eliminarU(usuario, password, prv)
    elif(b == "Modificar"):
        modificarU(usuario, password, prv)
    else:
        conectar(usuario, password, prv)
    
    return render_template("/admin/user/")
# Create admin
admin = flask_admin.Admin(
    app,
    'Network Manager',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        
        db.session.add(user_role)
        db.session.add(super_user_role)

        db.session.commit()

        usernames = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        routers = ['R1', 'R2', 'R3', 'R4']
        routers_ip= ['192.168.0.1','10.10.0.130','10.10.0.134']
        privs = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        IPtempadmin=random.choice(routers_ip)
        test_user = user_datastore.create_user(
            username='Admin',
            router='R1',
            IP=IPtempadmin,
            privileges=15,
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        for i in range(len(usernames)):
            IPtemp = random.choice(routers_ip)
            tmp_email = usernames[i].lower() + "@" + IPtemp
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                username=usernames[i],
                router=routers[1],
                privileges=random.choice(privs),
                IP=IPtemp,
                email=tmp_email,
                #password=encrypt_password(tmp_pass),
                password=tmp_pass,
                roles=[user_role,]
            )
        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    app.run(debug=True)
