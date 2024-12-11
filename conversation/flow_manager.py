from conversation.intent_classifier import IntentClassifier
from utils.nlp_validator import NLPValidator
from services.appointment import AppointmentService
from services.patient import PatientService
from utils.logger import logger

class ConversationManager:
    def __init__(self, db_manager):
        self.intent_classifier = IntentClassifier()
        self.appointment_service = AppointmentService(db_manager)
        self.patient_service = PatientService(db_manager)
        self.conversation_state = None
        self.current_appointment = {}
        self.current_patient = {}
        self.validator = NLPValidator()
        self.db = db_manager

    def process_input(self, user_input):
        try:
            # Check if we're in the middle of a registration flow
            if self.conversation_state and self.conversation_state.startswith('register_'):
                return self.handle_registration_flow(user_input)
                
            # Check if we're in the middle of a scheduling flow
            if self.conversation_state and self.conversation_state.startswith('scheduling_'):
                return self.handle_scheduling_flow(user_input)

            # If not in a flow, process as new intent
            intent = self.intent_classifier.classify_intent(user_input)
            logger.info(f"Classified intent: {intent}")

            if intent == 'schedule' or user_input == '1':
                self.conversation_state = 'scheduling_name'
                self.current_appointment = {}
                return "Please enter your name:"
            
            elif intent == 'services' or user_input == '2':
                return self.handle_services_query()
            
            elif intent == 'registration' or user_input == '3':
                self.conversation_state = 'register_name'
                self.current_patient = {}
                return "Welcome to patient registration! Please enter your full name:"
            
            elif intent == 'cancel' or user_input == '4':
                return self.handle_cancellation()
            
            elif intent == 'general' or user_input == '5':
                return self.handle_general_info()
            
            else:
                return self.handle_unknown()

        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return "I'm sorry, there was an error. Please try again."

    def handle_registration_flow(self, user_input):
        """Handle the registration flow states"""
        try:
            if self.conversation_state == 'register_name':
                valid, message = self.validator.validate_name(user_input)
                if not valid:
                    return message
                self.current_patient['name'] = user_input
                self.conversation_state = 'register_dob'
                return "Please enter your date of birth (DD/MM/YYYY):"
            
            elif self.conversation_state == 'register_dob':
                valid, message = self.validator.validate_date(user_input, allow_past=True)
                if not valid:
                    return message
                self.current_patient['dob'] = user_input
                self.conversation_state = 'register_phone'
                return "Please enter your phone number:"
            
            elif self.conversation_state == 'register_phone':
                valid, message = self.validator.validate_phone(user_input)
                if not valid:
                    return message
                self.current_patient['phone'] = user_input
                self.conversation_state = 'register_email'
                return "Please enter your email address:"
            
            elif self.conversation_state == 'register_email':
                valid, message = self.validator.validate_email(user_input)
                if not valid:
                    return message
                self.current_patient['email'] = user_input
                self.conversation_state = 'register_insurance'
                return "Please enter your insurance provider (or 'none' if not insured):"
            
            elif self.conversation_state == 'register_insurance':
                self.current_patient['insurance'] = user_input if user_input.lower() != 'none' else None
                return self.complete_registration()
            
        except Exception as e:
            logger.error(f"Error in registration flow: {str(e)}")
            return "There was an error processing your registration. Please try again."

    def handle_unknown(self):
        """Handle unknown or unclear inputs"""
        return """
        I'm not sure what you're asking for. Please choose from:
        1. Schedule an appointment
        2. Ask about our services
        3. Patient registration
        4. Cancel/reschedule appointment
        5. General information

        You can type the number or describe what you need.
        """

    def handle_services_query(self):
        """Handle services related queries"""
        return """
        Our Dental Services:
        ===================
        
        1. Regular Check-ups and Cleaning ($80)
           - Comprehensive examination
           - Professional cleaning
           - X-rays if needed
        
        2. Fillings and Restorations ($150-$300)
           - Tooth-colored fillings
           - Amalgam fillings
           - Inlays and onlays
        
        3. Root Canal Treatment ($800-$1200)
           - Complete procedure
           - Post-treatment care
           - Follow-up visits
        
        4. Teeth Whitening ($400)
           - Professional whitening
           - Take-home kits
           - Maintenance advice
        
        5. Dental Crowns and Bridges ($900-$1500)
           - Porcelain crowns
           - Metal crowns
           - Bridge work
        
        6. Emergency Dental Care ($200-$500)
           - Same-day appointments
           - Pain management
           - Temporary solutions
        
        Would you like to schedule an appointment for any of these services?
        """

    def handle_general_info(self):
        """Handle general information requests"""
        return """
        General Information About Our Dental Clinic:
        =========================================
        
        📍 Location: 123 Dental Street, Healthcare City
        
        ⏰ Working Hours:
        - Monday to Friday: 9:00 AM - 5:00 PM
        - Saturday: 9:00 AM - 2:00 PM
        - Sunday: Closed
        
        📞 Contact Information:
        - Phone: (555) 123-4567
        - Emergency: (555) 987-6543
        - Email: info@dentalclinic.com
        
        💳 Payment Options:
        - Most insurance plans accepted
        - Credit/Debit cards
        - Cash payments
        - Payment plans available
        
        🏥 Facilities:
        - Modern equipment
        - Sterilized environment
        - Comfortable waiting area
        - Wheelchair accessible
        
        🚗 Parking:
        - Free parking available
        - Handicap spots available
        
        Need more specific information? Feel free to ask!
        """

    def handle_cancellation(self):
        """Handle appointment cancellation requests"""
        return "Please contact our office at (555) 123-4567 to cancel or reschedule your appointment."

    def complete_registration(self):
        """Complete the registration process"""
        try:
            # Save to database
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO Patients (name, dob, phone, email, insurance)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_patient['name'],
                self.current_patient['dob'],
                self.current_patient['phone'],
                self.current_patient['email'],
                self.current_patient['insurance']
            ))
            
            conn.commit()
            conn.close()
            
            # Prepare confirmation message
            registration_details = f"""
            Registration completed successfully!
            
            Patient Details:
            ===============
            Name: {self.current_patient['name']}
            Date of Birth: {self.current_patient['dob']}
            Phone: {self.current_patient['phone']}
            Email: {self.current_patient['email']}
            Insurance: {self.current_patient['insurance'] or 'None'}
            
            Thank you for registering with our clinic!
            You can now schedule appointments using your registered information.
            """
            
            # Reset state
            self.conversation_state = None
            self.current_patient = {}
            
            return registration_details
            
        except Exception as e:
            logger.error(f"Error completing registration: {str(e)}")
            return "There was an error saving your registration. Please try again."

    def handle_scheduling_flow(self, user_input):
        """Handle the scheduling flow states"""
        try:
            if self.conversation_state == 'scheduling_name':
                valid, message = self.validator.validate_name(user_input)
                if not valid:
                    return message
                self.current_appointment['name'] = user_input
                self.conversation_state = 'scheduling_phone'
                return "Please enter your phone number:"
            
            elif self.conversation_state == 'scheduling_phone':
                valid, message = self.validator.validate_phone(user_input)
                if not valid:
                    return message
                self.current_appointment['phone'] = user_input
                self.conversation_state = 'scheduling_email'
                return "Please enter your email address:"
            
            elif self.conversation_state == 'scheduling_email':
                valid, message = self.validator.validate_email(user_input)
                if not valid:
                    return message
                self.current_appointment['email'] = user_input
                self.conversation_state = 'scheduling_date'
                return "Please enter your preferred date (DD/MM/YYYY):"
            
            elif self.conversation_state == 'scheduling_date':
                valid, message = self.validator.validate_date(user_input)
                if not valid:
                    return message
                self.current_appointment['date'] = user_input
                self.conversation_state = 'scheduling_time'
                return "Please enter your preferred time (e.g., 10:30 AM):"
            
            elif self.conversation_state == 'scheduling_time':
                valid, message = self.validator.validate_time(user_input)
                if not valid:
                    return message
                self.current_appointment['time'] = user_input
                self.conversation_state = 'scheduling_type'
                return """
                Please select the type of appointment:
                1. Regular Check-up
                2. Cleaning
                3. Emergency
                4. Consultation
                """
            
            elif self.conversation_state == 'scheduling_type':
                appointment_types = {
                    '1': 'Regular Check-up',
                    '2': 'Cleaning',
                    '3': 'Emergency',
                    '4': 'Consultation'
                }
                if user_input not in appointment_types:
                    return "Please select a valid appointment type (1-4)"
                self.current_appointment['type'] = appointment_types[user_input]
                return self.complete_appointment()
            
        except Exception as e:
            logger.error(f"Error in scheduling flow: {str(e)}")
            return "There was an error processing your request. Please try again."

    def complete_appointment(self):
        """Complete the appointment scheduling process"""
        try:
            # Save to database
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
                    self.current_appointment['phone'],
                    self.current_appointment['email']
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
            self.conversation_state = None
            self.current_appointment = {}
            
            return appointment_details
            
        except Exception as e:
            logger.error(f"Error saving appointment: {str(e)}")
            return "There was an error scheduling your appointment. Please try again."