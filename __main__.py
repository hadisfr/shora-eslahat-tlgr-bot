#!/usr/bin/env python3

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, DefaultDict

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
    )
    bot.run()


if __name__ == '__main__':
    main()
