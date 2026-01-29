from flask import Flask, request, jsonify
from pytrends.request import TrendReq
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/')
def home():
    return 'API działa! Użyj /trends?keyword=bitcoin lub /trending'

@app.route('/trending')
def get_trending():
    try:
        geo = request.args.get('geo', 'PL')
        url = f'https://trends.google.com/trending/rss?geo={geo}'
        
        response = requests.get(url)
        root = ET.fromstring(response.content)
        
        items = []
        for item in root.findall('.//item'):
            title = item.find('title').text
            traffic = item.find('{https://trends.google.com/trending/rss}approx_traffic').text
            items.append({
                'keyword': title,
                'traffic': traffic
            })
        
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
