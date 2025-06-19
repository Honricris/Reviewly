from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from flask import request
from app.models.product import Product
from app.services.product_service import (
    get_all_products, get_product_by_id, create_product, update_product, 
    delete_product, get_all_categories, searchProduct, autocomplete_products, 
    get_product_count, get_product_favorite_count, get_most_favorited_products
)
from app.services.review_service import get_reviews_by_product
from datetime import datetime

api = Namespace('products', description='Product related operations')

product_model = api.model('Product', {
    'product_id': fields.Integer(description='Product ID', example=1),
    'title': fields.String(required=True, description='Title of the product', example="Smartphone XYZ"),
    'main_category': fields.String(required=True, description='Main category of the product', example="Electronics"),
    'average_rating': fields.Float(description='Average rating of the product', example=4.5),
    'rating_number': fields.Integer(required=True, description='Number of ratings', example=200),
    'features': fields.Raw(description='List of product features', example={"color": "black", "size": "6 inches"}),
    'description': fields.Raw(description='Description of the product', example={"short": "High-quality smartphone", "long": "This smartphone has all the latest features"}),
    'price': fields.Float(description='Price of the product', example=599.99),
    'resume_review': fields.String(description='Summary of product reviews', example="Great product, highly recommended."),
    'images': fields.Raw(description='List of images', example=["image1.jpg", "image2.jpg"]),
    'videos': fields.Raw(description='List of videos', example=["video1.mp4", "video2.mp4"]),
    'store': fields.String(description='Store name', example="Amazon"),
    'categories': fields.Raw(description='Categories of the product', example=["Smartphones", "Electronics"]),
    'details': fields.Raw(description='Additional details of the product', example={"brand": "XYZ", "battery_life": "12 hours"}),
    'parent_asin': fields.String(description='Parent ASIN if any', example="B08J6F174Z"),
    'asin': fields.String(description='Amazon ASIN', example="B08R29V9FQ"),
    'bought_together': fields.Raw(description='Products bought together', example=[{"asin": "B08V4V1N4F", "title": "Smartphone case"}]),
    'amazon_link': fields.String(description='Amazon link of the product', example="https://www.amazon.com/dp/B08R29V9FQ"),
    'created_at': fields.DateTime(description='Product creation time', example="2023-12-01T12:00:00Z")
})

autocomplete_model = api.model('Autocomplete', {
    'search_term': fields.String(required=True, description='Search term used for autocomplete', example="smart"),
    'suggestions': fields.List(fields.Nested(api.model('Suggestion', {
        'product_id': fields.Integer(description='Product ID'),
        'title': fields.String(description='Product title'),
        'main_category': fields.String(description='Product category'),
        'price': fields.Float(description='Product price')
    })))
})

@api.route('/')
class ProductList(Resource):
    @jwt_required()
    def get(self):
        """List products with filters"""
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category')
        name = request.args.get('name')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        store = request.args.get('store')
        min_rating = request.args.get('min_rating', type=float)
        min_favorites = request.args.get('min_favorites', type=int)
        include_favorites = request.args.get('include_favorites', 'false').lower() == 'true'

        try:
            response = get_all_products(
                category=category,
                name=name,
                price_min=price_min,
                price_max=price_max,
                store=store,
                page=page,
                limit=limit,
                include_favorites=include_favorites
            )
            return response, 200
        except Exception as e:
            return {"error": str(e)}, 500

    @api.expect(product_model)
    @jwt_required()
    def post(self):
        """Create a new product"""
        data = request.json
        try:
            product = create_product(data)
            if "error" in product:
                return product, 409
            return product, 201
        except Exception as e:
            return {"error": str(e)}, 400

@api.route('/<int:id>')
class Product(Resource):
    @api.marshal_with(product_model)
    @jwt_required()
    def get(self, id):
        """Get a product by ID"""
        product = get_product_by_id(id)
        if not product:
            return {"error": "Product not found"}, 404
        return product, 200

    @api.expect(product_model)
    @jwt_required()
    def put(self, id):
        """Update a product by ID"""
        data = api.payload
        product = update_product(id, data)
        if not product:
            return {"error": "Product not found"}, 404
        return product, 200

    @jwt_required()
    def delete(self, id):
        """Delete a product by ID"""
        success = delete_product(id)
        if not success:
            return {"error": "Product not found"}, 404
        return {"message": "Product deleted"}, 200

