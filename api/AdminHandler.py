from api.libraries import *
from api.BaseHandler import BaseHandler

class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # Decode the current user from the session
        user = self.current_user
        if user["role"] != "admin":  # Only allow admin users
            self.redirect("/user")
            return
            
        view_file = self.get_argument("view", None)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Return results as dictionaries
        try:
            # Fetch users from the database, excluding the admin user
            cursor.execute("SELECT username, role, created_at FROM users WHERE username != 'admin'")
            users = {user["username"]: {"role": user["role"], "created_at": user["created_at"]} for user in cursor.fetchall()}
            
            # Fetch files from the database
            cursor.execute("SELECT * FROM files")
            files = cursor.fetchall()
            
            # If a specific file is requested, serve it
            if view_file:
                cursor.execute("SELECT * FROM files WHERE filename = %s", (view_file,))
                file_info = cursor.fetchone()
                if file_info:
                    self.set_header("Content-Type", "application/octet-stream")
                    self.set_header("Content-Disposition", f"inline; filename={file_info['original_name']}")
                    with open(f"static/uploads/{view_file}", "rb") as f:
                        self.write(f.read())
                    return
                
            # Render the admin template with users and files data
            self.render("admin.html", users=users, files=files)
        except Exception as e:
            self.set_status(500)
            self.write(f"Error in admin handler: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    @tornado.web.authenticated
    def post(self):
        user = self.current_user
        if user["role"] != "admin":  # Only allow admin users
            self.redirect("/user")
            return
            
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
                
                # Prevent updating the admin user's role
                if username == "admin":
                    self.set_status(400)
                    self.write("Cannot update the role of the admin user")
                    return
                
                # Validate the role value
                valid_roles = ["admin", "viewer", "manager", "creator"]  # Add all valid roles here
                if role not in valid_roles:
                    self.set_status(400)
                    self.write("Invalid role value")
                    return
                
                cursor.execute(
                    "UPDATE users SET role = %s WHERE username = %s",
                    (role, username)
                )
                conn.commit()
            elif action == "delete_user":
                username = self.get_argument("username")
                
                # Prevent deleting the admin user
                if username == "admin":
                    self.set_status(400)
                    self.write("Cannot delete the admin user")
                    return
                
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