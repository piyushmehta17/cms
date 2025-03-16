from api.libraries import *
class MainHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")
