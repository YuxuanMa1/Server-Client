import socket
import threading

SERVER_IP = "127.0.0.1" #connect to server by IP address
PORT = 12345

def receive_messages(client_socket): #
   
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("Server disconnected.")
                break
            print(message)
        except:
            print("Connection lost. Exiting...")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_IP, PORT)) #failure handling:If the server is not started or the IP/port is wrong, connect() will throw ConnectionRefusedError
    except ConnectionRefusedError:
        print("Failed to connect to the server. Make sure the server is running.")
        return

    nickname = ""
    while not nickname.strip(): #Let the user enter a nickname and send it to the server
        nickname = input(client.recv(1024).decode()).strip()

    client.send(nickname.encode())

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        try: #failure handling: If the server is down or the client unexpectedly disconnects, errors will be caught
            message = input()
            if message.strip() == "/quit":
                client.send(message.encode())
                break
            client.send(message.encode())
        except:
            print("Error sending message.")
            break

    client.close()

if __name__ == "__main__":
    main()
