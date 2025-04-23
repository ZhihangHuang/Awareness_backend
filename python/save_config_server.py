from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/save-config', methods=['POST'])
def save_config():
    config = request.json
    save_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(save_path, "w") as f:
        json.dump(config, f, indent=2)
    print("✅ 已接收到配置：", config)
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
