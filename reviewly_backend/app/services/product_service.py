from app.models.product import Product
from app import db
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from app.utils.model_loader import get_model
from app.models.productdetail import ProductDetail
from app.models.productfeature import ProductFeature
from app.models.review import Review 
model = get_model()

def get_all_products(category=None, price_min=None, price_max=None, name=None,store=None, page=1, limit=43):
    if page is None:
        page = 1
    print(f"Inicio del método: category={category}, page={page}, limit={limit}")

    query = Product.query


    if name:
        query = query.filter(Product.title.ilike(f'%{name}%')) 

    if category:
        query = query.filter(Product.main_category == category)
        

    if store:
            query = query.filter(Product.store.ilike(f'%{store}%'))
            
    if price_min is not None:
        query = query.filter(Product.price >= price_min)


    if price_max is not None:
        query = query.filter(Product.price <= price_max)


    total_products = query.count()
    total_pages = (total_products + limit - 1) // limit  

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    try:
        products = query.options(joinedload(Product.reviews)).all()
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return {"error": "Error al obtener productos"}

    result = []
    for i, p in enumerate(products):
        try:
            large_images = [img.get("large") for img in p.images if isinstance(img, dict) and "large" in img] if p.images else []

            result.append({
                "product_id": p.product_id,
                "title": p.title,
                "main_category": p.main_category,
                "average_rating": p.average_rating,
                "rating_number": p.rating_number,
                "price": p.price,
                "images": large_images, 
                "store": p.store
            })
        except Exception as e:
            print(f"Error procesando producto {i}: {e}")


    response = {
        "products": result,
        "total_products": total_products,
        "total_pages": total_pages,
        "current_page": page
    }
    print("Respuesta generada correctamente.")
    return response



def get_product_by_id(product_id: int) -> dict:
    """
    Obtiene un producto por su ID.

    Args:
        product_id (int): ID del producto.

    Returns:
        dict: Diccionario con la información del producto en formato JSON o `None` si no se encuentra.
    """
    product = Product.query.get(product_id)

    if not product:
        return None

    return {
        "product_id": product.product_id,
        "title": product.title,
        "main_category": product.main_category,
        "average_rating": product.average_rating,
        "rating_number": product.rating_number,
        "price": product.price,
        "features": product.features,
        "description": product.description,
        "resume_review": product.resume_review,
        "images": product.images,
        "videos": product.videos,
        "store": product.store,
        "categories": product.categories,
        "details": product.details,
        "parent_asin": product.parent_asin,
        "bought_together": product.bought_together,
        "amazon_link": product.amazon_link
    }

