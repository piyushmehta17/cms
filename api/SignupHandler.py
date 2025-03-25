import tornado.web
import json
import bcrypt
import re
from db import get_db_connection
from api.BaseHandler import BaseHandler

class SignupHandler(BaseHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        validation_message = self.validate_password(password)
        if validation_message:
            self.set_status(400)
            self.write(json.dumps({"error": validation_message}))
            return

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                self.set_status(400)
                self.write(json.dumps({"error": "Username already exists"}))
                return
            
            cursor.execute(
                "INSERT INTO users (username, password, role, created_at) VALUES (%s, %s, %s, NOW())",
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
        return None