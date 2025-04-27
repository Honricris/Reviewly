from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.models.user import User
from app import db, create_app

class UserService:
    VALID_ROLES = {"user", "admin"}

    @staticmethod
    def get_users(
        limit=5,
        email=None,
        email_starts_with=None,
        role=None,
        github_id=None,
        has_github_id=None,
        order_by='created_at',
        descending=True
    ):
        """
        Get users with optional filtering parameters.
        """
        app = create_app()
        with app.app_context():
            query = User.query
            
            if email:
                query = query.filter_by(email=email.lower())
                
            if email_starts_with:
                query = query.filter(User.email.ilike(f"{email_starts_with.lower()}%"))
                
            if role:
                if role.lower() not in UserService.VALID_ROLES:
                    raise ValueError(f"Invalid role. Must be one of: {', '.join(UserService.VALID_ROLES)}")
                query = query.filter_by(role=role.lower())
                
            if github_id is not None:
                query = query.filter_by(github_id=github_id)
                
            if has_github_id is not None:
                if has_github_id:
                    query = query.filter(User.github_id.isnot(None))
                else:
                    query = query.filter(User.github_id.is_(None))
                
            order_column = getattr(User, order_by) if hasattr(User, order_by) else User.created_at
            if descending:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
                
            return query.limit(limit).all()
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get a single user by ID."""
        app = create_app()
        with app.app_context():
            return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get a single user by email."""
        app = create_app()
        with app.app_context():
            return User.query.filter_by(email=email.lower()).first()
    
    @staticmethod
    def set_user_role(user_id, new_role):
        """
        Change a user's role with explicit session management.
        
        Args:
            user_id (int): The ID of the user to modify
            new_role (str): The new role to assign (must be 'user' or 'admin')
            
        Returns:
            User: The updated user object, or None if user not found
            
        Raises:
            ValueError: If new_role is not 'user' or 'admin'
        """
        if new_role.lower() not in UserService.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(UserService.VALID_ROLES)}")
            
        app = create_app()
        with app.app_context():
            session = Session(db.engine)
            try:
                user = session.get(User, user_id)
                if not user:
                    session.close()
                    return None
                
                user.role = new_role.lower()
                session.commit()
                session.refresh(user)
                return user
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()