product_search_model = api.model('ProductSearch', {
    'query': fields.String(required=True, description='Search query for products', example="Smartphone with good camera"),
    'top_n': fields.Integer(required=False, description='Number of top products to return', example=5, default=5),
    'category': fields.String(description='Main category of the product (e.g., electronics, clothing, books). Optional.'),
    'min_price': fields.Float(description='Minimum price filter for the search results. Optional.'),
    'max_price': fields.Float(description='Maximum price filter for the search results. Optional.')
})

@api.route('/search')
class ProductSearch(Resource):
    @api.expect(product_search_model)
    @jwt_required()
    def post(self):
        """Search products by query"""
        data = request.json
        query = data.get('query')
        top_n = data.get('top_n', 5)
        category = data.get('category')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if not query:
            return {"error": "Query parameter is required."}, 400
        
        result = searchProduct(query, top_n, category, min_price, max_price)
        return result, 200

@api.route('/categories')
class ProductCategories(Resource):
    @jwt_required()
    def get(self):
        """Get all product categories"""
        categories = get_all_categories()
        return {"categories": categories}, 200

favorite_count_model = api.model('FavoriteCount', {
    'favoriteCount': fields.Integer(description='Number of users who favorited the product')
})

@api.route('/<int:product_id>/favorite-count')
class ProductFavoriteCount(Resource):
    @jwt_required()
    @api.marshal_with(favorite_count_model)
    def get(self, product_id):
        """Get the number of users who favorited a product"""
        try:
            count = get_product_favorite_count(product_id)
            return {'favoriteCount': count}, 200
        except Exception as e:
            return {"error": str(e)}, 500

@api.route('/<int:id>/reviews')
class ProductReviews(Resource):
    @api.param('page', 'Page number for review pagination', type=int, default=1)
    @api.param('limit', 'Number of reviews to return', type=int, default=10)
    @jwt_required()
    def get(self, id):
        """Get reviews for a product"""
        page = int(request.args.get('page', 1))
        per_page = 10
        offset = (page - 1) * per_page
        result = get_reviews_by_product(id, limit=per_page, offset=offset)
        reviews, total_reviews = result

        if not reviews:
            return {
                "error": "No reviews found for this product.",
                "page": page,
                "per_page": per_page
            }, 404

        return {
            "reviews": reviews,
            "total_reviews": total_reviews,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_reviews + per_page - 1) // per_page
        }, 200

@api.route('/autocomplete')
class ProductAutocomplete(Resource):
    @api.doc(params={
        'term': 'Partial search term to get suggestions for (min 2 characters)',
        'limit': 'Maximum number of suggestions to return (default 3, max 10)'
    })
    @api.marshal_with(autocomplete_model)
    @jwt_required()
    def get(self):
        """Autocomplete product search"""
        search_term = request.args.get('term', '').strip()
        limit = min(int(request.args.get('limit', 3)), 10)
        
        if len(search_term) < 2:
            return {
                "search_term": search_term,
                "suggestions": []
            }, 200
        
        suggestions = autocomplete_products(search_term, limit)
        
        return {
            "search_term": search_term,
            "suggestions": suggestions
        }, 200

product_count_model = api.model('ProductCount', {
    'total_products': fields.Integer(description='Total number of products')
})

@api.route('/count')
class ProductCount(Resource):
    @jwt_required()
    @api.marshal_with(product_count_model)
    def get(self):
        """Get the total number of products"""
        try:
            total_products = get_product_count()
            return {"total_products": total_products}, 200
        except Exception as e:
            return {"error": str(e)}, 500

most_favorited_input_model = api.model('MostFavoritedInput', {
    'start_date': fields.String(required=True, description='Fecha de inicio en formato YYYY-MM-DD', example='2025-01-01'),
    'end_date': fields.String(required=True, description='Fecha de fin en formato YYYY-MM-DD', example='2025-05-01'),
    'limit': fields.Integer(required=False, description='Número máximo de productos a devolver', example=10, default=10)
})

most_favorited_model = api.model('MostFavorited', {
    'product_id': fields.Integer(description='ID del producto', example=1),
    'favorite_count': fields.Integer(description='Número de veces que el producto fue marcado como favorito', example=50)
})

@api.route('/most-favorited')
class MostFavoritedProducts(Resource):
    @api.expect(most_favorited_input_model)
    @jwt_required()
    @api.marshal_list_with(most_favorited_model)
    def post(self):
        """Gets the IDs of the most favorited products within a date range"""
        data = request.json
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        limit = data.get('limit', 10)

        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return {"error": "Formato de fecha inválido. Use YYYY-MM-DD."}, 400

        try:
            result = get_most_favorited_products(start_date, end_date, limit)
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500