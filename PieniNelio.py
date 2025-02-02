from tkinter import Canvas

from const import RUUDUN_KOR, RUUDUN_LEV


class PieniNelio:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def siirra(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, toinen) -> bool:
        if type(toinen) != PieniNelio:
            return False
        return self.x == toinen.x and self.y == toinen.y

    def __add__(self, toinen) -> "PieniNelio":
        if type(toinen) != PieniNelio:
            raise ValueError(
                "Et voi laskea yhteen Pienineliötä ja jotain muuta")
        return PieniNelio(self.x + toinen.x, self.y + toinen.y)

    def __sub__(self, toinen) -> "PieniNelio":
        if type(toinen) != PieniNelio:
            raise ValueError("Et voi vähentää Pienineliöstä jotain muuta")
        return PieniNelio(self.x - toinen.x, self.y - toinen.y)

    def piirrettavaksi(self, c: Canvas, vari: str) -> "PiirrettavaNelio":
        return PiirrettavaNelio(self.x, self.y, c, vari)


class PiirrettavaNelio(PieniNelio):
    def __init__(self, x: int, y: int, c: Canvas, vari: str) -> None:
        super().__init__(x, y)
        self.canvas = c
        self.nelio = c.create_rectangle(x * RUUDUN_LEV, y * RUUDUN_KOR, x *
                                        RUUDUN_LEV + RUUDUN_LEV, y * RUUDUN_KOR +
                                        RUUDUN_KOR, fill=vari)
        self.poistettu = False

    def siirra(self, x: int, y: int):
        super().siirra(x, y)
        self.paivita()

    def paivita(self):
        if self.poistettu:
            raise ValueError("Neliö poistettu")
        self.canvas.moveto(self.nelio, self.x *
                           RUUDUN_LEV, self.y * RUUDUN_KOR)

    def poista(self):
        self.canvas.delete(self.nelio)
        self.poistettu = True
