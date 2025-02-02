from tkinter import Canvas
from PieniNelio import PieniNelio, PiirrettavaNelio
from apuf import yhdista, pyorista
from suunnat import *


class Tippuminen:
    def __init__(self, neliot: list[PiirrettavaNelio], muut: list["Palikka"], tama_palikka: "Palikka", oikea: bool = True) -> None:
        self.muut_palikat = muut
        self.neliot = neliot
        if oikea:
            while self.tipu():
                pass
            kaikkineliot = yhdista(
                *list(map(lambda p: p.neliot, muut))) + neliot
            allaeipalaa = False
            for nelio in neliot:
                if nelio + Y1 not in kaikkineliot and nelio.y < 19:
                    allaeipalaa = True
            vari = "red" if allaeipalaa else "green"
            tama_palikka.peli.varicanvas.itemconfig(
                tama_palikka.peli.varipallo, fill=vari, outline=vari)

    def tipu(self) -> bool:
        uudet = list(map(lambda sij: PieniNelio(
            sij.x, sij.y + 1), self.neliot))
        tulos = self.tarkista_sijainnit(uudet)
        if tulos == "GAMEOVER":
            return "GAMEOVER"
        if not tulos:
            return False
        for nelio in self.neliot:
            nelio.siirra(nelio.x, nelio.y + 1)
        return True

    def tarkista_sijainnit(self, uudet: list[PieniNelio]) -> bool:
        for paikka in uudet:
            if paikka.y >= 20:
                return False
            if paikka.x < 0:
                return False
            if paikka.x >= 10:
                return False
            for palikka in filter(lambda palikka: palikka != self, self.muut_palikat):
                for sijainti in palikka.neliot:
                    if paikka == sijainti:
                        return False
        return True


