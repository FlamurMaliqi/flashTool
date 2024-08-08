import logging
import socket
import time
from paramiko import SSHClient, SSHConfig, AuthenticationException, SSHException, AutoAddPolicy
import paramiko
from scp import SCPClient, SCPException
from tkinter import filedialog, simpledialog, StringVar, Tk, ttk, messagebox
from tkinter.messagebox import showerror, showwarning 
from threading import Thread
from constants import *
from expections import *
from a2lFastLogPostProcessing import *


# variables
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("flashing-tool.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


def ask_user(root_window: Tk) -> tuple[str, str]:
    target = simpledialog.askstring(
                "Connect to target",
                "Target name:",
                initialvalue=default_target_name,
                parent=root_window
            )
    if not target:
        raise UserCancel("Target name entry is empty or input canceled.")

    password = simpledialog.askstring(
                    "Password for user",
                    "Password:",
                    show='*',
                    parent=root_window)
    if not password:
        raise EmptyPasswordField("Empty password entry or password input canceled.")

    return target, password


def get_config_data(target_name: str) -> tuple[str, str, int]:
    config_file = open(SSH_CONFIG_FILE)
    ssh_config_object = SSHConfig.from_file(config_file)
    config_file.close()

    host_list = ssh_config_object.get_hostnames()

    if target_name not in host_list:
        raise HostConfigNotFound(f"There are no configuration for the host {target_name} in {SSH_CONFIG_FILE}")

    config_values = ssh_config_object.lookup(target_name)
    host_adress = config_values.get('hostname')
    user_name = config_values.get('user')
    port_number = config_values.get('port')

    if not host_adress or host_adress == '*':     # avoid wildcard hostname
        raise HostConfigNotFound(f"There is no address for {target_name} in {SSH_CONFIG_FILE}.")
    if not user_name:
        raise HostConfigNotFound(f"There is no username for {target_name} in {SSH_CONFIG_FILE}.")
    if not port_number:
        port_number = SSH_DEFAULT_PORT

    return host_adress, user_name, port_number


def connect_button_function(connect_state_lokal: StringVar, software_version_lokal: StringVar, root_window: Tk, connect_button_lokal: ttk.Button, recovery_system):
    global connection_state, software_version_text, connect_button

    connect_button = connect_button_lokal
    connection_state = connect_state_lokal
    software_version_text= software_version_lokal

    try:
        if not path.exists(SSH_CONFIG_FILE):    # Check whether config file for ssh connection exists
            raise FileNotFoundError(f"There is no config file '{SSH_CONFIG_FILE}' for the ssh connection.")
           
        if saved_credentials["target_name"] and saved_credentials["password"]:
            target_name = saved_credentials["target_name"]
            password = saved_credentials["password"]
        else:
            target_name, password = ask_user(root_window)   # Get target name and password from user
            saved_credentials["target_name"] = target_name
            saved_credentials["password"] = password
            
        host_adress, user_name, port_number = get_config_data(target_name)   # Read parameters for ssh connection from the config file
        try:
            return_value = connect_to_host(host_adress, port_number, user_name, password, TIMEOUT)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print("Fehler passiert hier")
            print(host_adress)
            print(port_number)
            print(user_name)
            print(password)
        if return_value == 0:
            logger.info("Verbindung aktiv, passt alles")
            recovery_system.grid_forget()
        else:
            if check_if_recovery_system_active():
                host_adress, user_name, port_number = get_config_data("recovery")   # Read parameters for ssh connection from the config file
                recovery_system.grid(row=0,column=2)
            else:
                logger.info("kein recovery system aktiv")

        if is_connection_alive():
            connection_state.set(f"Connected to {host_adress}")
            a2l_file_as_string = read_a2l_file_from_remote(PATH_TO_TARGET_FOLDER_A2L_SW_VERSION)
            epk_string = teilstring_nach_epk(a2l_file_as_string)
            if epk_string:
                software_version_text.set(f'{epk_string} ')
            else: 
                software_version_text.set("recovery System aktiv")
                recovery_system.grid(row=0, column=2)

    except FileNotFoundError as no_config_file:
        logger.info(f"File not found: {no_config_file}")
        showerror(title="File not found", message=str(no_config_file))
    except EmptyPasswordField as password_input:
        logger.info(f"Exception during user input: {password_input}")
        showwarning(
            title="Empty Password entry",
            message="Not possible to connect without password. Canceling the connection.")
    except UserCancel as target_name_input:
        connection_state.set("Canceled")
        logger.info(f"Exception during user input: {target_name_input}")
    except HostConfigNotFound as msng_config:
        showerror(title="Configuration not found", message=str(msng_config))
        connection_state.set("Failed")
        software_version_text.set("--:--")



def teilstring_nach_epk(string, count=3): 
    index = -1
    for _ in range(count):
        index = string.find("EPK", index + 1)
        if index == -1:
            return None
    start_quote_index = string.find('"', index)
    end_quote_index = string.find('"', start_quote_index + 1)
    if start_quote_index == -1 or end_quote_index == -1:
        return None
    return string[start_quote_index + 1:end_quote_index]

def reset_progress_section_values():
    global file_state, progress_state
    try:
        file_state.set(default_file_value_file_entry)
        progress_state.set(default_progress_state_value)
    except NameError:
        pass

def read_a2l_file_from_remote(target_folder: str) -> str:
    global ssh_client, logger  # Die SSH-Client- und Logger-Variablen werden global verwendet.

    if is_connection_alive():  # Überprüfe, ob eine SSH-Verbindung besteht.
        try:
            # Listen alle Dateien im Zielordner auf
            stdin, stdout, stderr = ssh_client.exec_command('ls ' + target_folder)
            file_list = stdout.read().decode("utf-8").split('\n')
            # Filtere die Dateien, um nur die mit der Endung ".a2l" zu erhalten
            a2l_files = [file_name for file_name in file_list if file_name.endswith('.a2l')]
            # Überprüfe, ob genau eine ".a2l"-Datei gefunden wurde
            if len(a2l_files) == 1:
                a2l_file_path = path.join(target_folder, a2l_files[0])
                # Lese den Inhalt der ".a2l"-Datei
                stdin, stdout, stderr = ssh_client.exec_command('cat ' + a2l_file_path)
                file_content = stdout.read().decode("utf-8")
                # Schließe die Verbindungen
                stdin.close()
                stdout.close()
                stderr.close()
                return file_content
            elif len(a2l_files) > 1:
                logger.error("Mehr als eine Datei mit der Endung '.a2l' im Zielordner gefunden.")
                return ""
            else:
                logger.error("Keine Datei mit der Endung '.a2l' im Zielordner gefunden.")
                return ""
        except SSHException as e:
            logger.error(f"Fehler beim Lesen der Dateien im Zielordner: {e}")
            return ""
    else:
        logger.info("SSH-Sitzung ist nicht aktiv, kann keine Datei lesen.")
        return ""

def browse_button_function(path_value: StringVar, file_type):

    file_name = filedialog.askopenfilename(title=browse_window_title, filetypes=[
        ("Update file", file_type),
    ])

    if file_name:
        path_value.set(file_name)



def update_button_function(
        path_value: StringVar,
        file_state_value: StringVar,
        progress_state_value: StringVar,
        browse_button_lokal: ttk.Button,
        upload_button_lokal: ttk.Button,
        path_to_target_folder,
        file_type,
        label,
        window):
    global file_state, progress_state, raucb_browse_button, upload_button
    file_state = file_state_value
    progress_state = progress_state_value
    browser_button = browse_button_lokal
    upload_button = upload_button_lokal

    path_to_file = path_value.get()

    if path.exists(path_to_file):
        Thread(target=upload_file_raucb, args=(path_to_file, path_to_target_folder, file_type,label,window,)).start()
    else:
        raise FileNotFoundError


# connect section
def is_connection_alive() -> bool:
    global ssh_client, logger
    return_statement = False

    try:
        transport = ssh_client.get_transport()
        if transport is not None and transport.is_active():
            return_statement = True
    except SSHException:
        logger.warning("There is no connection to the target!")
        return False
    return return_statement


def connect_to_host(host_adress: str, port_number: int, user_name: str, password_lokal: str, timeout_timer):
    global ssh_client
    global connection_state

    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        ssh_client.connect(
            hostname=host_adress,
            port=port_number,
            username=user_name,
            password=password_lokal,
            timeout=timeout_timer)
        return 0
    except socket.timeout:
        print("Time out, Ice Ice Baby")
        return 2
    except AuthenticationException as e:
        ssh_client.close()
        connection_state.set("Failed")
        er_title = str(e)
        er_message = "Connection to Hostname:\n" + host_adress + "\nwith Username: " + user_name + "\nfailed!"

        showerror(title=er_title, message=er_message)


# transfer section
def extract_file_size_from(ls_otpt: str) -> int:
    ls_otpt_elmnts = ls_otpt.split()

    if len(ls_otpt_elmnts) > FILE_SIZE_INDEX and ls_otpt_elmnts[FILE_SIZE_INDEX].isdigit():
        return int(ls_otpt_elmnts[FILE_SIZE_INDEX])
    else:
        logger.info(f"ls output provides no value: {ls_otpt}")


def check_upload_file(path_to_file: str, path_to_target_file: str) -> bool:
    global ssh_client
    file_size = path.getsize(path_to_file)

    if is_connection_alive():
        file_name = path.basename(path_to_file)
        cmnd = 'ls -l ' + path_to_target_file + file_name
        stdin, stdout, stderr = ssh_client.exec_command(cmnd)

        cmnd_otpt = stdout.read().decode("utf8")
        file_size_on_target = extract_file_size_from(cmnd_otpt)

        stdin.close()
        stdout.close()
        stderr.close()

        logger.info(f"Filesize on system: {file_size}")
        logger.info(f"Filesize on target: {file_size_on_target}")

        if file_size == file_size_on_target:
            return True
        return False


def update_upload_progress(file_name: bytes, file_size: int, snt: int):
    global progress_state

    upload_progress_value = snt/file_size
    upload_progress_value_frmtd = "Preparing for download \t{:2.2%}".format(upload_progress_value)
    progress_state.set(upload_progress_value_frmtd)

def update_progress_state(string, window):
    progress_state.set(string)
    window.update()


def update_progress_values(upload_file_name, progress_sts_st):
    global file_state, progress_state

    file_state.set(upload_file_name)
    progress_state.set(progress_sts_st)


def upload_file_raucb(path_to_file: str, path_to_target_folder, update_file_type, label, window):
    global ssh_client, logger
    global connect_button, raucb_browse_button, upload_button, logger

    if is_connection_alive():
        cmnd = 'cd ' + path_to_target_folder
        stdin, stdout, stderr = ssh_client.exec_command(cmnd)
        err_message_in_stderr = stderr.read()
        logger.info(f"Command {cmnd} output: {stdout.read()}")

        if err_message_in_stderr:
            logger.info(f"Path on target is not accessible {path_to_target_folder}")
            logger.error(f'STDERR: {err_message_in_stderr.decode("utf8")}')

        else:
            # Remove all update files in target folder.
            cmnd = 'rm ' + path_to_target_folder + '/*' + update_file_type
            stdin, stdout, stderr = ssh_client.exec_command(cmnd)

            logger.info(f"Command {cmnd} output: {stdout.read()}")
            logger.error(f"Command {cmnd} output error: {stderr.read()}")
            change_label_color(label, "orange", window)

            scp_client = SCPClient(ssh_client.get_transport(), progress=update_upload_progress)
            upload_file_name = path.basename(path_to_file)
            upload_file_name_state = upload_file_name + "\tOK"
            try:
                update_progress_values(upload_file_name, "Upload started")

                scp_client.put(files=path_to_file, remote_path=path_to_target_folder)

                is_file_size_sm = check_upload_file(path_to_file, path_to_target_folder)

                # Set filename and upload status to gui in transfer section
                if is_file_size_sm:
                    upload_file_name_state = upload_file_name + "\tOK"
            except SCPException as e:
                update_progress_values(upload_file_name_state, "Failed")
                logger.error(f"SCPException during bulk upload: {e}")

            scp_client.close()

            stdin, stdout, stderr = ssh_client.exec_command(SET_RECOVERY_SYSTEM_ON_REBOOT)

            logger.info(f"Command {SET_RECOVERY_SYSTEM_ON_REBOOT} output: {stdout.read().decode("utf-8")}")
            logger.error(f"Command {SET_RECOVERY_SYSTEM_ON_REBOOT} output error: {stderr.read().decode("utf-8")}")

            stdin, stdout, stderr = ssh_client.exec_command(REBOOT_COMMAND)

            logger.info(f"Command {REBOOT_COMMAND} output: {stdout.read().decode("utf-8")}")
            logger.error(f"Command {REBOOT_COMMAND} output error: {stderr.read().decode("utf-8")}")

            update_progress_values(upload_file_name_state, "Rebooting")
            change_label_color(label, "orange", window)  # Update progress state in the gui transfer section

        stdin.close()
        stdout.close()
        stderr.close()
       
        if wait_for_system_to_be_ready(window):
            update_progress_values(upload_file_name_state, "Reboot finished")
            change_label_color(label, "green", window)  # Update progress state in the gui transfer section
            messagebox.showinfo("Reboot erfolgreich", f"{upload_file_name} wurde erfolgreich hochgeladen.")
        else:
            update_progress_values(upload_file_name_state, "Reboot failed, Recovery System active")
            change_label_color(label, "red", window)  # Update progress state in the gui transfer section
            messagebox.showinfo("Reboot failed", f"{upload_file_name} konnte nicht gerebooted werden, recovery system ist active.")
        software_version_text.set(f'--:--')
        connection_state.set(f"Disconnected")
        ssh_client.close()

        upload_button['state'] = 'enabled'
        connect_button['state'] = 'enabled'
    else:
        logger.info(f"SSH Session is not alive, scp client can not be created.")

def wait_for_system_to_be_ready(window):
    global ssh_client, logger

    for i in range(101):
        upload_progress_value_frmtd = "Uploading \t{:2.2%}".format(i/100)
        progress_state.set(upload_progress_value_frmtd)
        wait_time = 80/100
        time.sleep(wait_time)
    counter = 0
    steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    
    while True:
        try:
            target_name = saved_credentials["target_name"]
            password = saved_credentials["password"]
            host_adress, user_name, port_number = get_config_data(target_name)   # Read parameters for ssh connection from the config file
            return_value = connect_to_host(host_adress, port_number, user_name, password, 0.5)
            if return_value == 2:
                logger.warning("connection to target failed. Retrying ...")
                update_progress_state("Reconnecting     " + steps[counter % 8], window)
                counter = counter + 1
                if check_if_recovery_system_active():
                        return False
                continue  
            return True
        except Exception as e:
            logger.error("irgendwie ist nix gut")
            

def check_if_recovery_system_active():
    try:
        password = saved_credentials["password"]
        host_adress, user_name, port_number = get_config_data("recovery")
        temp = connect_to_host(host_adress, port_number, user_name, password, 0.5)
        if temp == 2:
            return False
        elif temp == 0:
            logger.info("recovery System aktiv")
            return True
    except Exception as e:
        logger.warning("Kein recovery System aktiv")
        return False

def connect_with_recovery_system():
    password = saved_credentials["password"]
    host_adress, user_name, port_number = get_config_data("recovery")
    temp = connect_to_host(host_adress, port_number, user_name, password, 0.5)

def rename_file(file_path, new_name):
    # Splitte das Verzeichnis und den Dateinamen
    directory, old_name = os.path.split(file_path)
    
    # Baue den neuen Dateipfad mit dem neuen Dateinamen
    new_file_path = os.path.join(directory, new_name)
    
    # Versuche, die Datei umzubenennen
    try:
        os.rename(file_path, new_file_path)
        logger.info(f"Datei erfolgreich umbenannt zu: {new_file_path}")
        return new_file_path
    except OSError as e:
        logger.error(f"Fehler beim Umbenennen der Datei: {e}")
        return None

def upload_file_to_target(path_to_file: StringVar, path_to_target_folder: str):
    global ssh_client, logger, connection_state, software_version_text
    old_file_path= path_to_file.get()
    thrash,old_file_name = os.path.split(old_file_path)
    new_file_name = rename_file(old_file_path, "fastlog.a2l")
    if is_connection_alive():
        # Verbindung zum Zielordner herstellen
        cmnd = 'cd ' + path_to_target_folder
        stdin, stdout, stderr = ssh_client.exec_command(cmnd)
        err_message_in_stderr = stderr.read()
        logger.info(f"Command {cmnd} output: {stdout.read()}")

        if err_message_in_stderr:
            logger.error(f'Path on target is not accessible: {path_to_target_folder}')
            logger.error(f'STDERR: {err_message_in_stderr.decode("utf8")}')
            return

        # Datei auf den Zielordner hochladen
        scp_client = SCPClient(ssh_client.get_transport())
        upload_file_name = path.basename(new_file_name)
        
        try:
            scp_client.put(files=new_file_name, remote_path=path_to_target_folder)
            logger.info(f"File {upload_file_name} uploaded successfully to {path_to_target_folder}")
            
            messagebox.showinfo("Upload erfolgreich", f"Datei {upload_file_name} wurde erfolgreich nach {path_to_target_folder} hochgeladen.")

        except SCPException as e:
            logger.error(f"Failed to upload file {upload_file_name}: {e}")
        finally:
            scp_client.close()
        
        ssh_client.close()
        software_version_text.set(f'--:--')
        connection_state.set(f"Disconnected")
        rename_file(new_file_name, old_file_name)
    else:
        logger.info("SSH session is not alive, upload failed.")

def update_display(displayVariable: StringVar, text: str, window,a2l_progress_status_state, color):
    displayVariable.set(text)
    change_label_color(a2l_progress_status_state, color, window)

def change_label_color(label, color, window):
    label.config(foreground=color)
    window.update()

def create_new_fastlog_file(a2l_path_lokal : StringVar, csv_path_lokal : StringVar, a2l_path_value: StringVar, a2l_progress_status_value : StringVar, window, a2l_file_name, a2l_progress_status_state):

    a2l_path = a2l_path_lokal.get()
    csv_path = csv_path_lokal.get()
    
    destination_path = a2l_fast_log_post_processing(a2l_path, csv_path, a2l_file_name)
    update_display(a2l_progress_status_value, "A2l Build process finished", window, a2l_progress_status_state, "green")
    
    a2l_path_value.set(destination_path)



