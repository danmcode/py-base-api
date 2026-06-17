# Architecture Principles

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Docker Compose

De acuerdo a las técnologías mencionadas, y el template del proyecto, necesito completar la implementación del proyecto de fastapi core template. A continuación, se detallan los pasos para completar la implementación del proyecto:

# Infraestructura y Configuración inicial del proyecto:

Se debe configurar la infraestructura del proyecto, docker y docker compose, para facilitar el desarrollo y despliegue del proyecto. Además, se debe configurar la base de datos PostgreSQL y la conexión a la misma desde FastAPI.

1. Revisar los archivos de configuración de Docker y Docker Compose para asegurarse de que estén correctamente configurados para el proyecto.
2. Configurar la conexión a la base de datos PostgreSQL en el archivo de configuración de FastAPI, asegurándose de que las credenciales y la URL de conexión sean correctas.
3. Revisar la configuración para los entornos de desarrollo y producción, asegurándose de que las variables de entorno estén correctamente configuradas para cada entorno.
4. Todo lo configurable, debe ser configurable a través de variables de entorno, para facilitar la gestión de la configuración en diferentes entornos.
5. Ten en cuenta la seguridad de la información para la configuración de los dockers.
6. Crear README.md con instrucciones claras para configurar y ejecutar el proyecto, incluyendo cómo configurar las variables de entorno y cómo iniciar los contenedores de Docker.
7. Sigue las mejores prácticas de seguridad para la configuración de Docker y la gestión de secretos, asegurándote de no exponer información sensible en los archivos de configuración o en el código fuente.
8. El nginx debe estar configurado para servir la aplicación FastAPI y manejar las solicitudes de manera eficiente, asegurándose de que esté correctamente configurado para el entorno de producción.

adicionalmente por el momento no se podrá usar un certificado SSL, por lo que se debe configurar nginx para generar un certificado autofirmado para el entorno de desarrollo, pero que se pueda tener en /nginx/certs y así se puedan tener los .pem para que sea más sencillo de migrar luego a un certificado válido en producción.

solo enfocarse en la infraestructura y configuración inicial del proyecto, no es necesario implementar funcionalidades específicas de la aplicación en esta etapa.

es decir necesito tener la infraestructura y configuración inicial del proyecto lista para comenzar a desarrollar las funcionalidades específicas de la aplicación.

lo unico que neesito es un endpoint de prueba para verificar que la infraestructura y configuración inicial del proyecto estén funcionando correctamente, por ejemplo un endpoint que devuelva un mensaje de "Hello World" o algo similar para confirmar que la aplicación está corriendo correctamente. y que se conecto a la base de datos correctamente.

el dominio para el entorno de desarrollo debe ser "https://test.dev" y para el entorno de producción debe ser "https://test.prod". Asegúrate de configurar nginx para manejar estos dominios correctamente, redirigiendo las solicitudes al contenedor de FastAPI según el entorno.

si se puede generar un script para generar el certificado autofirmado y colocarlo en la carpeta /nginx/certs, sería ideal para facilitar la configuración del entorno de desarrollo. Este script debe ser fácil de ejecutar y debe generar los archivos .pem necesarios para configurar nginx con el certificado autofirmado. y que solo pida el nombre del dominio para el cual se generará el certificado, en este caso "test.dev".


