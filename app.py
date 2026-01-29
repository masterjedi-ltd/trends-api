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
        
        url = f'https://trends.google.com/trends/api/dailytrends?hl=pl&tz=-120&geo={geo}&ns=15'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        # Debug
        if response.status_code != 200:
            return jsonify({'error': f'Status: {response.status_code}', 'body': response.text[:500]}), 500
        
        text = response.text
        
        # Usuń prefix ")]}'"
        if text.startswith(")]}'"):
            text = text[5:]
        
        data = json.loads(text)
        
        items = []
        for day in data.get('default', {}).get('trendingSearchesDays', []):
            for search in day.get('trendingSearches', []):
                title = search.get('title', {}).get('query', '')
                traffic = search.get('formattedTraffic', 'N/A')
                
                items.append({
                    'keyword': title,
                    'traffic': traffic
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
        
        url = f'https://trends.google.com/trends/api/realtimetrends?hl=pl&tz=-120&geo={geo}&cat=all&fi=0&fs=0&ri=300&rs=20&sort=0'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        # Debug
        if response.status_code != 200:
            return jsonify({'error': f'Status: {response.status_code}', 'body': response.text[:500]}), 500
        
        text = response.text
        
        if text.startswith(")]}'"):
            text = text[5:]
        
        data = json.loads(text)
        
        items = []
        for story in data.get('storySummaries', {}).get('trendingStories', []):
            title = story.get('title', '')
            
            items.append({
                'title': title
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
