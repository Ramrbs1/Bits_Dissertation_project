from flask import Flask, jsonify, request, render_template
from psycopg2 import connect
from prometheus_flask_exporter import PrometheusMetrics
import os
from faker import Faker

app = Flask(__name__)
metrics = PrometheusMetrics(app)
fake = Faker()  # Create a Faker instance


def get_db_connection():
    try:
        conn = connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host='postgres-service'
        )
        return conn
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return None

@app.route('/')
def home():
    #return "Welcome to the Flask App!"
    return render_template('index.html')  # Serve the index.html file

@app.route('/insert-random-row', methods=['POST'])
def insert_random_row():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Generate random name and address
        name = fake.name()
        address = fake.address()

        # Insert statement with randomly generated values
        insert_query = "INSERT INTO test_table (name, address) VALUES (%s, %s);"
        values_to_insert = (name, address)

        # Execute the INSERT statement
        cursor.execute(insert_query, values_to_insert)

        # Commit the transaction
        conn.commit()

        # Optionally, get the count of rows after the insert
        cursor.execute("SELECT count(*) FROM test_table;")
        count = cursor.fetchone()[0]

        cursor.close()
        return jsonify({"message": "Random row inserted successfully!", "row_count": count}), 201
    except Exception as e:
        app.logger.error(f"Insert operation failed: {e}")
        return jsonify({"error": "Insert operation failed"}), 500
    finally:
        conn.close()

@app.route('/fetch-rows', methods=['POST'])
def fetch_rows():
    num_rows = request.form.get('num_rows', type=int)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM test_table LIMIT %s;", (num_rows,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"rows": rows})


@app.route('/row-count', methods=['GET'])
def get_row_count():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM test_table;")
        count = cursor.fetchone()[0]
        
        cursor.close()
        return jsonify({"row_count": count}), 200
    except Exception as e:
        app.logger.error(f"Failed to get row count: {e}")
        return jsonify({"error": "Failed to get row count"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
