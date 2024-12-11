import os

# Get the base directory of your project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOG_DIR, 'dental_clinic.log')

# Database path
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'dental_clinic.db')

# Cohere API Key
COHERE_API_KEY = "your-cohere-api-key"