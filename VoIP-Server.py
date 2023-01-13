import wmi
import tkinter as tk
import socket
import threading
import queue
import ipaddress


def get_nic_list():
    local_nic_list = {}
    c = wmi.WMI()
    for interface in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        local_nic_list[interface.Description] = interface.IPAddress[0]
    return local_nic_list


def select_nic(nic_list):
    valid_input = False
    print("Select the ID of the network interface you want to use:")
    for i, nic_name in enumerate(nic_list.keys()):
        print(f"{i+1}. {nic_name}")
    while not valid_input:
        selection = input()
        if selection.isnumeric() and (1 <= int(selection) <= len(nic_list)):
            local_selected_nic = list(nic_list.keys())[int(selection) - 1]
            print(f"You selected: {local_selected_nic}")
            valid_input = True
            return local_selected_nic
        else:
            print("Invalid input, please enter a valid ID.")


def get_nic_ip(nic_name):
    # Connect to the WMI provider
    c = wmi.WMI()
    # Get the IP addresses of the selected NIC
    for interface in c.Win32_NetworkAdapterConfiguration(Description=nic_name):
        if interface.IPAddress:
            return interface.IPAddress[0]
    return None


nic_list = get_nic_list()
selected_nic = select_nic(nic_list)
nic_ip = get_nic_ip(selected_nic)
if nic_ip:
    print(f"The IP address of the selected NIC {selected_nic} is {nic_ip}")
else:
    print(f"No IP address is configured for the selected NIC {selected_nic}")

# Get the client IP address from the command line
while True:
    client_ip = input("Enter the client IP address: ")
    try:
        # Try to create an IP address object from the entered IP address
        ipaddress.ip_address(client_ip)
        break
    except ValueError:
        print("Invalid IP address. Please enter a correct IP address.")

# Create a queue to store received data
q = queue.Queue()


# Create a thread to handle incoming connections
def handle_incoming_connections():
    while True:
        try:
            # Accept a connection
            c, addr = s.accept()
            print('Got connection from', addr)
            data = b''
            while True:
                # receiving data
                new_data = c.recv(1024)
                data += new_data
                if not new_data:
                    break
            q.put(data)
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

# Create a Tkinter GUI
root = tk.Tk()
root.title("Server GUI")

# Create a text box to display received data
text_box = tk.Text(root)
text_box.grid(row=0, column=0, columnspan=4, pady=4, padx=20)

# Create a text box for the server to enter the message to be sent
server_message_entry = tk.Entry(root)
server_message_entry.grid(row=1, column=0, pady=4, padx=20)

register_label = tk.Label(text="VoIP Register Name: ")
register_label.grid(row=1, column=1, pady=4, padx=20)

password_label = tk.Label(text="VoIP Password: ")
password_label.grid(row=2, column=1, pady=4, padx=20)

register_entry = tk.Entry(root)
register_entry.grid(row=1, column=2, pady=4, padx=20)

password_entry = tk.Entry(root)
password_entry.grid(row=2, column=2, pady=4, padx=20)


# Create a function to send data to the client
def send_data():
    try:
        # Connect to the client
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.connect((client_ip, 12345))
        # Get the message from the text box
        message = server_message_entry.get()
        # Send data to the client
        ls.send(bytes(message, 'utf-8'))
        ls.close()
    except Exception as e:
        print(f'Error: {e}')


def send_response_data(message):
    try:
        # Connect to the client
        ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ls.connect((client_ip, 12345))
        # Send data to the client
        ls.send(bytes(message, 'utf-8'))
        ls.close()
    except Exception as e:
        print(f'Error: {e}')


# Create a button to send data
server_send_button = tk.Button(root, text="Send Data", command=send_data)
server_send_button.grid(row=2, column=0)


def check_queue():
    # check if there is any data in queue
    if not q.empty():
        data = q.get()
        received_data = data.decode("utf-8")
        register_name, passwd, sip = received_data.split(":")
        # insert the data in the text box
        text_box.insert("end", data.decode() + "\n")
        if sip == nic_ip and passwd == password_entry.get() and register_name == register_entry.get():
            # send_response_data("Server Received Data: " + data.decode())
            send_response_data("Registered")
        else:
            send_response_data("Register Failed")
    root.after(1000, check_queue)


root.after(1000, check_queue)
root.mainloop()
