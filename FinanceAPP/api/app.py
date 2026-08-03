from common.DatabaseManager import DatabaseManager
from flask import Flask, jsonify
import json

app =  Flask(__name__)
db = DatabaseManager()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    anomalies_list = db.get_anomalies()
    return jsonify(anomalies_list)

if __name__ == '__main__':
    app.run(debug=True, port=5000)