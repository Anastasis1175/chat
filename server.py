import socket
import threading
import json
import os
import base64

HOST = '0.0.0.0'
PORT = 65432

clients = []
client_usernames = {}
lock = threading.Lock()

class Credentials:
    def __init__(self):
        self.accounts_file = "accounts.json"
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading accounts file: {e}. Starting with empty accounts.")
                return {}
        else:
            return {}

    def save_accounts(self):
        try:
            with open(self.accounts_file, 'w') as file:
                json.dump(self.accounts, file, indent=2)
        except IOError as e:
            print(f"Error saving accounts file: {e}")

    def create_account(self, username, password):
        if username in self.accounts:
            return False, "Username already exists."
        self.accounts[username] = password
        self.save_accounts()
        return True, "Account created successfully."

    def authenticate(self, username, password):
        return self.accounts.get(username) == password

def broadcast(message, sender_conn, sender_username):
    encrypted_message = base64.b64encode(message.encode('utf-8'))
    with lock:
        for client_conn, username in clients:
            if client_conn != sender_conn:
                try:
                    full_message = f"{sender_username}: {encrypted_message.decode('utf-8')}"
                    client_conn.sendall(full_message.encode('utf-8'))
                except Exception as e:
                    print(f"Error broadcasting message to {username}: {e}")
                    client_conn.close()
                    clients.remove((client_conn, username))

def handle_client(conn, addr, credentials_manager):
    print(f"Connected by {addr}")
    username = ""
    try:
        while True:
            conn.sendall("Sign Up (1) or Log In (2)?".encode('utf-8'))
            choice_data = conn.recv(1024).decode('utf-8').strip()

            if choice_data == '1':
                conn.sendall("Please enter a new username and password, separated by a space.".encode('utf-8'))
                creds = conn.recv(1024).decode('utf-8').strip().split()
                if len(creds) == 2:
                    new_username, new_password = creds
                    success, msg = credentials_manager.create_account(new_username, new_password)
                    conn.sendall(msg.encode('utf-8'))
                    if success:
                        username = new_username
                        break
            elif choice_data == '2':
                conn.sendall("Please enter your username and password, separated by a space.".encode('utf-8'))
                creds = conn.recv(1024).decode('utf-8').strip().split()
                if len(creds) == 2:
                    login_username, login_password = creds
                    if credentials_manager.authenticate(login_username, login_password):
                        conn.sendall("Login successful!".encode('utf-8'))
                        username = login_username
                        break
                    else:
                        conn.sendall("Invalid username or password.".encode('utf-8'))
            else:
                conn.sendall("Invalid choice. Please enter 1 or 2.".encode('utf-8'))
        with lock:
            clients.append((conn, username))
            client_usernames[conn] = username
        print(f"User {username} from {addr} authenticated.")
        broadcast(f"{username} has joined the chat.", conn, "SERVER")

        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Connection from {username} ({addr}) closed.")
                break
            message = data.decode('utf-8')
            print(f"Received from {username}: {message}")
            broadcast(message, conn, username)

    except (socket.error, ConnectionResetError) as e:
        print(f"Connection error with {addr}: {e}")
    finally:
        if username:
            print(f"User {username} disconnected.")
            broadcast(f"{username} has left the chat.", conn, "SERVER")
        with lock:
            if (conn, username) in clients:
                clients.remove((conn, username))
            if conn in client_usernames:
                del client_usernames[conn]
        conn.close()

def main():
    credentials_manager = Credentials()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, credentials_manager))
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")

if __name__ == "__main__":
    main()
