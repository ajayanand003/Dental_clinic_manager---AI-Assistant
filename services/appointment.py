from database.database_manager import DatabaseManager
from utils.logger import logger

class AppointmentService:
    def __init__(self, db_manager):  # Add db_manager parameter
        self.db = db_manager
        self.appointment_state = None
        self.current_appointment = {}
        
    def start_scheduling(self):
        self.appointment_state = 'get_name'
        self.current_appointment = {}
        return """
        Let's schedule your appointment.
        Please enter your name:
        """

    def handle_scheduling_input(self, user_input):
        if self.appointment_state == 'get_name':
            self.current_appointment['name'] = user_input
            self.appointment_state = 'get_phone'
            return "Please enter your phone number:"
            
        elif self.appointment_state == 'get_phone':
            self.current_appointment['phone'] = user_input
            self.appointment_state = 'get_email'
            return "Please enter your email address:"
            
        elif self.appointment_state == 'get_email':
            self.current_appointment['email'] = user_input
            self.appointment_state = 'get_date'
            return "Please enter your preferred date (DD/MM/YYYY):"
        


    def handle_scheduling(self):
        self.appointment_state = 'check_registration'
        self.current_appointment = {}
        return "Please enter your name to verify registration:"

    def process_appointment_input(self, user_input):
        if user_input.lower() in ['quit', 'cancel', 'exit']:
            self.appointment_state = None
            return "Appointment scheduling cancelled. How else can I help you?"

        if self.appointment_state == 'check_registration':
            # Check if patient exists
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM Patients WHERE name = ?', (user_input,))
            patient = cursor.fetchone()
            conn.close()

            if not patient:
                self.appointment_state = None
                return """
                You need to register as a patient first.
                Please type '3' or 'register' to start the registration process.
                """
            
            self.current_appointment['name'] = user_input
            self.appointment_state = 'date'
            return 'Please enter your preferred date (DD/MM/YYYY):'

        states = {
            'date': ('time', 'Please enter your preferred time (e.g., 10:00 AM):'),
            'time': ('type', '''
                Please select the type of appointment (enter the number):
                1. Regular Check-up
                2. Cleaning
                3. Emergency
                4. Consultation
            '''),
            'type': (None, self.complete_scheduling)
        }

        # Save current input
        if self.appointment_state == 'date':
            self.current_appointment['date'] = user_input
        elif self.appointment_state == 'time':
            self.current_appointment['time'] = user_input
        elif self.appointment_state == 'type':
            appointment_types = {
                '1': 'Regular Check-up',
                '2': 'Cleaning',
                '3': 'Emergency',
                '4': 'Consultation'
            }
            self.current_appointment['type'] = appointment_types.get(user_input, user_input)

        next_state, response = states[self.appointment_state]
        self.appointment_state = next_state

        if callable(response):
            return response()
        return response

    def complete_appointment(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # First check if patient exists
            cursor.execute('''
                SELECT id FROM Patients 
                WHERE name = ?
            ''', (self.current_appointment['name'],))
            
            patient = cursor.fetchone()
            
            # If patient doesn't exist, create new patient record
            if not patient:
                cursor.execute('''
                    INSERT INTO Patients (name, phone, email) 
                    VALUES (?, ?, ?)
                ''', (
                    self.current_appointment['name'],
                    self.current_appointment.get('phone'),
                    self.current_appointment.get('email')
                ))
                patient_id = cursor.lastrowid
            else:
                patient_id = patient[0]
            
            # Insert the appointment
            cursor.execute('''
                INSERT INTO Appointments 
                (patient_id, date, time, procedure_type)
                VALUES (?, ?, ?, ?)
            ''', (
                patient_id,
                self.current_appointment['date'],
                self.current_appointment['time'],
                self.current_appointment['type']
            ))
            
            conn.commit()
            conn.close()
            
            appointment_details = f"""
            Appointment scheduled successfully!
            
            Details:
            Name: {self.current_appointment['name']}
            Date: {self.current_appointment['date']}
            Time: {self.current_appointment['time']}
            Type: {self.current_appointment['type']}
            
            We look forward to seeing you!
            """
            
            # Reset state
            self.appointment_state = None
            self.current_appointment = {}
            
            return appointment_details
            
        except Exception as e:
            logger.error(f"Error saving appointment: {str(e)}")
            return "There was an error scheduling your appointment. Please try again."