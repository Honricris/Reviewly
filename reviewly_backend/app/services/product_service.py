from app.models.product import Product
from app import db
from sqlalchemy import text
from sqlalchemy.orm import joinedload
from app.utils.model_loader import get_model
from app.models.productdetail import ProductDetail
from app.models.productfeature import ProductFeature
model = get_model()

def get_all_products(category=None, price_min=None, price_max=None, name=None, page=1, limit=43):
    if page is None:
        page = 1
    print(f"Inicio del método: category={category}, page={page}, limit={limit}")

    query = Product.query


    if name:
        query = query.filter(Product.title.ilike(f'%{name}%')) 

    if category:
        query = query.filter(Product.main_category == category)
        


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

def searchProduct(query: str, top_n=5):
    # Generar embedding para la frase de búsqueda
    #TODO Juntar consultas
    #TODO Diagrama con codigo.
    query_embedding = model.encode([query]).tolist()[0]  # Convertir a lista para usar en la consulta

    # 1. Buscar los 30 productos cuyo título coincida parcialmente y sumar puntos
    tle_matches = db.session.execute(
    text("""
            SELECT product_id, title, description,
                (SIMILARITY(title, :query) * 70 + 
                SIMILARITY(COALESCE(CAST(description AS TEXT), ''), :query) * 30) AS total_score
            FROM products
            WHERE SIMILARITY(title, :query) > 0.05
            OR SIMILARITY(COALESCE(CAST(description AS TEXT), ''), :query) > 0.05
            ORDER BY total_score DESC
            LIMIT 30
            """),
        {'query': query}
    ).fetchall()
    # Obtener los IDs de los 30 productos seleccionados
    top_product_ids = [row.product_id for row in tle_matches]

    if not top_product_ids:  # Si no hay coincidencias en título, devolver vacío
        return {
            "query": query,
            "top_products": []
        }

    # 2. Buscar en detalles de productos seleccionados y sumar puntos
    detail_scores = db.session.execute(
        text("""
        SELECT pd.product_id, 
               SUM(1 - (pd.detail_embedding <=> CAST(:query_embedding AS vector))) AS detail_score
        FROM product_details pd
        WHERE pd.product_id IN :product_ids
        GROUP BY pd.product_id
        """),
        {"query_embedding": query_embedding, "product_ids": tuple(top_product_ids)}
    ).fetchall()

    # 3. Buscar en características de productos seleccionados y sumar puntos
    feature_scores = db.session.execute(
        text("""
        SELECT pf.product_id, 
               SUM(1 - (pf.embedding <=> CAST(:query_embedding AS vector))) AS feature_score
        FROM product_features pf
        WHERE pf.product_id IN :product_ids
        GROUP BY pf.product_id
        """),
        {"query_embedding": query_embedding, "product_ids": tuple(top_product_ids)}
    ).fetchall()

    # 4. Sumar scores de título, detalles y características
    product_scores = {}

    # Sumar puntos por coincidencias en el título
    title_score_map = {}
    for row in tle_matches:
        product_id, title, description, title_score = row
        if product_id not in product_scores:
            product_scores[product_id] = 0
        product_scores[product_id] += title_score
        title_score_map[product_id] = title_score

    # Sumar puntos por detalles
    detail_score_map = {}
    for row in detail_scores:
        product_id, detail_score = row
        if product_id not in product_scores:
            product_scores[product_id] = 0
        product_scores[product_id] += detail_score
        detail_score_map[product_id] = detail_score

    # Sumar puntos por características
    feature_score_map = {}
    for row in feature_scores:
        product_id, feature_score = row
        if product_id not in product_scores:
            product_scores[product_id] = 0
        product_scores[product_id] += feature_score
        feature_score_map[product_id] = feature_score

    # 5. Ordenar por puntaje total y obtener los top_n productos
    sorted_products = sorted(product_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    product_ids = [product_id for product_id, _ in sorted_products]

    # 6. Obtener información de los productos ordenados
    products = Product.query.filter(Product.product_id.in_(product_ids)).all()

    # Construir respuesta con los puntajes detallados
    result = []
    for product in products:
        result.append({
            "product_id": product.product_id,
            "title": product.title,
            "main_category": product.main_category,
            "average_rating": product.average_rating,
            "rating_number": product.rating_number,
            "price": product.price,
            "store": product.store,
            "images": product.images,
            "scores": {
                "title_score": title_score_map.get(product.product_id, 0),
                "detail_score": detail_score_map.get(product.product_id, 0),
                "feature_score": feature_score_map.get(product.product_id, 0),
                "total_score": product_scores.get(product.product_id, 0)
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
                    # Generar embedding para la feature
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
    Elimina un producto existente en la base de datos.

    Args:
        product_id (int): ID del producto a eliminar.

    Returns:
        bool: `True` si el producto fue eliminado, `False` si no se encontró.
    """
    # Buscar el producto en la base de datos por su ID
    product = Product.query.get(product_id)

    if not product:
        return False

    db.session.delete(product)
    db.session.commit()

    return True



def get_all_categories():
    categories = Product.query.with_entities(Product.main_category).distinct().all()
    return [category[0] for category in categories]