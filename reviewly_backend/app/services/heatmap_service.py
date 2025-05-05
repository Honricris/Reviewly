from app.models.LoginLog import LoginLog
from app import db
from datetime import datetime
from collections import Counter
import maxminddb

class HeatmapService:
    GEO_DB_PATH = 'app/data/GeoLite2-City.mmdb' 
    try:
        GEO_READER = maxminddb.open_database(GEO_DB_PATH)
    except Exception as e:
        GEO_READER = None

    @staticmethod
    def geolocate_ip(ip_address):
        if not HeatmapService.GEO_READER:
            return None

        try:
            data = HeatmapService.GEO_READER.get(ip_address)
            if data and 'location' in data and 'latitude' in data['location'] and 'longitude' in data['location']:
                return {
                    'latitude': data['location']['latitude'],
                    'longitude': data['location']['longitude']
                }
            return None
        except Exception as e:
            return None

    @staticmethod
    def get_heatmap_data(start_date=None, end_date=None):
        
        query = db.session.query(LoginLog).filter(
            LoginLog.ip_address.isnot(None),
            LoginLog.ip_address.notin_(['127.0.0.1', '::1'])
        )
        if start_date:
            query = query.filter(LoginLog.login_at >= start_date)
        if end_date:
            query = query.filter(LoginLog.login_at <= end_date)

        logs = query.all()
        print(f"Se encontraron {len(logs)} registros de login")

        geo_counts = Counter()
        for log in logs:
            geo_data = HeatmapService.geolocate_ip(log.ip_address)
            if geo_data and geo_data['latitude'] and geo_data['longitude']:
                lat = round(geo_data['latitude'], 2)
                lng = round(geo_data['longitude'], 2)
                geo_counts[(lat, lng)] += 1
            else:
                print(f"No se pudieron obtener coordenadas para {log.ip_address}")

        heat_data = [
            {'lat': lat, 'lng': lng, 'weight': count}
            for (lat, lng), count in geo_counts.items()
        ]


        return heat_data