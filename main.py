import base64

class Server:
    def __init__(self):
        self.encrypted_message = None

    def encrypt(self, message):
        self.encrypted_message = base64.b64encode(message.encode('utf-8'))
    def decrypt(self):
        if self.encrypted_message:
            decrypted_message = base64.b64decode(self.encrypted_message).decode('utf-8')
            return decrypted_message
        return None

class Client:
    def __init__(self, server_instance):
        self.server = server_instance
        self.message = None

    def send_message(self):
        self.message = input(">> ")
        if self.message.lower() == "exit":
            print("Goodbye!")
            return False
        self.server.encrypt(self.message)
        return True

    def receive_message(self):
        decrypted = self.server.decrypt()
        if decrypted:
            print(f"{decrypted}")

server = Server()
client = Client(server)

while True:
    if not client.send_message():
        break
    client.receive_message()
    print("-" * 20)