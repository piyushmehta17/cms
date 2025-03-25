# api/BaseHandler.py
import tornado.web
import json
from db import get_db_connection
from datetime import datetime

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_cookie = self.get_secure_cookie("user")
        if not user_cookie:
            return None
        
        try:
            user_data = json.loads(user_cookie.decode("utf-8"))
            session_id = user_data.get("session_id")
            username = user_data.get("username")
            if not session_id or not username:
                return None
        except (ValueError, KeyError):
            return None
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT username FROM sessions WHERE session_id = %s AND username = %s AND expires_at > %s",
                (session_id, username, datetime.now())
            )
            if cursor.fetchone():
                return user_data  # Return cookie data directly if session is valid
            return None
        except Exception as e:
            print(f"Error checking session: {e}")
            return None
        finally:
            cursor.close()
            conn.close()