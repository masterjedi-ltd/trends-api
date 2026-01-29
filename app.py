from flask import Flask, request, jsonify
from pytrends.request import TrendReq
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return 'API działa! Użyj /trends?keyword=bitcoin lub /trending'

@app.route('/trending')
def get_trending():
    try:
        geo = request.args.get('geo', 'PL')
        limit = int(request.args.get('limit', 50))
        
        # Daily Trends API - więcej danych
        url = f'https://trends.google.com/trends/api/dailytrends?hl=pl&tz=-120&geo={geo}&ns=15'
        
        response = requests.get(url)
        # Usuń prefix ")]}'\n"
        clean = response.text[5:]
        data = json.loads(clean)
        
        items = []
        for day in data['default']['trendingSearchesDays']:
            for search in day['trendingSearches']:
                title = search['title']['query']
                traffic = search.get('formattedTraffic', 'N/A')
                
                # Related queries
                related = [q['query'] for q in search.get('relatedQueries', [])]
                
                # Articles
                articles = []
                for article in search.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'source': article.get('source', ''),
                        'url': article.get('url', '')
                    })
                
                items.append({
                    'keyword': title,
                    'traffic': traffic,
                    'related': related,
                    'articles': articles
                })
                
                if len(items) >= limit:
                    break
            if len(items) >= limit:
                break
        
        return jsonify(items)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/realtime')
def get_realtime():
    try:
        geo = request.args.get('geo', 'PL')
        limit = int(request.args.get('limit', 50))
        
        # Realtime Trends API
        url = f'https://trends.google.com/trends/api/realtimetrends?hl=pl&tz=-120&geo={geo}&cat=all&fi=0&fs=0&ri=300&rs=20&sort=0'
        
        response = requests.get(url)
        clean = response.text[5:]
        data = json.loads(clean)
        
        items = []
        for story in data.get('storySummaries', {}).get('trendingStories', []):
            title = story.get('title', '')
            entities = [e.get('title', '') for e in story.get('entityNames', [])]
            
            articles = []
            for article in story.get('articles', []):
                articles.append({
                    'title': article.get('articleTitle', ''),
                    'source': article.get('source', ''),
                    'url': article.get('url', '')
                })
            
            items.append({
                'title': title,
                'keywords': entities,
                'articles': articles
            })
            
            if len(items) >= limit:
                break
        
        return jsonify(items)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/trends')
def get_trends():
    try:
        keyword = request.args.get('keyword', '')
        geo = request.args.get('geo', 'PL')
        timeframe = request.args.get('timeframe', 'now 1-d')
        
        if not keyword:
            return jsonify({'error': 'Podaj keyword'}), 400
        
        pytrends = TrendReq(hl='pl-PL', tz=120)
        pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
        
        df = pytrends.interest_over_time()
        
        if df.empty:
            return jsonify([])
        
        df = df.reset_index()
        df['date'] = df['date'].astype(str)
        return jsonify(df.to_dict(orient='records'))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
