from flask import Flask, request, jsonify
from pytrends.request import TrendReq
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/')
def home():
    return 'API działa!'

@app.route('/trending')
def get_trending():
    try:
        geo = request.args.get('geo', 'PL')
        
        url = f'https://trends.google.com/trending/rss?geo={geo}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': f'Status: {response.status_code}'}), 500
        
        root = ET.fromstring(response.content)
        
        ns = {'ht': 'https://trends.google.com/trending/rss'}
        
        items = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            traffic = item.find('ht:approx_traffic', ns)
            traffic_text = traffic.text if traffic is not None else 'N/A'
            
            items.append({
                'keyword': title,
                'traffic': traffic_text
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
