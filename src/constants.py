from paramiko import SSHClient
from tkinter import StringVar, ttk
from os import path


FILE_SIZE_INDEX = 4
PATH_TO_TARGET_FOLDER_RAUCB = "/media/data/"
FILE_TYPE_RAUCB = ".raucb"
FILE_TYPE_A2L = ".a2l"
FILE_TYPE_CSV = '.csv'
SET_RECOVERY_SYSTEM_ON_REBOOT = "rauc status mark-active recovery.0"
REBOOT_COMMAND = "systemctl reboot"
PATH_TO_TARGET_FOLDER_A2L_SW_VERSION = "/xcp/"
PATH_TO_TARGET_FOLDER_A2L_FASTLOGGING = "/etc/module-app/"
PATH_TO_FASTLOG_FILE = "/"


SSH_CONFIG_FILE = "./config"
SSH_DEFAULT_PORT = 22
TIMEOUT = 2
#test

default_value_file_a2l_entry = "Browse a2l-file to upload"
default_value_file_entry = "Browse raucb-file to upload ->"
default_file_value_file_entry = "No update file in progress"
default_progress_state_value = "Waiting for upload"
default_value_file_fastlog = "Browse fastlog-file to upload"
default_value_file_csv = "Browse csv-file to upload"

main_window_title = 'Flashing tool'
main__window_size = '520x380'
tool_version = 'v.2.0'

default_padx = 5
default_pady = 5
saved_credentials = {"target_name": None, "password": None}
saved_credentials["target_name"] = "root"
saved_credentials["password"] = "root"


browse_window_title = "Select file for upload"

ssh_client: SSHClient
default_target_name = ""
connect_button: ttk.Button     # Connect button
connection_state: StringVar      # Connection state
software_version_tex: StringVar      # Software version



raucb_browse_button: ttk.Button     # Browse button
raucb_upload_button: ttk.Button     # Upload button
raucb_file_state: StringVar      # File state
raucb_progress_state: StringVar      # Progress state




