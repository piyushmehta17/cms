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
                username = user_data.get("username")
                if username:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("DELETE FROM sessions WHERE username = %s", (username,))
                        conn.commit()
                    except Exception as e:
                        
                        pass
                    finally:
                        cursor.close()
                        conn.close()
            except (ValueError, KeyError):
                
                pass
        
        self.clear_cookie("user")
        self.redirect("/login")