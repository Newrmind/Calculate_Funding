import time

import requests
import xml.etree.ElementTree as ET


def get_prevsettlerprice():
    url = "https://iss.moex.com/iss/engines/futures/markets/forts/securities?securities=USDRUBF,EURRUBF,CNYRUBF,GLDRUBF,IMOEXF&iss.meta=on&iss.only=securities&securities.columns=SECID,PREVSETTLEPRICE"

    retries = 10
    while retries > 0:
        try:
            response = requests.request('GET', url)

            # Разбор XML
            try:
                root = ET.fromstring(response.text)
            except ET.ParseError:
                raise ValueError("Ошибка парсинга XML")

            # Извлекаем нужные данные
            data_dict = {}
            for row in root.findall(".//row"):
                secid = row.get("SECID")
                prevsettleprice = row.get("PREVSETTLEPRICE")
                data_dict[secid] = float(prevsettleprice)

            if not data_dict:
                return None

            return data_dict

        except Exception as e:
            print(e)
            time.sleep(15)
            retries -= 1

if __name__ == "__main__":
    usd = get_prevsettlerprice()
    print(usd["USDRUBF"])

