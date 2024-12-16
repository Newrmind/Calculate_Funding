import requests
import xml.etree.ElementTree as ET


def get_prevsettlerprice():
    url = "https://iss.moex.com/iss/engines/futures/markets/forts/securities?securities=USDRUBF,EURRUBF,CNYRUBF,GLDRUBF,IMOEXF&iss.meta=on&iss.only=securities&securities.columns=SECID,PREVSETTLEPRICE"
    response = requests.request('GET', url)

    # Разбор XML
    root = ET.fromstring(response.text)

    # Извлекаем нужные данные
    data_dict = {}
    for row in root.findall(".//row"):
        secid = row.get("SECID")
        prevsettleprice = row.get("PREVSETTLEPRICE")
        data_dict[secid] = float(prevsettleprice)

    return data_dict

if __name__ == "__main__":
    usd = get_prevsettlerprice()
    print(usd["USDRUBF"])

