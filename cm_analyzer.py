import tqdm
class CMAnalyzer:
    def __init__(self, full_seller_dict, wanted_cards):
        self.full_seller_dict = full_seller_dict
        self.wanted_cards = [card.replace(" ","-").replace("'","").replace(",","").replace(":","").replace("//-","") for card in wanted_cards]
    
    def _filter_left_to_buy(input_dict, left_to_buy):
        result = list()
        for name in input_dict.keys():
            tmp = list()
            for i in input_dict[name]:
                if i[0] in left_to_buy:
                    tmp.append(i)
                    sum += i[1]
            if len(tmp) > 0:
                if len(tmp)>4:
                    sum += 1.4
                elif len(tmp)>17:
                    sum += 2.3
                else:
                    sum += 1.25
                quota = sum / len(tmp)
                result.append([quota, name, tmp])
        result.sort()
        return result

    def _insert_vendor_top(seller_list, vendor_name, full_dict):
        offering = full_dict[vendor_name]
        sum = 1.25
        if len(offering)>4:
            sum = 1.4
        if len(offering)>17:
            sum = 2.3
        sum = 2.3
        for card in offering:
            sum += card[1]
        seller_list.insert(0, [sum / len(offering), vendor_name, offering])
        return seller_list


    def _filter_for_card(input_dict, card):
        result = list()
        for name in input_dict.keys():
            sum = 1.25
            if len(input_dict[name])>4:
                sum = 1.4
            if len(input_dict[name])>17:
                sum = 2.3
            sum = 2.3
            tmp = list()
            keep = False
            for i in input_dict[name]:
                if i[0]==card: keep = True
                tmp.append(i)
                sum += i[1]
            if not keep: tmp = list()
            if len(tmp) > 0:
                quota = sum / len(tmp)
                result.append([quota, name, tmp])
        result.sort()
        return result
    
    def _run_greedy_quota(self, forced_vendors = None):

        left_to_buy = self.wanted_cards.copy()
        shopping_cart = list()

        total = 0

        seller_list = CMAnalyzer._filter_left_to_buy(self.full_seller_dict, left_to_buy)
        while len(left_to_buy) > 0 and len(seller_list) > 0:
            if forced_vendors:
                CMAnalyzer._insert_vendor_top(seller_list, forced_vendors[0], self.full_seller_dict)
                forced_vendors.pop(0)
            seller = seller_list[0]
            buy_from_seller = list()
            seller_name = seller[1]
            cards = seller[2]
            for card in cards:
                if card[0] in left_to_buy:
                    buy_from_seller.append(card)
            if buy_from_seller:
                sum = 1.25
                if len(buy_from_seller)>4:
                    sum = 1.4
                if len(buy_from_seller)>17:
                    sum = 2.3

                for card in buy_from_seller:
                    sum += card[1]
                    left_to_buy.remove(card[0])
                shopping_cart.append([sum, round(sum/len(buy_from_seller),2), len(buy_from_seller), seller_name, buy_from_seller])
                total += sum

                seller_list = CMAnalyzer._filter_left_to_buy(self.full_seller_dict, left_to_buy)
            else:
                seller_list.pop(0)
        
        return total, len(shopping_cart), shopping_cart

    def _optimize_shopping_card(self, shopping_cart):

        sellers = [i[3] for i in shopping_cart]
        cards_dict = dict()
        for seller in sellers:
            for offer in self.full_seller_dict[seller]:   
                if offer[0] in self.wanted_cards:
                    if not offer[0] in cards_dict.keys():
                        cards_dict[offer[0]]=[[offer[1],seller]]
                    else:
                        cards_dict[offer[0]].append([offer[1],seller])
                        cards_dict[offer[0]].sort()

        optimized_cart = dict()
        for card in cards_dict.keys():
            offer = cards_dict[card][0]
            if not offer[1] in optimized_cart.keys():
                optimized_cart[offer[1]]=[[offer[0],card]]
            else:
                optimized_cart[offer[1]].append([offer[0],card])

        total = 0

        new_cart = list()

        for seller in optimized_cart.keys():
            buy_from_seller = optimized_cart[seller]
            sum = 1.25
            if len(buy_from_seller)>4:
                sum = 1.4
            if len(buy_from_seller)>17:
                sum = 2.3

            for card in buy_from_seller:
                sum += card[0]
            new_cart.append([sum, round(sum/len(buy_from_seller),2), len(buy_from_seller), seller, buy_from_seller])
            total += sum
        
        return total, len(new_cart), new_cart
    
    def get_vendors_for_card_by_quote(self, card_name, n=5):
        return CMAnalyzer._filter_for_card(self.full_seller_dict, card_name)[:n]

    def force_vendors(self, vendors : list[str, str]):
        return self._optimize_shopping_card(self._run_greedy_quota(vendors)[2])
    
    def force_vendor(self, vendor : str):
        return self.force_vendors([vendor]), vendor
    
    def run_default(self):
        return self._optimize_shopping_card(self._run_greedy_quota()[2])
    
    def force_all_vendors_once(self):
        res = list()
        for vendor in tqdm.tqdm(list(self.full_seller_dict.keys())):
            tmp = self.force_vendors([vendor])
            res.append([tmp[0], tmp[1], vendor])
        res.sort()
        return res[:20]
    
    def force_all_vendors_once_threaded(self):
        from multiprocessing import Pool

        with Pool(processes=8) as pool:
            return pool.map(self.force_vendor, list(self.full_seller_dict.keys()))