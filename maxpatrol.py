import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import paramiko
import platform
import re
import logging
from datetime import datetime
import psycopg2

class GUIStyle:
    def __init__(self):
        self.background_color = '#ffffff'
        self.button_color = '#FFFAFA'
        self.textbox_color = '#F8F8FF'
        self.text_color = '#000000'
        self.font = ('Poppins', 10, 'bold')

class GUI:
    def __init__(self, master, gui_style, max_patrol_instance):
        
        self.max_patrol = max_patrol_instance
        self.master = master
        self.master.title("MaxPatrol Scanner")
        self.master.resizable(width=False, height=False)
        self.gui_style = gui_style

        self.clear_log_file()

        self.widgets()

        window_width = 500
        window_height = 500
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x_coordinate = int((screen_width - window_width) / 2)
        y_coordinate = int((screen_height - window_height) / 2)

        self.master.geometry(f"700x500+{x_coordinate}+{y_coordinate}")

        logging.basicConfig(filename='app_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    def savedatabase(self, ip, os_info):
        postgres_host = self.postgres_host_entry.get()
        postgres_db = self.postgres_db_entry.get()
        postgres_user = self.postgres_user_entry.get()
        postgres_password = self.postgres_password_entry.get()

        if not postgres_host or not postgres_db or not postgres_user or not postgres_password:
            self.mshow("Error", "Please fill in all database fields.")
            return

        connection = None
        try:
            connection = psycopg2.connect(
                host=postgres_host,
                database=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            cursor = connection.cursor()

            cursor.execute("INSERT INTO os_info (ip_address, os_details, timestamp) VALUES (%s, %s, %s)",
                           (ip, os_info, datetime.now()))
            connection.commit()

        except Exception as e:
            print(f"Error connecting to PostgreSQL: {str(e)}")

        finally:
            if connection:
                cursor.close()
                connection.close()


    def clear_log_file(self):
        with open('app_log.txt', 'w'):
            pass

    def log_info(self, message):
        logging.info(message)

    def log_error(self, message):
        logging.error(message)

    def widgets(self):
        self.master.configure(bg=self.gui_style.background_color)

        tk.Label(self.master, text="IP:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Port:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=1, column=0, padx=5, pady=5)
        self.port_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Username:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=2, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.username_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Password:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=3, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.master, show="*", bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.password_entry.grid(row=3, column=1, padx=5, pady=5)

        self.connect_button = tk.Button(self.master, text="Connect", command=self.sshconnect, bg=self.gui_style.button_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.output_text = tk.Text(self.master, height=10, width=40, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.output_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.show_table_button = tk.Button(self.master, text="Show Table", command=self.showtable, bg=self.gui_style.button_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.show_table_button.grid(row=4, column=2, columnspan=2, pady=10)

        self.clear_table_button = tk.Button(self.master, text="Clear Table", command=self.clear_table, bg=self.gui_style.button_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.clear_table_button.grid(row=5, column=2, columnspan=2, pady=10)

        tk.Label(self.master, text="PostgreSQL Host:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=0, column=2, padx=5, pady=5)
        self.postgres_host_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.postgres_host_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(self.master, text="PostgreSQL Database:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=1, column=2, padx=5, pady=5)
        self.postgres_db_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.postgres_db_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(self.master, text="PostgreSQL User:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=2, column=2, padx=5, pady=5)
        self.postgres_user_entry = tk.Entry(self.master, bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.postgres_user_entry.grid(row=2, column=3, padx=5, pady=5)

        tk.Label(self.master, text="PostgreSQL Password:", bg=self.gui_style.background_color, fg=self.gui_style.text_color, font=self.gui_style.font).grid(row=3, column=2, padx=5, pady=5)
        self.postgres_password_entry = tk.Entry(self.master, show="*", bg=self.gui_style.textbox_color, font=self.gui_style.font, fg=self.gui_style.text_color)
        self.postgres_password_entry.grid(row=3, column=3, padx=5, pady=5)


    def showtable(self):
        
        postgres_host = self.postgres_host_entry.get()
        postgres_db = self.postgres_db_entry.get()
        postgres_user = self.postgres_user_entry.get()
        postgres_password = self.postgres_password_entry.get()

        if not postgres_host or not postgres_db or not postgres_user or not postgres_password:
            self.mshow("Error", "Please fill in all database fields.")
            return

        table_window = tk.Toplevel(self.master)
        table_window.title("Data Table")
        
        table_frame = ttk.Frame(table_window)
        table_frame.grid(row=0, column=0, padx=5, pady=5)

        table_window.resizable(width=False, height=False)
        table_window.maxsize(800, 600)

        table_copy = ttk.Treeview(table_frame, columns=('ID', 'IP Address', 'OS Details', 'Timestamp'), show='headings')
        table_copy.heading('ID', text='ID')
        table_copy.heading('IP Address', text='IP Address')
        table_copy.heading('OS Details', text='OS Details')
        table_copy.heading('Timestamp', text='Timestamp')

        table_copy.bind('<Double-Button-1>', lambda event, table_copy=table_copy: self.showosdetails(event, table_copy))

        postgres_host = self.postgres_host_entry.get()
        postgres_db = self.postgres_db_entry.get()
        postgres_user = self.postgres_user_entry.get()
        postgres_password = self.postgres_password_entry.get()

        connection = None
        try:
            connection = psycopg2.connect(
                host=postgres_host,
                database=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM os_info")
            rows = cursor.fetchall()

            for row in rows:
                decoded_row = [str(item, 'utf-8', 'replace') if isinstance(item, bytes) else item for item in row]
                table_copy.insert('', 'end', values=decoded_row)

        except Exception as e:
            print(f"Error fetching data from database: {str(e)}")

        finally:
            if connection:
                cursor.close()
                connection.close()

        table_copy.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        scrollbar_y = ttk.Scrollbar(table_frame, orient='vertical', command=table_copy.yview)
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        table_copy['yscrollcommand'] = scrollbar_y.set

        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal', command=table_copy.xview)
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        table_copy['xscrollcommand'] = scrollbar_x.set

        return table_copy

    def showosdetails(self, event, table_copy):
        item = table_copy.selection()
        if item:
            item = item[0]
            os_details = table_copy.item(item, 'values')[2]
            self.mshow('OS Details', os_details)
        else:
            pass

    def clear_table(self):
        postgres_host = self.postgres_host_entry.get()
        postgres_db = self.postgres_db_entry.get()
        postgres_user = self.postgres_user_entry.get()
        postgres_password = self.postgres_password_entry.get()

        if not postgres_host or not postgres_db or not postgres_user or not postgres_password:
            self.mshow("Error", "Please fill in all database fields.")
            return

        connection = None
        try:
            connection = psycopg2.connect(
                host=postgres_host,
                database=postgres_db,
                user=postgres_user,
                password=postgres_password
            )
            cursor = connection.cursor()

            cursor.execute("DELETE FROM os_info;")
            connection.commit()

            cursor.execute("SELECT setval(pg_get_serial_sequence('os_info', 'id'), coalesce(max(id),0)+1, false) FROM os_info;")
            connection.commit()

            self.output_text.delete(1.0, tk.END)

        except Exception as e:
            print(f"Error clearing table: {str(e)}")

        finally:
            if connection:
                cursor.close()
                connection.close()


    def sshconnect(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        postgres_host = self.postgres_host_entry.get()
        postgres_db = self.postgres_db_entry.get()
        postgres_user = self.postgres_user_entry.get()
        postgres_password = self.postgres_password_entry.get()

        if not ip or not port or not username or not password or not postgres_host or not postgres_db or not postgres_user or not postgres_password:
            self.mshow("Error", "Please fill in all fields.")
            return

        try:
            port = int(port)
        except ValueError:
            self.mshow("Error", "Invalid port. Please enter a valid integer.")
            return

        ip_pattern = re.compile(
            r"^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\."
            r"(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$"
        )

        self.output_text.delete(1.0, tk.END)

        if "-" in ip:
            self.rangessh(ip, port, username, password)
        elif not ip_pattern.match(ip):
            self.mshow("Error", "Invalid IP address. Please enter a valid IP.")
        else:
            self.singlesshconnect(ip, port, username, password, postgres_host, postgres_db, postgres_user, postgres_password)

    def singlesshconnect(self, ip, port, username, password, postgres_host, postgres_db, postgres_user, postgres_password):
        scanner = MaxPatrol(ip, port, username, password, postgres_host, postgres_db, postgres_user, postgres_password)

        if scanner.sshconnect():
            os_info = scanner.detect_OS()
            self.output_text.insert(tk.END, os_info + "\n")
            self.log_info(f"Connected to {ip} successfully at {datetime.now()}")
            self.savedatabase(ip, os_info)
            scanner.ssh.close()
        else:
            self.mshow("Error", f"Unable to establish SSH connection to {ip}.")
            self.log_error(f"Failed to connect to {ip} at {datetime.now()}")

    def rangessh(self, ip_range, port, username, password):
        start_ip, end_ip = ip_range.split('-')
        ip_list = self.genlist(start_ip, end_ip)
        for ip in ip_list:
            self.singlesshconnect(ip, port, username, password)

    def genlist(self, start_ip, end_ip):
        start = list(map(int, start_ip.split('.')))
        end = list(map(int, end_ip.split('.')))
        ip_list = []

        while start <= end:
            ip_list.append('.'.join(map(str, start)))
            start[3] += 1

            for i in (3, 2, 1):
                if start[i] == 256:
                    start[i] = 0
                    start[i - 1] += 1

        return ip_list

    def mshow(self, title, message):
        messagebox.showinfo(title, message)


class MaxPatrol:
    def __init__(self, ip, port, username, password, postgres_host, postgres_db, postgres_user, postgres_password, gui_instance=None):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.postgres_host = postgres_host
        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.gui_instance = gui_instance

    def sshconnect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.ip, port=self.port, username=self.username, password=self.password)

            if self.gui_instance:
                self.gui_instance.save_to_database(self.ip, "Connection established")

            if self.gui_instance and hasattr(self.gui_instance, 'save_to_database_postgres'):
                self.gui_instance.save_to_database_postgres(
                    self.postgres_host,
                    self.postgres_db,
                    self.postgres_user,
                    self.postgres_password
                )

            return True
        except Exception as e:
            print(f"Error connecting to {self.ip}: {str(e)}")
            return False


    
    def set_gui(self, gui_instance):
        self.gui_instance = gui_instance

    def execute(self, command):
        if self.ssh:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode("utf-8")
            return output
        else:
            print("SSH connection not established.")
            return None

    def detect_OS(self):
        try:
            command_os = "cat /etc/os-release"
            output_os = self.execute(command_os)

            os_info = "OS information is not available."

            if "debian" in output_os.lower():
                os_info = "Debian Linux\n"
            elif "ubuntu" in output_os.lower():
                os_info = "Ubuntu Linux\n"
            elif "manjaro" in output_os.lower():
                os_info = "Manjaro Linux\n"
            else:
                os_info = "Unknown Linux Distribution\n"

            os_info += "\nAdditional OS Information:\n"
            for line in output_os.splitlines():
                if line.startswith("PRETTY_NAME"):
                    os_info += "OS: {}\n".format(line.split('=')[1].strip('\"'))
                elif line.startswith("VERSION_ID"):
                    os_info += "Version: {}\n".format(line.split('=')[1].strip('\"'))
                elif line.startswith("HOME_URL"):
                    os_info += "Architecture: {}\n".format(platform.architecture()[0])

            command_drivers = "lspci -k"
            output_drivers = self.execute(command_drivers)

            os_info += "\nDriver Information:\n{}".format(output_drivers)

            return "OS Details:\n{}".format(os_info)
        except Exception as e:
            return "Error: {}".format(str(e))

def main():
    gui_style = GUIStyle()
    root = tk.Tk()
    
    max_patrol_instance = MaxPatrol("", 0, "", "", "", "", "", "")
    
    app = GUI(root, gui_style, max_patrol_instance)
    max_patrol_instance.set_gui(app)
    root.mainloop()

if __name__ == "__main__":
    main()
