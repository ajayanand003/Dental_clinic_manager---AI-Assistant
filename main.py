from database.database_manager import DatabaseManager
from conversation.flow_manager import ConversationManager
from services.doctor_portal import DoctorPortal
from utils.logger import logger
import os

def initialize_database():
    try:
        # Create new database and tables if they don't exist
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        cursor = conn.cursor()

        # Create Patients table if it doesn't exist
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

        # Create Appointments table if it doesn't exist
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
        logger.info("Database initialized successfully")
        return db_manager

    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise e
def display_welcome_menu():
    return """
    Welcome to Our Dental Clinic! 👋
    ===============================
    
    Please select your role:
    1. Patient
    2. Doctor
    
    Type '1' for Patient Services or '2' for Doctor Portal
    Type 'quit' to exit.
    ===============================
    """

def display_patient_menu():
    return """
    Our Services:
    -------------
    1. Regular Check-ups and Cleaning ($80)
    2. Fillings and Restorations ($150-$300)
    3. Root Canal Treatment ($800-$1200)
    4. Teeth Whitening ($400)
    5. Dental Crowns and Bridges ($900-$1500)
    6. Emergency Dental Care ($200-$500)

    How can we help you today?
    -------------------------
    1. Schedule an appointment
    2. Ask about our services
    3. Patient registration
    4. Cancel/reschedule appointment
    5. General information

    You can type the number or describe what you need.
    Type 'quit' to exit.
    ===============================
    """

def display_doctor_menu():
    return """
    Doctor Portal
    ============
    1. Search patient by name
    2. Search patient by phone number
    3. View all appointments for a date
    4. View patient history
    5. Return to main menu

    Type the number of your choice.
    Type 'quit' to exit.
    ===============================
    """

def main():
    try:
        # Initialize database first
        db_manager = initialize_database()
        
        # Initialize services with database manager
        conversation_manager = ConversationManager(db_manager)  # Pass db_manager here
        doctor_portal = DoctorPortal(db_manager)
        
        while True:
            print(display_welcome_menu())
            role = input("\nSelect role (1/2): ").strip()
            
            if role.lower() == 'quit':
                print("\nThank you for using our service. Have a great day! 👋")
                break
                
            if role == '1':  # Patient
                print(display_patient_menu())
                while True:
                    user_input = input("\nUser: ").strip()
                    if user_input.lower() in ['quit', 'back', 'return']:
                        break
                    response = conversation_manager.process_input(user_input)
                    print(f"\nAssistant: {response}")
                    
            elif role == '2':  # Doctor
                while True:
                    print(display_doctor_menu())
                    choice = input("\nDoctor: ").strip()
                    if choice.lower() in ['quit', 'back', 'return']:
                        break
                    response = doctor_portal.process_request(choice)
                    print(f"\n{response}")
            else:
                print("\nInvalid selection. Please choose 1 for Patient or 2 for Doctor.")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print("An error occurred. Please try again.")

if __name__ == "__main__":
    main()