from django.urls import path
from . import views
from games.whoosh_config.whoosh_config import load_index, search_games_by_title, search_games_by_date, search_games_by_genres
from games.recommendations.recommendations import recommend_games

urlpatterns = [
    path('', views.home, name='home'),
    path('load-data', views.confirm_load_data, name='confirm_load_data'),
    path('load-index', load_index, name='load_index'),
    path('games', views.games_list, name='games_list'),
    path('search/search-by-title', search_games_by_title, name='search_games_by_title'),
    path('search/search-by-date', search_games_by_date, name='search_games_by_date'),
    path('search/search_games_by_genres', search_games_by_genres, name='search_games_by_genres'),
    path('recommend', recommend_games, name='recommend_games'),

]
