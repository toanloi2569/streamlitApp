class IntentDetector:
    def __init__(self):
        pass

    def detect(self, text):
        intents = [
            'get_project_milestone'
        ]

        entities = {
            'project': ['ATM - eKYC ']
        }

        return intents, entities


