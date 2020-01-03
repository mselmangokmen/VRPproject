#!python

import sys

from Truck import Kamyon
from myNode import myNode
import ctypes as c
from Iteration import iterasyon
import numpy as np
import multiprocessing as mp
from multiprocessing import Process, Value, Manager, Queue
from sklearn.cluster import KMeans


import  pandas as pd
import statistics
from datetime import datetime
from geopy.distance import distance
import time
from math import cos,sin

def nodeOlustur(nList,dolulukList,orjDolulukList):
    xl = pd.ExcelFile(sys.argv[1])
    #xl = pd.ExcelFile("C:\\Users\\selman\\Desktop\\bolvadin.xlsx")
    sheets = xl.sheet_names
    df1 = xl.parse(sheets[0])
    sinir = df1.shape[0]
    #sinir = 200
    cnt = 0
    for i in range(sinir):
        if i == 0:

            x = cos(df1.iloc[i, 2]) * cos(df1.iloc[i, 1])
            y = cos(df1.iloc[i, 2]) * sin(df1.iloc[i, 1])
            n = myNode(i, df1.iloc[i, 0], df1.iloc[i, 1], df1.iloc[i, 2],x,y, 0, True)
            dolulukList.append(0)
            orjDolulukList.append(0)
            nList.append(n)
        else:
            x = cos(df1.iloc[i, 2]) * cos(df1.iloc[i, 1])
            y = cos(df1.iloc[i, 2]) * sin(df1.iloc[i, 1])
            n = myNode(i, df1.iloc[i, 0], df1.iloc[i, 1], df1.iloc[i, 2],x,y, 30, False)
            dolulukList.append(30)
            orjDolulukList.append(30)
            nList.append(n)



def filo_olustur(manager,filo):

    xl = pd.ExcelFile(sys.argv[2])
    #xl = pd.ExcelFile("C:\\Users\\selman\\Desktop\\bolvadin.xlsx")
    sheets = xl.sheet_names
    df1 = xl.parse(sheets[0])

    sinir = df1.shape[0]
    for i in range(sinir):
        k = Kamyon(manager,i, df1.iloc[i, 0], df1.iloc[i, 1], df1.iloc[i, 2], df1.iloc[i, 3], df1.iloc[i, 4])
        filo.append(k)






def nodeGetir(nList, ID):
    nd = None
    for n in nList:
        if n.id == ID:
            nd = n
            break
    return nd

def distProcess(l ,distCnt,mesafeMatrix, nList, start, end):
    scHold=int(time.time())
    starttime=int(time.time())
    for i in range(start, end):

        for j in range(len(nList)):

            scHold=int(time.time())
            dValue = distance([nList[i].Y, nList[i].X], [nList[j].Y, nList[j].X]).m
            l.acquire()
            mesafeMatrix[(i * len(nList)) + j] = dValue
            distCnt.value=distCnt.value+1
            percent=(100*distCnt.value)/(len(nList)*len(nList))

            if (scHold - int(starttime)) > 1:
                msfStr="mesafe "+str(int(percent))
                print(msfStr.encode('ascii'),file=sys.stdout, flush=True)
                scHold=int(time.time())
                starttime=int(time.time())
            l.release()



