
import tkinter as tk
import threading
import socket
import time
import pickle

nickname = ""
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 53212

window_dimensions = {"Width": 229, "Height": 377}

on_cooldown = False
cooldown_time = 1
sent_nickname = False

# define tkinter window
root = tk.Tk()
root.title("Chat room")
root.geometry(f'{window_dimensions["Width"]}x{window_dimensions["Height"]}')
root.resizable(0, 0)

'''
 ---- NETWORKING ----
'''


def receive():
    global server, sent_nickname
    while True:
        try:
            print("receiving from server")
            message = server.recv(1024)
            if not sent_nickname:
                message = message.decode('ascii')
                if message == "get_nickname":
                    server.send(nickname.encode('ascii'))
                    join_success(server.recv(1024).decode('ascii') == "unique_nickname")
            else:
                # handling message box contents received
                update_contents(pickle.loads(message))
        except Exception as e:
            print(e)
            server.close()
            break


def server_connection():
    global server, host
    # creating server connection
    host = host_entry.get()
    server.connect((host, port))
    # creating thread to receive messages from server
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()


def common_nickname():
    nickname_entry.delete(0, tk.END)
    nickname_entry.insert(0, "Common nickname!")


'''
 ---- SENDING MESSAGES LOGIC ----
'''


# updating message box contents to what server has sent back
def update_contents(server_contents):
    global contents
    contents = server_contents
    for index, content in enumerate(contents):
        content = content.decode('ascii')
        message_boxes[index].config(text=content, fg=text_colour(content))


def send_message(event=False):
    global on_cooldown
    if not on_cooldown:
        message = message_entry.get()
        message_entry.delete(0, tk.END)
        server.send(f'{nickname}: {message}'.encode('ascii'))
        on_cooldown = True
        threading.Thread(target=cooldown_timer).start()


def cooldown_timer():
    global on_cooldown
    time.sleep(cooldown_time)
    on_cooldown = False


def text_colour(content):
    if ":" in content:
        return "Black"
    elif "joined" in content:
        return "Green"
    else:
        return "Red"


'''
 ---- TKINTER WIDGET PLACEMENT AND FORGETTING ----
'''


def chat_window():
    # filler (spacing)
    tk.Label(root, height=23).grid(row=0, column=2)
    # placing message boxes
    for index, element in enumerate(message_boxes):
        element.place(x=0, y=index*30)
    # placing message box and send button
    message_entry.grid(row=8, column=0)
    send_button.grid(row=8, column=1)
    # using enter key to send messages
    root.bind('<Return>', send_message)


def attempt_join():
    global nickname
    nickname = nickname_entry.get()
    if nickname != "Nickname" and len(nickname) <= 8:
        print("joining chat")
        # makes join button useless while attempting connection
        join_button.config(command="")
        # connect to server through ip and port
        server_connection()
    else:
        nickname_entry.delete(0, tk.END)
        nickname_entry.insert(0, "Change nickname!")


def join_success(successful):
    global sent_nickname
    if successful:
        # set sent nickname to true
        sent_nickname = True
        # forget lobby widgets and place chat room widgets
        forget_lobby()
        chat_window()
        # assigns method to when user closes window to alert server of client disconnect
        root.protocol("WM_DELETE_WINDOW", on_closing)
    else:
        join_button.config(command=rejoin_rechose)
        common_nickname()


def rejoin_rechose():
    global nickname
    nickname = nickname_entry.get()
    if len(nickname) <= 8:
        join_button.config(command="")
        server.send("rechose_nickname".encode('ascii'))
    else:
        nickname_entry.delete(0, tk.END)
        nickname_entry.insert(0, "Nickname too long!")


def forget_lobby():
    join_button.grid_forget()
    title.grid_forget()
    filler.grid_forget()
    nickname_entry.grid_forget()
    host_entry.grid_forget()


def on_closing():
    server.send("window_close".encode('ascii'))
    root.destroy()


'''
 ---- CREATING CHAT ROOM WIDGETS ----
'''

# message entry and send message button
message_entry = tk.Entry(root, width=30)
send_button = tk.Button(root, text="Send", width=5, command=send_message)

# creating 12 label widgets for messages to appear in
message_boxes = []
for i in range(12):
    message_boxes.append(tk.Label(root))

# message box contents
contents = ["" for i in message_boxes]

'''
 ---- CREATING LOBBY WIDGETS AND PLACING THEM ----
'''

# title
title = tk.Label(root, text="Chat room", font=("Helvetica", 25))
title.grid(row=0, column=0, columnspan=2, pady=25)

# filler (spacing)
filler = tk.Label(root)
filler.grid(row=1, column=1, pady=50)

# nickname entry
nickname_entry = tk.Entry(root, width=20)
nickname_entry.grid(row=2, column=1, padx=60)
nickname_entry.insert(0, "Nickname")

# ip entry
host_entry = tk.Entry(root, width=20)
host_entry.grid(row=3, column=1)
host_entry.insert(0, "Host IP")

# join button
join_button = tk.Button(root, width=10, height=2, text="Join", command=attempt_join)
join_button.grid(row=4, column=1)

tk.mainloop()
