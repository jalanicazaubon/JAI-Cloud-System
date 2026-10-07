from flask import Flask, jsonify
import logging
from routes.task_routes import task_routes
from routes.schedule_routes import schedule_routes

app = Flask(__name__)

app.register_blueprint(task_routes)

app.register_blueprint(schedule_routes)

@app.route('/')
def index():
    return jsonify({"message": "JAI API SERVER IS RUNNING"})

@app.route('/health', methods=['GET'])
def health_check():
    logging.info("Health check")
    return jsonify({"status": "healthy!"}), 200

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True    
    )