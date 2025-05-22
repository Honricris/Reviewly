import json
from app import create_app
from app.services.user_service import UserService
import time


from sqlalchemy.sql import func, text
from sqlalchemy import and_
from datetime import datetime, timedelta
from app import db
from app.models.product import Product
from app.models.user import User, user_favorites
from app.models.review import Review
from app.models.LoginLog import LoginLog
import json


class AdminHandlers:
    VALID_ROLES = {"user", "admin"}

    @staticmethod
    def handle_get_users(args):
        limit = args.get("limit", 5)
        email = args.get("email")
        email_contains = args.get("email_contains")
        role = args.get("role")
        github_id = args.get("github_id")
        has_github_id = args.get("has_github_id")
        
        app = create_app()
        with app.app_context():
            try:
                users = UserService.get_users(
                    limit=limit,
                    email=email,
                    email_contains=email_contains,
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

    @staticmethod
    def handle_delete_user(args):
        user_id = args.get("user_id")
        
        if not user_id:
            return json.dumps({"error": "user_id is required"})
            
        app = create_app()
        with app.app_context():
            success, message = UserService.delete_user(user_id)
            
            if not success:
                return json.dumps({
                    "response_text": message,
                    "additional_data": {}
                })
            
            response_text = f"User with ID {user_id} has been successfully deleted"
            
            return json.dumps({
                "response_text": response_text,
                "additional_data": {}
            })

    @staticmethod
    def handle_generate_user_activity_report(args):
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        role = args.get("role")
        time.sleep(1)

        response_text = f"Generating User Activity Report with parameters: Start Date: {start_date}, End Date: {end_date}, Role: {role or 'All'}"
        
        additional_data = {
            "report_type": "user_activity",
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "role": role
            }
        }
        
        return json.dumps({
            "response_text": response_text,
            "additional_data": additional_data
        })

    @staticmethod
    def handle_generate_product_popularity_report(args):
        category = args.get("category")
        min_price = args.get("min_price")
        max_price = args.get("max_price")
        min_rating = args.get("min_rating")
        min_favorites = args.get("min_favorites")
        sort_by = args.get("sort_by", "title")
        sort_order = args.get("sort_order", "asc")
        
        time.sleep(1)

        response_text = f"Generating Product Popularity Report with parameters: Category: {category or 'All'}, Min Price: {min_price or 'Any'}, Max Price: {max_price or 'Any'}, Min Rating: {min_rating or 'Any'}, Min Favorites: {min_favorites or 'Any'}, Sort By: {sort_by or 'Title'}"
        
        additional_data = {
            "report_type": "product_popularity",
            "parameters": {
                "category": category,
                "min_price": min_price,
                "max_price": max_price,
                "min_rating": min_rating,
                "min_favorites": min_favorites,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        return json.dumps({
            "response_text": response_text,
            "additional_data": additional_data
        })

    @staticmethod
    def handle_generate_dynamic_chart(args):
        # Extract arguments
        chart_type = args.get("chart_type")
        data_source = args.get("data_source")
        x_axis = args.get("x_axis")
        y_axis = args.get("y_axis")
        title = args.get("title")
        aggregation_field = args.get("aggregation_field")
        group_by_field = args.get("group_by_field")
        time_field = args.get("time_field")
        time_range = args.get("time_range", "all_time")
        join_tables = args.get("join_tables", [])
        filter_conditions = args.get("filter_conditions", {})

        # Validate required parameters
        required_params = [chart_type, data_source, x_axis, y_axis, title, aggregation_field, group_by_field]
        if not all(required_params):
            return json.dumps({
                "error": "All parameters (chart_type, data_source, x_axis, y_axis, title, aggregation_field, group_by_field) are required"
            })

        # Validate chart_type
        if chart_type not in ["bar", "line", "pie", "doughnut"]:
            return json.dumps({"error": "Invalid chart_type. Must be one of: bar, line, pie, doughnut"})

        # Validate data_source
        model_map = {
            "products": Product,
            "users": User,
            "reviews": Review,
            "login_logs": LoginLog,
            "user_favorites": user_favorites
        }
        if data_source not in model_map:
            return json.dumps({
                "response_text": "Invalid data source",
                "additional_data": {},
                "error": "Data not valid",
                "debug": f"Invalid data_source: {data_source}"
            })
        base_model = model_map[data_source]

        # Define valid fields for each table
        valid_fields = {
            "products": ["product_id", "title", "main_category", "average_rating", "rating_number", "price", "created_at"],
            "users": ["id", "github_id", "email", "role", "created_at"],
            "reviews": ["review_id", "product_id", "rating", "helpful_vote", "verified_purchase", "timestamp", "created_at"],
            "login_logs": ["id", "user_id", "ip_address", "login_at"],
            "user_favorites": ["user_id", "product_id", "created_at"]
        }

        # Combine valid fields for data_source and join_tables
        all_valid_fields = valid_fields[data_source].copy()
        for join_table in join_tables:
            all_valid_fields.extend(valid_fields.get(join_table, []))

        # Validate group_by_field and aggregation_field
        if group_by_field not in all_valid_fields:
            return json.dumps({
                "response_text": "Invalid group by field",
                "additional_data": {},
                "error": "Data not valid",
                "debug": f"Invalid group_by_field: {group_by_field}"
            })
        if aggregation_field != "count" and aggregation_field not in valid_fields[data_source]:
            return json.dumps({
                "response_text": "Invalid aggregation field",
                "additional_data": {},
                "error": "Data not valid",
                "debug": f"Invalid aggregation_field: {aggregation_field}"
            })

        # Validate x_axis and y_axis alignment
        if x_axis != group_by_field or y_axis != aggregation_field:
            return json.dumps({
                "error": "x_axis must match group_by_field and y_axis must match aggregation_field"
            })

        # Fetch data
        start_date = None
        if time_range == "last_month":
            start_date = datetime.utcnow() - timedelta(days=30)
        elif time_range == "last_week":
            start_date = datetime.utcnow() - timedelta(days=7)

        app = create_app()
        with app.app_context():
            try:
                query = db.session.query()

                # Determine group_by_column
                if group_by_field in valid_fields.get("products", []) and "products" in join_tables:
                    group_by_column = getattr(Product, group_by_field)
                elif isinstance(base_model, db.Table):
                    group_by_column = base_model.c[group_by_field]
                else:
                    group_by_column = getattr(base_model, group_by_field)

                # Set up aggregation
                if aggregation_field == "count":
                    query = query.add_columns(group_by_column, func.count().label("agg_value"))
                else:
                    agg_column = base_model.c[aggregation_field] if isinstance(base_model, db.Table) else getattr(base_model, aggregation_field)
                    query = query.add_columns(group_by_column, func.sum(agg_column).label("agg_value"))

                query = query.select_from(base_model)

                # Handle joins
                join_map = {
                    ("user_favorites", "products"): (Product, user_favorites.c.product_id == Product.product_id),
                    ("products", "user_favorites"): (user_favorites, user_favorites.c.product_id == Product.product_id),
                    ("reviews", "products"): (Product, Review.product_id == Product.product_id),
                    ("login_logs", "users"): (User, LoginLog.user_id == User.id),
                    ("users", "user_favorites"): (user_favorites, User.id == user_favorites.c.user_id)
                }
                for join_table in join_tables:
                    key = (data_source, join_table)
                    if key not in join_map:
                        return json.dumps({
                            "response_text": "Invalid join configuration",
                            "additional_data": {},
                            "error": "Data not valid",
                            "debug": f"Invalid join between {data_source} and {join_table}"
                        })
                    join_model, condition = join_map[key]
                    query = query.join(join_model, condition)

                # Apply time filter
                if time_field and start_date:
                    time_column = base_model.c[time_field] if isinstance(base_model, db.Table) else getattr(base_model, time_field)
                    query = query.filter(time_column >= start_date)

                # Apply additional filters
                for field, condition in filter_conditions.items():
                    if field not in valid_fields[data_source]:
                        return json.dumps({
                            "response_text": "Invalid filter field",
                            "additional_data": {},
                            "error": "Data not valid",
                            "debug": f"Invalid filter field: {field}"
                        })
                    operator, value = condition.split(" ", 1)
                    column = base_model.c[field] if isinstance(base_model, db.Table) else getattr(base_model, field)
                    if operator == ">":
                        query = query.filter(column > value)
                    elif operator == "<":
                        query = query.filter(column < value)
                    elif operator == "=":
                        query = query.filter(column == value)

                query = query.group_by(group_by_column)
                results = query.all()
                output = [{"group": row[0], "value": row[1]} for row in results]

                # Map data to labels and values directly from query results
                labels = [str(item["group"]) for item in output]
                values = [item["value"] for item in output]

                # Validate data
                if not labels or len(labels) != len(values):
                    return json.dumps({
                        "response_text": "Invalid data: labels and values must be non-empty and have the same length",
                        "additional_data": {},
                        "error": "Data not valid"
                    })

                # Chart generation
                background_colors = []
                border_colors = []
                modern_colors = [
                    "rgba(30, 136, 229, 0.4)",  
                    "rgba(255, 87, 34, 0.4)",  
                    "rgba(0, 200, 83, 0.4)",    
                    "rgba(255, 193, 7, 0.4)",  
                    "rgba(171, 71, 188, 0.4)", 
                ]
                modern_border_colors = [
                    "rgba(30, 136, 229, 1)",
                    "rgba(255, 87, 34, 1)",
                    "rgba(0, 200, 83, 1)",
                    "rgba(255, 193, 7, 1)",
                    "rgba(171, 71, 188, 1)",
                ]
                for i in range(len(labels)):
                    background_colors.append(modern_colors[i % len(modern_colors)])
                    border_colors.append(modern_border_colors[i % len(modern_border_colors)])

                # Chart options
                options = {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "animation": {
                        "duration": 1000,
                        "easing": "easeOutQuart"
                    },
                    "plugins": {
                        "legend": {
                            "position": "top" if chart_type not in ["pie", "doughnut"] else "right",
                            "labels": {
                                "font": {"family": "Roboto", "size": 14},
                                "color": "#202124",
                                "padding": 15
                            }
                        },
                        "title": {
                            "display": True,
                            "text": title,
                            "font": {"family": "Roboto", "size": 18, "weight": "500"},
                            "color": "#202124",
                            "padding": {"top": 10, "bottom": 20}
                        },
                        "tooltip": {
                            "backgroundColor": "rgba(32, 33, 36, 0.9)",
                            "titleFont": {"family": "Roboto", "size": 14},
                            "bodyFont": {"family": "Roboto", "size": 12},
                            "cornerRadius": 4,
                            "caretSize": 6
                        }
                    }
                }

                if chart_type not in ["pie", "doughnut"]:
                    options["scales"] = {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": y_axis,
                                "font": {"family": "Roboto", "size": 14},
                                "color": "#202124"
                            },
                            "grid": {
                                "color": "rgba(0, 0, 0, 0.05)",
                                "borderColor": "#dadce0"
                            },
                            "ticks": {
                                "color": "#5f6368",
                                "font": {"family": "Roboto", "size": 12}
                            }
                        },
                        "x": {
                            "title": {
                                "display": True,
                                "text": x_axis,
                                "font": {"family": "Roboto", "size": 14},
                                "color": "#202124"
                            },
                            "grid": {
                                "display": False
                            },
                            "ticks": {
                                "color": "#5f6368",
                                "font": {"family": "Roboto", "size": 12}
                            }
                        }
                    }

                # Prepare response
                response_text = f"Preparing Chart.js {chart_type} chart for {data_source} data with title: {title}"
                additional_data = {
                    "chart_type": chart_type,
                    "data_source": data_source,
                    "chart_config": {
                        "type": chart_type,
                        "data": {
                            "labels": labels,
                            "datasets": [{
                                "label": y_axis,
                                "data": values,
                                "backgroundColor": background_colors,
                                "borderColor": border_colors,
                                "borderWidth": 2,
                                "borderRadius": 4 if chart_type == "bar" else 0,
                                "pointRadius": 4 if chart_type in ["line", "scatter"] else 0,
                                "pointHoverRadius": 6 if chart_type in ["line", "scatter"] else 0,
                                "tension": 0.4 if chart_type == "line" else 0
                            }]
                        },
                        "options": options
                    }
                }

                return json.dumps({
                    "response_text": response_text,
                    "additional_data": additional_data
                })

            except Exception as e:
                return json.dumps({
                    "response_text": "Failed to retrieve or generate chart",
                    "additional_data": {},
                    "error": "Operation failed",
                    "debug": f"Error: {str(e)}"
                })