from database.database_manager import DatabaseManager
from utils.logger import logger

class PatientService:
    def __init__(self, db_manager):  # Add db_manager parameter
        self.db = db_manager
        self.registration_state = None
        self.current_patient = {}

    def register_patient(self, patient_data):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO Patients 
                (name, dob, phone, email, insurance)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                patient_data['name'],
                patient_data['dob'],
                patient_data['phone'],
                patient_data['email'],
                patient_data['insurance']
            ))
            
            conn.commit()
            conn.close()
            
            return True, "Patient registered successfully!"
            
        except Exception as e:
            logger.error(f"Error registering patient: {str(e)}")
            return False, "Error registering patient. Please try again."