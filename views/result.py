import os
import sys
import json
import googlemaps
from xml.dom import minidom
import simplekml
import math
from flask import current_app as app

from flask import Flask, flash, request, render_template, Blueprint,send_file
from ast import literal_eval
import subprocess
import threading

result_blueprint = Blueprint('result', __name__)
import pandas as pd

nodeList = list()
kamyonList = list()
iterasyonList = list()
maliyetDusuk = ""
maliyetUygun = ""
maliyetList = list()
uygunlukList = list()
minUygDict = dict()
minMalDict = dict()


def nodeOlustur(path):
    global nodeList
    nodeList.clear()
    xl = pd.ExcelFile(path)
    sheets = xl.sheet_names
    df1 = xl.parse(sheets[0])
    sinir = df1.shape[0]
    #sinir = 200
    cnt = 0
    for i in range(sinir):
        n = (i, df1.iloc[i, 0], df1.iloc[i, 1], df1.iloc[i, 2])
        nodeList.append(n)


def read_output():
    global nodeList
    global iterasyonList
    global maliyetList
    global uygunlukList
    global minUygDict
    global minMalDict
    global kamyonList
    f = open('output')
    line = f.readline()
    iterasyonList = []
    maliyetList = []
    uygunlukList = []
    minUygDict.clear()
    minMalDict.clear()
    kamyonList = []
    while line:
        if "rota" in line:
            spText = line.split("#")
            kamyonID = spText[0].split(" ")[1]

            kamyonPlaka = spText[0].split(" ")[2]
            iterasyonID = spText[1].split(" ")[0]

            rotaTxt = spText[1].split(" ")[1]
            print(rotaTxt)
            splitRota = rotaTxt.split("-")
            print(str(len(splitRota))+(" split"))
            kRota = ""
            for s in splitRota:
                kRota += str(nodeList[int(s)][0]) + "," + str(nodeList[int(s)][3]) + "," + str(
                    nodeList[int(s)][2]) + ";"
            kRota = kRota[:-1]
            d = dict()
            d["iterasyonID"] = int(iterasyonID)
            d["kamyonID"] = int(kamyonID)
            d["kamyonPlaka"] = kamyonPlaka
            d["rota"] = kRota
            d["maliyet"]=float(spText[2].strip().rstrip().lstrip())
            if (kamyonID, kamyonPlaka) not in kamyonList:
                kamyonList.append((kamyonID, kamyonPlaka))
            iterasyonList.append(d)
        if "iterasyon maliyet" in line:
            maliyetList.append((int(line.split(" ")[2]), line.split(" ")[3]))
        if "uygunluk" in line and "min uygunluk" not in line:
            uygunlukList.append((int(line.split(" ")[1]), line.split(" ")[2]))
        if "min uygunluk" in line:
            minUygDict["minID"] = int(line.split(" ")[2])
            minUygDict["uygunluk"] = line.split(" ")[3]
        if "min maliyet" in line:
            minMalDict["minID"] = int(line.split(" ")[2])
            minMalDict["maliyet"] = line.split(" ")[3]

        line = f.readline()
    f.close()


@result_blueprint.route('/result', methods=['POST'])
def main():
    if request.method == 'POST':
        koordinatPath = request.form['koordinatPath']

        nodeOlustur(koordinatPath)

        read_output()

        return render_template('result.html', iterasyonList=iterasyonList, maliyetList=maliyetList,
                               uygunlukList=uygunlukList, minUygDict=minUygDict, minMalDict=minMalDict,
                               kamyonList=kamyonList, maliyetLen=len(maliyetList))


