import os
from dotenv import load_dotenv
import sqlite3

import psycopg2
from flask import Flask,jsonify

app = Flask(__name__)
load_dotenv()
@app.route("/")
def home():
    return jsonify({
        'message': 'Student Management API',
        'endpoints': {
            'GET /api/students': 'Get all students',
            'GET /api/students/<id>': 'Get specific student',
            'POST /api/students': 'Create new student',
            'PUT /api/students/<id>': 'Update student',
            'DELETE /api/students/<id>': 'Delete student',
            'GET /api/students/dietary/<need>': 'Filter by dietary needs'
        }
    })


@app.route('/api/students', methods=['GET'])
def get_all_students():
    statement = "SELECT * FROM students ORDER BY id"
    try:
        with psycopg2.connect(os.getenv('db_url')) as conn:
            with conn.cursor() as cursor:
                cursor.execute(statement)
                students = cursor.fetchall()

                return jsonify(students)

    except psycopg2.Error as e:
        print(jsonify({'database error': str(e)})),500
    except Exception as e:
        return jsonify({'Run time Error': str(e)}),500

@app.route("/api/students/<student_id>", methods=['GET'])
def get_student(student_id):
    statement = f"SELECT * FROM students WHERE id = %s"
    if student_id.isdigit() == False:
        return jsonify({"Invalid student ID": student_id}), 404
    try:
        with psycopg2.connect(os.getenv('db_url')) as conn:
            with conn.cursor() as cursor:
                cursor.execute(statement,(student_id,))
                students = cursor.fetchone()
                if students is None:
                    return jsonify({'database error': 'Student not found'}), 404
                return jsonify(students)

                cursor.close()
                conn.close()
                return jsonify(students)

    except psycopg2.Error as e:
        print(jsonify({'database error': str(e)})),500
    except Exception as e:
        return jsonify({'Run time Error': str(e)}),500



def setup():
    ##create table
    table = """CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT,
            surname TEXT,
            age INTEGER,
            level INTEGER
    );
    """
    insert_statement = """INSERT INTO students (id, name, surname, age, level) VALUES (%s, %s, %s, %s, %s)"""
    sample_data = [
        (1, "amanda", "Moloi", 2, 1),
        (2, "Tshitshi", "Mofokeng", 5, 3),
        (3, "Tshepang", "Diekedi", 4, 2)
    ]

    try:
        with psycopg2.connect(os.getenv("db_url")) as conn:
            print("connected to database")
            with conn.cursor() as cursor:
                cursor.execute(table)
                cursor.executemany(insert_statement, sample_data)
                conn.commit()
                print("Table created successfully")

    except psycopg2.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"Something went wrong: {e}")



if __name__ == "__main__":
    # setup()
    app.run(debug=True)
