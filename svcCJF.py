from pathlib import Path
from SMWinservice import SMWinservice
import mainCJF
import utils as tool
import sys
import traceback
from InternalControl import cInternalControl

objControl=cInternalControl()
log_Dir=objControl.log_Dir

class svcCJF(SMWinservice):
    _svc_name_ = "svcCJF_Excel"
    _svc_display_name_ = "svcCJF_Excel"
    _svc_description_ = "Service CJF that reads from excel files"

    def start(self):
        self.isrunning = True

    def stop(self):
        self.isrunning = False

    def main(self):
        tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt','Starting CJF excel service')
        try:
            mainCJF.maincjf()
        except:
            tool.writeLogAndConsole(log_Dir,'log_excelcjf.txt',str(traceback.print_exc()))          

if __name__ == '__main__':
    svcCJF.parse_command_line()
