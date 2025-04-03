import json
from app import create_app
from app.services.product_service import searchProduct, get_product_by_id
from app.services.review_service import get_reviews_by_embedding

class CustomerHandlers:
    @staticmethod
    def handle_search_product(args):
        query = args["query"]
        top_n = args.get("top_n", 5)
        app = create_app()
        with app.app_context():
            response = searchProduct(query, top_n)
        
        response.pop('query', None)
        
        products = response.get('top_products', [])

        modified_products = []
        for product in products:
            modified_product = product.copy() 
            modified_product.pop('images', None)
            modified_product.pop('product_id', None)
            modified_products.append(modified_product)

        
        return json.dumps({
            "response_text": json.dumps(modified_products), 
            "additional_data": {
                "products": products
            }
        })
    
    @staticmethod
    def handle_get_reviews_by_embedding(args):
        query_text = args["query_text"]
        product_id = args.get("product_id")
        product_name_or_description = args.get("product_name_or_description")
        
        
        if product_id:
            app = create_app()
            with app.app_context():
                reviews = get_reviews_by_embedding(query_text, product_id, top_k=3)
        elif product_name_or_description:
            app = create_app()
            with app.app_context():
                product = searchProduct(product_name_or_description, top_n=1)
            if not product or "top_products" not in product or not product["top_products"]:
                return json.dumps({"error": "No se encontró el producto."})
            
            product_id = product["top_products"][0]["product_id"]
            app = create_app()
            with app.app_context():
                reviews = get_reviews_by_embedding(query_text, product_id, top_k=1)
        else:
            return json.dumps({"error": "Faltan argumentos: se requiere product_id o product_name_or_description."})
        

        review_ids = [review.review_id for review in reviews] if reviews else []

        reviews_text = "\n".join([review.text for review in reviews]) if reviews else "No hay reviews disponibles."
        

        
        return json.dumps({
            "response_text": reviews_text,
            "additional_data": {
                "review_ids": review_ids
            }
        })