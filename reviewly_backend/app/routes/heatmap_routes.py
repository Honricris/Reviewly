from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from app import db
from datetime import datetime, timedelta
from app.services.heatmap_service import HeatmapService 
from flask_jwt_extended import jwt_required

api = Namespace('heatmap', description='Heatmap related operations')

heatmap_filter_model = api.model('HeatmapFilter', {
    'start_date': fields.Date(description='Fecha de inicio (YYYY-MM-DD)'),
    'end_date': fields.Date(description='Fecha de fin (YYYY-MM-DD)')
})

@api.route('/heatmap_data')
class HeatmapData(Resource):
    @api.expect(heatmap_filter_model, validate=False)
    @jwt_required()
    def get(self):
        data = request.args
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        try:
            start_date = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
            end_date = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
        except ValueError:
            return {"message": "Formato de fecha inválido. Use YYYY-MM-DD"}, 400

        heat_data = HeatmapService.get_heatmap_data(start_date, end_date)

        return jsonify(heat_data)