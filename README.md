# Apie:

Ši programa naudoja `tkinter` biblioteką, kad sukurtų grafinį langą, kuris atvaizduoja orų informaciją, NordPool elektros kainas ir naujienas iš įvairių šaltinių.

## Diegimo instrukcijos

1. Įdiekite reikalingas bibliotekas:
   ```sh
   pip install -r requirements.txt 
2. Sukurkite config.py failą šakniniame programos kataloge, kuriame bus jūsų API KEY, lokacija ir kiti parametrai:
   ```sh
    key = "api_key"  # Enter your API KEY
    location = "city"  # Enter city    
3. Paleiskite programą:
    ```sh
   python main.py
## Naudojimo instrukcijos
Programa atvaizduoja šią informaciją:

Orai: Rodo orų informaciją.

NordPool elektros kainos: Rodo NordPool elektros kainų informaciją.

Naujienos: Rodo naujienas iš skirtingų šaltinių (15min, LRT, Delfi, Verslo žinios) iš news.py.

### Ši programa naudoja šias papildomas bibliotekas:

1. **beautifulsoup4==4.12.3**
   - HTML ir XML analizės biblioteka, naudojama duomenų ištraukimo iš tinklalapių, pvz., naujienų šaltinių (pvz., `news.py`).
2. **pillow==11.0.0**
    - Išplėstinė vaizdų apdorojimo biblioteka, naudojama orų ir vėjo krypties ikonų perdirbimui ir atvaizdavimui.

3. **pynordpool==0.2.3**
    - Biblioteka, skirta NordPool elektros kainų duomenų gavimui.
