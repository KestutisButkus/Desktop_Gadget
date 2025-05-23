import json

from bs4 import BeautifulSoup
import requests
bullet = '\u2022'
lines_news = 4

def get_15min_news():
    news = []
    source_15min = requests.get("https://www.15min.lt/naujienos")
    source_15min.encoding = 'utf-8'
    soup_15min = BeautifulSoup(source_15min.text, "html.parser")
    item_data_15min = soup_15min.find_all("h4", class_="vl-title item-no-front-style")
    for item in item_data_15min[:lines_news]:
        items_15min = item.get_text(strip=True)
        news.append(f"{bullet} {items_15min}\n")
    return ''.join(news)

def get_lrt_news():
    news = []
    source_lrt = requests.get("https://www.lrt.lt")
    source_lrt.encoding = "utf-8"
    soup_lrt = BeautifulSoup(source_lrt.text, "html.parser")
    item_data_lrt = soup_lrt.find_all("h3", class_="news__title")
    for item in item_data_lrt[:lines_news]:
        items_lrt = item.get_text(strip=True)
        news.append(f"{bullet} {items_lrt}\n")
    return ''.join(news)

def get_delfi_news():
    news = []
    source_delfi = requests.get("https://www.delfi.lt/paieska")
    soup_delfi = BeautifulSoup(source_delfi.text, "html.parser")
    item_data_delfi = soup_delfi.find_all("h5", class_="headline-title headline-title--size-h4 headline-title--size-sm-h6")
    for item in item_data_delfi[:lines_news]:
        items_delfi = item.get_text(strip=True)
        news.append(f"{bullet} {items_delfi}\n")
    return ''.join(news)

def get_vz_news():
    """Funkcija ištraukia naujausias Verslo Žinios naujienas, praleidžiant komentarų nuorodas."""
    
    news = []  # Sąrašas, kuriame bus saugomos naujienų antraštės ir nuorodos
    source_vz = requests.get("https://www.vz.lt/")  # Užklausa puslapiui
    source_vz.encoding = "utf-8"  # Nustatome koduotę, kad būtų išvengta lietuviškų simbolių problemų
    soup_vz = BeautifulSoup(source_vz.text, "html.parser")  # Sukuriame BeautifulSoup objektą

    # Surandame naujienų bloką
    item_data_vz = soup_vz.find_all("ul", class_="ordered-articles col")

    for item in item_data_vz:
        articles = item.find_all("a", href=True)  # Surandame visas nuorodas

        for article in articles:
            # Jei nuoroda veda į komentarų sekciją, praleidžiame
            if "comments" in article["href"]:
            # if article.find_parent("div", class_="comments"):
                continue

            # Ištraukiame antraštę ir nuorodą
            title = article.get_text(strip=True)
            link = article["href"]

            # Jei nuoroda nėra pilna, pridėti tinklalapio pagrindinį adresą
            if not link.startswith("http"):
                link = f"https://www.vz.lt{link}"

            news.append((title, link))  # Saugojame naujieną

            # ✅ Užtikriname, kad surinksime **tik tiek naujienų, kiek nurodyta**
            if len(news) == lines_news:
                break
        if len(news) == lines_news + 1:
            break

    return news  # Grąžiname surinktas naujienas




if __name__ == "__main__":
    print("15min naujienos:\n", get_15min_news())
    print("\nLRT naujienos:\n", get_lrt_news())
    print("\nDelfi naujienos:\n", get_delfi_news())
    print("\nVerslo žinios naujienos:\n", get_vz_news())
