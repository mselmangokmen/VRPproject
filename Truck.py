import random
import numpy as np
from numpy.random import choice


class Kamyon:
    def __init__(self, manager, id, plaka, kapasite, tuketim, yakitDeposu, ortHiz):
        self.id = id

        self.plaka = plaka
        self.kapasite = manager.Value('i', kapasite)
        self.tuketim = tuketim
        self.yakitDeposu = manager.Value('i', yakitDeposu)
        self.ortHiz = ortHiz
        self.rota = manager.list()
        self.mevcutKonum = manager.Value('i', 0)
        self.merkezKonum = manager.Value('i', 0)
        self.orjKapasite = kapasite
        self.maliyet = manager.Value('i', 0)

    def konumDegistir(self, konumID):
        self.mevcutKonum.value = konumID

    def rota_ekle(self, n1, n2, dist):
        self.rota.append([n1, n2, dist])

    def secim_yap(self, cluster,kamyonSayisi, dolulukList, ziyaretList, enYakinKontrol, alfa, beta, omega, nodeList,
                  mesafeMatrix, ziyaretMatrix):
        probList = list()
        indexList = list()
        zMatrix = []
        for i in range(len(cluster)):
            if i != 0:
                if ziyaretMatrix[cluster[i]] == 0:
                    zMatrix.append(cluster[i])
            else:
                zMatrix.append(cluster[i])

        npZiyaret = np.array(zMatrix)

        # zeroArr= np.where(npZiyaret==0)[0]

        enYakin = list()

        if len(zMatrix) <= 1:
            return None

        # for i in range(enYakinKontrol):
        #    rVal=random.randint(1,len(zeroArr)-1)
        #    ix = zeroArr[rVal]
        #    if nodeList[ix].id != self.mevcutKonum.value and dolulukList[ix]>0:
        #        dist = mesafeMatrix[self.mevcutKonum.value][nodeList[ix].id]
        #        enYakin.append([dist,nodeList[ix].id])

        for i in range(1, len(zMatrix)):
            ix = zMatrix[i]
            if nodeList[ix].id != self.mevcutKonum.value and dolulukList[ix] > 0:
                dist = mesafeMatrix[self.mevcutKonum.value][nodeList[ix].id]
                enYakin.append([dist, nodeList[ix].id])

        ds = sorted(enYakin, key=lambda x: x[0])
        if len(ds) >= (kamyonSayisi * enYakinKontrol):
            ds = ds[0:(kamyonSayisi * enYakinKontrol)]
        if len(ds) > 0:
            if ds[0][0] < 200:
                return nodeList[ds[0][1]].id

        # for i in range(1,len(zeroArr)):
        for i in range(len(ds)):
            ix = ds[i][1]
            dist = ds[i][0]
            doluluk = dolulukList[ix]
            ziyaretCnt = ziyaretList.count([self.id, self.mevcutKonum.value, nodeList[ix].id]) + 1
            prob = pow((1 / (dist + 1)), alfa) * pow(1 / doluluk, beta) * pow((1 / ziyaretCnt), omega)
            probList.append(prob)
            indexList.append(nodeList[ix].id)

        if len(indexList) >= 1:

            sumProb = 0
            for p in probList:
                sumProb += p

            for i in range(len(probList)):
                probList[i] = probList[i] / sumProb
            secilenIndex = choice(indexList, p=probList)
            return secilenIndex
        else:
            return None



