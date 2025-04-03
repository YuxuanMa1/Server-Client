import socket
import threading

#Transparency：Users can switch channels freely, and everyone can see messages in the same channel.
#Scalability：Use multi-threading to handle multiple users, theoretically supporting unlimited clients.
            #The server does not limit the number of channels and listens to 0.0.0.0. Clients with any IP address can connect.

HOST = "0.0.0.0" 
PORT = 12345 

clients = {}  
channels = {"general": set()}  #Join the general channel by default

def broadcast(message, channel, sender_nick=None):#Forward messages accurately to users in the same channel
 
    if channel in channels:
        for nickname in channels[channel]:
            if nickname in clients and nickname != sender_nick:
                try:
                    clients[nickname].send(message.encode())
                except:
                    pass

def handle_client(client_socket, nickname):
    
    current_channel = "general"
    channels[current_channel].add(nickname)
    broadcast(f"{nickname} joined the channel {current_channel}", current_channel)

    while True:
        try:
            message = client_socket.recv(1024).decode()  # failure handling 1: If message is empty, break exits the loop and safely 
                                                         # closes the client connection.
            if not message:
                break

            if message.startswith("/"):
                command, *args = message.split(" ", 1)

                if command == "/join" and args:  # The server supports channel switching /join <channel> and private chat /msg <user> <message>
                    new_channel = args[0].strip()

                    # Exit current channel
                    if nickname in channels[current_channel]:
                        channels[current_channel].remove(nickname)
                        if not channels[current_channel]:  
                            del channels[current_channel]

                    # Join new channel
                    if new_channel not in channels:
                        channels[new_channel] = set()
                    channels[new_channel].add(nickname)

                    broadcast(f"{nickname} joined the channel {new_channel}", new_channel)
                    current_channel = new_channel

                elif command == "/leave":  
                    if current_channel == "general":  # failure handling: users cannot leave the default general channel
                        client_socket.send("You cannot leave the general channel.\n".encode())
                        continue

                    broadcast(f"{nickname} left the channel {current_channel}", current_channel)

                    if nickname in channels[current_channel]:
                        channels[current_channel].remove(nickname)
                        if not channels[current_channel]:
                            del channels[current_channel]  # If the channel is empty, delete it
                    if not any(nickname in users for users in channels.values()):
                        current_channel = "general"
                        channels[current_channel].add(nickname)

                elif command == "/msg" and args:  # failure handling: if the format command is not correct, it will throw a ValueError
                    try:
                        target, private_msg = args[0].split(" ", 1)
                        if target in clients:
                            clients[target].send(f"[Private] {nickname}: {private_msg}".encode())
                        else:
                            client_socket.send(f"User {target} not found.".encode())
                    except ValueError:
                        client_socket.send("Usage: /msg <nickname> <message>".encode())

                elif command == "/quit":
                    break

            else:
                broadcast(f"{nickname}: {message}", current_channel, sender_nick=nickname)

        except:
            break


    #Client disconnection handling
    client_socket.close()
    if nickname in clients:
        del clients[nickname]

    if nickname in channels[current_channel]:
        channels[current_channel].remove(nickname)
        if not channels[current_channel]:
            del channels[current_channel]

    broadcast(f"{nickname} has left the chat", current_channel)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Handling multiple clients, each new client will start a thread
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server.accept()
            client_socket.send("Enter your nickname: ".encode())
            nickname = client_socket.recv(1024).decode().strip()

            if not nickname or nickname in clients:
                client_socket.send("Nickname already in use or invalid. Try another one.".encode())
                client_socket.close()
                continue

            clients[nickname] = client_socket
            print(f"{nickname} connected from {addr}")

            thread = threading.Thread(target=handle_client, args=(client_socket, nickname))
            thread.start()

    except KeyboardInterrupt: #failure handling: The server will shut down when it is abnormally interrupted
        print("\nServer shutting down...")
        server.close()

    except Exception as e:#faliure handling: Any unexpected errors will be caught and an error message will be printed instead of crashing the server.
        print(f"Server error: {e}")
        server.close()

if __name__ == "__main__":
    main()

