# Reviewly

## Descripción del proyecto

### El Problema

El proceso de compra en línea puede ser tedioso, ya que los usuarios deben navegar por múltiples productos, analizar reseñas y comparar características manualmente, lo que consume tiempo y puede generar confusión. Además, los motores de búsqueda tradicionales basados en palabras clave a menudo no comprenden la intención del usuario, resultando en recomendaciones poco relevantes. Por otro lado, los administradores de plataformas de comercio electrónico necesitan herramientas analíticas avanzadas para gestionar datos y tomar decisiones informadas.

### ¿Qué hace la app?

Reviewly es una aplicación web que transforma la experiencia de búsqueda y gestión en plataformas de comercio electrónico mediante un chatbot basado en inteligencia artificial generativa y técnicas avanzadas de recuperación de información. La aplicación combina búsqueda semántica, generación de respuestas contextuales y herramientas analíticas para usuarios y administradores. En su versión actual, la aplicación ofrece las siguientes funcionalidades:

#### Búsqueda Conversacional de Productos
- **Funcionalidad:** Los usuarios pueden realizar consultas en lenguaje natural y recibir resultados relevantes basados en la similitud semántica.
- **Sistema:** Utiliza embeddings generados por stella_en_v5 y búsqueda vectorial en PostgreSQL con pgvector.

#### Generación de Respuestas Contextuales con RAG
- **Funcionalidad:** Chatbot que recupera reseñas relevantes y genera resúmenes/comparativas con RAG.
- **Sistema:** Combina búsqueda vectorial con GPT-4o-mini (OpenRouter).

#### Herramientas Analíticas para Administradores
- **Funcionalidad:** Consultas en lenguaje natural para generar reportes, gráficos, mapas de calor, eliminación de cuentas, etc.
- **Sistema:** Function Calling con integración Flask y React.

#### Gestión de Usuarios y Productos
- **Funcionalidad:** Registro, login, favoritos, detalles de producto, gestión por roles.
- **Sistema:** Autenticación con tokens, API protegida.

#### Procesamiento de Datos en Tiempo Real
- **Funcionalidad:** Ingesta y procesamiento continuo de reseñas y metadatos.
- **Sistema:** Apache Kafka + Zookeeper + PostgreSQL.

#### Interfaz Intuitiva y Responsiva
- **Funcionalidad:** Navegación clara, adaptable y profesional.
- **Sistema:** React + React Router + Material UI.

## Futuras características

### Análisis de Sentimientos de Reseñas
- Clasificación de reseñas mediante PLN.

### Generación de Etiquetas mediante Clustering
- Clustering de embeddings para detectar temas clave.

### Resúmenes de Reseñas
- Generación de resúmenes automáticos.

### Comparación de Productos
- Consultas tipo: "Which is better, A or B?" → Comparación basada en reseñas y características.

### Productos Destacados en una Categoría
- Consultas tipo: "Top product in [category]" → Lista destacada.

## Objetivos

### Mejorar la Experiencia del Consumidor
- ✅ Logrado mediante búsqueda semántica y chatbot con RAG.

### Construir un Motor de Búsqueda Eficiente
- ✅ Implementado con stella_en_v5 y pgvector.

### Proveer Herramientas Analíticas para Administradores
- ✅ Function Calling y generación de reportes en lenguaje natural.

### Aprender Tecnologías Modernas
- ✅ React, LLMs, pgvector, Kafka, Docker, etc.

## Arquitectura del sistema

### Frontend
- React + React Router
- Material UI

### Backend
- Python + Flask + SQLAlchemy
- Endpoints protegidos + Swagger

### Origen de datos
- Dataset Amazon Reviews'23
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

## Arquitectura de IA: Implementación de RAG

1. Usuario envía consulta (frontend)
2. Se convierte a embedding (backend)
3. Búsqueda vectorial (pgvector)
4. Reseñas se envian a GPT-4o-mini (OpenRouter)
5. Respuesta generada y enviada al usuario

## Despliegue con Docker

- Cada componente en un contenedor Docker
- `docker-compose.yml` orquesta todos los servicios

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

Acceso: http://localhost:5173

