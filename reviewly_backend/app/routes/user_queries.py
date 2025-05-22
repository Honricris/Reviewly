from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.models.user_query import UserQuery 
from app.models.user import User
from app import db
from datetime import datetime

api = Namespace('user', description='User related operations')

query_history_model = api.model('QueryHistory', {
    'id': fields.Integer(description='Query ID'),
    'query_text': fields.String(description='The query text'),
    'created_at': fields.DateTime(description='Timestamp of the query')
})

user_count_model = api.model('UserCount', {
    'total_users': fields.Integer(description='Total number of users')
})

new_query_model = api.model('NewQuery', {
    'query_text': fields.String(required=True, description='The query text to save'),
    'execution_time': fields.Float(required=False, description='Execution time in seconds')
})

execution_time_model = api.model('ExecutionTime', {
    'id': fields.Integer(description='Query ID'),
    'user_id': fields.Integer(description='User ID'),
    'query_text': fields.String(description='The query text'),
    'execution_time': fields.Float(description='Execution time in seconds'),
    'created_at': fields.DateTime(description='Timestamp of the query')
})

@api.route('/queries')
class UserQueries(Resource):
    @jwt_required()
    @api.marshal_list_with(query_history_model)
    def get(self):
        """Get the last 5 user queries"""
        current_user_id = get_jwt_identity()
        
        try:
            queries = UserQuery.query.filter_by(user_id=current_user_id)\
                                   .order_by(UserQuery.created_at.desc())\
                                   .limit(5)\
                                   .all()
            return queries, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @jwt_required()
    @api.expect(new_query_model)
    def post(self):
        """Save a user query to their history (keeps last 5 queries)"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        query_text = data.get('query_text')
        execution_time = data.get('execution_time')  
        
        if not query_text:
            return {"error": "No query_text provided"}, 400

        try:
            new_query = UserQuery(
                user_id=current_user_id, 
                query_text=query_text,
                execution_time=execution_time if execution_time is not None else None
            )
            db.session.add(new_query)
            
            query_count = UserQuery.query.filter_by(user_id=current_user_id).count()
            
            if query_count > 5:
                oldest_queries = UserQuery.query.filter_by(user_id=current_user_id)\
                                              .order_by(UserQuery.created_at.asc())\
                                              .limit(query_count - 5)\
                                              .all()
                for query in oldest_queries:
                    db.session.delete(query)
            
            db.session.commit()
            
            return {"status": "success", "message": "Query saved"}, 200
        
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        
@api.route('/count')
class UserCount(Resource):
    @jwt_required()
    @api.marshal_with(user_count_model)
    def get(self):
        """Get the total number of users"""
        try:
            total_users = User.query.count()
            return {"total_users": total_users}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@api.route('/execution-times')
class QueryExecutionTimes(Resource):
    @jwt_required()
    @api.marshal_list_with(execution_time_model)
    def get(self):
        """Get execution times for user queries between two timestamps"""
        current_user_id = get_jwt_identity()
        
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        if not start_time_str or not end_time_str:
            return {"error": "Both start_time and end_time parameters are required"}, 400

        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            if start_time >= end_time:
                return {"error": "start_time must be earlier than end_time"}, 400

            end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999999)

            print(f"Iniciando get execution times - start_date: {start_time}, end_date: {end_time}")

            queries = UserQuery.query.filter(
                UserQuery.created_at.between(start_time, end_time)
            ).order_by(UserQuery.created_at.asc()).all()

            return queries, 200

        except ValueError as ve:
            return {"error": "Invalid timestamp format. Use ISO format (e.g., 2023-01-01T00:00:00Z)"}, 400
        except Exception as e:
            return {"error": str(e)}, 500
        
@api.route('/<int:user_id>/queries')
class UserSpecificQueries(Resource):
    @jwt_required()
    @api.marshal_list_with(query_history_model)
    def get(self, user_id):
        """Get the last 5 queries for a specific user"""
        try:
            queries = UserQuery.query.filter_by(user_id=user_id)\
                                    .order_by(UserQuery.created_at.desc())\
                                    .limit(5)\
                                    .all()
            if not queries:
                return [], 200  
            return queries, 200
        except Exception as e:
            return {"error": str(e)}, 500