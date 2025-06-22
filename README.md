# Reviewly

## Abstract

Esta aplicación web integra un chatbot basado en inteligencia artificial generativa que transforma la experiencia de búsqueda, análisis y gestión en plataformas de comercio electrónico. Su diseño responde a tres objetivos principales: agilizar la exploración de productos para los consumidores, proporcionar un motor de búsqueda semántico avanzado y facilitar herramientas analíticas a los administradores.

El núcleo de esta solución reside en la conversión tanto de las características de los productos como de las consultas de los usuarios a un mismo espacio semántico mediante representaciones vectoriales. Esto permite realizar búsquedas más precisas, priorizando la similitud conceptual sobre las coincidencias exactas de palabras. Así, cuando un usuario busca algo como “quiero un portátil ligero con buena batería”, el sistema evalúa la proximidad entre su intención y la descripción de los productos, devolviendo los resultados más relevantes.

Además, este mismo enfoque vectorial se aplica a las reseñas de usuarios, lo que habilita el uso de técnicas como RAG (Retrieval-Augmented Generation). Al recibir una consulta, el chatbot puede recuperar opiniones cercanas semánticamente y utilizarlas para generar respuestas fundamentadas, ofreciendo resúmenes o comparativas basadas en experiencias reales.

Para gestionar estas capacidades, el sistema utiliza Function Calling, una técnica que permite al modelo de lenguaje invocar funciones específicas del backend cuando detecta que la consulta lo requiere. Esto incluye no solo funciones administrativas, sino también operaciones como la búsqueda de productos y análisis de reseñas. También es capaz de construir gráficos interactivos, facilitando así la toma de decisiones basada en datos.

En resumen, esta aplicación combina procesamiento del lenguaje natural, búsqueda semántica avanzada y generación contextualizada de respuestas mediante RAG y Function Calling. Esta arquitectura permite una experiencia conversacional fluida, adaptada tanto a consumidores como a administradores, superando las limitaciones de los motores de búsqueda tradicionales.

---

## ¿Qué problema resuelve?

El comercio electrónico moderno enfrenta dos retos principales: por un lado, los usuarios necesitan encontrar productos relevantes de forma rápida y precisa; por otro, los administradores de plataformas requieren herramientas de análisis y gestión efectivas. Los motores de búsqueda tradicionales basados en palabras clave suelen ser ineficientes, ya que no comprenden la intención real del usuario. Además, la navegación por reseñas es manual, extensa y poco sintetizada.

---

## ¿Qué hace la app?

**Reviewly** transforma este proceso mediante un chatbot inteligente potenciado por IA generativa, que puede:

- **Buscar productos** en lenguaje natural usando búsqueda semántica (RAG).
- **Buscar y analizar reseñas** relacionadas con la intención del usuario (RAG).
- **Generar respuestas contextuales, resúmenes y comparativas** basadas en experiencias reales.
- **Ejecutar funciones administrativas mediante Function Calling**, incluyendo:
  - Generación de gráficos.
  - Generación de reportes en lenguaje natural.
  - Consulta de rendimiento de productos.
  - Análisis de usuarios y tendencias.

Además, implementa un **motor de búsqueda semántico**, que prioriza la similitud conceptual entre consultas y productos.

---

## Arquitectura del sistema

### Frontend
- React + React Router
- Material UI

### Backend
- Python + Flask + SQLAlchemy
- Endpoints protegidos + Swagger

### Origen de datos
- Dataset Amazon Reviews'23 (https://amazon-reviews-2023.github.io/)
- Ingesta con Apache Kafka

### Almacenamiento
- PostgreSQL con pgvector
- SQLite auxiliar

### LLM y Servicios de IA
- Embeddings: stella_en_v5
- Respuestas: GPT-4o-mini (OpenRouter)
- Function Calling

### Procesamiento en Tiempo Real
- Kafka + Zookeeper

### Despliegue
- Docker + docker-compose

---

## Arquitectura de IA: RAG

1. El usuario envía una consulta (producto o reseña).
2. La consulta se convierte a embedding.
3. Se busca la información más relevante en la base de datos vectorial (pgvector).
4. Se envía el contenido recuperado al modelo (GPT-4o-mini).
5. El modelo genera una respuesta contextualizada con RAG.
6. La respuesta se muestra al usuario.

---

## Arquitectura de Function Calling

1. El usuario realiza una consulta en lenguaje natural.
2. El modelo detecta que debe invocar una función del backend (ej. `generarGraficoVentas()` o `buscarProducto()`).
3. El backend ejecuta la función y devuelve los datos.
4. El modelo interpreta la respuesta y la presenta al usuario de forma comprensible.

---

## Instrucciones de instalación y despliegue

### Requisitos previos
- Docker y Docker Compose
- API token y URL de OpenRouter: https://openrouter.ai/
- Dataset Amazon Reviews'23 descomprimido en `/data`

### Paso 0: Descomprimir la BBDD
- Descomprimir dataset en la carpeta `/data`

### Paso 1: Obtener el API Token y la URL
- Registrarse en OpenRouter y copiar token y URL

### Paso 2: Configurar archivo .env
```env
OPENROUTER_API_TOKEN=<tu_api_token_aqui>
OPENROUTER_API_URL=<tu_api_url_aqui>
```

### Paso 3: Construcción y despliegue
```bash
docker compose --env-file .env up
```

Acceso al frontend: [http://localhost:5173/](http://localhost:5173/)  
Acceso al backend: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Documentación de la API

La documentación de la API está disponible en la **ruta base del backend**:  
[http://127.0.0.1:5000](http://127.0.0.1:5000)

Base URL de la API: `/api/v0`
