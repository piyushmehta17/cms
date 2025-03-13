# main.py
import tornado.ioloop
import tornado.web
import os
import uuid
import json
import sys
from db import get_db_connection

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class MainHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")

class SignupHandler(BaseHandler):
    def get(self):
        self.render("signup.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                self.write("Username already exists")
                return
            
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, "viewer")
            )
            conn.commit()
        except Exception as e:
            self.set_status(500)
            self.write(f"Error during signup: {str(e)}")
            return
        finally:
            cursor.close()
            conn.close()
        
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
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            cursor.execute(
                "SELECT username, role FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            if user:
                self.set_secure_cookie("user", json.dumps({
                    "username": user["username"],
                    "role": user["role"]
                }))
                self.redirect("/user")
            else:
                self.write("Invalid credentials")
        except Exception as e:
            self.set_status(500)
            self.write(f"Error during login: {str(e)}")
        finally:
            cursor.close()
            conn.close()

class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = json.loads(self.current_user.decode())
        view_file = self.get_argument("view", None)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            cursor.execute("SELECT * FROM files")
            files = cursor.fetchall()
            
            if view_file:
                cursor.execute("SELECT * FROM files WHERE filename = %s", (view_file,))
                file_info = cursor.fetchone()
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
        except Exception as e:
            self.set_status(500)
            self.write(f"Error in user handler: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def post(self):
        user = json.loads(self.current_user.decode())
        action = self.get_argument("action", "")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            if action == "delete" and user["role"] == "manager":
                filename = self.get_argument("filename")
                cursor.execute("DELETE FROM files WHERE filename = %s AND is_admin = FALSE", (filename,))
                conn.commit()
                os.remove(f"static/uploads/{filename}")
            
            elif user["role"] in ["creator", "manager"]:
                file = self.request.files.get("file")[0]
                filename = str(uuid.uuid4()) + "_" + file["filename"]
                with open(f"static/uploads/{filename}", "wb") as f:
                    f.write(file["body"])
                
                cursor.execute(
                    "INSERT INTO files (filename, original_name, uploader, is_admin) VALUES (%s, %s, %s, %s)",
                    (filename, file["filename"], user["username"], False)
                )
                conn.commit()
        except Exception as e:
            self.set_status(500)
            self.write(f"Error in user post: {str(e)}")
            return
        finally:
            cursor.close()
            conn.close()
        self.redirect("/user")

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = json.loads(self.current_user.decode())
        if user["role"] != "admin":
            self.redirect("/user")
            return
            
        view_file = self.get_argument("view", None)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            cursor.execute("SELECT username, role FROM users")
            users = {user["username"]: {"role": user["role"]} for user in cursor.fetchall()}
            
            cursor.execute("SELECT * FROM files")
            files = cursor.fetchall()
            
            if view_file:
                cursor.execute("SELECT * FROM files WHERE filename = %s", (view_file,))
                file_info = cursor.fetchone()
                if file_info:
                    self.set_header("Content-Type", "application/octet-stream")
                    self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
                    with open(f"static/uploads/{view_file}", "rb") as f:
                        self.write(f.read())
                    return
                
            self.render("admin.html", users=users, files=files)
        except Exception as e:
            self.set_status(500)
            self.write(f"Error in admin handler: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def post(self):
        action = self.get_argument("action", "")
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if action == "upload":
                file = self.request.files.get("file")[0]
                filename = str(uuid.uuid4()) + "_" + file["filename"]
                with open(f"static/uploads/{filename}", "wb") as f:
                    f.write(file["body"])
                
                cursor.execute(
                    "INSERT INTO files (filename, original_name, uploader, is_admin) VALUES (%s, %s, %s, %s)",
                    (filename, file["filename"], "admin", True)
                )
                conn.commit()
            elif action == "update_role":
                username = self.get_argument("username")
                role = self.get_argument("role")
                cursor.execute(
                    "UPDATE users SET role = %s WHERE username = %s",
                    (role, username)
                )
                conn.commit()
            elif action == "delete_user":
                username = self.get_argument("username")
                cursor.execute("DELETE FROM users WHERE username = %s", (username,))
                conn.commit()
            elif action == "delete_file":
                filename = self.get_argument("filename")
                cursor.execute("DELETE FROM files WHERE filename = %s", (filename,))
                conn.commit()
                os.remove(f"static/uploads/{filename}")
        except Exception as e:
            self.set_status(500)
            self.write(f"Error in admin post: {str(e)}")
            return
        finally:
            cursor.close()
            conn.close()
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
    static_url_prefix="/static/",
    cookie_secret="your-secret-key",
    login_url="/login")

if __name__ == "__main__":
    if not os.path.exists("static/uploads"):
        os.makedirs("static/uploads")
    
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