from os.path import exists
from random import randint
from time import time
from tkinter import Button, Canvas, Frame, Label, TclError, Tk, Toplevel, messagebox, simpledialog

from Palikka import J, L, V, IsoNelio, Suorakulmio
from Pisteet import Pisteet
from apuf import yhdista
from suunnat import *
from const import ODOTUS, RUUDUN_KOR, RUUDUN_LEV
from PieniNelio import PieniNelio


class Tetris:
    def __init__(self) -> None:
        self.alkunopeus = ODOTUS
        self.nopeus = self.alkunopeus
        self.gameover = True
        self.onpause = False
        self.nopeutus = 0.9

        self.normaalit_pisteet = Pisteet("pisteet.csv")
        self.normaalit_pisteet.lue()
        self.hitaat_pisteet = Pisteet("pisteet_hidas.csv")
        self.hitaat_pisteet.lue()
        self.pisteet = self.normaalit_pisteet

        self.ikkuna = Tk()
        self.ikkuna.geometry("500x500")
        self.ikkuna.title("Tetris")
        self.ikkuna.resizable(False, False)

        self.canvas = Canvas(self.ikkuna, width=250,
                             height=500, background="#3333ff")
        self.canvas.grid(column=0, row=0)

        self.pausenakyma = Canvas(self.ikkuna, width=250, height=500)
        self.pausenakyma.create_text(
            125, 250, text="PAUSE", font=("Arial", 30, "bold"))

        for x in range(10):
            for y in range(20):
                self.canvas.create_rectangle(x * RUUDUN_LEV, y * RUUDUN_KOR,
                                             x * RUUDUN_LEV + RUUDUN_LEV,
                                             y * RUUDUN_KOR + RUUDUN_KOR,
                                             fill="#3333ff", outline="gray")

        frame = Frame(self.ikkuna)
        frame.grid(column=1, row=0)
        Label(frame, text="Tetris", font=("Arial", 25, "bold")).pack()
        Label(frame, text="Seuraava palikka:").pack()
        self.seuraava_canvas = Canvas(
            frame, width=100, height=50, background="#3333ff")
        self.seuraava_canvas.pack()
        Label(frame, text="Pisteet:").pack()
        self.pisteet_teksti = Label(frame, text="0", font=(
            "Arial", 25, "bold"), borderwidth=3, relief="groove")
        self.pisteet_teksti.pack()
        Button(frame, text="Uusi peli", command=self.uusi_peli).pack()
        Button(frame, text="Asetukset", command=self.asetukset).pack()
        Button(frame, text="Pause", command=self.pause).pack()
        Button(frame, text="Näytä pisteet", command=self.nayta_pisteet).pack()
        Button(frame, text="Näytä napit", command=self.napit).pack()
        Button(frame, text="Anna palautetta", command=self.palaute).pack()
        Button(frame, text="Näytä palautteet", command=self.palautteet).pack()
        self.varicanvas = Canvas(frame, width=50, height=50)
        self.varicanvas.pack()
        self.varipallo = self.varicanvas.create_oval(
            12.5, 12.5, 37.5, 37.5, fill="red", outline="red")

        self.palikat = []

        self.ikkuna.bind(
            "<Left>", lambda event: self.palikat[-1].vasen() if not self.gameover else None)
        self.ikkuna.bind(
            "<Right>", lambda event: self.palikat[-1].oikea() if not self.gameover else None)
        self.ikkuna.bind("<Down>", lambda event: self.alastap()
                         if not self.gameover else None)
        self.ikkuna.bind(
            "<space>", lambda event: self.palikat[-1].kaanna() if not self.gameover else None)
        self.ikkuna.bind("<Up>", lambda event: self.pause())

        self.asetukset_auki = False
        self.alastap = None
        self.nayta_tippuminen = None
        self.varikkaat = None
        aika = time()
        while True:
            try:
                self.ikkuna.update()
                if time() - aika > self.nopeus and (not (self.gameover or self.asetukset_auki or self.onpause)):
                    aika = time()
                    if not self.palikat:
                        self.nayta_seuraava()
                    if (not self.palikat) or self.palikat[-1].on_maassa:
                        self.uusi_palikka()
                    else:
                        tulos = self.palikat[-1].tipu()
                        if tulos == "GAMEOVER":
                            self.gameover = True
                            self.tallenna_pisteet()
            except TclError:
                break

    def uusi_palikka(self) -> None:
        tyyppi = type(self.seuraava_palikka)
        palikka = tyyppi(PieniNelio(
            randint(0, 10 - self.seuraava_palikka.leveys), 0), self.canvas, self)
        self.palikat.append(palikka)
        self.nopeus = self.alkunopeus
        self.nayta_seuraava()

    def nayta_seuraava(self):
        self.seuraava_canvas.delete("all")
        muoto = randint(1, 5)
        # 1111
        if muoto == 1:
            palikka = Suorakulmio(PieniNelio(
                0, 0.5), self.seuraava_canvas, self)
        # 111
        # 1
        elif muoto == 2:
            palikka = L(PieniNelio(0.5, 0), self.seuraava_canvas, self)
        # 111
        #  1
        elif muoto == 3:
            palikka = V(PieniNelio(0.5, 0), self.seuraava_canvas, self)
        # 11
        # 11
        elif muoto == 4:
            palikka = IsoNelio(PieniNelio(1, 0), self.seuraava_canvas, self)
        # 111
        #   1
        else:
            palikka = J(PieniNelio(0.5, 0), self.seuraava_canvas, self)
        self.seuraava_palikka = palikka

    def nopeuta(self):
        self.nopeus /= 2

    def tiputa(self):
        while True:
            tulos = self.palikat[-1].tipu()
            if not tulos:
                break
            if tulos == "GAMEOVER":
                self.gameover = True
                self.tallenna_pisteet()
                break

    def uusi_peli(self):
        def asetukset_valmis(onnistuiko: bool):
            if onnistuiko:
                self.gameover = False
        self.gameover = True
        self.tyhjenna()
        self.pisteet_teksti["text"] = "0"
        self.alastap = None
        self.nayta_tippuminen = False
        self.varikkaat = True
        self.alkunopeus = ODOTUS
        self.nopeutus = 0.9
        if self.onpause:
            self.pause()
        self.asetukset(asetukset_valmis)

    def tyhjenna(self):
        kaikki_sijainnit = yhdista(
            *list(map(lambda pal: pal.neliot, self.palikat)))
        for sij in kaikki_sijainnit:
            sij.poista()
        for palikka in self.palikat:
            for nelio in palikka.tippuminen.neliot:
                nelio.poista()
        self.palikat.clear()

    def asetukset(self, kun_valittu: callable = lambda x: None):
        try:
            self.asetusikkuna.winfo_width()
            self.asetusikkuna.focus()
            return
        except (TclError, AttributeError):
            pass

        def aseta_alastap(arvo: callable):
            self.alastap = arvo

        def aseta_tippuminen(arvo: bool):
            self.nayta_tippuminen = arvo

        def aseta_varikkaat(arvo: bool):
            self.varikkaat = arvo

        def aseta_nopeus(arvot: tuple[float, Pisteet]):
            self.nopeutus, self.pisteet = arvot

        def ok():
            if any(map(lambda a: a == None, [self.alastap, self.nayta_tippuminen])):
                kun_valittu(False)
            else:
                kun_valittu(True)
            self.asetukset_kiinni()

        def peruuta():
            kun_valittu(False)
            self.asetukset_kiinni()
        self.asetukset_auki = True
        self.asetusikkuna = Toplevel(self.ikkuna)
        self.asetusikkuna.title("Asetukset")
        self.asetusikkuna.geometry("400x500")

        Label(self.asetusikkuna, text="Asetukset",
              font=("Arial", 25, "bold")).pack()
        Label(self.asetusikkuna, text="Pakolliset",
              font=("Arial", 15, "bold")).pack()

        Label(self.asetusikkuna, text="Kun painetaan \u2193").pack()
        Button(self.asetusikkuna, text="Tiputa",
               command=lambda: aseta_alastap(self.tiputa)).pack()
        Button(self.asetusikkuna, text="Nopeuta",
               command=lambda: aseta_alastap(self.nopeuta)).pack()

        Label(self.asetusikkuna, text="Paina OK",
              font=("Arial", 15, "bold")).pack()
        Button(self.asetusikkuna, text="OK", command=ok).pack()
        Button(self.asetusikkuna, text="Peruuta", command=peruuta).pack()

        Label(self.asetusikkuna, text="Lisäasetukset",
              font=("Arial", 15, "bold")).pack()

        Label(self.asetusikkuna, text="Värikkäät palikat").pack()
        Button(self.asetusikkuna, text="Kyllä",
               command=lambda: aseta_varikkaat(True)).pack()
        Button(self.asetusikkuna, text="Ei",
               command=lambda: aseta_varikkaat(False)).pack()

        Label(self.asetusikkuna, text="Näytetäänkö minne palikka tippuu").pack()
        Button(self.asetusikkuna, text="Kyllä",
               command=lambda: aseta_tippuminen(True)).pack()
        Button(self.asetusikkuna, text="Ei",
               command=lambda: aseta_tippuminen(False)).pack()

        nopeus_state = "normal" if self.gameover else "disabled"
        Label(self.asetusikkuna, text="Nopeus").pack()
        Button(self.asetusikkuna, text="Normaali", command=lambda: aseta_nopeus(
            (0.9, self.normaalit_pisteet)), state=nopeus_state).pack()
        Button(self.asetusikkuna, text="Hitaampi", command=lambda: aseta_nopeus(
            (0.95, self.hitaat_pisteet)), state=nopeus_state).pack()
        Label(self.asetusikkuna, text="ERI NOPEUKSILLA ON OMAT PISTEENSÄ!").pack()

        self.asetusikkuna.protocol("WM_DELETE_WINDOW", peruuta)

    def asetukset_kiinni(self):
        self.asetukset_auki = False
        self.asetusikkuna.destroy()

    def pause(self):
        self.onpause = not self.onpause
        if self.onpause:
            self.canvas.grid_forget()
            self.pausenakyma.grid(row=0, column=0)
        else:
            self.pausenakyma.grid_forget()
            self.canvas.grid(row=0, column=0)

    def nayta_pisteet(self):
        try:
            self.pisteikkuna.winfo_width()
            self.pisteikkuna.focus()
            return
        except (TclError, AttributeError):
            pass
        self.pisteikkuna = Toplevel(self.ikkuna)
        self.pisteikkuna.title("Pisteet")
        self.pisteikkuna.geometry("400x400")

        Label(self.pisteikkuna, text="Pisteet",
              font=("Arial", 25, "bold")).pack()

        Label(self.pisteikkuna, text="Normaali",
              font=("Arial", 20, "bold")).pack()
        nframe = Frame(self.pisteikkuna)
        nframe.pack()
        Label(nframe, text="Nimi").grid(row=0, column=1)
        Label(nframe, text="Pisteet").grid(row=0, column=2)
        for i in range(len(self.normaalit_pisteet.pisteet)):
            Label(nframe, text=f"{i + 1}.").grid(row=i + 1, column=0)
            Label(nframe, text=self.normaalit_pisteet.pisteet[i][0]).grid(
                row=i + 1, column=1)
            Label(nframe, text=str(self.normaalit_pisteet.pisteet[i][1])).grid(
                row=i + 1, column=2)

        Label(self.pisteikkuna, text="Hidastettu",
              font=("Arial", 20, "bold")).pack()
        hframe = Frame(self.pisteikkuna)
        hframe.pack()
        Label(hframe, text="Nimi").grid(row=0, column=1)
        Label(hframe, text="Pisteet").grid(row=0, column=2)
        for i in range(len(self.hitaat_pisteet.pisteet)):
            Label(hframe, text=f"{i + 1}.").grid(row=i + 1, column=0)
            Label(hframe, text=self.hitaat_pisteet.pisteet[i][0]).grid(
                row=i + 1, column=1)
            Label(hframe, text=str(self.hitaat_pisteet.pisteet[i][1])).grid(
                row=i + 1, column=2)

    def tallenna_pisteet(self):
        def kysy_ja_tallenna():
            tulos = simpledialog.askstring(
                "Nimi", "Anna nimesi\nPeruuta painamalla Cancel.")
            if tulos == None:
                self.tallenna_pisteet()
            elif tulos:
                self.pisteet.lisaa(tulos, int(self.pisteet_teksti["text"]))
                messagebox.showinfo(
                    "Pisteet tallennettu", "Pisteet tallennettu. Paina Näytä pisteet nähdäksesi listan.")
            else:
                kysy_ja_tallenna()

        tulos = messagebox.askyesno(
            "GAMEOVER", "Hävisit pelin! Haluatko tallentaa pisteesi?")
        if tulos:
            kysy_ja_tallenna()
        if messagebox.askyesno("Palaute", "Haluatko antaa palautetta?"):
            self.palaute()
        else:
            messagebox.showinfo(
                "Palaute", "Paina palaute antaaksesi palautetta myöhemmin")

    def palaute(self):
        tulos = simpledialog.askstring("Palaute", "Anna palautetta")
        if tulos:
            with open("palaute.txt", "a", encoding="utf-8") as tied:
                tied.write(tulos + "\n")
            messagebox.showinfo("Palaute", "Kiitos palautteestasi")

    def palautteet(self):
        ikkuna = Toplevel(self.ikkuna)
        ikkuna.title("Palautteet")

        Label(ikkuna, text="Palautteet", font=("Arial", 25, "bold")).pack()

        if exists("palaute.txt"):
            with open("palaute.txt", encoding="utf-8") as tied:
                for rivi in tied:
                    Label(ikkuna, text=rivi).pack()

    def napit(self):
        ikkuna = Toplevel(self.ikkuna)
        ikkuna.title("Napit")
        ikkuna.geometry("450x100")

        Label(ikkuna, text="Välilyönti = käännä palikkaa 90\u00B0 myötäpäivään",
              borderwidth=3, relief="groove").pack()

        frame = Frame(ikkuna)
        frame.pack()

        alastap = self.alastap.__name__ if self.alastap else "tiputa/nopeuta"
        Label(frame, text="\u2190 = siirrä palikkaa vasemmalle", borderwidth=3, relief="groove").grid(row=1, column=0)
        Label(frame, text="\u2191 = pause", borderwidth=3, relief="groove").grid(row=0, column=1)
        Label(frame, text="\u2192 = siirrä palikkaa oikealle", borderwidth=3, relief="groove").grid(row=1, column=2)
        Label(frame, text=f"\u2193 = {alastap}", borderwidth=3, relief="groove").grid(row=2, column=1)
