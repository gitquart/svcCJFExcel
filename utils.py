from selenium.webdriver.common.by import By
from textwrap import wrap
from InternalControl import cInternalControl
import cassandraSent as bd
import PyPDF2
import uuid
import base64
import time
import json
import os
import sys


objControl=cInternalControl()
excel_directory=objControl.excel_dir
done_dir=objControl.done_dir
log_Dir=objControl.log_Dir
download_dir=objControl.download_dir

def devuelveElemento(xPath, browser):
    cEle=0
    while (cEle==0):
        cEle=len(browser.find_elements_by_xpath(xPath))
        if cEle>0:
            ele=browser.find_elements_by_xpath(xPath)[0]

    return ele

def appendInfoToFile(path,filename,strcontent):
    txtFile=open(path+filename,'a+')
    txtFile.write(strcontent+'\n')
    txtFile.close()

def writeLogAndConsole(path,file,msg):
    appendInfoToFile(path,file,msg)
    print(msg)    

def processRow(cRow,sheet):
    for col in range(0,6):
        #For row 0 and column 0
        if col==0:
            juris_rev=sheet.cell_value(cRow,col)
            continue
        if col==1:
            filetype=sheet.cell_value(cRow,col)
            continue
        if col==2:
            subject=sheet.cell_value(cRow,col)
            continue
        if col==3:
            fileNumber=sheet.cell_value(cRow,col)
            continue
        if col==4:
            #I remove (') because some text got it and cassandra failed to insert it
            summary=summary=sheet.cell_value(cRow,col)
            str(summary).replace("'"," ")
            continue
        if col==5:
            date=sheet.cell_value(cRow,col)
            if date=='':
                date='1000/01/01'
            continue

    #Except: Code withoud pdf
    #Build the json by row            
    json_sentencia = devuelveJSON('json_sentencia.json')
    json_sentencia['id']=str(uuid.uuid4())
    json_sentencia['filenumber']=fileNumber
    data=''
    data=fileNumber.split('/')
    year=0
    year=int(data[1])
    json_sentencia['year']=year
    json_sentencia['filetype']=filetype
    json_sentencia['jurisdictionalreviewer']=juris_rev
    # timestamp accepted for cassandra: yyyy-mm-dd 
    #In web site, the date comes as day-month-year
    dateStr=date.split('/') #0:day,1:month,2:year
    dtDate=dateStr[2]+'-'+dateStr[1]+'-'+dateStr[0]
    json_sentencia['publication_datetime']='1000-01-01'
    json_sentencia['strpublicationdatetime']=dtDate
    json_sentencia['subject']=subject
    json_sentencia['summary']=str(summary).replace("'"," ")   

    #Insert information to cassandra
    lsRes=bd.cassandraBDProcess(json_sentencia)
    if lsRes[0]:
        writeLogAndConsole(log_Dir,'log_excelcjf.txt','Sentencia added:'+str(fileNumber))
    else:
        writeLogAndConsole(log_Dir,'log_excelcjf.txt','Keep going...sentencia existed:'+str(fileNumber))

        

"""
readPDF is done to read a PDF no matter the content, can be image or UTF-8 text
"""
def readPDF(file):  
    with open(download_dir+'\\'+file, "rb") as pdf_file:
        bContent = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    return bContent  
    

"""
This is the method to call when fetching the pdf enconded from cassandra which is a list of text
but that text is really bytes.
"""
def decodeFromBase64toNormalTxt(b64content):
    normarlText=base64.b64decode(b64content).decode('utf-8')
    return normarlText


def getPDFfromBase64(bContent):
    #Tutorial : https://base64.guru/developers/python/examples/decode-pdf
    bytes = base64.b64decode(bContent, validate=True)
    # Write the PDF contents to a local file
    f = open(download_dir+'\\result.pdf', 'wb')
    f.write(bytes)
    f.close()
    return "PDF delivered!"

def TextOrImageFromBase64(bContent):
    #If sData got "EOF" is an image, otherwise is TEXT
    sData=str(bContent)
    if "EOF" in sData:
        res=getPDFfromBase64(bContent) 
    else:
        res=decodeFromBase64toNormalTxt(bContent)

    return res 

def devuelveJSON(jsonFile):
    with open(jsonFile) as json_file:
        jsonObj = json.load(json_file)
    
    return jsonObj 

def processPDF(json_sentencia,lsRes):
    lsContent=[]  
    for file in os.listdir(download_dir): 
        strFile=file.split('.')[1]
        if strFile=='PDF' or strFile=='pdf':
            strContent=readPDF(file) 
            print('Start wrapping text...') 
            lsContent=wrap(strContent,1000)  
            json_documento=devuelveJSON('json_documento.json')
            if lsRes[0]:
                json_documento['idDocumento']=json_sentencia['id']
            else:
                json_documento['idDocumento']=lsRes[1]

            json_documento['documento']=json_sentencia['filenumber']
            json_documento['fuente']='cjf'
            totalElements=len(lsContent)
            result=insertPDFChunks(0,0,0,totalElements,lsContent,json_documento,0)
            if result==False:
                print('PDF Ended!')       
           
        
def insertPDFChunks(startPos,contador,secuencia,totalElements,lsContent,json_documento,done):
    if done==0:
        json_documento['lspdfcontent'].clear()
        json_documento['id']=str(uuid.uuid4())
        for i in range(startPos,totalElements):
            if i!=totalElements-1:
                if contador<=20:
                    json_documento['lspdfcontent'].append(lsContent[i])
                    contador=contador+1
                else:
                    currentSeq=secuencia+1
                    json_documento['secuencia']=currentSeq
                    res=bd.insertPDF(json_documento) 
                    if res:
                        print('Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))  
                    else:
                        print('Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq)) 

                    return insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,0) 
            else:
                json_documento['lspdfcontent'].append(lsContent[i])
                currentSeq=secuencia+1
                json_documento['secuencia']=currentSeq
                res=bd.insertPDF(json_documento) 
                if res:
                    print('Last Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))
                else:
                    print('Last Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))

                return  insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,1)
    else:
        return False            

                             


                

def readPyPDF(file):
    #This procedure produces a b'blabla' string, it has UTF-8
    #PDF files are stored as bytes. Therefore to read or write a PDF file you need to use rb or wb.
    lsContent=[]
    pdfFileObj = open(download_dir+'\\'+file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pags=pdfReader.numPages
    for x in range(0,pags):
        pageObj = pdfReader.getPage(x)
        #UTF-8 is the right encodeing, I tried ascii and didn't work
        #1. bContent is the actual byte from pdf with utf-8, expected b'bla...'
        bcontent=base64.b64encode(pageObj.extractText().encode('utf-8'))
        lsContent.append(str(bcontent.decode('utf-8')))
                         
    pdfFileObj.close()    
    return lsContent       