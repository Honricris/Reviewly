from app.models.product import Product
from app import db
from sqlalchemy.orm import joinedload



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
    print(f"Total de productos encontrados: {total_products}")
    total_pages = (total_products + limit - 1) // limit  
    print(f"Total de páginas calculadas: {total_pages}")

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    print(f"Offset aplicado: {offset}, límite: {limit}")

    try:
        products = query.options(joinedload(Product.reviews)).all()
        print(f"Productos obtenidos: {len(products)}")
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return {"error": "Error al obtener productos"}

    result = []
    for i, p in enumerate(products):
        try:
            large_images = [img.get("large") for img in p.images if isinstance(img, dict) and "large" in img] if p.images else []
            print(f"Producto {i} procesado: {p.product_id}")

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

    print(f"Resultados procesados: {len(result)}")

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
    # Buscar el producto en la base de datos por su ID
    product = Product.query.get(product_id)

    if not product:
        return None

    # Convertir el producto a un formato serializable
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
def create_product(data: dict) -> dict:
    """
    Crea uno o varios productos en la base de datos.
    
    Args:
        data (dict): Diccionario con los datos de los productos. 
                     Puede ser un solo producto (dict) o una lista de productos (list[dict]).
    
    Returns:
        dict: Información sobre los productos creados.
    """
    created_products = []

    # Asegurar que se puede procesar tanto un solo producto como múltiples productos
    if isinstance(data, dict):
        data = [data]

    for product_data in data:
        # Crear instancia del producto
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
        created_products.append(product)

    # Confirmar los cambios en la base de datos
    db.session.commit()

    # Retornar los productos creados en formato serializable
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