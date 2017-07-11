import sys
import getpass
from manager import Manager
from utils import tools
from ssr_panel import app, AsyncBaseModel
from ssr_panel.models import User


AsyncBaseModel.select().database.set_allow_sync(True)

manager = Manager()

GREEN_COLOR = '\033[01;32m'
RED_COLOR = '\033[01;31m'
DEFAULT_COLOR = '\033[0;0m'


@manager.command
def createadmin():
    """create admin account"""
    email = None
    while email is None:
        email = input('Email: ').strip()
        if email == '':
            email = None
            continue

        if User.select().where(User.email == email).exists():
            print(RED_COLOR + "Error: '%s' is already exists." % email + DEFAULT_COLOR, file=sys.stderr)
            email = None

    password = None
    while password is None:
        password = getpass.getpass()
        password2 = getpass.getpass('Password (again): ')
        if password != password2:
            print(RED_COLOR + "Error: Your passwords didn't match." + DEFAULT_COLOR, file=sys.stderr)
            password = None
            # Don't validate passwords that don't match.
            continue

        if password.strip() == '':
            print(RED_COLOR + "Error: Blank passwords aren't allowed." + DEFAULT_COLOR, file=sys.stderr)
            password = None
            # Don't validate blank passwords.
            continue

    try:
        max_port = User.select().order_by(User.port.desc()).get().port
    except User.DoesNotExist:
        max_port = 1024

    user = User()
    user.user_name = ''
    user.email = email
    user.password = user.hash_password(password)
    user.passwd = tools.random_string(6)
    user.port = max_port + 1
    user.t = 0
    user.u = 0
    user.d = 0
    user.transfer_enable = tools.gb_to_byte(app.config.DEFAULT_TRAFFIC)
    user.invite_num = app.config.INVITE_NUM
    user.ref_by = 0
    user.is_admin = 1

    try:
        user.save()
    except Exception as e:
        print(RED_COLOR + "Error: %s" % e + DEFAULT_COLOR, file=sys.stderr)
    else:
        print(GREEN_COLOR + "admin account created successfully." + DEFAULT_COLOR)


@manager.command
def changepassword():
    """change admin account's password"""
    user = None
    while user is None:
        email = input('Email: ').strip()
        if email == '':
            continue

        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            print(RED_COLOR + "Error: '%s' does not exist" % email + DEFAULT_COLOR, file=sys.stderr)

    print("Changing password for user '%s'" % user.email)

    password = None
    while password is None:
        password = getpass.getpass()
        password2 = getpass.getpass('Password (again): ')
        if password != password2:
            print(RED_COLOR + "Error: Your passwords didn't match." + DEFAULT_COLOR, file=sys.stderr)
            password = None
            # Don't validate passwords that don't match.
            continue

        if password.strip() == '':
            print(RED_COLOR + "Error: Blank passwords aren't allowed." + DEFAULT_COLOR, file=sys.stderr)
            password = None
            # Don't validate blank passwords.
            continue

    user.password = user.hash_password(password)

    try:
        user.save()
    except Exception as e:
        print(RED_COLOR + "Error: %s" % e + DEFAULT_COLOR, file=sys.stderr)
    else:
        print(GREEN_COLOR + "Password changed successfully." + DEFAULT_COLOR)


if __name__ == '__main__':
    manager.main()
