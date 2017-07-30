import select


class poll:
    def __init__(self):
        self.nested = select.poll()

    def register(self, sock, events):
        self.nested.register(sock, events)

    def unregister(self, sock):
        self.nested.unregister(sock)

    def ipoll(self, timeout):
        return self.nested.poll(1)