from os.path import exists

class Pisteet:
    def __init__(self, tiedosto: str) -> None:
        self.tiedosto = tiedosto
        self.pisteet = []

    def lue(self):
        self.pisteet.clear()
        if exists(self.tiedosto):
            with open(self.tiedosto) as tied:
                for rivi in tied:
                    osat = rivi.strip().split(";")
                    self.pisteet.append([osat[0], int(osat[1])])

    def lisaa(self, nimi: str, pisteet: int):
        nimet = list(map(lambda p: p[0], self.pisteet))
        if nimi in nimet:
            piste = self.pisteet[nimet.index(nimi)]
            piste[1] = max(pisteet, piste[1])
        else:
            self.pisteet.append([nimi, pisteet])
        self.pisteet.sort(key=lambda p: p[1], reverse=True)
        self.paivita_tied()

    def paivita_tied(self):
        with open(self.tiedosto, "w") as tied:
            for piste in self.pisteet:
                tied.write(piste[0] + ";" + str(piste[1]) + "\n")
