import tkinter as tk
from tkinter import ttk
from control import (
    connect_button_function,
    browse_button_function,
    update_button_function,
    upload_file_to_target,
    create_new_fastlog_file,
    update_display,
    change_label_color
)
from constants import *
from expections import *

# the gui window
window = tk.Tk()
window.title(main_window_title)
window.geometry(main__window_size)

# Create a notebook
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Create first tab
tab_raucb = ttk.Frame(notebook)
notebook.add(tab_raucb, text='Flash')

# widgets - window sections
title_section_frame = tk.Frame(master=tab_raucb, width=500, height=50)
title = ttk.Label(master=title_section_frame, text='Flashing Tool')
version = ttk.Label(master=title_section_frame, text=tool_version)
recovery_system = ttk.Label(master=title_section_frame, text="Recovery system active", foreground="red")

title_section_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')
title.grid(row=0, column=0, padx=default_padx, pady=default_pady, sticky='w')
version.grid(row=0, column=1, padx=(150,110), pady=default_pady, sticky='w')

# — Info section (title and content frame)
info_section_frame = tk.Frame(master=tab_raucb, width=500, height=80, borderwidth=5, relief='groove')
info_section_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')
info_section_frame.grid_propagate(False)

info_section_title = ttk.Label(master=info_section_frame, text='Info section')
info_section_content_frame = tk.Frame(master=info_section_frame, width=300, height=30)

info_section_title.grid(row=0, column=0, padx=default_padx, sticky='w')
info_section_content_frame.grid(row=1, column=0, padx=default_padx, sticky='w')

# –– Row 1: connect-button, status frame
connect_state = tk.StringVar(value='Disconnected')
software_version_text_value= tk.StringVar(value='--:--')
connect_button = ttk.Button(
    master=info_section_content_frame,
    text='connect',
    command=lambda: connect_button_function(connect_state, software_version_text_value, window, connect_button, recovery_system)
)
info_section_status_frame= tk.Frame(master=info_section_content_frame, width=150, height=15)

connect_button.grid(row=0, column=0, padx=5)
info_section_status_frame.grid(row=0, column=1, padx=50, pady=default_pady, sticky='w')

# —– Row 1: Connection status and version
connect_status_title = ttk.Label(master=info_section_status_frame, text='Connection state:')
connect_status = ttk.Label(master=info_section_status_frame, textvariable=connect_state)
software_version_label = ttk.Label(master=info_section_status_frame, text='SW Version:')
software_version = ttk.Label(master=info_section_status_frame, textvariable=software_version_text_value)

connect_status_title.grid(row=0, column=0, sticky='w')
connect_status.grid(row=0, column=1, padx=15, sticky='w')
software_version_label.grid(row=1, column=0, sticky='w')
software_version.grid(row=1, column=1, padx=15, sticky='w')

# — Select file section (title and content frame)
raucb_select_section_frame = tk.Frame(master=tab_raucb, width=500, height=90, borderwidth=5, relief='groove')
raucb_select_section_frame.grid(row=2, column=0, padx=10, pady=10, sticky='w')
raucb_select_section_frame.grid_propagate(False)

location_section_title = ttk.Label(master=raucb_select_section_frame, text='Select raucb file section')
raucb_select_section_content_frame = tk.Frame(master=raucb_select_section_frame, width=300, height=30)

location_section_title.grid(row=0, column=0, padx=default_padx, sticky='w')
raucb_select_section_content_frame.grid(row=1, column=0, padx=default_padx, pady=default_pady, sticky='w')

# —– Row 1: path filed and buttons
path_value_raucb = tk.StringVar()
path_value_raucb.set(default_value_file_entry)

raucb_file_state_value = tk.StringVar()
raucb_file_state_value.set(default_file_value_file_entry)
raucb_progress_state_value = tk.StringVar()
raucb_progress_state_value.set(default_progress_state_value)

path_entry = ttk.Entry(master=raucb_select_section_content_frame, textvariable=path_value_raucb, state="readonly")
raucb_browse_button = ttk.Button(master=raucb_select_section_content_frame, text='Browse', command=lambda: browse_button_function(path_value_raucb,FILE_TYPE_RAUCB))
raucb_update_button = ttk.Button(
    master=raucb_select_section_content_frame,
    text='Update',
    command=lambda: update_button_function(path_value_raucb, raucb_file_state_value, raucb_progress_state_value,raucb_browse_button, raucb_update_button, PATH_TO_TARGET_FOLDER_RAUCB, FILE_TYPE_RAUCB, progress_status_state_raucb, window)
)

