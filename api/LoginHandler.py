import tornado.web
import json
import bcrypt
import uuid
from datetime import datetime, timedelta
from db import get_db_connection
from api.BaseHandler import BaseHandler

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")
    
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password").encode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT username, password, role FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password, user["password"].encode("utf-8")):
                
                session_id = str(uuid.uuid4())
                expires_at = datetime.now() + timedelta(minutes=30)
                
                
                cursor.execute(
                    "INSERT INTO sessions (session_id, username, expires_at) VALUES (%s, %s, %s)",
                    (session_id, user["username"], expires_at)
                )
                conn.commit()

                
                self.set_secure_cookie(
                    "user",
                    json.dumps({
                        "username": user["username"],
                        "role": user["role"],
                        "session_id": session_id
                    }),
                    expires=expires_at
                )
                
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