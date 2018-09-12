import pandas as pd
from itertools import product

def expand_grid(dictionary):
    return pd.DataFrame(
        [row for row in product(*dictionary.values())],
        columns=dictionary.keys()
    )