path_entry.grid(row=0, column=0, padx=default_padx, sticky='w')
raucb_browse_button.grid(row=0, column=1, padx=15)
raucb_update_button.grid(row=0, column=2, padx=50)

# — Progress section (title and content frame)
progress_section_frame = tk.Frame(master=tab_raucb, width=500, height=80, borderwidth=5, relief='groove')
progress_section_frame.grid(row=3, column=0, padx=10, pady=10, sticky='w')
progress_section_frame.grid_propagate(False)

progress_section_title = ttk.Label(master=progress_section_frame, text='Progress section')
progress_section_content_frame = tk.Frame(master=progress_section_frame)

progress_section_title.grid(row=0, column=0, padx=default_padx, sticky='w')
progress_section_content_frame.grid(row=1, column=0, padx=default_padx, pady=default_pady, sticky='w')

# —– Row 1: File status and progress status
file_label = ttk.Label(master=progress_section_content_frame, text='File:')
file_state = ttk.Label(master=progress_section_content_frame, textvariable=raucb_file_state_value)
progress_status_label_raucb = ttk.Label(master=progress_section_content_frame, text='Status:')
progress_status_state_raucb = ttk.Label(master=progress_section_content_frame, textvariable=raucb_progress_state_value)

file_label.grid(row=0, column=0, padx=default_padx, sticky='w')
file_state.grid(row=0, column=1, padx=15, sticky='w')
progress_status_label_raucb.grid(row=1, column=0, padx=default_padx, sticky='w')
progress_status_state_raucb.grid(row=1, column=1, padx=15, sticky='w')

#
# — Select file section
#
# - Select file section - section, frame and title

tab_a2l = ttk.Frame(notebook)
notebook.add(tab_a2l, text='Create a2l File')

title_section_frame_a2l = tk.Frame(master=tab_a2l, width=500, height=50)
title_a2l = ttk.Label(master=title_section_frame_a2l, text='Create a2l File')
version_a2l = ttk.Label(master=title_section_frame_a2l, text=tool_version)

title_section_frame_a2l.grid(row=0, column=0, padx=10, pady=10, sticky='w')
title_a2l.grid(row=0, column=0, padx=default_padx, pady=default_pady, sticky='w')
version_a2l.grid(row=0, column=1, padx=150, pady=default_pady, sticky='w')

a2l_select_section_frame = tk.Frame(master=tab_a2l, width=500, height=80, borderwidth=5, relief='groove')
a2l_select_section_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')
a2l_select_section_frame.grid_propagate(False)

a2l_location_section_title = ttk.Label(master=a2l_select_section_frame, text='Select a2l file section')
a2l_select_section_content_frame = tk.Frame(master=a2l_select_section_frame, width=300, height=30)

a2l_location_section_title.grid(row=0, column=0, padx=default_padx, sticky='w')
a2l_select_section_content_frame.grid(row=1, column=0, padx=default_padx, pady=default_pady, sticky='w')

# - Select file section - entry + button 

a2l_path_value = tk.StringVar()
a2l_path_value.set(default_value_file_a2l_entry)
a2l_file_state_value = tk.StringVar()
a2l_file_state_value.set(default_file_value_file_entry)

a2l_path_entry = ttk.Entry(master=a2l_select_section_content_frame, textvariable = a2l_path_value, state="readonly", width=28)
a2l_browse_button = ttk.Button(master = a2l_select_section_content_frame, text='Browse a2l file',command=lambda: browse_button_function(a2l_path_value, FILE_TYPE_A2L))
a2l_update_button = ttk.Button(master = a2l_select_section_content_frame, 
                               text='Upload a2l file', 
                               command=lambda: upload_file_to_target(a2l_path_value, PATH_TO_TARGET_FOLDER_A2L_FASTLOGGING)
)

a2l_path_entry.grid(row=1, column=0,  padx=default_padx, sticky='w')
a2l_browse_button.grid(row=1, column=1, padx=15)
a2l_update_button.grid(row=1, column= 2, padx=50)

#
# - Browse a2l & csv file section
#
# - Browse a2l & csv file section - section, frame and title

a2l_browse_section_frame = tk.Frame(master=tab_a2l, width=500, height=90, borderwidth=5, relief='groove')
a2l_browse_section_frame.grid(row=2, column=0, padx=10, pady=10, sticky='w')
a2l_browse_section_frame.grid_propagate(False)

a2l_location_create_title = ttk.Label(master=a2l_browse_section_frame, text='Browse a2l & csv file section')
a2l_create_section_content_frame = tk.Frame(master=a2l_browse_section_frame, width=300, height=30)

