from queue import SimpleQueue


class Action:
    def __init__(self):
        pass


class Histroy:
    def __init__(self):
        self.queue = SimpleQueue()

    def put(self, action: Action):
        self.queue.put(action)

    def get(self):
        return self.queue.get()
