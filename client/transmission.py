class Protocol:
    def __init__(self, session, first_packet):
        self.session = session
        self.package_info = first_packet['data']
