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


import re
import bcrypt
import json
import tornado.web
from db import get_db_connection

class SignupHandler(tornado.web.RequestHandler):
    def get(self):
        """Render the signup page."""
        self.render("signup.html")

    def post(self):
        """Handle user signup with validation and database insertion."""
        username = self.get_argument("username")
        password = self.get_argument("password")

        # Validate password
        validation_message = self.validate_password(password)
        if validation_message:
            self.set_status(400)  # Bad request
            self.write(json.dumps({"error": validation_message}))
            return

        # Hash password securely
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if the username already exists
            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                self.set_status(400)
                self.write(json.dumps({"error": "Username already exists"}))
                return
            
            # Insert new user into MySQL database with hashed password
            cursor.execute(
                "INSERT INTO user (username, password, role, created_at) VALUES (%s, %s, %s, NOW())",
                (username, hashed_password, "viewer")
            )
            conn.commit()
            self.write(json.dumps({"message": "User registered successfully"}))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"error": f"Error during signup: {str(e)}"}))
        finally:
            cursor.close()
            conn.close()

    def validate_password(self, password):
        """Validate password according to security rules."""
        if len(password) < 8:
            return "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return "Password must contain at least one digit (0-9)"
        if not re.search(r"[@$!%*?&]", password):
            return "Password must contain at least one special character (@$!%*?&)"
        return None  # Password is valid




# class LoginHandler(BaseHandler):
#     def get(self):
#         self.render("login.html")
    
#     def post(self):
#         username = self.get_argument("username")
#         password = self.get_argument("password")
        
#         if username == "admin" and password == "admin123":
#             self.set_secure_cookie("user", json.dumps({"username": "admin", "role": "admin"}))
#             self.redirect("/admin")
#             return
        
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
#         try:
#             cursor.execute(
#                 "SELECT username, role FROM users WHERE username = %s AND password = %s",
#                 (username, password)
#             )
#             user = cursor.fetchone()
#             if user:
#                 self.set_secure_cookie("user", json.dumps({
#                     "username": user["username"],
#                     "role": user["role"]
#                 }))
#                 self.redirect("/user")
#             else:
#                 self.write("Invalid credentials")
#         except Exception as e:
#             self.set_status(500)
#             self.write(f"Error during login: {str(e)}")
#         finally:
#             cursor.close()
#             conn.close()






import bcrypt
import json
import tornado.web
from db import get_db_connection

import bcrypt
import json
import tornado.web
from db import get_db_connection

