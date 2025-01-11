# Reviewly

## Descripción del proyecto

### El Problema
El proceso de compra en línea suele ser tedioso y confuso, ya que los usuarios deben investigar múltiples reseñas y comparar productos por su cuenta. Esto puede ser abrumador y llevar mucho tiempo.

### ¿Qué hace la app?
Este proyecto consiste en un chatbot que actúa como dependiente, simplificando el proceso de compra. El chatbot puede en esta v0:
1. **Guiarnos sobre las carácterísticas del producto**
   - **Funcionalidad**: Podemos hablar en lenguaje natural sobre las características del producto.
   - **Sistema**: Generación Aumentada por Recuperación.

#### Futuras características
1. **Análisis de sentimientos (Modelo propio)**
   - **Funcionalidad**: Clasifica sentimientos (positivo/negativo/neutral) en reseñas.
   - **Sistema**: Clasificador entrenado sobre dataset de Amazon.

2. **Generación de etiquetas (LLM + clustering)**
   - **Funcionalidad**: Detecta temas clave (problemas/puntos positivos).
   - **Sistema**: Embeddings + clustering (modelo propio o preentrenado).

3. **Reseñas resumen (LLM)**
   - **Funcionalidad**: Crea un resumen con quejas y puntos positivos.
   - **Sistema**: LLM con prompts o ajuste fino.

4. **Comparación de productos**
   - **User Input**:
     - "How does [product name] compare to [product name]?"
     - "Which product has better reviews, [product name] or [product name]?"
     - "I’d like to know which is more recommended between [product name] and [product name]."
   - **Expected Output**: 
     - Una comparación directa basada en calificaciones, palabras clave de reseñas y características destacadas.

5. **Productos destacados en una categoría**
   - **User Input**:
     - "What are the best-selling products in [category name]?"
     - "Recommend me a top product in [category name]."
     - "Which product has the best reviews in [category name]?"
   - **Expected Output**: 
     - Una lista de productos más vendidos o mejor valorados con información breve sobre su popularidad.


## Objetivos

Este proyecto fue concebido con varios objetivos principales, muchos de los cuales ya se han logrado en el breve plazo de 3 semanas de desarrollo:

1. **Aprender React**  
   - Explorar y desarrollar habilidades en React para construir interfaces de usuario interactivas y modernas.  
   - Aprender a usar **Material UI** para el diseño y estilo de botones, así como otros componentes, facilitando la creación de una interfaz consistente y profesional.  
   - Objetivo cumplido: La aplicación utiliza React y Material UI como base para su interfaz.

2. **Aprender sobre Modelos LLM e Inteligencia Artificial**  
   - Entender los conceptos fundamentales de los modelos de lenguaje grande (LLM) y cómo aplicarlos a tareas específicas.  
   - Implementar un sistema de Generación Aumentada por Recuperación (RAG) que combina:  
     - **Modelos de embedding** para representación semántica de datos.  
     - **Bases de datos vectoriales** para realizar búsquedas rápidas y precisas en grandes volúmenes de información.  
     - **Generación de respuestas** basada en las reseñas disponibles, asegurando que las respuestas sean relevantes y contextuales.  
   - Objetivo cumplido: El sistema de RAG está implementado, demostrando un aprendizaje profundo en estas áreas.

Este proyecto ha servido como una plataforma de aprendizaje integral para tecnologías modernas de frontend e inteligencia artificial.  


## Arquitectura del sistema

### Arquitectura general
El sistema se compone de las siguientes partes principales:

1. **Frontend**  
   - Desarrollado en **React**, ofreciendo una interfaz de usuario interactiva y moderna.

2. **Backend**  
   - Implementado en **Python** utilizando el framework **Flask** para gestionar la lógica del negocio y servir datos al frontend.

