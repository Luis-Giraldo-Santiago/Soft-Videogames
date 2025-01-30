# Soft-Videogames

## Luis Giraldo Santiago  
08/01/2024  

## Índice  
1. [Objetivos](#objetivos)  
2. [Tecnologías](#tecnologías)  
   - [Django](#django)  
   - [Beautiful Soup](#beautiful-soup)  
   - [Whoosh](#whoosh)  
   - [Sistema de Recomendación](#sistema-de-recomendación)  
3. [Manual de uso](#manual-de-uso)  

---

## Objetivos  

El objetivo de este proyecto es la creación de una página web donde se recopilen todos los juegos que hayan salido en la página web de Steam en el año anterior a la ejecución de la carga de datos. En este caso, se analizará el año 2024.  

---

## Tecnologías  

### Django  
Se ha usado Django para la creación de la página web. En esta, se puede acceder a las diferentes funciones a través de URLs y se mostrarán en diferentes pantallas dentro del sitio web.  

### Beautiful Soup  
Se ha utilizado Beautiful Soup para hacer scraping de dos páginas web:  

1. **Wikipedia**: Se extraen los juegos lanzados para Windows, Mac y Linux en el año anterior a la fecha de ejecución de la carga de datos, a través de la URL:  https://en.wikipedia.org/wiki/{year}_in_video_games, donde `{year}` es el año correspondiente.  

2. **Steam**: Con la lista de juegos obtenida, se busca cada juego en Steam mediante la URL: https://store.steampowered.com/search/?term={game}, donde `{game}` es el título del juego. Se toma el primer resultado y se extrae información detallada, como:  

- Título  
- Descripción  
- Desarrolladores  
- Editores  
- Géneros  
- Fecha de lanzamiento  
- Precio  
- Clasificación  
- Número de reseñas  

Esta información se almacena en una base de datos `sqlite3`.  

### Whoosh  
Se ha utilizado Whoosh para crear un índice y permitir tres tipos de búsquedas en la página web:  

1. **Búsqueda por título**: No es necesario que el título sea exacto; basta con que contenga la palabra clave.  
2. **Búsqueda por fecha**: Permite seleccionar un rango de fechas y muestra los juegos lanzados en ese periodo.  
3. **Búsqueda por género**: Devuelve los juegos que contienen al menos uno de los géneros ingresados.  

### Sistema de Recomendación  
Se ha implementado un sistema de recomendación basado en contenido. Se utiliza la descripción, los géneros, los desarrolladores y los editores de los juegos para calcular la similitud TF-IDF entre ellos. Para esto, se han empleado las librerías `pandas` y `scikit-learn`.  

---

## Manual de uso  

1. **Descomprimir el archivo** `Soft_Videogames.zip` y abrirlo en el IDE de preferencia.  
2. **Crear un entorno virtual** e instalar las dependencias con el siguiente comando:  pip install -r requirements.txt
3. **Ejecutar el servidor de Django**:  python manage.py runserver. Luego, acceder a la página web en:  http://127.0.0.1:8000/
4. **Cargar los datos** de dos formas:  
- Desde la página inicial, haciendo clic en el botón **"Load data in database"**.  
- Desde la opción **"Load database"** en la barra superior y luego en **"Confirm"**.  
5. **Cargar el índice** accediendo a la opción **"Load index"** y presionando **"Confirm"**.  
6. **Acceder al sistema de recomendaciones** a través de **"Recomendations"** en la barra superior. Al ingresar un título de videojuego, se mostrarán recomendaciones similares.  
7. **Listar todos los videojuegos** en la base de datos desde la opción **"Games list"** en la barra superior.  
8. **Realizar búsquedas** desplegando el menú **"Searchs"** y eligiendo el método de búsqueda:  
- **Por título**: Ingresar parte del nombre del juego para obtener coincidencias.  
- **Por fecha**: Seleccionar un rango de fechas para listar los juegos lanzados en ese periodo.  
- **Por género**: Ingresar uno o más géneros para obtener los juegos que los contengan.  