class Palikka:
    def __init__(self, neliot: list[PiirrettavaNelio], peli, leveys: int) -> None:
        self.neliot = neliot
        self.peli = peli
        self.muut_palikat = peli.palikat
        self.on_maassa = False
        self.asento = 1
        self.leveys = leveys
        self.tippuminen = Tippuminen(list(map(lambda nelio: nelio.piirrettavaksi(peli.canvas, "#ffffff"), self.neliot)),
                                     self.muut_palikat, self, False)
        self.aseta_tippuminen()

    def tarkista_sijainnit(self, uudet: list[PieniNelio], rivit: bool = False, tarkista_muut: bool = True) -> bool:
        self.aseta_tippuminen()
        for paikka in uudet:
            if paikka.y >= 20:
                return self.kun_on_maassa(rivit)
            if paikka.x < 0:
                return False
            if paikka.x >= 10:
                return False
            for palikka in filter(lambda palikka: palikka != self, self.muut_palikat):
                for sijainti in palikka.neliot:
                    if paikka == sijainti:
                        if tarkista_muut:
                            return self.kun_on_maassa(rivit)
                        else:
                            return False
        return True

    def rivi(self, y: int) -> None:
        for pal in self.muut_palikat:
            for i in range(len(pal.neliot) - 1, -1, -1):
                sij = pal.neliot[i]
                if sij.y == y:
                    pal.neliot[i].poista()
                    del pal.neliot[i]
        for i in range(len(self.muut_palikat) - 1, -1, -1):
            if len(self.muut_palikat[i].neliot) == 0:
                del self.muut_palikat[i]
        pisteet = int(self.peli.pisteet_teksti["text"])
        for i in range(pyorista(1 / self.peli.alkunopeus / 5) + 1):
            pisteet += 1
            if pisteet % 10 == 0:
                self.peli.alkunopeus *= self.peli.nopeutus
        self.peli.pisteet_teksti["text"] = str(pisteet)

    def tarkista_rivit(self) -> None:
        kaikki_sijainnit = yhdista(
            *list(map(lambda pal: pal.neliot, self.muut_palikat)))
        tiputettavat = []
        for y in range(20):
            maara = 0
            for x in range(10):
                if PieniNelio(x, y) in kaikki_sijainnit:
                    maara += 1
            if maara == 10:
                self.rivi(y)
                tiputettavat.append(y)
        for rivi in tiputettavat:
            for palikka in self.muut_palikat:
                for nelio in palikka.neliot:
                    if nelio.y < rivi:
                        nelio.siirra(nelio.x, nelio.y + 1)
        if tiputettavat:
            for palikka in self.muut_palikat:
                while palikka.tipu():
                    pass

    def kun_on_maassa(self, rivit: bool) -> bool:
        for palikka in self.tippuminen.neliot:
            palikka.poista()
        self.on_maassa = True
        if self.neliot[0].y == 0:
            return "GAMEOVER"
        if rivit:
            self.tarkista_rivit()
        return False

    def tipu(self, rivit: bool = True) -> bool:
        uudet = list(map(lambda sij: PieniNelio(
            sij.x, sij.y + 1), self.neliot))
        tulos = self.tarkista_sijainnit(uudet, rivit)
        if tulos == "GAMEOVER":
            return "GAMEOVER"
        if not tulos:
            return False
        for nelio in self.neliot:
            nelio.siirra(nelio.x, nelio.y + 1)
        return True

    def vasen(self) -> bool:
        uudet = list(map(lambda sij: PieniNelio(
            sij.x - 1, sij.y), self.neliot))
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for nelio in self.neliot:
            nelio.siirra(nelio.x - 1, nelio.y)
        self.on_maassa = False
        return True

    def oikea(self) -> bool:
        uudet = list(map(lambda sij: PieniNelio(
            sij.x + 1, sij.y), self.neliot))
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for nelio in self.neliot:
            nelio.siirra(nelio.x + 1, nelio.y)
        self.on_maassa = False
        return True

    def aseta_tippuminen(self):
        for palikka in self.tippuminen.neliot:
            palikka.poista()
        if self.peli.canvas == self.neliot[0].canvas:
            self.tippuminen = Tippuminen(
                list(map(lambda nelio: nelio.piirrettavaksi(
                    self.peli.canvas, "#777777"), self.neliot)),
                list(filter(lambda p: p != self, self.muut_palikat)), self)
            if not self.peli.nayta_tippuminen:
                for palikka in self.tippuminen.neliot:
                    palikka.poista()


class IsoNelio(Palikka):                                                    # 11
    def __init__(self, vasenYla: PieniNelio, canvas: Canvas, peli) -> None:  # 11
        neliot = [vasenYla, vasenYla + X1, vasenYla + Y1, vasenYla + X1Y1]
        super().__init__(list(map(lambda nelio: nelio.piirrettavaksi(canvas, "red"), neliot)), peli, 2)

    def kaanna(self) -> bool:
        return True


class Suorakulmio(Palikka):                                              # 1111
    def __init__(self, vasen: PieniNelio, canvas: Canvas, peli) -> None:
        neliot = [vasen, vasen + X1, vasen + X2, vasen + X3]
        super().__init__(list(map(lambda nelio: nelio.piirrettavaksi(canvas,
                         "orange" if peli.varikkaat else "red"), neliot)), peli, 4)

    def kaanna(self) -> bool:
        asento = self.asento + 1
        if asento > 2:
            asento = 1
        if asento == 1:
            uudet = [self.neliot[0] - X1 + Y1, self.neliot[1],
                     self.neliot[2] + X1 - Y1, self.neliot[3] + X2 - Y2]
        else:
            uudet = [self.neliot[0] + X1 - Y1, self.neliot[1],
                     self.neliot[2] - X1 + Y1, self.neliot[3] - X2 + Y2]
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for i in range(4):
            self.neliot[i].siirra(uudet[i].x, uudet[i].y)
        self.asento = asento
        return True


