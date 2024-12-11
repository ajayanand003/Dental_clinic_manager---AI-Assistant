import spacy
import re
from datetime import datetime, timedelta
from utils.logger import logger

class NLPValidator:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def validate_name(self, name):
        """Validate if input is a proper name"""
        if len(name.strip()) < 2:
            return False, "Name is too short. Please enter your full name."
            
        if any(char.isdigit() for char in name):
            return False, "Name should not contain numbers."
        
        # Check for obviously invalid inputs
        invalid_inputs = ['123', 'test', 'xyz', 'abc', 'none', 'nil', 'na']
        if name.lower() in invalid_inputs:
            return False, "Please enter your actual name."
        
        if re.search(r'[!@#$%^&*()_+={}\[\]|\\:;"\'<>,.?/~`]', name):
            return False, "Name should not contain special characters."
        
        return True, name.strip()

    def validate_date(self, date_str, allow_past=False):
        """Validate if input is a proper date"""
        try:
            # Clean the input
            date_str = date_str.lower().strip()
            
            # Convert various formats to standard format
            if re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
                date_str = date_str.replace('-', '/')
                if len(date_str.split('/')[0]) == 1:
                    date_str = '0' + date_str
                if len(date_str.split('/')[1]) == 1:
                    date_str = date_str.replace('/', '/0', 1)
            
            # Validate the date
            try:
                date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            except ValueError:
                return False, "Please enter date as DD/MM/YYYY (e.g., 25/12/2024)"
            
            # Check if date is in future (for appointments only)
            if not allow_past:
                if date_obj.date() <= datetime.now().date():
                    return False, "Please select a future date."
                
                # Check if date is within next year
                if date_obj.date() > datetime.now().date() + timedelta(days=365):
                    return False, "Please select a date within the next year."
            else:
                # For DOB, check if date is not in future
                if date_obj.date() > datetime.now().date():
                    return False, "Date of birth cannot be in the future."
                
                # Check if age is reasonable (e.g., less than 150 years)
                age = (datetime.now().date() - date_obj.date()).days / 365
                if age > 150:
                    return False, "Please enter a valid date of birth."
                
            return True, date_str
        
        except Exception as e:
            logger.error(f"Date validation error: {str(e)}")
            return False, "Please enter a valid date"

    def validate_time(self, time_str):
        """Validate if input is a proper time"""
        try:
            # Clean the input
            time_str = time_str.lower().strip()
            
            # Only accept proper time formats
            if not re.match(r'\d{1,2}(?::\d{2})?\s*(?:am|pm)', time_str):
                return False, "Please enter time as HH:MM AM/PM (e.g., 10:30 AM)"
            
            # Convert to standard format if minutes not specified
            if ':' not in time_str:
                time_str = time_str.replace('am', ':00 am').replace('pm', ':00 pm')
                
            # Validate the time
            try:
                time_obj = datetime.strptime(time_str, '%I:%M %p')
            except ValueError:
                return False, "Please enter time as HH:MM AM/PM (e.g., 10:30 AM)"
            
            # Check business hours (9 AM to 5 PM)
            hour = time_obj.hour
            if hour < 9 or hour >= 17:
                return False, "Please select a time between 9 AM and 5 PM"
            
            return True, time_str.upper()
            
        except Exception as e:
            logger.error(f"Time validation error: {str(e)}")
            return False, "Please enter a valid time (e.g., 10:30 AM)"

    def validate_phone(self, phone):
        """Validate if input is a proper phone number"""
        # Clean the input
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Handle international format
        if phone.startswith('+'):
            if not re.match(r'^\+\d{1,3}\d{10}$', phone):
                return False, "Please enter a valid phone number with country code (e.g., +911234567890)"
        else:
            # Handle local format
            if not re.match(r'^\d{10}$', phone):
                return False, "Please enter a 10-digit phone number"
        
        return True, phone

    def validate_email(self, email):
        """Validate if input is a proper email"""
        # Basic cleaning
        email = email.lower().strip()
        
        # Check format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Please enter a valid email address (e.g., name@example.com)"
            
        # Check common domains
        common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        domain = email.split('@')[1]
        if domain not in common_domains and not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            # If not common domain, do additional validation
            if not self.validate_domain_format(domain):
                return False, "Please enter a valid email domain"
        
        return True, email

    def validate_domain_format(self, domain):
        """Helper method to validate email domain format"""
        parts = domain.split('.')
        return (
            len(parts) >= 2 and
            all(part.isalnum() or '-' in part for part in parts) and
            len(parts[-1]) >= 2
        )