from flask import Flask, request, jsonify
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/')
def home():
    return 'API działa! Użyj /trends?keyword=bitcoin'

@app.route('/trends')
def get_trends():
    try:
        keyword = request.args.get('keyword', '')
        geo = request.args.get('geo', 'PL')
        timeframe = request.args.get('timeframe', 'now 1-d')
        
        if not keyword:
            return jsonify({'error': 'Podaj keyword, np. /trends?keyword=bitcoin'}), 400
        
        pytrends = TrendReq(hl='pl-PL', tz=120, retries=3, backoff_factor=1)
        pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
        
        df = pytrends.interest_over_time()
        
        if df.empty:
            return jsonify([])
        
        df = df.reset_index()
        df['date'] = df['date'].astype(str)
        return jsonify(df.to_dict(orient='records'))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