@result_blueprint.route('/ciktiOlustur', methods=['GET'])
def ciktiOlustur():


    kamyonOption = request.args.get('kamyonOption')
    kMaliyetList=list()
    if len(iterasyonList) > 0:
        rota=""
        minMaliyet = float("inf")
        minIndex=0
        for iter in iterasyonList:
            if  iter["kamyonID"] == int(kamyonOption):
                maliyet=float(iter["maliyet"])
                kMaliyetList.append(maliyet)
                if minMaliyet>=maliyet:
                    minMaliyet=maliyet
                    minIndex=int(iter["iterasyonID"])
                    rota=iter["rota"]
        print(kMaliyetList)
        print("minMaliyet: "+str(minMaliyet))
        fname=app.config['ROOT_PATH']+"\\single_"+str(minIndex)+"_"+str(kamyonOption)+".kml"
        if os.path.exists(fname):
            os.remove(fname)
            print("kaldırıldı")
            if len(rota) <= 0:
                return "hata"
        rotaList = rota.split(';')
        for i in range(len(rotaList)):
            r = rotaList[i].split(',')[1] + "," + rotaList[i].split(',')[2]
            rotaList[i] = r

            if len(rotaList) <= 1:
                return "hata"

        gmaps = googlemaps.Client(key='AIzaSyB9ieuSqTWkOu6OzFIF8Bec8_OOPW1MRNM')

        legList = list()
        k = 20
        print(k)
        for i in range(math.ceil(len(rotaList) / k)):
            directions_result = ""
            if len(rotaList) - (i * k) <= k:
                if len(legList)>0:
                    directions_result = gmaps.directions(legList[-1], rotaList[-1],
                                                                 waypoints=rotaList[((i * k)):(len(rotaList))],
                                                                 mode="driving", optimize_waypoints=True)
                else:
                    directions_result = gmaps.directions(rotaList[i * k], rotaList[-1],
                                                                 waypoints=rotaList[((i * k) + 1):(len(rotaList))],
                                                                 mode="driving", optimize_waypoints=True)
            else:
                if len(legList)>0:
                    directions_result = gmaps.directions(legList[-1], rotaList[(i * k) + k],
                                                                 waypoints=rotaList[((i * k)):((i * k) + k)],
                                                                 mode="driving", optimize_waypoints=True)
                else:
                    directions_result = gmaps.directions(rotaList[i * k], rotaList[(i * k) + k],
                                                                 waypoints=rotaList[((i * k) + 1):((i * k) + k)],
                                                                 mode="driving", optimize_waypoints=True)

            for k in range(len(directions_result[0]["legs"])):
                for l in range(len(directions_result[0]["legs"][k]["steps"])):
                    legList.append(str(
                        directions_result[0]["legs"][k]["steps"][l]["start_location"]["lat"]) + "," + str(
                        directions_result[0]["legs"][k]["steps"][l]["start_location"]["lng"]))
                    legList.append(
                        str(directions_result[0]["legs"][k]["steps"][l]["end_location"]["lat"]) + "," + str(
                            directions_result[0]["legs"][k]["steps"][l]["end_location"]["lng"]))


        kml = simplekml.Kml()
        for i in range(len(legList) - 1):
            ll = legList[i].split(',')
            lln = legList[i + 1].split(',')
            linestring = kml.newlinestring()
            linestring.coords = [(ll[1], ll[0]), (lln[1], lln[0])]

        kovaList = rota.split(';')
        for i in range(len(kovaList)):
            pnt = kml.newpoint()
            if i==0:
                pnt.style.labelstyle.color = 'ff0000ff'
            if i == len(kovaList)-1:
                pnt.style.labelstyle.color = 'ff00ff00'

            pnt.name="kova "+str(kovaList[i].split(',')[0])
            pnt.coords = [(kovaList[i].split(',')[2], kovaList[i].split(',')[1])]
        kmlName="single_"+str(minIndex)+"_"+str(kamyonOption)+".kml"
        kml.save(app.config['ROOT_PATH']+"\\"+kmlName)
        return send_file(kmlName,as_attachment=True, cache_timeout=0)
    else:
        return "lütfen önce işlem yapın!"
