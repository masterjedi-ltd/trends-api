from flask import Flask, request, jsonify
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/trends')
def get_trends():
    keyword = request.args.get('keyword', '')
    geo = request.args.get('geo', 'PL')
    timeframe = request.args.get('timeframe', 'now 1-d')
    
    pytrends = TrendReq(hl='pl-PL', tz=120)
    
    # Jeśli brak keyword → zwróć trending searches
    if not keyword:
        trending = pytrends.trending_searches(pn='poland')
        return jsonify(trending[0].tolist())
    
    # Jeśli jest keyword → interest over time
    pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    
    if df.empty:
        return jsonify([])
    
    df = df.reset_index()
    df['date'] = df['date'].astype(str)
    return jsonify(df.to_dict(orient='records'))
