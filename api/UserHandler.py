from api.libraries import *
from api.BaseHandler import BaseHandler
class UserHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            # Decode the current user from the cookie
            user = self.current_user
            
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
            user = self.current_user
            
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

