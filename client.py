import socket
import threading
import base64
import sys

HOST = '176.92.124.17'
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            full_message = data.decode('utf-8')
            parts = full_message.split(':', 1)
            if len(parts) == 2:
                sender_username, encrypted_message = parts
                try:
                    decrypted_message = base64.b64decode(encrypted_message.strip()).decode('utf-8')
                    if sender_username.strip().upper() == "SERVER":
                        print(f"[{sender_username.strip()}] {decrypted_message}")
                    else:
                        print(f"[{sender_username.strip()}] {decrypted_message}")

                except base64.binascii.Error:
                    print(f"[{sender_username.strip()}]: {encrypted_message.strip()}")

            else:
                print(f"Received unformatted message: {full_message}")
        except (socket.error, ConnectionResetError) as e:
            print(f"Error receiving data: {e}")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except socket.error as e:
            print(f"Could not connect to server: {e}")
            sys.exit()
        
        # This loop handles the entire login/signup process
        while True:
            prompt = s.recv(1024).decode('utf-8')
            print(prompt, end="")
            
            user_choice = input()
            s.sendall(user_choice.encode('utf-8'))
            
            # Now, receive the next prompt from the server based on the user's choice
            login_prompt = s.recv(1024).decode('utf-8')
            print(login_prompt, end="")
            
            # Get the username and password from the user
            creds_input = input()
            s.sendall(creds_input.encode('utf-8'))
            
            # Get the final login/signup response
            response = s.recv(1024).decode('utf-8')
            print(response)
            
            if "successful" in response or "created successfully" in response:
                break
                
        # Start the message receiving thread after a successful login/signup
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.daemon = True
        receive_thread.start()

        # Main loop for sending chat messages
        while True:
            try:
                message = input("")
                if message.lower() == "exit":
                    break
                s.sendall(message.encode('utf-8'))
            except (socket.error, ConnectionResetError) as e:
                print(f"Error sending data: {e}")
                break
            except KeyboardInterrupt:
                print("Exiting...")
                break

    print("Connection closed.")

if __name__ == "__main__":
    main()
