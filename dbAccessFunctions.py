import os
import mysql.connector
import tkinter as tk
from tkinter import ttk


def batch_insert_image_metadata(db_configur, image_data):
    """
    Insert multiple rows into the database in one operation.
    """
    try:
        connection = mysql.connector.connect(**db_configur)
        cursor = connection.cursor()
        query = "INSERT INTO images (file_path, label) VALUES (%s, %s)"
        cursor.executemany(query, image_data)
        connection.commit()
        print(f"Successfully inserted {len(image_data)} rows.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        if connection:
            connection.close()


def create_database(db_name):
    my_db = mysql.connector.connect(host='localhost',
                                    user='root',
                                    password='12')
    my_cursor = my_db.cursor()
    create_db_query = "CREATE DATABASE IF NOT EXISTS {}".format(db_name)
    my_cursor.execute(create_db_query)
    my_db.close()


db_configuration = {
    "host": os.environ.get("MyDB_HOST", "localhost"),
    "user": os.environ.get("MyDB_USER", "root"),
    "password": os.environ.get("MyDB_PASSWORD", ""),
    "database": "reflask",
    "use_pure": "True"
}


def drop_database(db_name):
    my_db = mysql.connector.connect(host='localhost',
                                    user='root',
                                    password='12')
    my_cursor = my_db.cursor()
    drop_db_query = "DROP DATABASE {}".format(db_name)
    my_cursor.execute(drop_db_query)
    my_db.close()


def fetch_processed_files():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT file_name FROM predicted_images")
    processed_files = {row[0] for row in cursor.fetchall()}
    cursor.close()
    connection.close()
    return processed_files


def get_db_connection(**db_konf):
    return mysql.connector.connect(**db_konf)


def insert_image_metadata(db_konf_iim, file_path, label):
    """
    Insert metadata for an image into the MySQL database only if it does not already exist.
    """
    try:
        connection = mysql.connector.connect(**db_konf_iim)
        cursor = connection.cursor()
        # Checking if the file_path already exists
        check_query = "SELECT COUNT(*) FROM images WHERE file_path = %s"
        cursor.execute(check_query, (file_path,))
        result = cursor.fetchone()
        if result[0] > 0:
            print(f"File {file_path} already exists in the database. Skipping insertion.")
        else:
            # Insert the new image metadata
            insert_query = "INSERT INTO images (file_path, label) VALUES (%s, %s)"
            cursor.execute(insert_query, (file_path, label))
            connection.commit()
            print(f"Successfully inserted {file_path} with label {label}.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        if connection:
            connection.close()


def print_table_data(database_name, table_name):
    my_db = mysql.connector.connect(host='localhost',
                                    user='root',
                                    password='12',
                                    database=database_name)
    my_cursor = my_db.cursor()
    query = "SELECT * FROM {}".format(table_name)
    my_cursor.execute(query)
    print("Records of table {}".format(table_name))
    for i in my_cursor.description:
        print(i[0])
    for record in my_cursor.fetchall():
        print(record)
    my_db.close()


def save_processed_file(file_name):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO predicted_images (file_name, prediction_date) VALUES (%s, NOW())",
        (file_name,)
    )
    connection.commit()
    cursor.close()
    connection.close()


def show_table_data(database_name, table_name):
    my_db = mysql.connector.connect(host='localhost',
                                    user='root',
                                    password='12',
                                    database=database_name)
    my_cursor = my_db.cursor()
    query = "SELECT * FROM {}".format(table_name)
    my_cursor.execute(query)
    columns = [i[0] for i in my_cursor.description]
    table_data = my_cursor.fetchall()
    # Create GUI
    root = tk.Tk()
    root_title = "Table {}".format(table_name)
    # Create table
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)
    for row in table_data:
        tree.insert('', "end", values=row)
    # Start GUI
    root.mainloop()
    my_db.close()


def store_results_to_db(db_config, predictions, test_labels, file_paths):
    """
    Store classification results into the database.
    """
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        # Validating input lengths
        if len(file_paths) != len(predictions) or len(file_paths) != len(test_labels):
            raise ValueError("Mismatch in lengths of file_paths, predictions, and test_labels.")
        for file_path, prediction, true_label in zip(file_paths, predictions, test_labels):
            insert_query = """
                INSERT INTO classification_results (file_path, predicted_label, true_label)
                VALUES (%s, %s, %s)
                """
            cursor.execute(insert_query, (file_path, int(prediction), int(true_label)))
            print(f"Inserted: {file_path}, Predicted: {prediction}, True: {true_label}")  # Debug log
        connection.commit()
        print(f"Successfully stored {len(predictions)} results.")
    except Exception as db_error:
        print(f"Error storing results to database: {db_error}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def update_image_processed_status(db_configuration, image_id, processed=True):
    try:
        connection = mysql.connector.connect(**db_configuration)
        cursor = connection.cursor()
        query = "UPDATE images SET processed = %s WHERE id = %s"
        cursor.execute(query, (processed, image_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection:
            connection.close()
