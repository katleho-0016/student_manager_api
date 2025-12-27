import os
from dotenv import load_dotenv
import sqlite3

import psycopg2
from flask import Flask, jsonify, request
from rate_limiter import rate_limit

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


@rate_limit(60, 60)
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

@rate_limit(30, 60)
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


@rate_limit(20, 60)
@app.route("/api/students/add_student", methods=['POST'])
def add_student():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

        # 2. Check required fields
    required_fields = ['id', 'name', 'age', 'email', 'grade']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # 3. Type validation
    try:
        student_id = int(data['id'])
        age = int(data['age'])
        surname = str(data['surname'])
        name = str(data['name']).strip()
        level = int(data['level'])

    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid Parameters'}), 400

    statement = f"INSERT INTO students VALUES (%s,%s,%s,%s,%s)"
    params = (student_id,name,surname,age,level)
    try:
        with psycopg2.connect(os.getenv('db_url')) as conn:
            with conn.cursor() as cursor:
                cursor.execute(statement,params)
                cursor.close()
                conn.close()
                return jsonify("Student added successfully"),200

    except psycopg2.Error as e:
        print(jsonify({'database error': str(e)})),500
    except Exception as e:
        return jsonify({'Run time Error': str(e)}),500


@rate_limit(30, 60)
@app.route("/api/students/<int:student_id>", methods=['DELETE'])
def delete_student(student_id):
    """
    DELETE /api/students/123
    """
    statement = "DELETE FROM students WHERE id = %s"

    try:
        with psycopg2.connect(os.getenv('db_url')) as conn:
            with conn.cursor() as cursor:
                cursor.execute(statement, (student_id,))
                rows_deleted = cursor.rowcount
                conn.commit()

                if rows_deleted == 0:
                    return jsonify({'error': 'Student not found'}), 404

                return jsonify({
                    'message': 'Student deleted successfully',
                    'id': student_id
                }), 200

    except psycopg2.Error as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == "__main__":
    app.run(debug=True)
