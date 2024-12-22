import mysql.connector
import tkinter as tk
from tkinter import ttk


def batch_insert_image_metadata(db_configuration, image_data):
    """
    Insert multiple rows into the database in one operation.
    """
    try:
        connection = mysql.connector.connect(**db_configuration)
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


def drop_database(db_name):
    my_db = mysql.connector.connect(host='localhost',
                                    user='root',
                                    password='12')
    my_cursor = my_db.cursor()
    drop_db_query = "DROP DATABASE {}".format(db_name)
    my_cursor.execute(drop_db_query)
    my_db.close()


def insert_image_metadata(db_configuration, file_path, label):
    """
    Insert metadata for an image into the MySQL database.
    """
    try:
        print("Attempting to connect to the database...")
        connection = mysql.connector.connect(**db_configuration)
        cursor = connection.cursor()
        print(f"Connected successfully. Inserting {file_path} with label {label}.")
        query = "INSERT INTO images (file_path, label) VALUES (%s, %s)"
        cursor.execute(query, (file_path, label))
        connection.commit()
        print(f"Successfully inserted {file_path} with label {label}.")
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


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
        for file_path, prediction, true_label in zip(file_paths, predictions, test_labels):
            insert_query = """
            INSERT INTO classification_results (file_path, predicted_label, true_label)
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (file_path, prediction, true_label))
        connection.commit()
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
