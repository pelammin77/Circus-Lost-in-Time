# Pelin oma Anaconda-ympäristö

Ympäristö: `circus-lost-in-time`

Sijainti: `C:\Users\lammp\anaconda3\envs\circus-lost-in-time`

Python 3.12, Pygame 2.6.1 ja Pillow on asennettu tähän erilliseen ympäristöön.

## Helpoin käynnistys

Avaa `C:\Circus-Lost-in-Time` Resurssienhallinnassa ja kaksoisnapsauta
`Kaynnista-peli.cmd`. Editorin saa auki tiedostosta `Kaynnista-editori.cmd`.
Nämä konekohtaiset käynnistimet aktivoivat oikean ympäristön automaattisesti.

## Anaconda Prompt

```bat
conda activate circus-lost-in-time
cd /d C:\Circus-Lost-in-Time
python -B src\circus.py
```

Ohjaus: vasen/oikea nuoli liikuttaa, Ctrl vaihtaa hahmoa, välilyönti toimii.
Akrobaatti hyppää, veitsenheittäjä heittää ja voimamies nostaa/laskee laatikon.
Voimamies työntää laatikkoa kävelemällä sitä kohti käsien ollessa sen sivulla.
Sulje peli ikkunan ruksista.

## Testit

```bat
conda activate circus-lost-in-time
cd /d C:\Circus-Lost-in-Time
python -B -m unittest discover -s tests -v
python -m pip check
```

## Ympäristön luominen toiselle koneelle

```bat
conda env create -f environment.yml
```

Akrobaatti voi hypätä laatikon päälle. Akrobaatti ja veitsenheittäjä eivät
kävele laatikon läpi, ja siihen osuva veitsi pysähtyy. Peli on edelleen
prototyyppi: varsinainen kenttäjärjestelmä ja vahinkomekaniikka puuttuvat.
