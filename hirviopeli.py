import pygame, random, math

class Hahmo:
    def __init__(self, kuva, alkupiste: tuple, nopeus: int):
        self.kuva = kuva
        self.x = alkupiste[0]
        self.y = alkupiste[1]
        self.kolikoita = 0
        self.nopeus = nopeus


class Robo(Hahmo):
    def __init__(self, kuva, alkupiste: tuple, nopeus: int):
        super().__init__(kuva, alkupiste, nopeus)
        self.oikealle = False
        self.vasemmalle = False
        self.ylos = False
        self.alas = False


class Hirvio(Hahmo):
    def __init__(self, kuva, alkupiste: tuple, nopeus: int):
        super().__init__(kuva, alkupiste, nopeus)
        self.pysaytys = False  # Pysaytysta käytetään ilmaisemaan onko hirviö kerännyt kolikon tai törmännyt oveen
        self.pys_aika = 0  # Laskuri kauanko hirviö on ollut pysähdyksissä


class Tavara:
    def __init__(self, kuva, tiputus = False):
        self.kuva = kuva
        if tiputus:  #  Mikäli tiputetaan ovi kentälle niin muuttujassa tiputus on pelaajan sen hetkiset x,y-koordinaatit
            self.x = tiputus[0]
            self.y = tiputus[1]
        else:  # Muussa tapauksessa luodaan kolikko satunnaisilla x,y-koordinaateilla
            self.x = random.randint(0, 1080 - self.kuva.get_width() + 1)
            self.y = random.randint(0, 960 - self.kuva.get_height() + 1)


