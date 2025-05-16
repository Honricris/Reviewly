import json
from app import create_app
from app.services.user_service import UserService
import time
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
    def handle_generate_chart(args):
        chart_type = args.get("chart_type")
        data_source = args.get("data_source")
        x_axis = args.get("x_axis")
        y_axis = args.get("y_axis")
        title = args.get("title")
        data = args.get("data")

        time.sleep(1)


        if not all([chart_type, data_source, x_axis, y_axis, title, data]):
            return json.dumps({"error": "All parameters (chart_type, data_source, x_axis, y_axis, title, data) are required"})

        if not isinstance(data, dict) or "labels" not in data or "values" not in data:
            return json.dumps({"error": "The 'data' parameter must be an object with 'labels' and 'values' arrays"})
        
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not isinstance(labels, list) or not isinstance(values, list):
            return json.dumps({"error": "'labels' and 'values' must be arrays"})
        
        if len(labels) != len(values) or not labels:
            return json.dumps({"error": "'labels' and 'values' arrays must be non-empty and have the same length"})

        background_colors = []
        border_colors = []
        default_colors = [
            "rgba(75, 192, 192, 0.2)",  
            "rgba(255, 99, 132, 0.2)",  
            "rgba(54, 162, 235, 0.2)",  
            "rgba(255, 206, 86, 0.2)",  
            "rgba(153, 102, 255, 0.2)"  
        ]
        default_border_colors = [
            "rgba(75, 192, 192, 1)",
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(153, 102, 255, 1)"
        ]

        for i in range(len(labels)):
            background_colors.append(default_colors[i % len(default_colors)])
            border_colors.append(default_border_colors[i % len(default_border_colors)])

        options = {
            "responsive": True,
            "plugins": {
                "legend": {"position": "top"},
                "title": {
                    "display": True,
                    "text": title
                }
            }
        }

        if chart_type not in ["pie", "doughnut"]:
            options["scales"] = {
                "y": {
                    "beginAtZero": True,
                    "title": {"display": True, "text": y_axis}
                },
                "x": {
                    "title": {"display": True, "text": x_axis}
                }
            }

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
                        "borderWidth": 1
                    }]
                },
                "options": options
            }
        }

        return json.dumps({
            "response_text": response_text,
            "additional_data": additional_data
        })