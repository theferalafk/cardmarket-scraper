import cloudscraper
import random

class CMScraper:

    CARD_QUERY = "https://www.cardmarket.com/en/Magic/Cards/{}?sellerCountry=7&sellerType={}&language=1,3&minCondition=4"


    def __init__(self, delay):
        self.scraper = cloudscraper.create_scraper(delay=delay, interpreter='js2py')

    def http_get(self, url : str) -> str:
        res = self.scraper.get(url)
        if res.status_code != 200:
            print(res.text)
            raise RuntimeError("curl call failed")
        return res.text

    def get_card_by_name(self, name : str, type : str | None = None) -> str:
        if type:
            return self.http_get(self.CARD_QUERY.format(name, type))
        return self.http_get(f"https://www.cardmarket.com/en/Magic/Cards/{name}?sellerCountry=7&language=1,3&minCondition=4")


    def get_more_sellers_by_id(self, card_id : str, page : str, token : str, filters : str ="{\"idCountries\":[7]\\\\,\"idLanguage\":{\"1\":1\\\\,\"3\":3}\\\\,\"condition\":[\"MT\"\\\\,\"NM\"\\\\,\"EX\"\\\\,\"GD\"]}", url : str ="https://www.cardmarket.com/en/Magic/AjaxAction/Metacard_LoadMoreArticles") -> str:
        data = (
            "------geckoformboundary203d6753bc349ab9286ae8361576f6c9\r\n"
            "Content-Disposition: form-data; name=\"__cmtkn\"\r\n\r\n"
            f"{token}\r\n"
            "------geckoformboundary203d6753bc349ab9286ae8361576f6c9\r\n"
            "Content-Disposition: form-data; name=\"page\"\r\n\r\n"
            f"{page}\r\n"
            "------geckoformboundary203d6753bc349ab9286ae8361576f6c9\r\n"
            "Content-Disposition: form-data; name=\"filterSettings\"\r\n\r\n"
            f"{filters}\r\n"
            "------geckoformboundary203d6753bc349ab9286ae8361576f6c9\r\n"
            "Content-Disposition: form-data; name=\"idMetacard\"\r\n\r\n"
            f"{card_id}\r\n"
            "------geckoformboundary203d6753bc349ab9286ae8361576f6c9--\r\n"
        )

        header = {'Content-Type': 'multipart/form-data; boundary=----geckoformboundary203d6753bc349ab9286ae8361576f6c9'}

        res = self.scraper.post(url, headers=header, data=data)

        return res.text