def searchProduct(query: str, top_n=5, category: str = None, min_price: float = None, max_price: float = None):
    query_embedding = model.encode([query]).tolist()[0] 
    
    filters = ""
    params = {'query': query, 'query_embedding': query_embedding, 'top_n': top_n}
    
    if category:
        filters += " AND main_category = :category"
        params['category'] = category
    
    if min_price is not None:
        filters += " AND price >= :min_price"
        params['min_price'] = min_price
    
    if max_price is not None:
        filters += " AND price <= :max_price"
        params['max_price'] = max_price
    
    combined_query = db.session.execute(
        text(f"""
        WITH title_matches AS (
            SELECT product_id, title, description, main_category, price,
                   (SIMILARITY(title, :query) * 70 + 
                   SIMILARITY(COALESCE(CAST(description AS TEXT), ''), :query) * 30) AS title_score
            FROM products
            WHERE (SIMILARITY(title, :query) > 0.05
            OR SIMILARITY(COALESCE(CAST(description AS TEXT), ''), :query) > 0.05)
            {filters}
            ORDER BY title_score DESC
            LIMIT 30
        ),
        detail_scores AS (
            SELECT pd.product_id, 
                   SUM(1 - (pd.detail_embedding <=> CAST(:query_embedding AS vector))) AS detail_score
            FROM product_details pd
            WHERE pd.product_id IN (SELECT product_id FROM title_matches)
            GROUP BY pd.product_id
        ),
        feature_scores AS (
            SELECT pf.product_id, 
                   SUM(1 - (pf.embedding <=> CAST(:query_embedding AS vector))) AS feature_score
            FROM product_features pf
            WHERE pf.product_id IN (SELECT product_id FROM title_matches)
            GROUP BY pf.product_id
        ),
        product_features AS (
            SELECT pf.product_id, 
                   JSON_AGG(pf.feature) AS features  -- Agrupa las características en un JSON
            FROM product_features pf
            WHERE pf.product_id IN (SELECT product_id FROM title_matches)
            GROUP BY pf.product_id
        )
        SELECT tm.product_id, tm.title, tm.description, tm.main_category, tm.price,
               tm.title_score, 
               COALESCE(ds.detail_score, 0) AS detail_score,
               COALESCE(fs.feature_score, 0) AS feature_score,
               (tm.title_score * 0.7 + COALESCE(ds.detail_score, 0) * 0.2 + COALESCE(fs.feature_score, 0) * 0.1) AS total_score,
               pf.features  -- Incluir las características
        FROM title_matches tm
        LEFT JOIN detail_scores ds ON tm.product_id = ds.product_id
        LEFT JOIN feature_scores fs ON tm.product_id = fs.product_id
        LEFT JOIN product_features pf ON tm.product_id = pf.product_id
        ORDER BY total_score DESC
        LIMIT :top_n
        """),
        params
    ).fetchall()
    
    if not combined_query: 
        return {
            "query": query,
            "top_products": []
        }
    
    product_ids = [row.product_id for row in combined_query]
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()
    
    result = []
    for product in products:
        large_images = [img.get("large") for img in product.images if isinstance(img, dict) and "large" in img] if product.images else []
        
        features = next((row.features for row in combined_query if row.product_id == product.product_id), [])
        
        result.append({
            "product_id": product.product_id,
            "title": product.title,
            "description": product.description,  
            "main_category": product.main_category,
            "average_rating": product.average_rating,
            "rating_number": product.rating_number,
            "price": product.price,
            "store": product.store,
            "images": large_images,
            "features": features,  
            "scores": {
                "title_score": next((row.title_score for row in combined_query if row.product_id == product.product_id), 0),
                "detail_score": next((row.detail_score for row in combined_query if row.product_id == product.product_id), 0),
                "feature_score": next((row.feature_score for row in combined_query if row.product_id == product.product_id), 0),
                "total_score": next((row.total_score for row in combined_query if row.product_id == product.product_id), 0)
            }
        })
    
    return {
        "query": query,
        "top_products": result
    }


def create_product(data: dict) -> dict:
    """
    Crea uno o varios productos en la base de datos junto con sus detalles y características.
    
    Args:
        data (dict): Diccionario con los datos de los productos. 
                     Puede ser un solo producto (dict) o una lista de productos (list[dict]).
    
    Returns:
        dict: Información sobre los productos creados.
    """
    created_products = []

    if isinstance(data, dict):
        data = [data]

    for product_data in data:
        title = product_data.get("title")

        existing_product = Product.query.filter_by(title=title).first()
        if existing_product:
            return {"error": f"El producto con título '{title}' ya existe en la base de datos."}, 409

        product = Product(
            title=product_data.get("title"),
            main_category=product_data.get("main_category"),
            average_rating=product_data.get("average_rating"),
            rating_number=product_data.get("rating_number", 0),
            features=product_data.get("features"),
            description=product_data.get("description"),
            price=product_data.get("price"),
            resume_review=product_data.get("resume_review"),
            images=product_data.get("images"),
            videos=product_data.get("videos"),
            store=product_data.get("store"),
            categories=product_data.get("categories"),
            details=product_data.get("details"),
            parent_asin=product_data.get("parent_asin"),
            bought_together=product_data.get("bought_together"),
            amazon_link=product_data.get("amazon_link")
        )

        product.generate_amazon_link()

        db.session.add(product)
        db.session.flush()  

        # Añadir ProductDetails
        if product.details:
            for key, value in product.details.items():
                detail_text = f"{key}: {value}"
                
                try:
                    embedding = model.encode([detail_text])[0]  

                    new_detail = ProductDetail(
                        product_id=product.product_id,
                        detail=detail_text,
                        detail_embedding=embedding.tolist()
                    )
                    db.session.add(new_detail)
                    print(f"Detalle añadido para producto ID: {product.product_id}")

                except Exception as embed_error:
                    print(f"Error al generar embedding para producto ID: {product.product_id}, detalle: {detail_text}")
                    print(f"Detalles del error: {embed_error}")
                    continue  

        # Añadir ProductFeatures
        if product.features:
            for feature in product.features:
                try:
                    embedding = model.encode([feature])[0]  

                    new_feature = ProductFeature(
                        product_id=product.product_id,
                        feature=feature,
                        embedding=embedding.tolist()  
                    )
                    db.session.add(new_feature)
                    print(f"Feature añadida para producto ID: {product.product_id}")

                except Exception as embed_error:
                    print(f"Error al generar embedding para producto ID: {product.product_id}, feature: {feature}")
                    print(f"Detalles del error: {embed_error}")
                    continue  

        created_products.append(product)

    try:
        db.session.commit()
    except Exception as commit_error:
        print(f"Error al guardar productos: {commit_error}")
        db.session.rollback()
        return {"error": "No se pudo crear el producto."}

    return {
        "created_products": [
            {
                "product_id": p.product_id,
                "title": p.title,
                "main_category": p.main_category,
                "average_rating": p.average_rating,
                "rating_number": p.rating_number,
                "price": p.price
            } for p in created_products
        ]
    }


