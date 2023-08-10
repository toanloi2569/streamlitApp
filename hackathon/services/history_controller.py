class HistoryController:
    def __init__(self):
        self.round_history = []

    def add_round_history(self, round_history):
        self.round_history.append(round_history)

    def get_latest_round_history(self):
        return self.round_history[-1]

    def get_latest_entities(self):
        for round_history in reversed(self.round_history):
            if round_history.entities:
                return round_history.entities

    def remove_expired_round_history(self):
        self.round_history = self.round_history[-10:]


class RoundHistory:
    def __init__(self, round_id, intent, entities):
        self.round_id = round_id
        self.intent = intent
        self.entities = entities
