
import os
import sys
from flask import Flask, flash, request, render_template,Blueprint
from ast import literal_eval
from flask import current_app as app
import subprocess
import threading
process_blueprint = Blueprint('process', __name__)
import time
x=0
mesafeCnt=0
iterasyonCnt=0
toplamIterasyonCnt=0
tamamlandi=False
maliyet=0
maliyetList=list()
def worker(cmd):
    global x
    global mesafeCnt
    global iterasyonCnt
    global toplamIterasyonCnt
    global tamamlandi
    global maliyet
    global maliyetList
    global koordinatPath
    global filoPath
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
    sys.stdout.flush()

    ## But do not wait till netstat finish, start displaying output immediately ##
    while tamamlandi==False:
        nextline = p.stdout.readline().decode('ascii')
        sys.stdout.flush()

        if nextline and p.poll() is None:
            strOut = nextline.rstrip("\n\r")
            if len(strOut.split('\''))>1:
                strOut=strOut.split('\'')[1]
                #strOut=strOut.split('\'')[1]
                if "mesafe" in strOut:
                    mesafeCnt=strOut.split(" ")[1]
                elif "vrp1" in strOut:
                    iterasyonCnt = strOut.split(" ")[1]
                elif "vrp2" in strOut:
                    toplamIterasyonCnt = strOut.split(" ")[1]
                elif "tamamlandi" in strOut:
                    tamamlandi=True
                elif "maliyet" in strOut:
                    maliyet=strOut.split(" ")[1]
                    maliyetList.append(maliyet)

    if tamamlandi:
        p.kill()
t=None
@process_blueprint.route('/process',methods=[ 'GET'])
def main():
    global t
    global koordinatPath
    global filoPath
    obj=request.args.get('parameters')
    dict= literal_eval(obj)
    koordinatPath=app.config['UPLOAD_FOLDER']+ "\\"+str(dict['file1'])
    print(koordinatPath)
    filoPath = app.config['UPLOAD_FOLDER']+ "\\"+str(dict['file2'])
    print(filoPath)
    alfa=dict['alfa']
    beta = dict['beta']
    omega = dict['omega']
    kontrol=dict['kontrol']
    iterasyon=dict['iterasyon']
    stopVal=dict['stopVal']
    print(mesafeCnt)
    print(iterasyonCnt)
    print(toplamIterasyonCnt)
    if t==None:
        pyPath=app.config['ROOT_PATH']+"\\venv\\Scripts\\python.exe"
        print(pyPath)
        vrpPath=app.config['ROOT_PATH']+"\\VrpCluster.py"
        command = pyPath+" "+vrpPath+" "+koordinatPath+" "+filoPath+" "+alfa+" "+beta+" "+omega+" "+"10 "+kontrol+" "+iterasyon

        print(command)
        t = threading.Thread(target=worker, args=(command,))
        t.start()
    #elif tamamlandi:
    #    t=None
    #    tamamlandi=False
    maxMaliyet=0
    minMaliyet=0
    if len(maliyetList)>0:
        maxMaliyet=max(maliyetList)
        minMaliyet=min(maliyetList)
    return render_template("Process.html",alfa=alfa,beta=beta,omega=omega,mesafeCnt=mesafeCnt,iterasyonCnt=iterasyonCnt,toplamIterasyonCnt=toplamIterasyonCnt,tamamlandi=tamamlandi,
                           maliyet=maliyet,maxMaliyet=maxMaliyet,minMaliyet=minMaliyet,koordinatPath=koordinatPath,filoPath=filoPath)

