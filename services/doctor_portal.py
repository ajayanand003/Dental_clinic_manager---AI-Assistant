from utils.logger import logger

class DoctorPortal:
    def __init__(self, db_manager):
        self.db = db_manager

    def search_patient(self, name):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get patient details and their appointments
            cursor.execute('''
                SELECT 
                    p.name,
                    p.dob,
                    p.phone,
                    p.email,
                    p.insurance,
                    a.date,
                    a.time,
                    a.procedure_type
                FROM Patients p
                LEFT JOIN Appointments a ON p.id = a.patient_id
                WHERE p.name LIKE ?
            ''', (f'%{name}%',))  # Using LIKE for partial matches
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return "No patients found with that name."
                
            # Format the output
            output = "\nPatient Details:\n================"
            current_name = None
            
            for row in results:
                if current_name != row[0]:  # New patient
                    current_name = row[0]
                    output += f"""
                    Name: {row[0]}
                    DOB: {row[1] or 'Not provided'}
                    Phone: {row[2] or 'Not provided'}
                    Email: {row[3] or 'Not provided'}
                    Insurance: {row[4] or 'Not provided'}
                    """
                    output += "\nAppointments:\n-------------"
                    
                if row[5]:  # If there's an appointment
                    output += f"""
                    Date: {row[5]}
                    Time: {row[6]}
                    Type: {row[7]}
                    -------------"""
                    
            return output
            
        except Exception as e:
            logger.error(f"Error searching patient: {str(e)}")
            return "Error searching for patient."

    def process_request(self, choice):
        try:
            if choice == '1':
                name = input("Enter patient name: ")
                return self.search_patient(name)
            elif choice == '2':
                phone = input("Enter patient phone number: ")
                return self.search_by_phone(phone)
            elif choice == '3':
                date = input("Enter date (DD/MM/YYYY): ")
                return self.view_appointments_by_date(date)
            elif choice == '4':
                name = input("Enter patient name: ")
                return self.view_patient_history(name)
            elif choice == '5':
                return "Returning to main menu..."
            else:
                return "Invalid choice. Please try again."
                
        except Exception as e:
            logger.error(f"Error in doctor portal: {str(e)}")
            return "An error occurred. Please try again."

    def search_by_phone(self, phone):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.name,
                    p.dob,
                    p.phone,
                    p.email,
                    p.insurance,
                    a.date,
                    a.time,
                    a.procedure_type
                FROM Patients p
                LEFT JOIN Appointments a ON p.id = a.patient_id
                WHERE p.phone LIKE ?
            ''', (f'%{phone}%',))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return "No patients found with that phone number."
                
            # Format output similar to search_patient
            output = "\nPatient Details:\n================"
            current_phone = None
            
            for row in results:
                if current_phone != row[2]:  # New patient
                    current_phone = row[2]
                    output += f"""
                    Name: {row[0]}
                    DOB: {row[1] or 'Not provided'}
                    Phone: {row[2]}
                    Email: {row[3] or 'Not provided'}
                    Insurance: {row[4] or 'Not provided'}
                    """
                    output += "\nAppointments:\n-------------"
                    
                if row[5]:  # If there's an appointment
                    output += f"""
                    Date: {row[5]}
                    Time: {row[6]}
                    Type: {row[7]}
                    -------------"""
                    
            return output
            
        except Exception as e:
            logger.error(f"Error searching by phone: {str(e)}")
            return "Error searching for patient."

    def view_appointments_by_date(self, date):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.name,
                    p.phone,
                    p.email,
                    a.time,
                    a.procedure_type
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.id
                WHERE a.date = ?
                ORDER BY a.time
            ''', (date,))
            
            appointments = cursor.fetchall()
            conn.close()
            
            if not appointments:
                return f"\nNo appointments found for {date}"
            
            output = f"\nAppointments for {date}:\n========================="
            for apt in appointments:
                output += f"""
                Patient: {apt[0]}
                Contact: {apt[1] or 'Not provided'}
                Email: {apt[2] or 'Not provided'}
                Time: {apt[3]}
                Procedure: {apt[4]}
                -------------------------"""
                
            return output
            
        except Exception as e:
            logger.error(f"Error viewing appointments: {str(e)}")
            return "Error retrieving appointments."

    def view_patient_history(self, name):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    p.name,
                    p.dob,
                    p.phone,
                    p.email,
                    p.insurance,
                    a.date,
                    a.time,
                    a.procedure_type
                FROM Patients p
                LEFT JOIN Appointments a ON p.id = a.patient_id
                WHERE p.name LIKE ?
                ORDER BY a.date DESC
            ''', (f'%{name}%',))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                return "No patient history found."
                
            output = "\nPatient History:\n================"
            current_name = None
            
            for row in results:
                if current_name != row[0]:  # New patient
                    current_name = row[0]
                    output += f"""
                    Name: {row[0]}
                    DOB: {row[1] or 'Not provided'}
                    Phone: {row[2] or 'Not provided'}
                    Email: {row[3] or 'Not provided'}
                    Insurance: {row[4] or 'Not provided'}
                    """
                    output += "\nAppointment History:\n------------------"
                    
                if row[5]:  # If there's an appointment
                    output += f"""
                    Date: {row[5]}
                    Time: {row[6]}
                    Type: {row[7]}
                    ------------------"""
                    
            return output
            
        except Exception as e:
            logger.error(f"Error viewing patient history: {str(e)}")
            return "Error retrieving patient history."