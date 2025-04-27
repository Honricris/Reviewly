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
    @api.expect(api.model('NewQuery', {
        'query_text': fields.String(required=True, description='The query text to save')
    }))
    def post(self):
        """Save a user query to their history (keeps last 5 queries)"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        query_text = data.get('query_text')
        
        if not query_text:
            return {"error": "No query_text provided"}, 400

        try:
            new_query = UserQuery(user_id=current_user_id, query_text=query_text)
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