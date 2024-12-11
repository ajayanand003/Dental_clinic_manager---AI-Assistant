class IntentClassifier:
    def __init__(self):
        self.intents = {
            'schedule': [
                'schedule', 'book', 'make', 'set', 'appointment', '1',
                'schedule appointment', 'book appointment'
            ],
            'services': [
                'services', 'treatments', 'offer', 'provide', '2',
                'what services', 'dental services', 'what do you offer'
            ],
            'service_details': [
                'checkup', 'cleaning', 'root canal', 'whitening', 'crowns',
                'emergency', '1', '2', '3', '4', '5', '6'
            ],
            'patient_info': [
                'register', 'new patient', 'registration', '3',
                'patient registration', 'sign up'
            ],
            'cancel': [
                'cancel appointment', 'reschedule', 'change appointment',
                'cancel my appointment'
            ],
            'general': [
                'general', 'information', 'hours', 'location', '5',
                'contact', 'insurance', 'payment', 'address'
            ]
        }

    def classify_intent(self, text):
        # Convert input to lowercase for better matching
        text = text.lower().strip()
        
        # Define intent patterns
        intent_patterns = {
            'schedule': ['schedule', 'book', 'appointment', '1'],
            'services': ['services', 'treatments', 'costs', '2'],
            'registration': ['register', 'registration', 'new patient', '3'],
            'cancel': ['cancel', 'reschedule', 'change', '4'],
            'general': ['general', 'information', 'about', 'contact', '5']
        }
        
        # Check for exact number matches first
        if text in ['1', '2', '3', '4', '5']:
            return list(intent_patterns.keys())[int(text) - 1]
            
        # Check each intent pattern
        for intent, patterns in intent_patterns.items():
            if any(pattern in text for pattern in patterns):
                return intent
                
        return 'unknown'