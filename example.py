from cardmarketscraper import CardMarketScraper
from cm_analyzer import CMAnalyzer

decklist = []
with open("deck","r") as f:
    decklist = f.read().replace("1 ","").split("\n")

c = CardMarketScraper(decklist)

res = c.run()

with open("out.py","w") as f:
    f.write("out_data = " + str(res))

decklist_ = decklist.copy()
prices = CMAnalyzer(res, decklist_)
default = prices.run_default()
print(default)
print(prices.force_all_vendors_once())