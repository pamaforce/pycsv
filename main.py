import numpy as np
import eel
import os
import csv
import glob
import tkinter as tk
import pandas as pd
from tkinter import filedialog
import chardet

eel.init('web')

@eel.expose
def open_directory_dialog():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory()
    eel.receive_directory(directory_path)
    load_csv_files(directory_path)
    
@eel.expose
def load_current_directory():
    path = os.getcwd()
    eel.receive_directory(path)
    load_csv_files(path)
    
@eel.expose
def query_csv_files(query_words,query_files):
    for csv_file in query_files:
        if('rows' in csv_file): 
            continue
        df = pd.read_csv(csv_file['path'],encoding=csv_file['encoding'])
        df = df.replace(np.nan, '', regex=True)
        rows = df[df['REPKCode'] == query_words].to_dict(orient='records')
        csv_file['rows'] = rows
    eel.receive_csv_query_files(query_files)  
    
    

def get_encoding(file):
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


def load_csv_files(path):
    csv_files = glob.glob(os.path.join(path, '*.csv'))

    total_files = len(csv_files)
    current_file_number = 0

    result = []

    for csv_file in csv_files:
        encoding = get_encoding(csv_file)
        current_file_number += 1
        eel.update_progress(current_file_number,total_files, os.path.basename(csv_file))
        # 打开文件
        with open(csv_file, 'r',encoding=encoding) as f:
            reader = csv.reader(f)
            headers = next(reader)  # 获取表头

        file_info = {
            'id': current_file_number-1,
            'name': os.path.basename(csv_file),
            'path': csv_file,
            'encoding':encoding,
            'headers': headers
        }
        result.append(file_info)


    eel.receive_csv_files(total_files,result)  

eel.start('index.html',port=0,size=(1000, 600))