class Peli:
    def __init__(self):
        pygame.init()
        self.nayton_leveys = 1080
        self.nayton_korkeus = 960
        self.kello = pygame.time.Clock()

        self.naytto = pygame.display.set_mode((self.nayton_leveys, self.nayton_korkeus))
        
        self.lataa_kuvat()  # Ladataan objektien kuvat listaan self.kuvat
        self.fontti = pygame.font.SysFont("Arial", 24)

        self.alusta_peli()  # Luo robotti-, hirviö- ja kolikko-objektin
        self.silmukka()


    def alusta_peli(self):
        self.robo = Robo(self.kuvat["robo"], (self.nayton_leveys - self.kuvat["robo"].get_width(), 0), 5)
        self.hirvio = Hirvio(self.kuvat["hirvio"], (0, self.nayton_korkeus - self.kuvat["hirvio"].get_height()), 5)
        self.kolikko = self.luo_tavara()
        self.tiputettu_ovi = None  # Kertoo onko kentälle tiputettu ovea
        self.osuma = False  # Kertoo onko peli päättynyt robotin osuessa hirviöön


    def luo_tavara(self, positio=False):
        if positio:  # Jos positio annetaan jos halutaan tiputtaa ovi. Muussa tapauksessa luodaan kolikko, jolla on satunnainen positio.
            return Tavara(self.kuvat["ovi"], positio)
        return Tavara(self.kuvat["kolikko"])


    def lataa_kuvat(self):
        self.kuvat = {}
        for kuva in ["hirvio", "kolikko", "ovi", "robo"]:
            self.kuvat[kuva] = pygame.image.load("./kuvat/" + kuva + ".png")


    def silmukka(self):
        self.kaynnistys = True  # Käytetään ilmaisemaan aloitusruudun on-off-toimintaa
        self.peli_kaynnissa = False  # Käytetään ilmaisemaan pelimoden on-off-toimintaa
        self.lopetus = False  # Käytetään ilmaisemaan lopetusruudun on-off-toimintaa

        while True:
            while self.kaynnistys == True:
                pygame.display.set_caption("Kolikon jahtausta")
                self.tutki_tapahtumat_alku()  # Tutkitaan painaako käyttäjä näppäimiä F1, F2 tai sulkeeko käyttäjä ikkunan ruksista


            while self.peli_kaynnissa == True:
                pygame.display.set_caption(f"Sinulla on {self.robo.kolikoita} kolikkoa --  Hirviöllä on {self.hirvio.kolikoita}. Eronne on {self.kolikkoero()} kolikkoa.")
                if self.kolikkoero() == 10 or self.kolikkoero() == -10:  # Tarkistaa onko pelin loppumisen ehdot täyttyneet pisteiden osalta
                    self.peli_kaynnissa = False  # Mikäli ehdot täyttyvät, sammutetaan peli_kaynnissa silmukka ja annetaan vuoro lopetusruudun silmukalle
                    self.lopetus = True
                    break

                self.tutki_tapahtumat_peli()  # Tutkii käyttäjän näppäinten painalluksia

                if self.kolikko == None:  # Tarkistetaan onko kolikko kerätty edellisen ruudun päivityksen aikana
                    self.kolikko = self.luo_tavara()  # Luodaan uusi kolikko mikäli ehto täyttyy

                if self.osuma_hirvioon():  # Katsotaan onko robo osunut hirvioon
                    self.lopetus = True  # Mikäli on, niin asetaan lopetusruudun silmukan ehdoksi True ja katkaistaan nykyinen silmukka
                    break

                self.robon_osuma_kolikkoon()  # Tarkistetaan osuiko robo kolikkoon

                if self.tiputettu_ovi != None and self.kolikko != None:  # Katsotaan onko kentällä ovea ja kolikkoa
                    self.hirvion_osuma_tavaraan(tiputus=True)  # Mikäli molemmat löytyvät, niin tarkistetaan onko hirviö osunut oveen
                elif self.kolikko != None:
                    self.hirvion_osuma_tavaraan()  # Jos ei ole osunut oveen, niin katsotaan onko hirviö osunut kolikkoon mikäli kolikko on kentällä

                self.liikuta_roboa()  # Liikutetaan robottia

                if self.hirvio.pysaytys == False and self.kolikko != None:  # Tarkistetaan onko hirviö pysähtyneenä ja kolikko kentällä
                    self.hirvion_liike()  # Jos ei ole pysähtyneenä ja kentällä on kolikko, niin hirviön liike saa jatkua
                else:  # Mikäli hirviö on pysähtyneenä niin
                    if self.hirvio.pys_aika < 300:  # Katsotaan onko ollut pysähtyneenä riittävän kauan
                        self.hirvio.pys_aika += 1  # Jos ei niin kasvatetaan aikaa yhdellä päivityksell'
                    else:
                        self.hirvio.pysaytys = False  # Mikäli on ollut pysähtyneenä tarpeeksi kauan niin nollataan laskuri ja päästetään hirviö liikkeelle
                        self.hirvio.pys_aika = 0

                self.piirra_naytto()
                self.kello.tick(60)

            while self.lopetus == True:
                self.tutki_tapahtumat_loppu()  # Tutkitaan loppuruudun aikana tulleet tapahtumat
            

    def tutki_tapahtumat_peli(self):
        for tapahtuma in pygame.event.get():
            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_RIGHT:
                    self.robo.oikealle = True
                if tapahtuma.key == pygame.K_LEFT:
                    self.robo.vasemmalle = True
                if tapahtuma.key == pygame.K_UP:
                    self.robo.ylos = True
                if tapahtuma.key == pygame.K_DOWN:
                    self.robo.alas = True
                if tapahtuma.key == pygame.K_SPACE and self.tiputettu_ovi == None and self.hirvio.pysaytys == False:
                    self.tiputa_tavara()
                elif tapahtuma.key == pygame.K_SPACE and self.tiputettu_ovi != None:
                    self.nosta_tavara()

            if tapahtuma.type == pygame.KEYUP:
                if tapahtuma.key == pygame.K_RIGHT:
                    self.robo.oikealle = False
                if tapahtuma.key == pygame.K_LEFT:
                    self.robo.vasemmalle = False
                if tapahtuma.key == pygame.K_UP:
                    self.robo.ylos = False
                if tapahtuma.key == pygame.K_DOWN:
                    self.robo.alas = False
            if tapahtuma.type == pygame.QUIT:
                exit()


    def tutki_tapahtumat_alku(self):
        for tapahtuma in pygame.event.get():
            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_F1:
                    self.kaynnistys = False  # Mikäli näppäintä painetaan, aloitusruudun silmukan ehto muutetaan falseksi, jolloin suoritus siirtyy peli_kaynnissa-silmukalle
                    self.peli_kaynnissa = True
                if tapahtuma.key == pygame.K_F2:
                    exit()
            if tapahtuma.type == pygame.QUIT:
                exit()
        self.piirra_naytto(aloitus=True)  # Annetaan metodille aloitus-parametriksi true-arvo, jolloin aloitus-osa suoritaan
        self.kello.tick(60)


    def tutki_tapahtumat_loppu(self):
        for tapahtuma in pygame.event.get():
            if tapahtuma.type == pygame.KEYDOWN:
                if tapahtuma.key == pygame.K_F1:
                    self.kaynnistys = True
                    self.lopetus = False
                    self.alusta_peli()
                    
                if tapahtuma.key == pygame.K_F2:
                    exit()
            if tapahtuma.type == pygame.QUIT:
                exit()

        self.piirra_naytto(lopetus=True)
        self.kello.tick(60)


    def piirra_naytto(self, aloitus=False, lopetus=False):  # aloitus- ja lopetus-parametrit ilmaisevat mitä pelin osaa piirretään. Oletuksena piirretään peli_kaynnissa silmukkaa
        self.naytto.fill((25, 100, 20))
        self.naytto.blit(self.robo.kuva, positio(self.robo))
        self.naytto.blit(self.hirvio.kuva, positio(self.hirvio))
        if self.kolikko != None:  # Jos kolikko on olemassa, piirretään
            self.naytto.blit(self.kolikko.kuva, positio(self.kolikko))
        if self.tiputettu_ovi:  # Jos ovi on tiputettuna kentälle, piirretään
            self.naytto.blit(self.tiputettu_ovi.kuva, positio(self.tiputettu_ovi))

        if aloitus:
            
            ohje1 = "Kerää 10 kolikkoa hirviötä enemmän liikkumalla kolikoiden päälle nuolinäppäimillä."
            ohje2 = "Voit pudottaa oven kentälle VÄLILYÖNNILLÄ maksamalla yhden kolikon. Hirviö menettää hetkellisesti tajuntansa osuessaan siihen."
            ohje3 = "Et voi tiputtaa uutta ovea hirviön ollessa tajuttomana."
            ohje4 = "Kentällä voi olla yhtäaikaa vain yksi ovi. Voit nostaa sen takaisin painamalla VÄLILYÖNTIÄ, kun olet sen kohdalla."
            ohje5 = "Jos nostat oven, menetät kuitenkin siihen käyttämäsi kolikon."
            ohje6 = "Jos osut hirviöön, niin se on game over."
            ohje7 = "Pistetilanteen näet ikkunan yläpalkista."
            ohje8 = "Paina F1 aloittaaksesi."
            ohje9 = "Paina F2 lopettaaksesi."
            ohjeet = [ohje1, ohje2, ohje3, ohje4, ohje5, ohje6, ohje7, ohje8, ohje9]
            i = 0
            for ohje in ohjeet:
                teksti = self.fontti.render(ohje, True, (0, 0, 0))
                self.naytto.blit(teksti, (25, 20 + i))
                i += 30

        if lopetus:
            if self.robo.kolikoita < self.hirvio.kolikoita or self.osuma == True:  # Mikäli hirviöllä on enemmän kolikoita kuin pelaajalla tai pelaaja on osunut hirviöön, niin pelaaja häviää
                tulos = "HÄVISIT"
            else:
                tulos = "VOITIT"
            uudestaan = "Pelataanko uudestaan?"
            ohje1 = "Paina F1 aloittaaksesi uuden pelin."
            ohje2 = "Paina F2 lopettaaksesi."
            tekstit = [tulos, uudestaan, ohje1, ohje2]
            i = 0
            for teksti in tekstit:
                text = self.fontti.render(teksti, True, (0, 0, 0))
                self.naytto.blit(text, (50, 20 + i))
                i += 30
            
        pygame.display.flip()


    def liikuta_roboa(self):
        # Liikutetaan roboa sen nopeuden verran haluttuun suuntaan ja pidetään huoli että se pysyy peliruudun sisällä
        if self.robo.oikealle and (self.robo.x + mitat(self.robo)[0]) + self.robo.nopeus <= self.nayton_leveys:
            self.robo.x += self.robo.nopeus
        if self.robo.vasemmalle and self.robo.x - self.robo.nopeus >= 0:
            self.robo.x -= self.robo.nopeus
        if self.robo.ylos and self.robo.y - self.robo.nopeus >= 0:
            self.robo.y -= self.robo.nopeus
        if self.robo.alas and (self.robo.y + mitat(self.robo)[1]) + self.robo.nopeus <= self.nayton_korkeus:
            self.robo.y += self.robo.nopeus


    def laske_kulma(self, objekti1, objekti2):  # Lasketaan kahden objektin välinen kulma
        # keskipiste-funktiolla haetaan objektien keskipisteiden x,y-koordinaatit, jotta voidaan laskea positioerot
        o1_x, o1_y = keskipiste(objekti1)  
        o2_x, o2_y = keskipiste(objekti2)
        dy = o1_y - o2_y  # Lasketaan korkeusero objektien 1 ja 2 välillä
        dx = o1_x - o2_x  # Lasketaan leveysero objektien 1 ja 2 välillä
        return math.atan2(dy, dx)  # Palautetaan erojen perusteella laskettu kulma radiaaneina


    def hirvion_liike(self):
        kulma = self.laske_kulma(self.kolikko, self.hirvio)  # Lasketaan kolikon ja hirviön positioiden välinen kulma
        self.hirvio.x += math.cos(kulma) * self.hirvio.nopeus  # Lisätään hirviön x-koordinaattiin kulman perusteella laskettu lisäys
        self.hirvio.y += math.sin(kulma) * self.hirvio.nopeus  # Lisätään hirviön y-koordinaattiin kulman perusteella laskettu lisäys


    def positioerot(self, objekti1, objekti2):  # Käytetään määritäämään positioeroja kahden objektin välillä niiden keskipisteiden perusteella
        x_ero = abs(keskipiste(objekti1)[0] - keskipiste(objekti2)[0])
        y_ero = abs(keskipiste(objekti1)[1] - keskipiste(objekti2)[1])
        x_kokoero = mitat(objekti1)[0] / 2 + mitat(objekti2)[0] / 2
        y_kokoero = mitat(objekti1)[1] / 2 + mitat(objekti2)[1] / 2
        return x_ero, y_ero, x_kokoero, y_kokoero


    def osuma_hirvioon(self):
        # Haetaan robon ja hirviön keskipisteiden positioerot
        x_ero, y_ero, x_kokoero, y_kokoero = self.positioerot(self.robo, self.hirvio)
        if x_ero <= x_kokoero and y_ero <= y_kokoero:  # Mikäli ero on riittävän pieni, niin todetaan että osuma on tapahtunut
            self.osuma = True
            return True

    def robon_osuma_kolikkoon(self):
        # Haetaan robon ja kolikon keskipisteiden positioerot
        x_ero, y_ero, x_kokoero, y_kokoero = self.positioerot(self.robo, self.kolikko)
        if x_ero <= x_kokoero and y_ero <= y_kokoero:  # Mikäli ero on riittävän pieni, niin todetaan että osuma on tapahtunut
            self.robo.kolikoita += 1  # Lisätään pelaajan kolikkomäärää yhdell'
            self.kolikko = None  # Poistetaan kolikko johon on osuttu

    def hirvion_osuma_tavaraan(self, tiputus=False):
        # Tarkistetaan osuiko hirviö tavaraan. tiputus-parametrin ollessa false tarkastetaan osuma kolikkoon ja sen ollessa true tarkastetaan osuma oveen
        x_ero_k, y_ero_k, x_kokoero_k, y_kokoero_k = self.positioerot(self.hirvio, self.kolikko)
        if tiputus:
            x_ero_t, y_ero_t, x_kokoero_t, y_kokoero_t = self.positioerot(self.hirvio, self.tiputettu_ovi)
            if x_ero_t <= x_kokoero_t and y_ero_t <= y_kokoero_t:
                self.tiputettu_ovi = None  # Jos on osuttu oveen, niin poistetaan ovi kentältä
                self.hirvio.pysaytys = True  # Pysäytetään hirviön liike

        if x_ero_k <= x_kokoero_k and y_ero_k <= y_kokoero_k:
            self.kolikko = None  # Jos hirviö osuu kolikkoon niin poistetaan kolikko
            self.hirvio.kolikoita += 1  # Lisätään yksi kolikko hirviön saldoon
    
    def tiputa_tavara(self):
        # Tiputetaan ovi kentälle mikäli pelaajalla on vähintään yksi kolikko ja kentällä ei ole ennestään ovea
        if self.robo.kolikoita > 0 and self.tiputettu_ovi == None:
            # Oven tiputuskohta on pelaajan keskipiste
            robo_kp = keskipiste(self.robo)
            tiputuskohta_x = robo_kp[0] - self.kuvat["ovi"].get_width() / 2
            tiputuskohta_y = robo_kp[1] - self.kuvat["ovi"].get_height() / 2
            self.tiputettu_ovi = self.luo_tavara(positio=(tiputuskohta_x, tiputuskohta_y))  # Kutsutaan metodia luo_tavara positio-argumentilla
            self.robo.kolikoita -= 1  # Oven tiputus maksaa yhden kolikon

    def nosta_tavara(self):
        if self.tiputettu_ovi:  # Tarkistetaan onko ovi kentällä
            x_ero, y_ero, x_kokoero, y_kokoero = self.positioerot(self.robo, self.tiputettu_ovi)
            if x_ero <= x_kokoero and y_ero <= y_kokoero:  # Katsotaan onko pelaaja riittävän lähellä ovea 
                self.tiputettu_ovi = None  # Poistetaan ovi mikäli on

    def kolikkoero(self):
        return self.robo.kolikoita - self.hirvio.kolikoita
    

def mitat(objekti):  # Palautetaan objektin kuvan mitat
    return (objekti.kuva.get_width(), objekti.kuva.get_height())

def keskipiste(objekti):  # Palautetaan objektin keskipiste
    return (objekti.x + mitat(objekti)[0] / 2, objekti.y + mitat(objekti)[1] / 2)

def positio(objekti):  # Palautetaan objektin x,y-koordinaatit
    return (objekti.x, objekti.y)

if __name__ == "__main__":
    Peli()
