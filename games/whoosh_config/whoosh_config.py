from ast import Or
import shutil
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.fields import Schema, TEXT, ID, NUMERIC, DATETIME, KEYWORD
from whoosh.qparser import MultifieldParser, OrGroup
from whoosh.query import Term, NumericRange, Or, DateRange, And
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import JsonResponse
from games.models import Games
import os
from whoosh.qparser import QueryParser
from datetime import datetime, date

def load_index(request):
    if request.method == "POST":
        try:
            index_dir = os.path.join(os.path.dirname(__file__), 'index')

            schema = Schema(
                title=TEXT(stored=True),
                description=TEXT(stored=True),
                developer=TEXT(stored=True),
                publisher=TEXT(stored=True),
                genres=KEYWORD(stored=True, commas=True),  # Cambiado a KEYWORD
                release_date=DATETIME(stored=True),
                price_steam=NUMERIC(stored=True),
                rating=NUMERIC(stored=True, decimal_places=2),
                num_reviews=NUMERIC(stored=True)
            )


            if os.path.exists(index_dir):
                shutil.rmtree(index_dir)
            os.mkdir(index_dir)

            ix = create_in(index_dir, schema=schema)
            writer = ix.writer()

            games = Games.objects.all()

            for game in games:
                # Verificar si release_date es una fecha y convertirla a datetime
                if isinstance(game.release_date, date) and not isinstance(game.release_date, datetime):
                    release_date = datetime.combine(game.release_date, datetime.min.time())
                else:
                    release_date = game.release_date

                writer.add_document(
                    title=game.title,
                    description=game.description,
                    developer=game.developer,
                    publisher=game.publisher,
                    genres=",".join([genre.strip().lower() for genre in game.genres.split(",")]),
                    release_date=release_date,
                    price_steam=game.price_steam,
                    rating=game.rating,
                    num_reviews=game.num_reviews
                )
            writer.commit()

            messages.success(request, f"Index loaded successfully! {games.count()} games have been indexed.")

        except Exception as e:
            messages.error(request, f"An error occurred while loading the index: {str(e)}")

        return redirect("home")
    
    return render(request, "confirm_load_index.html")



'''SEARCH  BY TITLE'''
def search_games_by_title(request): 
    results_list = []

    if request.method == "GET" and "titulo" in request.GET:
        query = request.GET.get("titulo", "").strip()
        index_dir = os.path.join(os.path.dirname(__file__), 'index')

        try:
            ix = open_dir(index_dir)
            with ix.searcher() as searcher:
                if query:
                    # Crear un parser para buscar en el campo "title"
                    parser = QueryParser("title", schema=ix.schema)
                    search_query = parser.parse(query)  # Búsqueda directa con el término

                    # Ejecutar la búsqueda
                    results = searcher.search(search_query, limit=20)
                    
                    for result in results:
                        results_list.append({
                            "title": result.get("title", "N/A"),
                            "description": result.get("description", "N/A"),
                            "developer": result.get("developer", "N/A"),
                            "publisher": result.get("publisher", "N/A"),
                            "genres": result.get("genres", "N/A"),
                            "release_date": result.get("release_date", "N/A"),
                            "price_steam": result.get("price_steam", "N/A"),
                            "rating": result.get("rating", "N/A"),
                            "num_reviews": result.get("num_reviews", "N/A"),
                        })

        except Exception as e:
            print(f"Error while searching for games: {e}")
    
    return render(request, "search_games_by_title.html", {"results": results_list})



'''SEARCH GAMES BY DATE'''
def search_games_by_date(request):
    results_list = []

    if request.method == "GET":
        start_date = request.GET.get("start_date", "").strip()
        end_date = request.GET.get("end_date", "").strip()
        index_dir = os.path.join(os.path.dirname(__file__), 'index')

        try:
            ix = open_dir(index_dir)
            with ix.searcher() as searcher:
                query = None

                if start_date or end_date:
                    # Parsear las fechas ingresadas por el usuario
                    start_date_parsed = (
                        datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
                    )
                    end_date_parsed = (
                        datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
                    )

                    # Crear consulta de rango de fechas
                    query = DateRange("release_date", start_date_parsed, end_date_parsed)

                if query:
                    # Ejecutar la búsqueda
                    results = searcher.search(query, limit=20)
                    for result in results:
                        results_list.append({
                            "title": result.get("title", "N/A"),
                            "description": result.get("description", "N/A"),
                            "developer": result.get("developer", "N/A"),
                            "publisher": result.get("publisher", "N/A"),
                            "genres": result.get("genres", "N/A"),
                            "release_date": result.get("release_date", "N/A"),
                            "price_steam": result.get("price_steam", "N/A"),
                            "rating": result.get("rating", "N/A"),
                            "num_reviews": result.get("num_reviews", "N/A"),
                        })

        except Exception as e:
            print(f"Error while searching for games by date: {e}")

    return render(request, "search_games_by_date.html", {"results": results_list})

def search_games_by_genres(request):
    results_list = []
    error_message = None

    # Obtén los géneros disponibles desde el principio
    available_genres = Games.objects.values_list("genres", flat=True).distinct()
    available_genres = sorted({genre.strip() for genres in available_genres for genre in genres.split(",")})

    if request.method == "GET" and "genres" in request.GET:
        try:
            genres_query = request.GET.get("genres", "").strip().lower()

            index_dir = os.path.join(os.path.dirname(__file__), 'index')
            if not os.path.exists(index_dir):
                raise Exception(f"Index not found in {index_dir}")

            ix = open_dir(index_dir)

            with ix.searcher() as searcher:
                genre_queries = [genre.strip() for genre in genres_query.split(",") if genre.strip()]
                genre_query = And([Term("genres", genre) for genre in genre_queries])

                # Realizamos la búsqueda si existe la consulta
                results = searcher.search(genre_query, limit=None) if genre_query else []

                for result in results:
                    results_list.append({
                        "title": result.get("title", "Unknown Title"),
                        "description": result.get("description", "N/A"),
                        "developer": result.get("developer", "N/A"),
                        "publisher": result.get("publisher", "N/A"),
                        "genres": result.get("genres", "N/A").split(","),
                        "release_date": result.get("release_date", "N/A"),
                        "price_steam": result.get("price_steam", "N/A"),
                        "rating": result.get("rating", "N/A"),
                        "num_reviews": result.get("num_reviews", "N/A"),
                    })

            return render(request, "search_games_by_genres.html", {
                "games": results_list,
                "searched_genres": genres_query,
                "available_genres": available_genres,
            })

        except ValueError as ve:
            print(f"Value error: {ve}")
            error_message = str(ve)
        except Exception as e:
            print(f"General error: {e}")
            error_message = f"An error occurred: {str(e)}"

    return render(request, "search_games_by_genres.html", {
        "games": results_list,
        "available_genres": available_genres,
        "error": error_message
    })
