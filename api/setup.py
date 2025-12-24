import os

import psycopg2


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

