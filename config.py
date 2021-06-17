from dotenv import load_dotenv
import os

load_dotenv()

# Create dummy secrey key so we can use sessions
SECRET_KEY = os.getenv('SECRET_KEY')

# Create in-memory database
DATABASE_FILE = 'sample_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True

# Flask-Security config
SECURITY_URL_PREFIX = "/admin"
SECURITY_PASSWORD_HASH = os.getenv('PASSWORD_HASH')
SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT_')

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_REGISTER_URL = "/register/"

SECURITY_POST_LOGIN_VIEW = "/admin/"
SECURITY_POST_LOGOUT_VIEW = "/admin/"
SECURITY_POST_REGISTER_VIEW = "/admin/"

# Flask-Security features
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = True

# Flask-Mail config
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = os.getenv('PORT')
MAIL_USERNAME = os.getenv('MAIL')
MAIL_PASSWORD = os.getenv('MAIL_PASS')
MAIL_USE_TLS = False
MAIL_USE_SSL = True