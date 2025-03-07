import tornado.ioloop
import tornado.web
import os
import uuid
from datetime import datetime
import json

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        user = json.loads(self.current_user.decode())
        if user.get("role") == "admin":
            self.redirect("/admin")
        else:
            self.redirect("/user")

class SignupHandler(BaseHandler):
    def get(self):
        self.render("signup.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        
        with open("users.json", "r+") as f:
            try:
                users = json.load(f)
            except:
                users = {}
            
            if username in users:
                self.write("Username already exists")
                return
                
            users[username] = {
                "password": password,
                "role": "viewer",
                "created_at": datetime.now().isoformat()
            }
            f.seek(0)
            json.dump(users, f)
        
        self.redirect("/login")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        
        if username == "admin" and password == "admin123":
            self.set_secure_cookie("user", json.dumps({"username": "admin", "role": "admin"}))
            self.redirect("/admin")
            return
            
        with open("users.json", "r") as f:
            try:
                users = json.load(f)
                if username in users and users[username]["password"] == password:
                    self.set_secure_cookie("user", json.dumps({
                        "username": username,
                        "role": users[username]["role"]
                    }))
                    self.redirect("/user")
                else:
                    self.write("Invalid credentials")
            except:
                self.write("Invalid credentials")

class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = json.loads(self.current_user.decode())
        view_file = self.get_argument("view", None)
        
        with open("files.json", "r") as f:
            try:
                files = json.load(f)
            except:
                files = []
                
        if view_file:
            file_info = next((f for f in files if f["filename"] == view_file), None)
            if file_info and (not file_info["is_admin"] or user["role"] == "admin"):
                self.set_header("Content-Type", "application/octet-stream")
                self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
                with open(f"static/uploads/{view_file}", "rb") as f:
                    self.write(f.read())
                return
            else:
                self.write("Permission denied")
                return
                
        self.render("user.html", user=user, files=files)
    
    def post(self):
        user = json.loads(self.current_user.decode())
        action = self.get_argument("action", "")
        
        if action == "delete" and user["role"] == "manager":
            filename = self.get_argument("filename")
            with open("files.json", "r+") as f:
                files = json.load(f)
                files = [f for f in files if f["filename"] != filename and not f["is_admin"]]
                f.seek(0)
                f.truncate()
                json.dump(files, f)
            os.remove(f"static/uploads/{filename}")
        
        elif user["role"] in ["creator", "manager"]:
            file = self.request.files.get("file")[0]
            filename = str(uuid.uuid4()) + "_" + file["filename"]
            with open(f"static/uploads/{filename}", "wb") as f:
                f.write(file["body"])
            
            with open("files.json", "r+") as f:
                try:
                    files = json.load(f)
                except:
                    files = []
                files.append({
                    "filename": filename,
                    "original_name": file["filename"],
                    "uploader": user["username"],
                    "is_admin": False
                })
                f.seek(0)
                f.truncate()
                json.dump(files, f)
        self.redirect("/user")

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = json.loads(self.current_user.decode())
        if user["role"] != "admin":
            self.redirect("/user")
            return
            
        view_file = self.get_argument("view", None)
        with open("users.json", "r") as f:
            users = json.load(f)
        with open("files.json", "r") as f:
            try:
                files = json.load(f)
            except:
                files = []
                
        if view_file:
            file_info = next((f for f in files if f["filename"] == view_file), None)
            if file_info:
                self.set_header("Content-Type", "application/octet-stream")
                self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
                with open(f"static/uploads/{view_file}", "rb") as f:
                    self.write(f.read())
                return
                
        self.render("admin.html", users=users, files=files)
    
    def post(self):
        action = self.get_argument("action", "")
        if action == "upload":
            file = self.request.files.get("file")[0]
            filename = str(uuid.uuid4()) + "_" + file["filename"]
            with open(f"static/uploads/{filename}", "wb") as f:
                f.write(file["body"])
            
            with open("files.json", "r+") as f:
                try:
                    files = json.load(f)
                except:
                    files = []
                files.append({
                    "filename": filename,
                    "original_name": file["filename"],
                    "uploader": "admin",
                    "is_admin": True
                })
                f.seek(0)
                json.dump(files, f)
        elif action == "update_role":
            username = self.get_argument("username")
            role = self.get_argument("role")
            with open("users.json", "r+") as f:
                users = json.load(f)
                if username in users:
                    users[username]["role"] = role
                    f.seek(0)
                    json.dump(users, f)
        elif action == "delete_user":
            username = self.get_argument("username")
            with open("users.json", "r+") as f:
                users = json.load(f)
                if username in users:
                    del users[username]
                    f.seek(0)
                    json.dump(users, f)
        elif action == "delete_file":
            filename = self.get_argument("filename")
            with open("files.json", "r+") as f:
                files = json.load(f)
                files = [f for f in files if f["filename"] != filename]
                f.seek(0)
                f.truncate()
                json.dump(files, f)
            os.remove(f"static/uploads/{filename}")
        self.redirect("/admin")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/signup", SignupHandler),
        (r"/login", LoginHandler),
        (r"/user", UserHandler),
        (r"/admin", AdminHandler),
    ],
    template_path="templates",
    static_path="static",
    cookie_secret="your-secret-key",
    login_url="/login")

if __name__ == "__main__":
    if not os.path.exists("static/uploads"):
        os.makedirs("static/uploads")
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    if not os.path.exists("files.json"):
        with open("files.json", "w") as f:
            json.dump([], f)
            
    app = make_app()
    port = 8888
    max_attempts = 10
    
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