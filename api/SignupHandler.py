from api.libraries import *

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


