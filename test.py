import utils as tool
import json
import time
import os
import sys
import requests
import cassandraSent as bd
import xlrd

excel_directory='C:\\Users\\1098350515\\Documents\\cjfexcel'
msj=''    
#Get the list
for fileName in os.listdir(excel_directory):
    print(excel_directory+'\\'+fileName)
    wb = xlrd.open_workbook(excel_directory+'\\'+fileName)
    sheet = wb.sheet_by_index(0)
    # For row 0 and column 0
    print(sheet.cell_value(3, 0))