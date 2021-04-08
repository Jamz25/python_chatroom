import threading
import socket
import pickle

host = ''
port = 53212

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
chat_contents = ["".encode('ascii') for i in range(12)]


def update_client_contents():
    for client in clients:
        client.send(pickle.dumps(chat_contents))


def rotate_messages(message):
    # rotating messages upwards
    for index, content in enumerate(chat_contents[1:]):
        chat_contents[index] = content
    chat_contents[len(chat_contents) - 1] = message
    update_client_contents()


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == "window_close":
                # on client leave
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                rotate_messages(f'{nickname} left the chat.'.encode('ascii'))
                print(f'{nickname} left the chat.')
                nicknames.remove(nickname)
                break
            elif message == "rechose_nickname":
                client.send("get_nickname".encode('ascii'))
                nickname = client.recv(1024).decode('ascii')
                if unique_nickname(nickname):
                    add_client(client, nickname)

                else:
                    print(f"Common nickname \"{nickname}\" chosen.")
                    client.send("common_nickname".encode('ascii'))
            else:
                rotate_messages(message.encode('ascii'))
        except Exception as e:
            print(e)
            break


def receive():
    while True:
        client, address = server.accept()
        print("Connected to" + str(address))

        client.send('get_nickname'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

        if unique_nickname(nickname):
            add_client(client, nickname)

        else:
            print(f"Common nickname \"{nickname}\" chosen.")
            client.send("common_nickname".encode('ascii'))


def unique_nickname(nickname):
    return nickname not in nicknames


def add_client(client, nickname):
    print(f"Unique nickname \"{nickname}\" chosen.")
    client.send("unique_nickname".encode('ascii'))
    nicknames.append(nickname)
    clients.append(client)

    rotate_messages(f"{nickname} joined the chat.".encode('ascii'))
    update_client_contents()


receive()
