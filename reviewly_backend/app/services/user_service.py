from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.models.user import User
from app import db, create_app
from app.models.product import Product
from sqlalchemy.exc import SQLAlchemyError

class UserService:
    VALID_ROLES = {"user", "admin"}

    @staticmethod
    def get_users(
        limit=5,
        email=None,
        email_contains=None,
        role=None,
        github_id=None,
        has_github_id=None,
        order_by='created_at',
        descending=True
    ):
        app = create_app()
        with app.app_context():
            query = User.query
            
            if email:
                query = query.filter_by(email=email.lower())
                
            if email_contains:
                query = query.filter(User.email.ilike(f"%{email_contains.lower()}%"))
                
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
        app = create_app()
        with app.app_context():
            return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        app = create_app()
        with app.app_context():
            return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def create_user(email, role, github_id=None):
        """Create a new user"""
        app = create_app()
        with app.app_context():
            session = Session(db.engine)
            try:
                if role.lower() not in UserService.VALID_ROLES:
                    return None, f"Invalid role. Must be one of: {', '.join(UserService.VALID_ROLES)}"
                
                if UserService.get_user_by_email(email):
                    return None, "Email already exists"
                
                user = User(
                    email=email.lower(),
                    role=role.lower(),
                    github_id=github_id
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return user, None
            except SQLAlchemyError as e:
                session.rollback()
                return None, str(e)
            finally:
                session.close()

    @staticmethod
    def update_user(user_id, email=None, role=None, github_id=None):
        """Update an existing user"""
        app = create_app()
        with app.app_context():
            session = Session(db.engine)
            try:
                user = session.get(User, user_id)
                if not user:
                    return None, "User not found"
                
                if email and email.lower() != user.email:
                    if UserService.get_user_by_email(email):
                        return None, "Email already exists"
                    user.email = email.lower()
                
                if role:
                    if role.lower() not in UserService.VALID_ROLES:
                        return None, f"Invalid role. Must be one of: {', '.join(UserService.VALID_ROLES)}"
                    user.role = role.lower()
                
                if github_id is not None:
                    user.github_id = github_id
                
                session.commit()
                session.refresh(user)
                return user, None
            except SQLAlchemyError as e:
                session.rollback()
                return None, str(e)
            finally:
                session.close()

    @staticmethod
    def get_user_favorite_ids(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            favorite_ids = [product.product_id for product in user.favorites]
            return favorite_ids, None
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def get_user_favorites(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "User not found"
            return user.favorites, None
        except SQLAlchemyError as e:
            return None, str(e)

    @staticmethod
    def add_to_favorites(user_id, product_id):
        try:
            user = User.query.get(user_id)
            product = Product.query.get(product_id)
            
            if not user:
                return False, "User not found"
            if not product:
                return False, "Product not found"
            if product in user.favorites:
                return False, "Product already in favorites"
                
            user.favorites.append(product)
            db.session.commit()
            return True, "Product added to favorites"
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def remove_from_favorites(user_id, product_id):
        try:
            user = User.query.get(user_id)
            product = Product.query.get(product_id)
            
            if not user:
                return False, "User not found"
            if not product:
                return False, "Product not found"
            if product not in user.favorites:
                return False, "Product not in favorites"
                
            user.favorites.remove(product)
            db.session.commit()
            return True, "Product removed from favorites"
        except SQLAlchemyError as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def delete_user(user_id):
        app = create_app()
        with app.app_context():
            session = Session(db.engine)
            try:
                user = session.get(User, user_id)
                if not user:
                    session.close()
                    return False, "User not found"
                
                session.delete(user)
                session.commit()
                return True, "User deleted successfully"
            except SQLAlchemyError as e:
                session.rollback()
                return False, str(e)
            finally:
                session.close()