import bcrypt

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password").encode("utf-8")  # Convert to bytes for hashing

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            # Fetch hashed password from the database
            cursor.execute("SELECT username, password, role FROM user WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password, user["password"].encode("utf-8")):
                # Set a secure cookie if credentials are valid
                self.set_secure_cookie("user", json.dumps({
                    "username": user["username"],
                    "role": user["role"]
                }))

                # Redirect based on role
                if user["role"] == "admin":
                    self.redirect("/admin")
                else:
                    self.redirect("/user")
            else:
                self.set_status(401)
                self.write(json.dumps({"error": "Invalid credentials"}))
        except Exception as e:
            self.set_status(500)
            self.write(json.dumps({"error": f"Error during login: {str(e)}"}))
        finally:
            cursor.close()
            conn.close()


# class UserHandler(BaseHandler):
#     @tornado.web.authenticated
#     def get(self):
#         user = json.loads(self.current_user.decode())
#         view_file = self.get_argument("view", None)
        
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
#         try:
#             cursor.execute("SELECT * FROM files")
#             files = cursor.fetchall()
            
#             if view_file:
#                 cursor.execute("SELECT * FROM files WHERE filename = %s", (view_file,))
#                 file_info = cursor.fetchone()
#                 if file_info and (not file_info["is_admin"] or user["role"] == "admin"):
#                     self.set_header("Content-Type", "application/octet-stream")
#                     self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
#                     with open(f"static/uploads/{view_file}", "rb") as f:
#                         self.write(f.read())
#                     return
#                 else:
#                     self.write("Permission denied")
#                     return
                
#             self.render("user.html", user=user, files=files)
#         except Exception as e:
#             self.set_status(500)
#             self.write(f"Error in user handler: {str(e)}")
#         finally:
#             cursor.close()
#             conn.close()
    
#     def post(self):
#         user = json.loads(self.current_user.decode())
#         action = self.get_argument("action", "")
        
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#         try:
#             if action == "delete" and user["role"] == "manager":
#                 filename = self.get_argument("filename")
#                 cursor.execute("DELETE FROM files WHERE filename = %s AND is_admin = FALSE", (filename,))
#                 conn.commit()
#                 os.remove(f"static/uploads/{filename}")
            
#             elif user["role"] in ["creator", "manager"]:
#                 file = self.request.files.get("file")[0]
#                 filename = str(uuid.uuid4()) + "_" + file["filename"]
#                 with open(f"static/uploads/{filename}", "wb") as f:
#                     f.write(file["body"])
                
#                 cursor.execute(
#                     "INSERT INTO files (filename, original_name, uploader, is_admin) VALUES (%s, %s, %s, %s)",
#                     (filename, file["filename"], user["username"], False)
#                 )
#                 conn.commit()
#         except Exception as e:
#             self.set_status(500)
#             self.write(f"Error in user post: {str(e)}")
#             return
#         finally:
#             cursor.close()
#             conn.close()
#         self.redirect("/user")

###ujjwaltesting



class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            # Decode the current user from the cookie
            user = json.loads(self.current_user.decode())
            
            # Check if the user is requesting to view a specific file
            view_file = self.get_argument("view", None)
            
            # Connect to the MySQL database using the get_db_connection function
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
            
            try:
                # Fetch all files from the database
                cursor.execute("SELECT * FROM files")
                files = cursor.fetchall()
                
                # If the user is requesting to view a specific file
                if view_file:
                    cursor.execute("SELECT * FROM files WHERE filename = %s", (view_file,))
                    file_info = cursor.fetchone()
                    
                    # Check if the file exists and the user has permission to view it
                    if file_info and (not file_info["is_admin"] or user["role"] == "admin"):
                        self.set_header("Content-Type", "application/octet-stream")
                        self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
                        
                        # Stream the file to the user
                        file_path = os.path.join("static/uploads", view_file)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                self.write(f.read())
                            return
                        else:
                            self.write("File not found")
                            return
                    else:
                        self.write("Permission denied")
                        return
                
                # Render the user page with the list of files
                self.render("user.html", user=user, files=files)
            
            except Exception as e:
                self.set_status(500)
                self.write(f"Error in user handler: {str(e)}")
            
            finally:
                # Close the database connection
                cursor.close()
                conn.close()
        
        except Exception as e:
            self.set_status(500)
            self.write(f"Error decoding user data: {str(e)}")
    
    def post(self):
        try:
            # Decode the current user from the cookie
            user = json.loads(self.current_user.decode())
            
            # Get the action from the request
            action = self.get_argument("action", "")
            
            # Connect to the MySQL database using the get_db_connection function
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            try:
                # Handle file deletion (only for managers)
                if action == "delete" and user["role"] == "manager":
                    filename = self.get_argument("filename")
                    print(f"Attempting to delete file: {filename}")  # Debugging
                    cursor.execute("DELETE FROM files WHERE filename = %s AND is_admin = FALSE", (filename,))
                    conn.commit()
                    
                    # Delete the file from the filesystem
                    file_path = os.path.join("static/uploads", filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"File deleted from filesystem: {filename}")  # Debugging
                    else:
                        print(f"File not found in filesystem: {filename}")  # Debugging
                
                # Handle file upload (for creators and managers)
                elif user["role"] in ["creator", "manager"]:
                    file = self.request.files.get("file")[0]
                    filename = str(uuid.uuid4()) + "_" + file["filename"]
                    file_path = os.path.join("static/uploads", filename)
                    
                    # Ensure the uploads directory exists
                    os.makedirs("static/uploads", exist_ok=True)
                    
                    # Save the file to the filesystem
                    with open(file_path, "wb") as f:
                        f.write(file["body"])
                    print(f"File saved to filesystem: {filename}")  # Debugging
                    
                    # Save the file metadata to the database
                    cursor.execute(
                        "INSERT INTO files (filename, original_name, uploader, is_admin) VALUES (%s, %s, %s, %s)",
                        (filename, file["filename"], user["username"], False)
                    )
                    conn.commit()
                    print(f"File metadata saved to database: {filename}")  # Debugging
            
            except Exception as e:
                self.set_status(500)
                self.write(f"Error in user post: {str(e)}")
                return
            
            finally:
                # Close the database connection
                cursor.close()
                conn.close()
            
            # Redirect to the user page after successful operation
            self.redirect("/user")
        
        except Exception as e:
            self.set_status(500)
            self.write(f"Error decoding user data: {str(e)}")



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









