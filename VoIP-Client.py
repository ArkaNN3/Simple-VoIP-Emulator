import customtkinter as ctk
import socket
import threading
import ipaddress

# Get the server IP address from the command line
while True:
    server_ip = input("Enter the server IP address: ")
    try:
        ipaddress.ip_address(server_ip)
        break
    except ValueError:
        print("Invalid IP address. Please enter a correct IP address.")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Create a Tkinter GUI
root = ctk.CTk()
root.title("Client GUI")


# Create a button to send data
def send_data():
    try:
        # Connect to the server
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.connect((server_ip, 12345))
        # Get the message from the text box
        message = f"{register_name_entry.get()}:{passwd_entry.get()}:{SIP_Entry.get()}"
        # Send data to the server
        ls.send(bytes(message, 'utf-8'))
        ls.close()
    except Exception as e:
        print(f'Error: {e}')


# ip label
iplab = ctk.CTkLabel(root, text="Register Name")
iplab.grid(row=0, column=0, pady=4, padx=20)

# Create a text box to enter message
register_name_entry = ctk.CTkEntry(root)
register_name_entry.grid(row=0, column=1, pady=4, padx=20)

# passwd label
passwd_label = ctk.CTkLabel(root, text="Password")
passwd_label.grid(row=1, column=0, pady=4, padx=20)

# password entry box
passwd_entry = ctk.CTkEntry(root)
passwd_entry.grid(row=1, column=1, pady=4, padx=20)

# sip entry label
SIP_Label = ctk.CTkLabel(root, text="SIP Server")
SIP_Label.grid(row=2, column=0, pady=4, padx=20)

# sip entry box
SIP_Entry = ctk.CTkEntry(root)
SIP_Entry.grid(row=2, column=1, pady=4, padx=20)

# register status label
StatusLabel = ctk.CTkLabel(root, text="Register Status: ")
StatusLabel.grid(row=0, column=2, pady=4, padx=20)

# Create a text box to display messages received from the server
received_text_box = ctk.CTkTextbox(root, width=150, height=20)
received_text_box.grid(row=1, column=2, pady=4, padx=20)
received_text_box.configure(state="disabled")

# send data button
button = ctk.CTkButton(root, text="Register", command=send_data)
button.grid(row=4, column=1)


# Create a thread to handle incoming connections
def handle_incoming_connections():
    while True:
        try:
            # Accept a connection
            c, addr = s.accept()
            data = b''
            while True:
                # receiving data
                new_data = c.recv(1024)
                data += new_data
                if not new_data:
                    received_text_box.configure(state="normal")
                    received_text_box.delete('1.0', ctk.END)
                    break
            # insert the data in the text box
            received_text_box.insert("end", data.decode() + "\n")
            received_text_box.configure(state="disabled")
            c.close()

        except Exception as e:
            print(f'Error: {e}')


# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
s.bind(("", 12345))

# Listen for incoming connections
s.listen(5)

# start the thread
thread = threading.Thread(target=handle_incoming_connections)
thread.start()

root.mainloop()
