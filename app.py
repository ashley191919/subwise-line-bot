from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "SubWise Backend is running!"
    })
    
if __name__ == "__main__":
    app.run(debug=True)