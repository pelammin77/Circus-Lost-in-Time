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
hahmon toiminnon. Akrobaatti hyppää ja veitsenheittäjä esittää heittoanimaation.
Voimamies nostaa, kantaa, laskee ja työntää kokeilulaatikkoa. Sulje peli ikkunan sulkupainikkeella.
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
Voimamiehellä ja veitsenheittäjällä on omat animaatioarkkinsa, jotka kuvataan alla.

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

Peli on edelleen prototyyppi. Kentänluonnin vanhat virheet, yleinen kenttäfysiikka
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
pelissä laatikko voi nyt myös toimia hyppyalustana.

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

## Veitsenheittäjän kävely ja heitto

`img/knife_animations.png`: 288 × 160 px RGBA, 4 saraketta ja 2 riviä,
ruutu 72 × 80 px. Jalkojen alin näkyvä rivi on 77. Hahmon kävelykorkeus
on noin 73 px kuten alkuperäisessä kuvassa; suurempi ruutu jättää tilan käsille.
Rivi 0 sisältää neljä kävelyvaihetta (8 fps), joista ruutua 1 käytetään myös
seisontana. Rivi 1 sisältää heiton valmistelun, käden noston, irrotusliikkeen
ja palautumisen. Kaikki ruudut peilataan vasemmalle tarpeen mukaan.

Välilyönti käynnistää yhden 0,48 sekunnin heiton (0,12 s per vaihe).
Hahmo pysähtyy ja pitää heittosuuntansa toiminnon ajan. Uudet painallukset
eivät käynnistä keskeneräistä heittoa uudestaan. Sen jälkeen hahmo palaa
seisontaan tai jatkaa kävelyä seuraavassa liikepäivityksessä. Hahmonvaihto
ei jäädytä heittoa: myös inaktiivinen hahmo päivitetään loppuun.

Heitto vapauttaa lentävän, pyörivän veitsispriten, joka pysähtyy laatikkoon
osuessaan. Vahinkoa tai vihollisjärjestelmää ei ole toteutettu.

Kuvat tehtiin sisäänrakennetulla ImageGenillä pelissä käytetyn huivipäisen
veitsenheittäjän pohjalta; vaihtoehtoista sarjakuvahahmoa ei käytetty.
Lähde ja alpha säilytettiin. Tekninen viimeistely poistaa lähes näkymättömän
alpha-kohinan, käyttää yhteistä skaalausta ja kohdistaa jalkalinjan.
Alkuperäisiä hahmokuvia ei korvattu.

- Esikatselu: `img/knife_animation_preview.gif` (oikeasta hahmokoodista, hidastettu).
- Lähde: `img/knife_animation_source.png`; kehote: `tools/knife_prompt.txt`.
- Valmistelu: `python tools/prepare_knife.py img/knife_animation_source.png img`.
- GIF:n uusinta: `python tools/preview_knife.py`.

Kuvatyökalut tarvitsevat Pillow-kirjaston ja GIF-työkalu myös Pygamen.
Pelin riippuvuudet eivät muuttuneet. `tests/test_knife_animation.py` tarkistaa
arkin, kävelyn, suunnat, heittovaiheet, päättymisen, uusintapainallukset ja
hahmonvaihdon oikeassa pelisilmukassa. Kaikki 19 testiä läpäisivät SDL dummylla.

## Lentävä veitsi

Veitsi irtoaa 0,24 sekunnin kohdalla heittokädestä. Se lentää vaakasuoraan
360 px/s ja pyörii kahdeksassa 45 asteen asennossa (16 asentovaihtoa/s).
Jokainen heitto luo yhden veitsen. Veitsi poistuu ruudun ulkopuolella tai
viimeistään kolmessa sekunnissa. Hahmonvaihto ei pysäytä lentoa.

Sprite: img/throwing_knife.png (28 × 14 px RGBA). ImageGen-kehote ja
viimeistelyohje: tools/throwing_knife_prompt.txt. Esikatselu oikeasta
hahmo- ja ammusluokasta: img/flying_knife_preview.gif (hidastettu).
Uusinta: python tools/preview_flying_knife.py (Pillow ja Pygame).

Kaikki 22 testiä läpäisivät SDL dummy -ajurilla. Uudet tarkistukset kattavat
irrotushetken, yhden ammuksen per heitto, molemmat suunnat, pyörimisen,
poistumisen sekä eri päivitysaikojen vastaavuuden. Laatikkotörmäys on lisätty;
vahinkologiikkaa ei ole.

## Voimamiehen animaatiot ja kokeilulaatikko

