from utils.expand import expand_grid

def _create_payloads(start=2015, end=2017):
    payloads = {
        'rules': [1],
        'pos': ['QB', 'RB', 'WR', 'TE', 'K', 'DST'],
        'yr': list(range(start, end + 1)),
        'wk': list(range(1, 17 + 1))
    }
    payloads = expand_grid(payloads)
    payloads = payloads.to_dict(orient='records')
    return payloads

def backfill():
    payloads = _create_payloads()
    df = pd.DataFrame()
    for payload in payloads:
        print(payload)
        d = _scrape(payload)
        d = _transform(d)
        df = df.append(d, sort=False)
    df = df[ALL_COLUMNS]
    return df
