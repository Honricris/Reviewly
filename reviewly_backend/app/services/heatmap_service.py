from app.models.LoginLog import LoginLog
from app import db
from datetime import datetime
from collections import Counter
import requests
from sqlalchemy.sql import func

class HeatmapService:
    @staticmethod
    def geolocate_ip(ip_address):
        try:
            print(f"Geolocalizando IP: {ip_address}")
            response = requests.get(f"http://ip-api.com/json/{ip_address}")
            data = response.json()
            print(f"Respuesta de ip-api para {ip_address}: {data}")
            if data['status'] == 'success':
                return {
                    'latitude': data['lat'],
                    'longitude': data['lon']
                }
            print(f"Geolocalización fallida para {ip_address}: {data.get('message', 'No success')}")
            return None
        except Exception as e:
            print(f"Error al geolocalizar {ip_address}: {str(e)}")
            return None

    @staticmethod
    def get_heatmap_data(start_date=None, end_date=None):
        print(f"Iniciando get_heatmap_data - start_date: {start_date}, end_date: {end_date}")
        
        query = db.session.query(LoginLog).filter(LoginLog.ip_address.isnot(None))
        if start_date:
            query = query.filter(LoginLog.login_at >= start_date)
        if end_date:
            query = query.filter(LoginLog.login_at <= end_date)

        logs = query.all()
        print(f"Total de logs encontrados: {len(logs)}")
        print(f"IPs de los logs: {[log.ip_address for log in logs]}")

        geo_counts = Counter()
        for log in logs:
            geo_data = HeatmapService.geolocate_ip(log.ip_address)
            if geo_data and geo_data['latitude'] and geo_data['longitude']:
                lat = round(geo_data['latitude'], 2)
                lng = round(geo_data['longitude'], 2)
                geo_counts[(lat, lng)] += 1
                print(f"Coordenadas para {log.ip_address}: ({lat}, {lng})")

        heat_data = [
            {'lat': lat, 'lng': lng, 'weight': count}
            for (lat, lng), count in geo_counts.items()
        ]
        print(f"Datos de heatmap generados: {len(heat_data)} puntos")
        print(f"Heatmap data: {heat_data}")

        return heat_data