class L(Palikka):                                                           # 111
    def __init__(self, vasenYla: PieniNelio, canvas: Canvas, peli) -> None:  # 1
        neliot = [vasenYla, vasenYla + X1, vasenYla + X2, vasenYla + Y1]
        super().__init__(list(map(lambda nelio: nelio.piirrettavaksi(canvas,
                         "yellow" if peli.varikkaat else "red"), neliot)), peli, 3)

    def kaanna(self) -> bool:
        asento = self.asento + 1
        if asento > 4:
            asento = 1
        if asento == 1:
            uudet = [self.neliot[0] - X1Y1, self.neliot[1],
                     self.neliot[2] + X1Y1, self.neliot[3] - X2]
        elif asento == 2:
            uudet = [self.neliot[0] + X1 - Y1, self.neliot[1],
                     self.neliot[2] - X1 + Y1, self.neliot[3] - Y2]
        elif asento == 3:
            uudet = [self.neliot[0] + X1Y1, self.neliot[1],
                     self.neliot[2] - X1Y1, self.neliot[3] + X2]
        else:
            uudet = [self.neliot[0] - X1 + Y1, self.neliot[1],
                     self.neliot[2] + X1 - Y1, self.neliot[3] + Y2]
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for i in range(4):
            self.neliot[i].siirra(uudet[i].x, uudet[i].y)
        self.asento = asento
        return True


class V(Palikka):                                                           # 111
    def __init__(self, vasenYla: PieniNelio, canvas: Canvas, peli) -> None:  # 1
        neliot = [vasenYla, vasenYla + X1, vasenYla + X2, vasenYla + X1Y1]
        super().__init__(list(map(lambda nelio: nelio.piirrettavaksi(canvas,
                         "green" if peli.varikkaat else "red"), neliot)), peli, 3)

    def kaanna(self) -> bool:
        asento = self.asento + 1
        if asento > 4:
            asento = 1
        if asento == 1:
            uudet = [self.neliot[0] - X1Y1, self.neliot[1],
                     self.neliot[2] + X1Y1, self.neliot[3] - X1 + Y1]
        elif asento == 2:
            uudet = [self.neliot[0] + X1 - Y1, self.neliot[1],
                     self.neliot[2] - X1 + Y1, self.neliot[3] - X1Y1]
        elif asento == 3:
            uudet = [self.neliot[0] + X1Y1, self.neliot[1],
                     self.neliot[2] - X1Y1, self.neliot[3] + X1 - Y1]
        else:
            uudet = [self.neliot[0] - X1 + Y1, self.neliot[1],
                     self.neliot[2] + X1 - Y1, self.neliot[3] + X1Y1]
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for i in range(4):
            self.neliot[i].siirra(uudet[i].x, uudet[i].y)
        self.asento = asento
        return True


class J(Palikka):                                                           # 111
    def __init__(self, vasenYla: PieniNelio, canvas: Canvas, peli) -> None:  # 1
        neliot = [vasenYla, vasenYla + X1, vasenYla + X2, vasenYla + X2Y1]
        super().__init__(list(map(lambda nelio: nelio.piirrettavaksi(canvas,
                         "purple" if peli.varikkaat else "red"), neliot)), peli, 3)

    def kaanna(self) -> bool:
        asento = self.asento + 1
        if asento > 4:
            asento = 1
        if asento == 1:
            uudet = [self.neliot[0] - X1Y1, self.neliot[1],
                     self.neliot[2] + X1Y1, self.neliot[3] + Y2]
        elif asento == 2:
            uudet = [self.neliot[0] + X1 - Y1, self.neliot[1],
                     self.neliot[2] - X1 + Y1, self.neliot[3] - X2]
        elif asento == 3:
            uudet = [self.neliot[0] + X1Y1, self.neliot[1],
                     self.neliot[2] - X1Y1, self.neliot[3] - Y2]
        else:
            uudet = [self.neliot[0] - X1 + Y1, self.neliot[1],
                     self.neliot[2] + X1 - Y1, self.neliot[3] + X2]
        if not self.tarkista_sijainnit(uudet, False, False):
            return False
        for i in range(4):
            self.neliot[i].siirra(uudet[i].x, uudet[i].y)
        self.asento = asento
        return True