a2l_location_create_title.grid(row=0, column=0, padx=default_padx, sticky='w')
a2l_create_section_content_frame.grid(row=1, column=0, padx=default_padx, pady=default_pady, sticky='w')

# - Browse a2l & csv file section - browse a2l file section: entry + button
 
a2l_path_value_fastlog = tk.StringVar()
a2l_path_value_fastlog.set(default_value_file_fastlog)

a2l_path_entry_fastlog = ttk.Entry(master=a2l_create_section_content_frame, textvariable=a2l_path_value_fastlog, state="readonly", width=28)
a2l_browse_button_fastlog = ttk.Button(master=a2l_create_section_content_frame, text='Browse fastlog file', command=lambda: browse_button_function(a2l_path_value_fastlog, FILE_TYPE_A2L))

a2l_path_entry_fastlog.grid(row=1, column=0, padx=default_padx, sticky='w')
a2l_browse_button_fastlog.grid(row=1, column=1, padx=15, sticky='w')

# - Browse a2l & csv file section - browse csv file section: entry + button 

csv_path_value = tk.StringVar()
csv_path_value.set(default_value_file_csv)

csv_path_entry = ttk.Entry(master=a2l_create_section_content_frame, textvariable=csv_path_value, state="readonly", width=28)
csv_browse_button = ttk.Button(master=a2l_create_section_content_frame, text='Browse csv file', command=lambda: browse_button_function(csv_path_value, FILE_TYPE_CSV))

csv_path_entry.grid(row=2, column=0, padx=default_padx, sticky='w')
csv_browse_button.grid(row=2, column=1, padx=15,sticky='w')

#
# - Create a2l file section
#
# - Create a2l file sectiom - section, frame and title

a2l_create_section_frame = tk.Frame(master=tab_a2l, width=500, height=80, borderwidth=5, relief='groove')
a2l_create_section_frame.grid(row=3, column=0, padx=10, pady=10, sticky='w')
a2l_create_section_frame.grid_propagate(False)

a2l_section_title = ttk.Label(master=a2l_create_section_frame, text='Create a2l section')
a2l_create_section_content_frame = tk.Frame(master=a2l_create_section_frame, width=300, height=30)

a2l_section_title.grid(row=0, column=0, padx=default_padx, sticky='w')
a2l_create_section_content_frame.grid(row=1, column=0, padx=default_padx, pady=default_pady, sticky='w')

# - Create a2l file section - browse a2l file section: entry + button 

a2l_input_text_label = ttk.Label(master=a2l_create_section_content_frame, text='Name:')
a2l_name_text_label = ttk.Label(master=a2l_create_section_content_frame, text="fastlog_")
a2l_name_text_label_suffix = ttk.Label(master = a2l_create_section_content_frame, text=".a2l")
a2l_input_file_name = tk.Text(master=a2l_create_section_content_frame, height=1.45,width=15)
create_new_fastlog_file_button = ttk.Button(master=a2l_create_section_content_frame, text='Create new fastlog file', command=lambda:(getTextInput(),update_display(a2l_progress_state_value, "In Progress", window,a2l_progress_status_state,"orange"),create_new_fastlog_file(a2l_path_value_fastlog, csv_path_value, a2l_path_value, a2l_progress_state_value, window, a2l_file_name, a2l_progress_status_state)))
a2l_file_name = tk.StringVar()
a2l_progress_state_value = tk.StringVar(value="No creation in progress")
a2l_progress_status_label = ttk.Label(master=a2l_create_section_content_frame, text='Status:')
a2l_progress_status_state = ttk.Label(master=a2l_create_section_content_frame, textvariable=a2l_progress_state_value)

a2l_input_text_label.grid(row=1, column= 0, sticky='w', padx=default_padx)
a2l_name_text_label.grid(row=1, column=1, sticky='e')
a2l_input_file_name.grid(row=1, column=2, sticky='w', padx=default_padx)
a2l_name_text_label_suffix.grid(row=1, column=3, sticky='w')
create_new_fastlog_file_button.grid(row=1, column = 4, padx=default_padx)
a2l_progress_status_label.grid(row=2, column=0, padx=default_padx, sticky='w')
a2l_progress_status_state.grid(row=2, column=1,columnspan=2, sticky='w')
a2l_input_file_name.insert(1.0, "generated")

def getTextInput():
    a2l_file_name.set(a2l_input_file_name.get("1.0","end"))

# run
window.mainloop()
