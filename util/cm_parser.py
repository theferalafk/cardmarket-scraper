from bs4 import BeautifulSoup
import base64
from typing import Iterator, Tuple

def _parse_seller_iterator(seller_iterator : Iterator) -> dict[str, str]:
    res = {}
    for article_row in seller_iterator:
        seller_name = article_row.find('span', class_='seller-name').find('a').contents[0]
        seller_price = article_row.find('div', class_='price-container').find('span', class_="color-primary").contents[0]
        if seller_name not in res.keys():
            res[seller_name] = float(seller_price.replace(".","").replace(",",".").replace(" €",""))
    return res

def parse_first_sellers(html_string : str) -> dict[str, str]:
    #goes down the tree of the parser and adds first match (lowers price) to result dict
    #if no matches are found the resulting dict is empty
    article_table = BeautifulSoup(html_string, 'html.parser').find('div', class_='table-body')
    res = dict()

    if article_table is None:
        return res
    
    return _parse_seller_iterator(article_table.children)

def parse_more_sellers(xml_string : str) -> dict[str, str]:
    #we expect ajax xml response
    try:
        xml_parser = BeautifulSoup(xml_string, "xml")
        table = base64.b64decode(xml_parser.find("rows").contents[0])
        
        table_parser = BeautifulSoup(table, 'html.parser')
        table_iterator = table_parser.find_all('div', class_="article-row")

        return _parse_seller_iterator(table_iterator)
    except Exception as e:
        print("failed parsing more sellers", e)
        return {}

def get_load_more_params(html_string : str) -> Tuple[str, str, str]:
    parser = BeautifulSoup(html_string, 'html.parser')
    card_id = parser.find(id='loadMore').find("input", {"name":"idMetacard"}).get('value')
    token = parser.find(id='loadMore').find("input", {"name":"__cmtkn"}).get('value')
    filters = parser.find(id='loadMore').find("input", {"name":"filterSettings"}).get('value')
    return card_id, token, filters
    