3. **Origen de datos**  
   - Los datos de reseñas provienen del repositorio público [Amazon Reviews 2023](https://amazon-reviews-2023.github.io/).  
   - Estos datos han sido procesados mediante scripts y cargados en la base de datos, concretamente los de appliances en esta v0.

4. **Almacenamiento**  
   - Base de datos **PostgreSQL** con la extensión **pgvector** para gestionar datos vectoriales, facilitando la búsqueda semántica eficiente.

5. **LLM y servicios de IA**  
   - Utilización de **EdenAI** para el acceso a modelos LLM como GPT-4o mini, encargado de la generación de respuestas.
   - Uso del modelo stella_en_1.5B_v5 en local para la generación de embeddings de reseñas y querys. Este junto con otros modelos se encuentran en la página de [huggingface](https://huggingface.co/spaces/mteb/leaderboard).

---

### Arquitectura de IA: Implementación de RAG (Generación Aumentada por Recuperación)
El flujo del sistema RAG es el siguiente:

1. **Consulta del usuario**  
   - El usuario realiza una consulta desde el frontend.

2. **Transformación de la consulta**  
   - El frontend envía la consulta al backend, donde se procesa con un modelo de **embedding** local para transformarla en un vector.

3. **Búsqueda semántica**  
   - El backend realiza una consulta en la base de datos PostgreSQL (con extensión pgvector) para recuperar las reseñas más relevantes a la consulta del usuario.

4. **Generación de respuesta**  
   - Las reseñas recuperadas se envían al modelo LLM, que genera una respuesta basada en la información contextual proporcionada por las reseñas.

5. **Respuesta al usuario**  
   - El backend devuelve la respuesta generada al frontend, donde se muestra al usuario en un formato amigable.

---

Este diseño garantiza un flujo eficiente y modular, combinando tecnologías modernas de frontend, backend, bases de datos y modelos de inteligencia artificial.  


## Instrucciones de instalación y despliegue

### Requisitos previos


Antes de comenzar, necesitas obtener un API token y la URL para configurar el archivo `.env`. Estos detalles pueden ser obtenidos en el siguiente enlace:  
[https://www.edenai.co/](https://www.edenai.co/)

Para más información acerca de como hacer esto ver el cideo de configuración de la app adjunto.

### Paso 0: Descomprimir la BBDD

Entrar en la carpeta data y descomprimir el zip que se encuentra dentro.

### Paso 1: Obtener el API Token y la URL

1. Visita el sitio web [EdenAI](https://www.edenai.co/).
2. Regístrate o inicia sesión en tu cuenta.
3. Obtén tu API token y la URL que se necesitarán para configurar el entorno.

### Paso 2: Configuración del archivo `.env`

Dentro del directorio `/docker`, encontrarás un archivo llamado `.env`. Abre este archivo y agrega los siguientes valores:

- `EDEN_API_TOKEN=<tu_api_token_aqui>`
- `EDEN_API_URL=<tu_api_url_aqui>`

### Paso 3: Construcción y despliegue de la aplicación

Una vez que hayas configurado el archivo `.env` con los valores obtenidos, podrás correr la aplicación dentro de un contenedor Docker.

1. Navega al directorio donde se encuentra la carpeta `docker`.
2. Abre una terminal y ejecuta el siguiente comando para iniciar la aplicación:

   ```bash
   docker compose --env-file .env up

## Documentación de la API

La API está diseñada para soportar las funcionalidades del sistema y está dividida en diferentes rutas agrupadas por propósito. Todas las rutas tienen como prefijo base `/api/v0`.

---

### **Rutas de Chat**  
Endpoints para interactuar con el chatbot y obtener información basada en las reseñas.

1. **Consulta general al chatbot**  
   **POST** `/api/v0/chat/query`  
   - **Descripción**: Envia una consulta general al chatbot.  
   - **Body** (JSON):  
     ```json
     {
       "prompt": "¿Qué opinan los usuarios sobre [producto]?"
     }
     ```  
   - **Respuesta** (200):  
     ```json
     {
       "answer": "Respuesta generada por el chatbot"
     }
     ```
   - **Errores**:  
     - `400`: "No question provided"  
     - `500`: "Internal server error, no response from Eden AI"

2. **Consulta específica sobre un producto**  
   **POST** `/api/v0/chat/product/<product_id>`  
   - **Descripción**: Devuelve la respuesta a una consulta sobre un producto y las reseñas utilizadas como base.  
   - **Body** (JSON):  
     ```json
     {
       "prompt": "¿Cuáles son las principales ventajas de este producto?"
     }
     ```  
   - **Respuesta** (200):  
     ```json
     {
       "answer": "Respuesta generada por el chatbot",
       "reviews": [1, 2, 3]
     }
     ```
   - **Errores**:  
     - `400`: "No question provided"  
     - `404`: "No reviews found for the product"

---

### **Rutas de Productos**  
Endpoints para gestionar productos.

1. **Listar productos**  
   **GET** `/api/v0/products`  
   - **Parámetros de consulta**:  
     - `category` (opcional): Filtrar por categoría.  
     - `limit` (opcional): Limitar el número de productos devueltos.  
     - `page` (opcional): Paginación.  
   - **Respuesta** (200): Lista de productos.  

2. **Crear producto**  
   **POST** `/api/v0/products`  
   - **Body** (JSON): Datos del producto.  
   - **Respuesta** (201): Producto creado.  

3. **Obtener un producto por ID**  
   **GET** `/api/v0/products/<int:id>`  
   - **Respuesta** (200): Detalles del producto.  

4. **Actualizar un producto**  
   **PUT** `/api/v0/products/<int:id>`  
   - **Body** (JSON): Datos actualizados.  
   - **Respuesta** (200): Producto actualizado.  

5. **Eliminar un producto**  
   **DELETE** `/api/v0/products/<int:id>`  
   - **Respuesta** (200): Producto eliminado.  

6. **Obtener reseñas de un producto**  
   **GET** `/api/v0/products/<int:id>/reviews`  
   - **Parámetros de consulta**:  
     - `page` (opcional): Número de página (paginación).  
   - **Respuesta** (200): Lista de reseñas del producto.  

---

### **Rutas de Reseñas**  
Endpoints para gestionar reseñas.

1. **Crear reseñas para un producto**  
   **POST** `/api/v0/reviews/<int:product_id>`  
   - **Body** (JSON): Lista de reseñas.  
   - **Respuesta** (201): Reseñas creadas.  

2. **Actualizar una reseña**  
   **PUT** `/api/v0/reviews/<int:review_id>`  
   - **Body** (JSON): Datos actualizados de la reseña.  
   - **Respuesta** (200): Reseña actualizada.  

3. **Eliminar una reseña**  
   **DELETE** `/api/v0/reviews/<int:review_id>`  
   - **Respuesta** (200): Reseña eliminada.  

---

### **Ruta de Salud del Sistema**  
Endpoint para verificar el estado del sistema.

1. **Comprobar salud del sistema**  
   **GET** `/health`  
   - **Descripción**: Verifica la conexión a la base de datos y la configuración de las variables de entorno requeridas.  
   - **Respuesta** (200):  
     ```json
     {
       "database": true,
       "env_vars": true
     }
     ```
   - **Errores** (500): Si la base de datos o las variables de entorno fallan.  

---

Esta documentación cubre todos los endpoints disponibles y sus respectivos casos de uso.  


## Ejemplos de Uso

Esta sección describe cómo utilizar las funcionalidades actualmente implementadas.

---

### Funcionalidades Actuales

#### 1. **Navegar Productos**  
- **Descripción**: Permite explorar productos disponibles, visualizar sus características y ser redirigido a su página de compra en Amazon.  
- **Cómo usar**:  
  - Navega por los distintos productos  
  - Haz clic en un producto para ver sus detalles y acceder al enlace de Amazon.  

#### 2. **Información General de Productos**  
- **Descripción**: Proporciona un resumen del producto, incluyendo especificaciones clave, puntos destacados de las reseñas y una calificación general.  
- **Ejemplo de entrada del usuario**:  
  - `"Tell me more about [product name]."`  
  - `"What are the standout features of [product name]?"`  
  - `"Which specifications are most praised in [product name]?"`  
- **Salida esperada**:  
  ```json
    {
       "answer": "Respuesta generada por el chatbot",
       "reviews": [1, 2, 3]
    }


  
  
