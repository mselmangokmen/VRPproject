class iterasyon:
    def __init__(self,itNumber,kamyonID,kamyonPlaka):
        self.itNumber=itNumber
        self.kamyonID=kamyonID
        self.rota=list()
        self.maliyet=0
        self.kamyonPlaka=kamyonPlaka

    def maliyetHesapla(self):
        toplamYol = 0
        for ix in range(len(self.rota)):
            toplamYol = toplamYol + self.rota[ix][2]
        self.maliyet=toplamYol



    def rotaAl(self):
        rotaStr = ""
        for ix in range(len(self.rota)):
            rotaStr = rotaStr + str(self.rota[ix][0]) + "-"
        rotaStr = str(self.itNumber)+" "+rotaStr + str(self.rota[-1][1])

        result = "rota "+str(self.kamyonID) + " " + self.kamyonPlaka + " #" + rotaStr + "# " + str(self.maliyet)
        return result


    def maliyet_hesapla(self):
        return 0
