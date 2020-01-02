
from Kamyon import  Kamyon
class Filo:
    def __init__(self,adet,merkezNode):
        self.adet = adet
        self.merkezNode=merkezNode
        self.filo=list()
    def filo_olustur(self):
        #buraya kapasite ve türetim ile ilgili bir dosya parametre olarak gönderilebilir
        for i in range(self.adet):
            plaka = "plaka "+str(i)
            k= Kamyon(i+1,plaka,2500,10,150,50,self.merkezNode)
            self.filo.append(k)

