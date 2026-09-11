# Circus-Lost-in-Time

Python/Pygame-peliprototyyppi, jossa ohjataan kolmea sirkushahmoa.

## Käynnistys

Testattu Python 3.12.14:llä ja Pygame 2.6.1:llä Windowsissa.
Suorita repositorion juuressa:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -B src\circus.py
```

Nuolinäppäimet liikuttavat, Ctrl vaihtaa hahmoa ja välilyönti tekee
hahmon toiminnon. Akrobaatti hyppää; muiden hahmojen erikoistoiminnot
ovat vielä paikkamerkkejä. Sulje peli ikkunan sulkupainikkeella.
Erillinen kenttäeditori: `python -B src/editor.py`.

## Akrobaatin animaatiot

`img/acrobat_idle_walk.png` on suoraan peliin ladattava RGBA-kuva:

- Koko 192 × 128 px, 4 saraketta ja 2 riviä.
- Ruudun koko 48 × 64 px. Ei ruutujen välisiä marginaaleja.
- Rivi 0: neljä seisontaruutua, toistojärjestys 0,1,2,3,2,1, nopeus 4 fps.
- Rivi 1: neljä kävelyruutua, toistojärjestys 0,1,2,3, nopeus 8 fps.
- Jalkojen alin näkyvä pikseli on jokaisen ruudun rivillä 61 (0-indeksointi).
- Sama skaala kaikissa ruuduissa, aito läpinäkyvä tausta.
- Kuvat katsovat oikealle. Vasemmalle suunnatut ruudut peilataan muistissa.

`src/animation.py` sisältää yhteisen `SpriteAnimation`-luokan.
Animaation aika annetaan sekunteina; tilan vaihtuessa animaatio alkaa alusta.
Hahmon `rect` pysyy samankokoisena, joten ruutujen vaihtuminen ei siirrä hahmoa.
Liikkumaton tai ruudun reunaan pysähtynyt akrobaatti käyttää seisontaa.
Hyppy käyttää erillisiä nousu-, lakipiste-, lasku- ja laskeutumisruutuja.
Muut hahmot käyttävät edelleen alkuperäisiä kuviaan.

Esikatselut: `img/acrobat_idle_walk_preview.png` (4× suurennos) ja
`img/acrobat_animation_preview.gif` (seisonta ja kävely).

Grafiikka tehtiin sisäänrakennetulla ImageGen-työkalulla alkuperäisen
`img/acrobat_char_sprite.png`-kuvan pohjalta. Alkuperäinen kuva säilytettiin.
Uusi hahmo on uudelleenpiirretty tulkinta, ei alkuperäisten pikselien kopio.
Vanhaa `acrobat_sprite_sheet.webp`-arkkia ei käytetty, koska se esittää eri hahmoa.
Generointi tuotti ruututaustan ilman alpha-kanavaa; teknisessä viimeistelyssä
poistettiin reunoihin yhdistyvä vaalea neutraali tausta, skaalattiin kaikki
asennot samalla kertoimella nearest-neighbor-menetelmällä ja kohdistettiin jalat.

Generoinnin alkuperäinen tulos on `img/acrobat_idle_walk_source.png`.
Teknisen viimeistelyn voi toistaa Pillow-kirjastolla:

```powershell
python tools/prepare_acrobat.py img/acrobat_idle_walk_source.png img
```

Pillow tarvitaan vain kuvien valmisteluun, ei peliin tai testeihin.
Generointikehote on tiedostossa `tools/acrobat_prompt.txt`.

## Testaus ja rajat

```powershell
.\.venv\Scripts\python -B -m unittest discover -s tests -v
```

Testit käyttävät SDL:n dummy-ajuria ilman näkyvää ikkunaa. Ne tarkistavat
arkin ruudut, jalkojen kohdistuksen, animaation ajan, tilanvaihdon ja peilauksen,
hypyn, muiden hahmojen toiminnan sekä pelisilmukan hahmonvaihdon.

Peli on edelleen prototyyppi. Kentänluonnin vanhat virheet, törmäykset
ja editorin tallennus ovat tämän muutoksen
ulkopuolella. Hahmojen liike ja hyppy ovat edelleen päivityskertoihin sidottuja;
ainoastaan kuvien animaatio käyttää kulunutta aikaa.

## Hyppyanimaatio

Pelin käyttämä yhdistelmäarkki on nyt `img/acrobat_animations.png` (192 × 192 px).
Sen kaksi ensimmäistä riviä ovat alkuperäisen seisonta/kävelyarkin muuttumattomat
ruudut. Kolmannella rivillä ovat 48 × 64 px:n hyppyruudut:

1. `rise`: nousu, pystynopeus alle -2.
2. `apex`: lakipiste, pystynopeuden itseisarvo enintään 2.
3. `fall`: lasku, pystynopeus yli 2.
4. `land`: 0,08 sekunnin palautuminen maahan osumisen jälkeen.

Ilmassa vaihe valitaan todellisesta pystynopeudesta, ei animaatioajastimesta.
Laskeutumisasennon jälkeen hahmo jatkaa seisontaa tai kävelyä liikkeen mukaan.
Uuden hypyn saa aloittaa myös laskeutumisasennosta; ilmassa ei voi hypätä uudelleen.
Ilmaposeissa pään ankkuri pysyy samassa kohdassa ruutua, joten jalkojen koukistus
ei aiheuta ylimääräistä koko hahmon siirtymää. Laskeutumisruudun jalat kohdistuvat
samaan rivin 61 alareunaan kuin seisonta/kävely. Kaikki ruudut peilautuvat vasemmalle.

`img/acrobat_jump.png` sisältää pelkän hyppyrivin. Näkyvä esikatselu:
`img/acrobat_jump_preview.gif`. GIF käyttää hahmon oikeaa päivityskoodia,
mutta toistuu hidastettuna vaiheiden havainnollistamiseksi. Esikatselu aloittaa
esikatselun maantasolta. Hyppy palautuu nyt aina omaan lähtökorkeuteensa;
erillistä alustatörmäysjärjestelmää ei ole.

Hyppykuvat luotiin sisäänrakennetulla ImageGenillä nykyisen hahmoarkin pohjalta.
Kehote: `tools/acrobat_jump_prompt.txt`; generoitu lähde: `img/acrobat_jump_source.png`.
Ruudutus ja ruututaustan poisto voidaan toistaa Pillow-kirjastolla:

```powershell
python tools/prepare_acrobat_jump.py img/acrobat_jump_source.png img
python tools/preview_acrobat_jump.py
```

Jälkimmäinen komento tarvitsee myös Pygamen. Testit tarkistavat hyppytilat,
laskeutumisen, liikkeen jatkumisen, peilauksen, kaksoishypyn eston ja vanhojen
animaatioruutujen säilymisen. Kenttäfysiikkaa ei muutettu.

## Toiminnallinen tarkistus 12.9.2026

Laajempi `tests/test_functional.py` ajaa oikeat peli- ja editorisilmukat
SDL dummy -ajurilla. Nuolten tila ja ikkunan fokus simuloidaan, muut tapahtumat
syötetään Pygamen tapahtumajonoon. Testaus kattaa kaikkien hahmojen liikkeen,
molemmat Ctrl-näppäimet, vaihdon nuoli pohjassa ja hypyn aikana, fokuksen menetyksen,
reunat, hypyn toistamisen, editorin ruutujen maalaamisen ja sulkemisen.
Peli käynnistetään repojuuresta, src-kansiosta ja ulkopuolisesta työhakemistosta.
Myös kaikkien PNG-kuvien lataus tarkistetaan.

Tarkistuksessa korjattiin kaksi toistettua vikaa: ensimmäinen hyppy siirsi
akrobaattia 132 pikseliä alaspäin, ja yhtäaikaiset vastakkaiset nuolet
liikuttivat hahmoa vasemmassa reunassa. Hyppy muistaa nyt lähtökorkeuden,
ja vastakkaiset nuolet kumoavat toisensa ennen reunarajausta.
Näkyvää Windows-ikkunan näppäimistö- ja hiiritestiä ei tässä ympäristössä tehty.
