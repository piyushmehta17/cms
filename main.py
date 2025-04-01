# main.py
import tornado.ioloop
import tornado.web
import os
import uuid
import json
import sys
from db import get_db_connection
import re
import bcrypt
import json
import tornado.web
from rbac import rbac, Permission

from api.SignupHandler import SignupHandler
from api.LoginHandler import LoginHandler
from api.LogoutHandler import LogoutHandler
from api.AdminHandler import AdminHandler
from api.UserHandler import UserHandler
from api.UserHandler import UserHandler
from api.BaseHandler import BaseHandler

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user:
            return json.loads(user)
        return None

    def get_user_role(self):
        user = self.get_current_user()
        if user and "role" in user:
            return user["role"]
        return None

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the current user has the specified permission
        """
        role = self.get_user_role()
        if not role:
            return False
        return rbac.has_permission(role, permission)

    def require_permission(self, permission: Permission):
        """
        Decorator to require a specific permission for a handler method
        """
        if not self.has_permission(permission):
            self.set_status(403)
            self.write({"error": "Permission denied"})
            self.finish()
            return False
        return True

class MainHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")





def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
         (r"/logout", LogoutHandler),
        (r"/login", LoginHandler),
        (r"/user", UserHandler),
        (r"/admin", AdminHandler),
    ],
    template_path="templates",
    static_path="static",
    static_url_prefix="/static/",
    cookie_secret="your-secret-key",
    login_url="/login")

if __name__ == "__main__":

    if not os.path.exists("static/uploads"):
        os.makedirs("static/uploads")
    
    app = make_app()
    port = 8888
    max_attempts = 10

    try:
        conn = get_db_connection()
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
    
    
    
    for i in range(max_attempts):
        try:
            app.listen(port)
            print(f"Server running on http://localhost:{port}")
            break
        except OSError as e:
            if "Only one usage of each socket address" in str(e):
                port += 1
                continue
            raise
    else:
        print(f"Could not find an available port between 8888 and {port-1}")
        sys.exit(1)
    
    tornado.ioloop.IOLoop.current().start()