def vrpProcess(cluster,l,q,index,dolulukList,ziyaretList,iterasyonList,cnt,kamyonSayisi,enYakinKontrol ,filo, mesafeMatrix, ziyaretMatrix, nList, alfa, beta, omega):

            starttime=int(time.time())

            zcnt=0
            for c in cluster:
                if ziyaretMatrix[c]!=0:
                    zcnt+=1
            nonZeroCnt=zcnt

            while nonZeroCnt< len(cluster)-1 :
                l.acquire()
                try:
                    scHold=int(time.time())
                    selectedID = filo[index].secim_yap(cluster,kamyonSayisi,dolulukList,ziyaretList,enYakinKontrol,alfa, beta, omega, nList, mesafeMatrix, ziyaretMatrix)

                    if selectedID!=None:
                        mess=str(index)+" "+str(cnt)+" "+str(selectedID)
                        q.put(mess)
                    else:
                        break

                    while True:
                        msg = q.get()
                        if int(msg.split(" ")[0]) ==index and int(msg.split(" ")[1]) ==cnt:
                            selectedID=int(msg.split(" ")[2])
                            break

                    if (selectedID != filo[index].mevcutKonum.value and ziyaretMatrix[selectedID] == 0):

                        ziyaretMatrix[selectedID] = filo[index].id


                        ziyaretList.append([filo[index].id,filo[index].mevcutKonum.value,selectedID])
                        filo[index].rota_ekle(filo[index].mevcutKonum.value, selectedID, mesafeMatrix[filo[index].mevcutKonum.value][selectedID])
                        filo[index].kapasite.value = filo[index].kapasite.value - dolulukList[selectedID]
                        dolulukList[selectedID] = 0
                        filo[index].konumDegistir(selectedID)
                        nonzero=np.count_nonzero(ziyaretMatrix)
                        yuzde= (100*nonzero)/(len(ziyaretMatrix)-1)
                        if (scHold- int(starttime)) > 1:
                            vrpStr="vrp1 "+str(yuzde)
                            print(vrpStr.encode('ascii'),file=sys.stdout, flush=True)
                            scHold=int(time.time())
                            starttime=int(time.time())

                finally:
                    l.release()
                zcnt = 0
                for c in cluster:
                    if ziyaretMatrix[c] != 0:
                        zcnt += 1
                nonZeroCnt = zcnt

            it= iterasyon(cnt,filo[index].id,filo[index].plaka)
            for r in filo[index].rota:
                it.rota.append(r)
            iterasyonList.append(it)

def veriSifirla(ziyaretMatrix,kList,nList,dolulukList):

    for ix in range(len(ziyaretMatrix)):
        ziyaretMatrix[ix]=0

    for k in kList:
        k.rota[:]=[]
        k.kapasite.value=k.orjKapasite
        k.konumDegistir(0)
    for ix in range(len(dolulukList)):
        dolulukList[ix]=orjDolulukList[ix]