def update_product(product_id: int, data: dict) -> dict:
    """
    Actualiza un producto existente en la base de datos.

    Args:
        product_id (int): ID del producto a actualizar.
        data (dict): Diccionario con los datos actualizados.

    Returns:
        dict: Información del producto actualizado o `None` si no se encuentra.
    """
    # Buscar el producto en la base de datos por su ID
    product = Product.query.get(product_id)

    if not product:
        return None

    # Actualizar los campos del producto
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)

    db.session.commit()

    # Retornar el producto actualizado en formato serializable
    return {
        "product_id": product.product_id,
        "title": product.title,
        "main_category": product.main_category,
        "average_rating": product.average_rating,
        "rating_number": product.rating_number,
        "price": product.price,
        "features": product.features,
        "description": product.description,
        "resume_review": product.resume_review,
        "images": product.images,
        "videos": product.videos,
        "store": product.store,
        "categories": product.categories,
        "details": product.details,
        "parent_asin": product.parent_asin,
        "bought_together": product.bought_together,
        "amazon_link": product.amazon_link
    }

def delete_product(product_id: int) -> bool:
    """
    Elimina un producto existente en la base de datos junto con sus detalles, características y reseñas asociadas.

    Args:
        product_id (int): ID del producto a eliminar.

    Returns:
        bool: `True` si el producto y sus datos asociados fueron eliminados, `False` si no se encontró el producto.
    """
    # Buscar el producto en la base de datos por su ID
    product = Product.query.get(product_id)

    if not product:
        return False

    try:
        ProductDetail.query.filter_by(product_id=product_id).delete()

        ProductFeature.query.filter_by(product_id=product_id).delete()

        Review.query.filter_by(product_id=product_id).delete()

        db.session.delete(product)

        db.session.commit()

        return True

    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar el producto y sus datos asociados: {e}")
        return False


def get_all_categories():
    categories = Product.query.with_entities(Product.main_category).distinct().all()
    return [category[0] for category in categories]


def autocomplete_products(search_term: str, limit: int = 3) -> list:
    """
    Busca productos que coincidan con el término de búsqueda para autocompletar.
    
    Args:
        search_term (str): Texto parcial para buscar coincidencias
        limit (int): Número máximo de sugerencias a devolver
        
    Returns:
        list: Lista de productos sugeridos
    """
    if not search_term or len(search_term.strip()) < 2:
        return []
    
    products = Product.query.filter(
        Product.title.ilike(f'%{search_term}%')
    ).order_by(
        Product.rating_number.desc()  
    ).limit(limit).all()
    
    suggestions = []
    for product in products:
        suggestions.append({
            "product_id": product.product_id,
            "title": product.title,
        })
    
    return suggestions