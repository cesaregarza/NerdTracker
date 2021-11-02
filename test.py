# %%
import nerdtracker as nt
from cloudscraper import create_scraper
scraper = create_scraper()
engine = nt.sql.return_engine()
li = [nt.classes.Node(x, scraper, i) for i,x in enumerate(nt.constants.nerd_list)]
nn = nt.classes.NodeNetwork(scraper, engine, 5, 50, li)
flagged_nodes = [node for node in nn.nodes if node.flag_for_stats_update]
from concurrent.futures import ThreadPoolExecutor, TimeoutError
with ThreadPoolExecutor() as executor:
    executor.map(lambda node: node.find_stats(), flagged_nodes, timeout=5)

# %%
