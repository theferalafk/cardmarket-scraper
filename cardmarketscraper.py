from util.cs_requests import CMScraper
from util.cm_parser import get_load_more_params, parse_first_sellers, parse_more_sellers
import random
import time
import tqdm

class CardMarketScraper:
    def __init__(self, card_list, pages_to_load=5, randomize_requests=True):
        #card list expected to be: of format ['Starfield Vocalist', 'Lich Knights' Conquest', ...]
        self.card_list = [card.replace(" ","-").replace("'","").replace(",","").replace(":","") for card in card_list]
        self.sellers_per_card = list()
        self.cards_per_seller = dict()
        self.pages_to_load = pages_to_load
        self.randomize_requests = randomize_requests
    
    def _query_all_cards(self):
        scraper = CMScraper(3)

        for index, card in enumerate(tqdm.tqdm(self.card_list)):
            try:
                if (index+1)%7==0:
                    scraper = CMScraper(3+(index%5))
                card_sellers = dict()
                for seller_type in ["0", "1,2"]:
                    initial_res = scraper.get_card_by_name(card, seller_type)
                    card_sellers.update(parse_first_sellers(initial_res))
                    if not card_sellers:
                        print(card)
                    card_id, token, filters = get_load_more_params(initial_res)

                    for i in range(1, self.pages_to_load+1):                    
                        more_res = scraper.get_more_sellers_by_id(card_id, i, token, filters)
                        more_seller_dict = parse_more_sellers(more_res)
                        if not more_seller_dict:
                            print(f"failed on {card}, Loading Page {i}, Seller Type (0 Pri, 1 Pro, 2 Pow): {seller_type}")
                            break
                        #update new dict with old, so the lower price gets saved per seller
                        more_seller_dict.update(card_sellers)
                        card_sellers = more_seller_dict

                        if self.randomize_requests:
                            time.sleep(random.random()*2)
                        time.sleep(0.5)

                    if self.randomize_requests:
                        time.sleep(random.random()*4)
                    time.sleep(2)
                self.sellers_per_card.append(list(card_sellers.keys()))

                for seller in card_sellers.keys():
                    if not seller in self.cards_per_seller.keys():
                        self.cards_per_seller[seller] = list()
                    self.cards_per_seller[seller].append([card, card_sellers[seller]])
            except Exception as e:
                print(f"Fail on Card: {card} with {e}")


    def run(self):
        self._query_all_cards()
        return self.cards_per_seller


if __name__ == "__main__":
    card_list = ["Sol Ring", "Arcane Signet", "Helga, Skittish Seer"]
    scraper = CardMarketScraper(card_list)
    print(scraper.run())
