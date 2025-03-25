import tornado.web
import json
from db import get_db_connection
from api.BaseHandler import BaseHandler

class LogoutHandler(BaseHandler):
    def get(self):
        user_cookie = self.get_secure_cookie("user")
        if user_cookie:
            try:
                user_data = json.loads(user_cookie.decode("utf-8"))
                session_id = user_data.get("session_id")
                if session_id:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
                        conn.commit()
                    except Exception as e:
                        print(f"Error during logout: {e}")
                    finally:
                        cursor.close()
                        conn.close()
            except (ValueError, KeyError):
                pass  # Invalid cookie, just clear it
        
        self.clear_cookie("user")
        self.redirect("/login")