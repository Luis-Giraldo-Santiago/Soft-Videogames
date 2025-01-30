import re
from django.shortcuts import render, redirect
from .models import Games
from django.http import JsonResponse
import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from datetime import datetime


def home(request):
    return render(request, 'home.html')

'''BEATUFIUL SOUP'''

def scrape_wikipedia_and_save_games():
    year = datetime.now().year - 1
    url = f"https://en.wikipedia.org/wiki/{year}_in_video_games"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Buscar todas las tablas con la clase 'wikitable'
    tables = soup.find_all("table", class_="wikitable")

    # Buscar todas las tablas que tienen un <caption> vacío
    valid_tables = []
    for tbl in tables:
        caption = tbl.find("caption")
        if caption and not caption.get_text(strip=True):  # <caption> existe y está vacío
            valid_tables.append(tbl)

    if not valid_tables:
        print("No se encontraron tablas deseadas en la página.")
        return

    # Lista para almacenar los nombres de los juegos
    games = []

    # Procesar cada tabla válida
    for table in valid_tables:
        rows = table.find_all("tr")
        for row in rows[1:]: 
            columns = row.find_all("td")

            title = None
            platforms = None

            # Iterar por las columnas y buscar <i> para el título y <a> para las plataformas
            for col in columns:
                # Buscar el título en la etiqueta <i>
                title_tag = col.find("i")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                else:
                    # Buscar las plataformas en las etiquetas <a>
                    platforms_tags = col.find_all("a")
                    if platforms_tags:
                        platforms = ", ".join([tag.get_text(strip=True) for tag in platforms_tags])
                if title and platforms:
                    break

            # Si se encuentra un título y las plataformas incluyen PC, guardar el juego
            if title and platforms and any(platform in platforms for platform in ["Win", "Mac", "Lin"]):
                games.append(title)

    # Guardar los nombres de los juegos en un archivo .txt
    with open("juegos.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(games))

# This function will be used to load the data from the BBC Good Food website
def load_data():
    games_saved = 0
    errors = []
    page = 1 
    cont = 0
    
    # Delete all the games in the database
    Games.objects.all().delete()
    
    try:
        with open("juegos.txt", "r", encoding="utf-8") as file:
            games = file.readlines()

        for game in games:
            game = game.strip()
            game = game.replace(" ","+")
            url = f"https://store.steampowered.com/search/?term={game}"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todas las tablas con la clase 'wikitable'
            game = game.replace("+"," ")
            if(soup.find("div", class_="col search_name ellipsis")):
                name = soup.find("div", class_="col search_name ellipsis").find('span', class_='title').text.strip()
            else:
                name = None
            if(soup.find("a", class_="search_result_row") and game.upper()==name.upper()):
                game_url = soup.find("a", class_="search_result_row").get('href')
                
                response = requests.get(game_url)
                if (response.status_code != 500):
                    videogame = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extraer title
                    title = videogame.find("div", class_="apphub_AppName").get_text(strip=True)
                    if not title:
                        title = None
                    
                    # Extraer descriptioin
                    if videogame.find("div", class_="game_description_snippet"):
                        description = videogame.find("div", class_="game_description_snippet").get_text(strip=True)
                    elif videogame.find('div', class_='glance_details'):
                        description =  videogame.find('div', class_='glance_details').get_text(strip=True)
                    else:
                        description = None
                    
                    details_block = videogame.find("div", id="genresAndManufacturer", class_="details_block")
                    # Extraer developer
                    developer_div = details_block.find("div", class_="dev_row")
                    developer = None
                    if developer_div and "Developer:" in developer_div.text:
                        developers = developer_div.find_all("a")
                        developer = ", ".join(dev.get_text(strip=True) for dev in developers) if developers else "No disponible"
                    
                    # Extraer publisher
                    publisher_divs = details_block.find_all("div", class_="dev_row")
                    publisher = None
                    if len(publisher_divs) > 1 and "Publisher:" in publisher_divs[1].text:
                        publishers = publisher_divs[1].find_all("a")
                        publisher = ", ".join(pub.get_text(strip=True) for pub in publishers) if publishers else "No disponible"
                    
                    # Extraer géneros
                    genres_span = details_block.find("span", attrs={"data-panel": '{"flow-children":"row"}'})
                    genres = ", ".join(gender.get_text(strip=True) for gender in genres_span.find_all("a")) if genres_span else "No disponible"
                    if not genres:
                        genres = None
                    
                    # Extraer fecha de lanzamiento
                    release_date_text = details_block.find(text=lambda text: "Release Date:" in text)
                    if release_date_text:
                        release_date = release_date_text.next_element.strip()
                        if release_date == "To be announced" or release_date == "Coming soon":
                            continue
                        else:
                            release_date = datetime.strptime(release_date, "%d %b, %Y").date()
                    else:
                        release_date = None
                    
                    # Extraer precio de steam
                    if videogame.find("div", class_="game_purchase_price"):
                        price_steam = videogame.find("div", class_="game_purchase_price").get_text(strip=True)
                    elif videogame.find("div", class_="discount_final_price"):
                        price_steam = videogame.find("div", class_="discount_final_price").get_text(strip=True)
                    else:
                        price_steam = None
                    
                    price_steam = price_steam.replace(",", ".")
                    price_steam = price_steam.replace("€","")
                    price_steam = price_steam.replace("--","00")
                    if(price_steam == "Free"):
                        price_steam = price_steam.replace("Free","00")
                    else:
                        price_steam = price_steam.replace("Free To Play","00")
                    
                    if(videogame.find('div', id='review_histogram_rollup_section')):
                        sumary = videogame.find('div', id='review_histogram_rollup_section')
                        summary_section = sumary.find('div', class_='summary_section')
                        review_summary = summary_section.find("span", class_="game_review_summary")
                        if review_summary:
                            rating_text = review_summary.get_text(strip=True)
                            # Mapear el texto del rating a un número
                            rating_map = {
                                "Overwhelmingly Positive": 7,
                                "Very Positive": 6,
                                "Positive": 5,
                                "Mostly Positive": 4,
                                "Mixed": 3,
                                "Mostly Negative": 2,
                                "Negative": 1,
                            }

                            # Buscar el número correspondiente
                            rating = rating_map.get(rating_text, 0)
                        else: 
                            rating = 0
                        
                        # Extraer el texto donde se muestra el número total de reseñas (dentro del span)
                        num_reviews = summary_section.find('span', class_=False, attrs={}).text.strip()
                        num_reviews = num_reviews.replace("(","")
                        num_reviews = num_reviews.replace(")","")
                        num_reviews = num_reviews.replace(" reviews","")
                        num_reviews = num_reviews.replace(",","")
                    else:
                        rating = 0
                        num_reviews = 0
                        
                    # Save the game to the database
                    try:
                        Games.objects.create(
                            title=title,
                            description=description,
                            developer=developer,
                            publisher=publisher,
                            genres=genres,
                            release_date=release_date,
                            price_steam=float(price_steam),
                            rating=float(rating),
                            num_reviews=int(num_reviews)
                        )
                        games_saved += 1
                    except Exception as e:
                        errors.append(f"Error saving game '{title}': {str(e)}")

    except Exception as e:
        errors.append(str(e))
    return games_saved, errors


def confirm_load_data(request):
    if request.method == "POST":        
        scrape_wikipedia_and_save_games()
        games_saved, errors = load_data()
        print(errors)
        if errors:
            messages.error(request, "An error occurred while loading the data.")
        else:
            messages.success(request, f"Data loaded successfully! {games_saved} games have been saved.")
        return redirect('home')
    return render(request, "confirm_load_data.html")



def games_list(request):
    all_games = Games.objects.all()
    for game in all_games:
        if game.genres:
            game.genres = [gender.strip() for gender in game.genres.split(",")]

    return render(request, 'games_list.html', {'games': all_games})
