from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import datetime
import time

app = Flask(__name__)

# -------- YOUR DATABASE CONFIG --------
DB_CONFIG = {
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    "port": 4000,
    "user": "ax6KHc1BNkyuaor.root",
    "password": "EP8isIWoEOQk7DSr",
    "database": "sensor"
}

API_KEY = "12b5112c62284ea0b3da0039f298ec7a85ac9a1791044052b6df970640afb1c5"

# -------- GLOBAL STATUS --------
esp_connected = False
collect_data = False
last_seen = 0


# -------- DB CONNECTION --------
def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# -------- HOME --------
@app.route("/")
def home():
    return render_template("index.html")


# -------- RECEIVE DATA --------
  @app.route("/api/data")
def receive_data():
    global esp_connected, last_seen, collect_data

    key = request.args.get("key")
    if key != API_KEY:
        return "Invalid Key", 403

    esp_connected = True
    last_seen = time.time()

    if not collect_data:
        return "Stopped"

    try:
        s1 = float(request.args.get("s1", 0))
        s2 = float(request.args.get("s2", 0))
        s3 = float(request.args.get("s3", 0))
    except:
        return "Invalid sensor values"

    try:
        db = get_db()
        cursor = db.cursor()

       sql = "INSERT INTO sensor_db (sensor1, sensor2, sensor3) VALUES (%s, %s, %s)"

        db.commit()
        cursor.close()
        db.close()

        return "Saved"

    except Exception as e:
        return str(e)  
    except Exception as e:
        return str(e)


# -------- START --------
@app.route("/start")
def start():
    global collect_data
    collect_data = True
    return "Started"


# -------- STOP --------
@app.route("/stop")
def stop():
    global collect_data
    collect_data = False
    return "Stopped"


# -------- STATUS --------
@app.route("/status")
def status():
    global esp_connected

    if time.time() - last_seen > 10:
        esp_connected = False

    return jsonify({
        "status": "Connected" if esp_connected else "Disconnected"
    })


# -------- GET DATA --------
@app.route("/data")
def get_data():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM sensor_db ORDER BY id DESC LIMIT 100")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)


# -------- DATE SEARCH --------
@app.route("/search", methods=["POST"])
def search():
    start = request.form.get("start")
    end = request.form.get("end")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT * FROM sensor_db 
    WHERE date BETWEEN %s AND %s
    ORDER BY id DESC
    """

    cursor.execute(query, (start, end))
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)

# -------- CUSTOM QUERY --------
@app.route("/query", methods=["POST"])
def query():
    sql = request.form["query"]

    if not sql.lower().startswith("select"):
        return "Only SELECT allowed"

    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(sql)
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
