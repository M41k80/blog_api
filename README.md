# Blog API

API RESTful para gestionar un blog, construida con Python.  
Esta API incluye funcionalidades para usuarios, publicaciones, comentarios y gestión de archivos, con soporte para autenticación y roles.

## Estructura del proyecto
```
app/
├── api/ # Endpoints y routers de la API
├── core/ # Configuraciones y utilidades centrales
├── models/ # Modelos de datos (ORM)
├── seeds/ # Scripts para poblar la base de datos
├── services/ # Lógica de negocio
├── utils/ # Funciones auxiliares
├── init.py
└── main.py # Punto de entrada de la aplicación
```

## Funcionalidades

- CRUD de publicaciones y usuarios
- Gestión de comentarios
- Autenticación y autorización
- Manejo de archivos (imágenes, adjuntos)
- Validación de datos y manejo de errores

## Tecnologías

- Python 3.x
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- Base de datos PostgreSQL (o Supabase)
- Pydantic para validación de modelos
- Uvicorn para servidor ASGI

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/M41k80/blog_api.git
cd blog_api

```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

```

3. Instala las dependencias:
```
pip install -r requirements.txt

```


4. Configura las variables de entorno:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=tu_clave_secreta
```

## Uso

# Para correr la API en modo desarrollo:
```
uvicorn app.main:app --reload

```

## Contribuciones

# ¡Contribuciones bienvenidas! Por favor abre un issue o pull request para sugerir mejoras.

## Licencia

## Este proyecto está bajo la licencia MIT.