Voimamiehellä on seisonta, kävely, nosto, kannattelu, kantokävely, laskeminen
ja työntö. Välilyönti aloittaa noston lähellä laatikkoa; kantaessa se aloittaa
laskun. Nosto ja lasku kestävät 0,8 s ja lukitsevat kävelyn toiminnon ajaksi.
Kantaessa nopeus puolittuu (nykyisin 2 -> 1 px/päivitys). Hahmonvaihto ei
keskeytä nostoa/laskua, ja inaktiivinen voimamies jää kannattelemaan laatikkoa.

Työntö käynnistyy nuolella, kun voimamiehen ojennetut kädet ovat laatikon
sivulla. Poispäin kävely ei vedä laatikkoa. Laskua ja työntöä rajoittavat
ruudun reunat, muut laatikot ja hahmojen suorakulmiot. Jos laskupaikka
on varattu, laatikko jää käsiin ja peli näyttää ohjeen siirtyä sivuun.
Tyhjällä alueella välilyönti opastaa siirtymään laatikon viereen.

Arkki img/strongman_animations.png: 384x320 RGBA, 4x4 ruutua, ruutu96x80.
Rivi0 kävely (6fps, ruutu1 myös seisonta), rivi1 nelivaiheinen nosto
(viimeinen ruutu myös kannattelu), rivi2 kantokävely (5fps), rivi3 työntö
(6fps). Laskeminen käyttää nostoruutuja käänteisesti, ja erillinen
img/strongman_lower.png sisältää laskurivin myös suoraan leikattavaksi.
Kaikissa ruuduissa jalkalinja78 ja yhtenäinen skaala. Vasemman suunnan
ruudut peilataan. Hahmon alkuperäiset kuvat säilytettiin.

ImageGenillä tehdyt lähteet: img/strongman_source.png ja img/crate_source.png.
Tarkat kehotteet: tools/strongman_prompts.txt. Viimeistely:
python tools/prepare_strongman.py img (Pillow).
Oikeasta hahmokoodista renderöity esikatselu: img/strongman_actions_preview.gif.
Sen uusinta: python tools/preview_strongman.py (Pillow ja Pygame).
GIF on hidastettu. Työntöosuuden alussa hahmo asetetaan laatikon viereen,
jotta eri animaatiot voidaan näyttää lyhyessä esikatselussa.

Testit kattavat nosto/kanto/laskusyklin, estyneen laskun myös animaation
kesken, työntämisen, suunnan ja reunat sekä hahmonvaihdon noston aikana.
Kaikki 28 testiä läpäisivät SDL dummy -ajurilla. Näkyvää käsin pelattavaa
Windows-testiä ei tehty.

Laatikko estää nyt akrobaatin ja veitsenheittäjän kävelyn sivulta läpi.
Akrobaatti voi hypätä laatikon päälle, kävellä sen päällä ja hypätä uudelleen.
Reunalta poistuminen tai laatikon siirtyminen alta pudottaa akrobaatin maahan.
Myös kannettu laatikko on kiinteä esine.
Muiden hahmojen nykyiset animaatiot ja lentävä veitsi säilyvät.

Laatikkoon osuva veitsi pysähtyy siihen sekunniksi ja katoaa. Osuman tarkistus
kattaa koko kuljetun matkan, joten suuri päivitysaika ei vie veistä laatikon läpi.
Laatikon yläpuolelta kulkeva veitsi voi lentää sen yli. Myös kannettu laatikko
pysäyttää veitsen; kiinni jäänyt veitsi seuraa laatikkoa lyhyen näkyvyysaikansa.
Kaikki 38 testiä läpäisivät, mukaan lukien oikean pelisilmukan hyppy laatikon päälle.

## Alataso ja ylempi tasanne

Kaikki hahmot ja laatikko alkavat näkyvän alatason päällä (y=540).
Oikealla on 200 px leveä tasanne 85 px ylempänä. Voimamies siirtää 40 px korkean
laatikon tasanteen lähelle väliportaaksi. Akrobaatti hyppää laatikolta tasanteelle
välilyönnillä. Suora hyppy maasta ei riitä. Tasanteen sivut ja alapinta ovat kiinteitä.
Tasanteelta pääsee alas kävelemällä reunan yli. Erillistä pudottautumisnäppäintä
ei ole. Myös tasanteelta hyppääminen ja uudelleen laskeutuminen toimivat.
Tasojen grafiikka piirretään Pygamella eikä tarvitse uusia kuvatiedostoja.
Hahmot kulkevat toistensa läpi. Laatikot, tasanteet ja veitsien osumat huomioidaan
esteinä. Voimamiehen työntö, nosto, kantaminen ja lasku tarkistavat myös laatikon
liikeradan esteiden varalta.
