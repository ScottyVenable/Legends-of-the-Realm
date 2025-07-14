"""
Dialogue system for managing conversations and interactions.
"""


class Dialogue:
    def __init__(self, text, responses=None, action=None, id=None, speaker=None, options=None, conditions=None):
        self.text = text
        self.responses = responses if responses is not None else []
        self.action = action
        self.id = id
        self.speaker = speaker
        self.options = options if options is not None else []
        self.conditions = conditions if conditions is not None else []
