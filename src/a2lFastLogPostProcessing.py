import pandas as pd
import re
import logging
import os
import shutil
from tkinter import messagebox

PATTERN_CHECK_LABELNAME = r'/\*\s*Name\s*\*/\s*FastLog\w+' 
PATTERN_CHECK_LABELNAME_ERR = r'/\*\s*Name\s*\*/\s*FastErrLog\w+' 
NAME_FASTLOGGING =                  '    /* Name                   */      '
LONG_IDENTIFIER_FASTLOGGING =       '    /* Long identifier        */      '
DATA_TYPE_FASTLOGGING =             '    /* Data type              */      '
CONVERSION_METHOD_FASTLOGGING =     '    /* Conversion method      */      '

# /begin MEASUREMENT 
#     /* Name                   */      FastLog02                              
#     /* Long identifier        */      "FastLog02_0_0x0000_0x0000_0x0000" 
#     /* Data type              */      FLOAT32_IEEE
#     /* Conversion method      */      NO_COMPU_METHOD
#     /* Resolution (Not used)  */      0      
#     /* Accuracy (Not used)    */      0      
#     /* Lower limit            */      -3.402823466385289e+38
#     /* Upper limit            */      3.402823466385289e+38
#     ECU_ADDRESS                       0x0000 /* @ECU_Address@FastLog02@ */
#     FORMAT "%6.3"
#   /end MEASUREMENT 


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("flashing-tool.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def copy_file_to_working_directory(file_path, new_file_name=None):
    if os.path.exists(file_path):
        # Determine the file name
        file_name = os.path.basename(file_path)
        
        # Determine the destination folder (the current working directory)
        destination_folder = os.getcwd()
        
        # Determine the destination path considering the new file name, if provided
        if new_file_name:
            destination_path = os.path.join(destination_folder, new_file_name)
        else:
            destination_path = os.path.join(destination_folder, file_name)
        
        # Copy the file to the destination directory
        shutil.copy(file_path, destination_path)
        return destination_path

        
def read_csv_file(csv_file_path): #reads csv-file
    try:
        default_values_table = pd.read_csv(csv_file_path)
        return default_values_table
    except:
        logger.error(f"Error during reading FastLogDefault.csv with file_path: {csv_file_path}")
        return

def read_a2l_file(a2l_file_path): #reads a2l-file
    try:
        with open(a2l_file_path, 'r') as file:
            a2l_file_content = file.read()
            a2l_file_content_lines = a2l_file_content.split('\n')
            return a2l_file_content_lines
    except:
        logger.info(f"Error during reading a2l file: {a2l_file_path}")
        return
    
def check_pattern_in_string(pattern, string): #checks if a string contains a regex expression
    match = re.search(pattern, string)
    if match:
        return match.group()
    else:
        return 0

def extract_label_name_from_line(line_with_label_name): #returns from a line like this "/* Name */ FastLog{number}"" -> FastLog{number}
    label_name = line_with_label_name.replace(" ", "").split("*/")[1] 
    return label_name

def return_array_of_fastlogging(label_name, default_values_table):
    for index, row in default_values_table.iterrows(): #iterates through csv-file
            if label_name in row.iloc[0]:
                entries = row.iloc[0].split(';') #line, that contain label_name
                entries.pop(0) #deletes fastlog{number} from list and contains only an array with 3 entries e.g.(McInF_stAnRaw_iElmPha1, McInF_stAnRaw_iElmPha1Dly, McInF_stAnRaw_iElmPha1Dly2)
                return entries
            

def get_fastlogging_block(a2l_file_content_lines, fastlogging_name): #returns a block - /begin MEASUREMENT to /end MEASUREMENT, e.g. line 15 
    in_block = False
    block_lines = []
    target_line = NAME_FASTLOGGING + fastlogging_name

    for line in a2l_file_content_lines: 
        if target_line  == line:
            in_block = True 

        if in_block:
            block_lines.append(line)
            if "/end MEASUREMENT" in line:
                in_block= False
                break
    return block_lines 

def get_data_type(block): # returns data type from a block(get_fastlogging_block), "/* Data type */ FLOAT32_IEEE" -> FLOAT32_IEE
    for line in block:
        if "Data type" in line:
            return line.replace(" ","").split('*/')[1]

def get_conversion_method(block): # returns conversion method from a block(get_fastlogging_block), "/* Conversion method */ NO_COMPU_METHOD" -> NO_COMPU_METHOD   
    for line in block:
        if "Conversion method" in line:
            return line.replace(" ","").split('*/')[1] 
        
def get_ecu_adress(block): # returns conversion method from a block(get_fastlogging_block), "ECU_ADDRESS  0x0000" -> 0x0000 
    for line in block:
        if "ECU_ADDRESS" in line:
            return line.replace(" ","").split('SS')[1] 

def get_data_type_size(data_type): # returns depending von the data type a specific value
    if re.search(r'32', data_type):
        return '4'
    elif re.search(r'64', data_type):
        return '8'
    elif re.search(r'BYTE', data_type):
        return '1'
    elif re.search(r'WORD', data_type):
        return '2'
    elif re.search(r'LONGLONG', data_type):
        return '8'
    elif re.search(r'LONG', data_type):
        return '4'
    else:
        return '0'

def get_long_identifier(label_name, a2l_file_content_lines, fastlogging): # returns depending on the ecu adresses in this format : FastLogXX_data-type-size_ecu-adr-1_ecu-adr-2_ecu-adr-3
    long_identifier = ""
    long_identifier = '"' + label_name + "_" 
    long_identifier = long_identifier + get_data_type_size(get_data_type(get_fastlogging_block(a2l_file_content_lines,fastlogging[0]))) + "_" 
    long_identifier = long_identifier + get_ecu_adress(get_fastlogging_block(a2l_file_content_lines, fastlogging[0])) + "_" 
    long_identifier = long_identifier +  get_ecu_adress(get_fastlogging_block(a2l_file_content_lines, fastlogging[1]))+ "_" 
    long_identifier = long_identifier +  get_ecu_adress(get_fastlogging_block(a2l_file_content_lines, fastlogging[2])) + ' "'
    return long_identifier


def modify_block_section(a2l_file_path, label_name, a2l_file_content_lines, fastlogging, flag): # modifies a block, e.g. get_fastlogging_block()
    with open(a2l_file_path, 'r') as file:
        lines = file.readlines()

    if flag == 1:
        flag_identifier = "_FLG"
    elif flag == 0:
        flag_identifier = "_FLGE"

    within_measurement_section = False
    target_line =  NAME_FASTLOGGING + label_name
    long_identifier = get_long_identifier(label_name, a2l_file_content_lines, fastlogging)
    block_fastlogging_0 = get_fastlogging_block(a2l_file_content_lines, fastlogging[0])
    data_type = get_data_type(block_fastlogging_0)
    conversion_method = get_conversion_method(block_fastlogging_0)
    special_case = '"' + label_name
    for i, line in enumerate(lines):
        within_measurement_section = False
        if target_line in line:
            within_measurement_section = True
            modified_line = NAME_FASTLOGGING + fastlogging[0] + flag_identifier +'\n'
            lines[i] = modified_line
        elif special_case in line and not within_measurement_section:
            modified_line = NAME_FASTLOGGING + fastlogging[0] + flag_identifier +'\n'
            lines[i-1] = modified_line
            modified_line = LONG_IDENTIFIER_FASTLOGGING + long_identifier+'\n'
            lines[i] = modified_line 
        elif '/end MEASUREMENT' in line and within_measurement_section:
            within_measurement_section = False
            continue
        elif within_measurement_section:
            if LONG_IDENTIFIER_FASTLOGGING in line:
                modified_line = LONG_IDENTIFIER_FASTLOGGING + long_identifier+'\n'
                lines[i] = modified_line
            elif DATA_TYPE_FASTLOGGING in line:
                modified_line = DATA_TYPE_FASTLOGGING + data_type+'\n'
                lines[i] = modified_line
            elif CONVERSION_METHOD_FASTLOGGING in line:
                modified_line = CONVERSION_METHOD_FASTLOGGING + conversion_method+'\n'
                lines[i] = modified_line
            

    # Schreibe die modifizierten Zeilen zurück in die Datei
    with open(a2l_file_path, 'w') as file:
        file.writelines(lines)

def check_if_array_only_empty_entries(fastlogging):
    all_empty = all(not x for x in fastlogging)

    if all_empty:
        return 1
    else:
        return 0

def check_if_array_entries_empty(fastlogging):
    for entry in fastlogging:
        if not entry:
            return 1
    return 0
    
def get_label_name_from_second_line(line):
    rightPart = line.split('"')[1]
    return rightPart.split("_")[0]

def check_if_fastlogging_exist(fastlogging, a2l_file_content_lines):
    for entry in fastlogging:
        for line in a2l_file_content_lines:
            if entry in line:
                return 1
    return 0
def check_consistency_fastlogging(fastlogging, label_name, a2l_file_content_lines): 
    if check_if_array_only_empty_entries(fastlogging) == 1:
        return 2
    elif check_if_array_entries_empty(fastlogging) == 1:
        messagebox.showinfo("Fehlende Fastlog Einträge", f"In der {label_name} fehlen Fastlogging Einträge")
        return 1
    elif check_if_fastlogging_exist(fastlogging, a2l_file_content_lines) == 0:
        messagebox.showinfo("Fastlog Eintrag existiert nicht", f"Die Fastlogging Einträge existieren nicht in der {label_name}")
        return 1
    return 0


def return_label_name(line, flag):
    special_case = return_special_case_from_flag(flag)
    if special_case in line:
        label_name = get_label_name_from_second_line(line)
    else:
        line_with_label_name = check_pattern_in_string(PATTERN_CHECK_LABELNAME, line)
        if line_with_label_name == 0:
            return ""
        label_name = extract_label_name_from_line(line_with_label_name)    

    return label_name
def return_special_case_from_flag(flag):
    if flag == 1:
        return '"FastLog'
    elif flag == 0:
        return '"FastErrLog'
    else:
        return "LebronJames"

def get_flag_line(line):
    if "FastLog" in line:
        return 1
    elif "FastErrLog" in line:
        return 0
    else:
        return 2 

def modify_file(a2l_file_path, default_values_table):
    a2l_file_content_lines = read_a2l_file(a2l_file_path)
    for line in a2l_file_content_lines:
        flag = get_flag_line(line)
        label_name = return_label_name(line,flag)
        if label_name == "":
            continue
        fastlogging = return_array_of_fastlogging(label_name, default_values_table)
        
        return_value = check_consistency_fastlogging(fastlogging, label_name, a2l_file_content_lines)  
        if return_value == 1:
            return
        elif return_value == 2:
            continue
        
        modify_block_section(a2l_file_path, label_name, a2l_file_content_lines, fastlogging, flag)

def create_fastlog_name(a2l_file_name_suffix): #returns name depending if a2l_file_name_suffix is set
    if not a2l_file_name_suffix.get().replace("\n",""):
        return "fastlog_generated.a2l"
    else:
        return "fastlog_" + a2l_file_name_suffix.get().replace("\n","") + ".a2l"

def a2l_fast_log_post_processing(a2l_file_path, csv_file_path, a2l_file_name_suffix): # wrapper function
    default_values_table = read_csv_file(csv_file_path)
    a2l_file_name = create_fastlog_name(a2l_file_name_suffix)
    destination_path = copy_file_to_working_directory(a2l_file_path, a2l_file_name)
    modify_file(destination_path, default_values_table)
    return destination_path

  # ~FM 