import orjson
from pprint import pprint
# show all options starting with OPT_
opts = {k: getattr(orjson, k) for k in dir(orjson) if k.startswith("OPT_")}
pprint(opts)
