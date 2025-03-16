from api.BaseHandler import BaseHandler
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")  # Remove the user session cookie
        self.redirect("/login")  # Redirect to login page