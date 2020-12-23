import utils as tool
import json
import time
import os
import sys
import requests
import cassandraSent as bd
import xlrd
import shutil
from InternalControl import cInternalControl

objControl=cInternalControl()
excel_directory=objControl.excel_dir
done_dir=objControl.done_dir
log_Dir=objControl.log_Dir
msj=''    
def maincjf():
    lsDir=os.listdir(excel_directory)
    if len(lsDir)>0:
        for fileName in os.listdir(excel_directory):
            tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt','Now reading: '+fileName)
            wb = xlrd.open_workbook(excel_directory+'\\'+fileName)
            sheet = wb.sheet_by_index(0)
            for cRow in range(3,sheet.nrows):
                tool.processRow(cRow,sheet)    
                    
            tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt','-----File done------')
            shutil.move(excel_directory+'\\'+fileName,done_dir)
        lsDir=os.listdir(excel_directory)
        if len(lsDir)==0:
            tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt','---Hey, I am done with the folder, no files remaining, baby-----')
            os.sys.exit(0)

    else:
        tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt','---Hey, the folder is empty, please add excel files-----')
        os.sys.exit(0) 
        
        

   
                           