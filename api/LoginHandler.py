from api.libraries import *
from api.BaseHandler import *
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
