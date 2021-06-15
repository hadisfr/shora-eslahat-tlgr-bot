#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, DefaultDict, Tuple

from bot import Bot


def get_token() -> str:
    with open(".token") as f:
        return f.read().strip()


def get_province_map() -> DefaultDict[str, str]:
    provice_cities = defaultdict(list)
    with open("province_map.csv") as f:
        for relation in csv.DictReader(f):
            provice_cities[relation["Province"]].append(relation["City"])
    return provice_cities


def get_city_lists() -> Dict[str, str]:
    def get_city_name(addr: str) -> str:
        return ".".join(addr.split("/")[-1].split(".")[:-1])

    return {get_city_name(addr): addr for addr in map(str, Path("lists").glob('*.*'))}


def get_advertises() -> Tuple[Dict[str, str], Dict[str, str]]:
    def get_ad_name(addr: str) -> str:
        return ".".join(addr.split("/")[-1].split(".")[:-1])

    advertises_media = {get_ad_name(addr): addr for addr in map(str, Path("ad").glob('*.*'))}
    advertises_texts = {get_ad_name(addr): addr for addr in map(str, Path("ad-txt").glob('*.*'))}
    for key in list(filter(lambda key: key not in advertises_texts, advertises_media.keys())):
        del advertises_media[key]
    for key in list(filter(lambda key: key not in advertises_media, advertises_texts.keys())):
        del advertises_texts[key]
    return advertises_media, advertises_texts


def get_config() -> Dict[str, object]:
    with open("config.json") as f:
        return json.load(f)


def main():
    config = get_config()
    bot = Bot(
        get_token(),
        config["msg"],
        config["promoted cities"],
        get_city_lists(),
        get_province_map(),
        *get_advertises(),
    )
    bot.run()


if __name__ == '__main__':
    main()
