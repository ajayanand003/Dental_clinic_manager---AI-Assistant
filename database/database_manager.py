import sqlite3
from utils.logger import logger

class DatabaseManager:
    def __init__(self):
        self.db_path = 'dental_clinic.db'
        self.initialize_database()  # Call this in constructor

    def initialize_database(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create Patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    dob TEXT,
                    phone TEXT,
                    email TEXT,
                    insurance TEXT
                )
            ''')

            # Create Appointments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    procedure_type TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES Patients(id)
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Database tables created successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise e

    def get_connection(self):
        return sqlite3.connect(self.db_path)