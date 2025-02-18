from flask_restx import Namespace, Resource, fields
from app.services.product_service import (
    get_all_products, get_product_by_id, create_product, update_product, delete_product, get_all_categories,searchProduct
)
from app.services.review_service import get_reviews_by_product
from flask import request

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

@api.route('/')
class ProductList(Resource):
    @api.param('name', 'Search term for product title', type=str) 
    @api.param('category', 'Category filter for products', type=str)
    @api.param('price_min', 'Minimum price filter for products', type=float)
    @api.param('price_max', 'Maximum price filter for products', type=float)
    @api.param('limit', 'Number of products to return', type=int, default=10)
    @api.param('page', 'Page number for pagination', type=int, default=1)
    def get(self):
        name = request.args.get('name')
        category = request.args.get('category')
        price_min = request.args.get('price_min', type=float)  
        price_max = request.args.get('price_max', type=float) 
        limit = request.args.get('limit', type=int)
        page = request.args.get('page', type=int)


        products = get_all_products(category=category, price_min=price_min, price_max=price_max, name=name, limit=limit, page=page)
        return products, 200

    @api.expect(product_model)
    def post(self):
        data = api.payload
        product = create_product(data)
        return product, 201

@api.route('/<int:id>')
class Product(Resource):
    @api.marshal_with(product_model)
    def get(self, id):
        product = get_product_by_id(id)
        if not product:
            return {"error": "Product not found"}, 404
        return product, 200

    @api.expect(product_model)
    def put(self, id):
        data = api.payload
        product = update_product(id, data)
        if not product:
            return {"error": "Product not found"}, 404
        return product, 200

    def delete(self, id):
        success = delete_product(id)
        if not success:
            return {"error": "Product not found"}, 404
        return {"message": "Product deleted"}, 200




product_search_model = api.model('ProductSearch', {
    'query': fields.String(required=True, description='Search query for products', example="Smartphone with good camera"),
    'top_n': fields.Integer(required=False, description='Number of top products to return', example=5, default=5)
})


@api.route('/search')
class ProductSearch(Resource):
    @api.expect(product_search_model)
    def post(self):
        data = request.json
        query = data.get('query')
        top_n = data.get('top_n', 5)
        
        if not query:
            return {"error": "Query parameter is required."}, 400
        
        result = searchProduct(query, top_n)
        return result, 200
    


@api.route('/categories')
class ProductCategories(Resource):
    def get(self):
        categories = get_all_categories() 
        return {"categories": categories}, 200
    
@api.route('/<int:id>/reviews')
class ProductReviews(Resource):
    @api.param('page', 'Page number for review pagination', type=int, default=1)
    @api.param('limit', 'Number of reviews to return', type=int, default=10)
    def get(self, id):
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
