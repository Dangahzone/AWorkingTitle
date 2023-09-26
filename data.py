class Data(object):
    def __init__(self):
        self.rooms = {}
        self.vocabulary = {}
        self.objects = {}
        self.messages = {}
        self.class_messages = []
        self.hints = {}
        self.magic_messages = {}

    def referent(self, word):
        if word.kind == 'noun':
            return self.objects[word.n % 1000]