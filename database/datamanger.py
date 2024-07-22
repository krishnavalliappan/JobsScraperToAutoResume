import mysql.connector
from mysql.connector import Error
import os
import sys

# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, current_dir)

class DataManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            # First, connect to MySQL server without specifying a database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                
                # Check if the database exists
                self.cursor.execute(f"SHOW DATABASES LIKE '{self.database}'")
                result = self.cursor.fetchone()
                
                if not result:
                    # Create the database if it doesn't exist
                    self.cursor.execute(f"CREATE DATABASE {self.database}")
                    print(f"Database '{self.database}' created successfully.")
                
                # Connect to the specific database
                self.connection.database = self.database
                print(f"Connected to database '{self.database}'.")
        
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("MySQL connection closed.")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
            print("Query executed successfully.")
        except Error as e:
            print(f"Error executing query: {e}")

    # Add more methods for database operations as needed
