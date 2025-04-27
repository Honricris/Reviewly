import json
from app import create_app
from app.services.user_service import UserService

class AdminHandlers:
    VALID_ROLES = {"user", "admin"}

    @staticmethod
    def handle_get_users(args):
        """
        Handle admin requests to get users with optional filters.
        """
        limit = args.get("limit", 5)
        email = args.get("email")
        email_starts_with = args.get("email_starts_with")
        role = args.get("role")
        github_id = args.get("github_id")
        has_github_id = args.get("has_github_id")
        
        app = create_app()
        with app.app_context():
            try:
                users = UserService.get_users(
                    limit=limit,
                    email=email,
                    email_starts_with=email_starts_with,
                    role=role,
                    github_id=github_id if github_id is not None else None,
                    has_github_id=has_github_id if has_github_id is not None else None
                )
            except ValueError as e:
                return json.dumps({"error": str(e)})
        
        users_data = [{
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "github_id": user.github_id
        } for user in users]
        
        if not users_data:
            response_text = "No users found matching the criteria."
        else:
            response_text = f"Found {len(users_data)} user(s):\n" + "\n".join(
                [f"ID: {user['id']}, Email: {user['email']}, Role: {user['role']}, GitHub ID: {user['github_id'] or 'None'}" 
                 for user in users_data]
            )
        
        return json.dumps({
            "response_text": response_text,
            "additional_data": {
                "users": users_data
            }
        })
    
    @staticmethod
    def handle_get_user_by_id(args):
        """
        Handle admin request to get a single user by ID.
        """
        user_id = args.get("user_id")
        if not user_id:
            return json.dumps({"error": "user_id is required"})
            
        app = create_app()
        with app.app_context():
            user = UserService.get_user_by_id(user_id)
            
        if not user:
            return json.dumps({
                "response_text": f"No user found with ID: {user_id}",
                "additional_data": {}
            })
            
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "github_id": user.github_id
        }
        
        response_text = (f"User found:\n"
                        f"ID: {user.id}\n"
                        f"Email: {user.email}\n"
                        f"Role: {user.role}\n"
                        f"GitHub ID: {user.github_id or 'None'}")
        
        return json.dumps({
            "response_text": response_text,
            "additional_data": {
                "user": user_data
            }
        })
    
    @staticmethod
    def handle_set_user_role(args):
        """
        Handle admin request to change a user's role.
        """
        user_id = args.get("user_id")
        new_role = args.get("new_role")
        
        if not user_id or not new_role:
            return json.dumps({"error": "user_id and new_role are required"})
            
        if new_role.lower() not in AdminHandlers.VALID_ROLES:
            return json.dumps({"error": f"Invalid role. Must be one of: {', '.join(AdminHandlers.VALID_ROLES)}"})
            
        app = create_app()
        with app.app_context():
            try:
                user = UserService.set_user_role(user_id, new_role)
            except ValueError as e:
                return json.dumps({"error": str(e)})
                
            if not user:
                return json.dumps({
                    "response_text": f"No user found with ID: {user_id}",
                    "additional_data": {}
                })
            
            user_data = {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "github_id": user.github_id
            }
            
            response_text = (f"User role updated:\n"
                            f"ID: {user.id}\n"
                            f"Email: {user.email}\n"
                            f"New Role: {user.role}")
            
            return json.dumps({
                "response_text": response_text,
                "additional_data": {
                    "user": user_data
                }
            })