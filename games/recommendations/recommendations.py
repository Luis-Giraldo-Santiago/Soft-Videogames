from django.shortcuts import render
from django.db.models import F, Value, TextField
from django.db.models.functions import Concat
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from games.models import Games

def get_recommendations(game_title, cosine_sim, df):
    # Obtener el índice del juego que coincide con el título
    idx = df[df['title'].str.lower() == game_title.lower()].index
    if idx.empty:
        return []
    
    idx = idx[0]
    
    # Obtener las puntuaciones de similitud para todos los juegos
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Ordenar los juegos por puntuación de similitud
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Obtener los títulos de los 10 juegos más similares (excluyendo el propio juego)
    sim_scores = sim_scores[1:11]  # Excluye el primer elemento (el mismo juego)
    game_indices = [i[0] for i in sim_scores]
    
    # Devolver los títulos de los juegos recomendados
    return df.iloc[game_indices]['title'].tolist()

def recommend_games(request):
    game_title = request.GET.get("titulo", "").strip()
    if not game_title:
        return render(request, 'confirm_load_recommendations.html', {'results': [], 'error': 'Please enter a game title.'})
    
    games = Games.objects.annotate(
        content=Concat(
            F('description'),
            Value(' '),
            F('genres'),
            Value(' '),
            F('developer'),
            Value(' '),
            F('publisher'),
            output_field=TextField()
        )
    ).values('id', 'title', 'content')

    df = pd.DataFrame(list(games))

    if df.empty:
        return render(request, 'confirm_load_recommendations.html', {'results': [], 'error': 'No games found in the database.'})

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(df['content'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    recommended_titles = get_recommendations(game_title, cosine_sim, df)

    # Filtrar juegos en la base de datos usando los títulos recomendados
    recommended_games = Games.objects.filter(title__in=recommended_titles)

    return render(request, 'confirm_load_recommendations.html', {
        'results': recommended_games,
        'game_title': game_title
    })