if __name__ == '__main__':
    alfa = float(sys.argv[3])
    beta =  float(sys.argv[4])
    omega =  float(sys.argv[5])
    distCnt = Value('i', 0)
    start_time = time.time()
    processCount = int(sys.argv[6])
    manager = Manager()
    enyakinkontrol=int(sys.argv[7])
    nList = manager.list()
    kontrolList=manager.list()
    mesafeMatrix = manager.list()
    ziyaretMatrix = manager.list()
    q=Queue()
    ziyaretList = manager.list()

    dolulukList = manager.list()
    orjDolulukList = manager.list()
    filo = manager.list()
    iterasyonList =manager.list()
    iterasyonCnt=int(sys.argv[8])


    iterasyonKontrol=manager.list()


    nodeOlustur(nList,dolulukList,orjDolulukList)

    nodeSayisi = len(nList)
    l = manager.Lock()

    filo_olustur(manager,filo)
    [ziyaretMatrix.append(0) for i in range(nodeSayisi )]
    [mesafeMatrix.append([]) for i in range(nodeSayisi )]

    mesafeMatrix = mp.Array(c.c_double, (nodeSayisi) * (nodeSayisi))

    lm = np.linspace(0, len(nList), num=processCount+1, dtype=int)

    matrixProcs = []


    for index in range(len(lm) - 1):
        proc = Process(target=distProcess, args=(l,distCnt,mesafeMatrix, nList, lm[index], lm[index + 1]))

        matrixProcs.append(proc)
        proc.start()

    #print("işlem sayısı==>"+str(len(matrixProcs))+"\n")
    for proc in matrixProcs:
        proc.join()
    arr = np.frombuffer(mesafeMatrix.get_obj())

    mesafeMatrix = arr.reshape(((nodeSayisi ), (nodeSayisi )))
    msfStrTam="mesafe 100"
    print(msfStrTam.encode('ascii'),file=sys.stdout, flush=True)

    # print(mesafeMatrix)


    xList=list()
    yList=list()
    for n in nList:
        xList.append(n.X)
        yList.append(n.Y)

    Data = {'x': xList, 'y': yList}
    dfTemp = pd.DataFrame(Data, columns=['x', 'y'])
    kmeans = KMeans(n_clusters=len(filo), init='k-means++', max_iter=900, n_init=10, random_state=0)
    y_kmeans = kmeans.fit(dfTemp)
    labels = kmeans.predict(dfTemp)

    c = labels.astype(int)

    #Data = {'x': xList, 'y': yList, 'c': c}
    #dfCluster = pd.DataFrame(Data, columns=['x', 'y', 'c'])
    clusters=[]
    for i in range(len(filo)):
        clusters.append([])
    for i in range(len(clusters)):
        clusters[i].append(0)

    for i in range(1,len(c)):
        clusters[c[i]].append(i)


    procs = []
    cnt=0
    dt = datetime.now()

    while cnt<iterasyonCnt:

        for index in range(len(filo)):

            proc = Process(target=vrpProcess,args=(clusters[index],l,q,index,dolulukList,ziyaretList,iterasyonList,cnt,len(filo),enyakinkontrol, filo, mesafeMatrix, ziyaretMatrix, nList, alfa, beta, omega))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()

        il = [x for x in iterasyonList if x.itNumber == cnt]
        toplamMaliyet = 0
        for it in il:
            it.maliyetHesapla()
            toplamMaliyet += it.maliyet
        mlytStr="maliyet "+str(toplamMaliyet)
        print(mlytStr.encode('ascii'),file=sys.stdout, flush=True)
        vrp1Str="vrp1 100"
        print(vrp1Str.encode('ascii'),file=sys.stdout, flush=True)
        totalYuzde=((cnt+1)*100)/iterasyonCnt
        vrp2Str="vrp2 "+str((totalYuzde))
        print(vrp2Str.encode('ascii'),file=sys.stdout, flush=True)
        veriSifirla(ziyaretMatrix,filo,nList,dolulukList)
        cnt+=1



    stdList=list()
    mList=list()
    uygList=list()
    f = open('output', 'w')  # python will convert \n to os.linesep
    for i in range(iterasyonCnt):
        stdVars=list()
        il=  [x for x in iterasyonList if x.itNumber == i]
        toplamMaliyet=0
        for it in il:
            it.maliyetHesapla()
            toplamMaliyet+=it.maliyet
            stdVars.append(it.maliyet)
        stdList.append(statistics.stdev(stdVars))
        mList.append(toplamMaliyet)
        f.write("iterasyon maliyet "+str(i)+" "+str(toplamMaliyet)+"\n")
        #print(str(i)+". maliyeti==>"+str(toplamMaliyet))
    maxVal= max(mList)
    for it in iterasyonList:
        it.maliyetHesapla()
        f.write(it.rotaAl()+"\n")
    #print("tamamlandı")
    #print("uygunluk değeri==>")
    for i in range(len(stdList)):
        uygList.append((stdList[i]/maxVal))
        f.write("uygunluk "+str(i)+" "+str(stdList[i]/maxVal)+"\n")
    #print("min uygunluk değeri index==>")
    f.write("min uygunluk "+ str(uygList.index(min(uygList)))+" " +str(min(uygList)) +"\n")
    f.write("min maliyet "+ str(mList.index( min(mList)))+" "+str(min(mList))+"\n")

    xlist = list()
    il = [x for x in iterasyonList if x.itNumber == 0]
    for i in il:
        for k in range(len(i.rota)):
            xlist.append(i.rota[k][0])
        xlist.append(i.rota[-1][1])

    f.close()
    tmmStr="tamamlandi"
    print(tmmStr.encode('ascii'),file=sys.stdout, flush=True)

    #print(xlist)

