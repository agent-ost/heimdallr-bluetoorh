import re


class EventParser:
    """I can parser line based inputs and emit events"""

    def __print(self, event):
        print self.name + '-Got event:', event

    def __init__(self, name):
        self.buffer = ''
        self.callbacks = {}
        self.default = self.__print
        self.name = name

    def consume(self, data):
        self.buffer += data
        parts = re.split('[\r\n]+', self.buffer)

        print parts
        if len(parts) > 1:
            self.buffer = parts.pop()
            for event in parts:
                self.__handle(event)

    def __handle(self, event):
        if event:
            self.callbacks.get(event, self.default)(event)

    def handlers(self, callbacks):
        self.callbacks = callbacks

