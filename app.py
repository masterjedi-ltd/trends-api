from flask import Flask, request, jsonify
from pytrends.request import TrendReq

app = Flask(__name__)

@app.route('/trends')
def get_trends():
    keyword = request.args.get('keyword', 'bitcoin')
    geo = request.args.get('geo', 'PL')
    timeframe = request.args.get('timeframe', 'today 3-m')
    
    pytrends = TrendReq(hl='pl-PL', tz=120)
    pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)
    
    df = pytrends.interest_over_time()
    if df.empty:
        return jsonify([])
    
    df = df.reset_index()
    df['date'] = df['date'].astype(str)
    return jsonify(df.to_dict(orient='records'))
