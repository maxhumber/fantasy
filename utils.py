import datetime


def flatten(d):
    return [item for sublist in d.values() for item in sublist]


def mondays():
    today = datetime.date.today()
    monday = today + datetime.timedelta(days=-today.weekday())
    next_monday = today + datetime.timedelta(days=(7 - today.weekday()))
    return monday.strftime("%Y-%m-%d"), next_monday.strftime("%Y-%m-%d")


monday, next_monday = mondays()


week = (
    datetime.date.today() - datetime.datetime.strptime("2021-01-24", "%Y-%m-%d").date()
).days // 7 + 2


yahoo = {84778: 12, 84570: 3, 84919: 5}


team_codes = {
    "anaheim-ducks": "Anh",
    "arizona-coyotes": "Ari",
    "boston-bruins": "Bos",
    "buffalo-sabres": "Buf",
    "calgary-flames": "Cgy",
    "carolina-hurricanes": "Car",
    "chicago-blackhawks": "Chi",
    "colorado-avalanche": "Col",
    "columbus-blue-jackets": "Cls",
    "dallas-stars": "Dal",
    "detroit-red-wings": "Det",
    "edmonton-oilers": "Edm",
    "florida-panthers": "Fla",
    "los-angeles-kings": "LA",
    "minnesota-wild": "Min",
    "montreal-canadiens": "Mon",
    "nashville-predators": "Nsh",
    "new-jersey-devils": "NJ",
    "new-york-islanders": "NYI",
    "new-york-rangers": "NYR",
    "ottawa-senators": "Ott",
    "philadelphia-flyers": "Phi",
    "pittsburgh-penguins": "Pit",
    "san-jose-sharks": "SJ",
    "st-louis-blues": "StL",
    "tampa-bay-lightning": "TB",
    "toronto-maple-leafs": "Tor",
    "vancouver-canucks": "Van",
    "vegas-golden-knights": "VGK",
    "washington-capitals": "Was",
    "winnipeg-jets": "Wpg",
}
