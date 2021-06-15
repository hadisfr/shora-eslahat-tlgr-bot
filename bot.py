from sys import stderr
from typing import Dict, List
from datetime import datetime

import telebot


class Bot:
    """Shora Bot"""
    def __init__(
        self,
        token: str,
        msgs: Dict[str, str],
        promoted_cities: List[str],
        city_lists: Dict[str, str],
        province_cities: Dict[str, str],
        advertises_media: Dict[str, str],
        advertises_texts: Dict[str, str],
    ):
        self.city_lists = dict(city_lists)
        self.msgs = msgs
        cities = set(city_lists.keys())
        self.promoted_cities = list(filter(lambda city: city in cities, promoted_cities))
        self.province_cities = dict(filter(
            lambda relation: relation[1],
            map(
                lambda relation: (relation[0], list(sorted(filter(
                    lambda city: city in cities,
                    relation[1]
                )))),
                province_cities.items()
             )
        ))
        self.provinces = list(sorted(self.province_cities.keys()))
        self.advertises_media = advertises_media
        self.advertises_texts = advertises_texts

        self.choices_main = self._get_reply_markup(map(self._get_city_name, self.promoted_cities + [self.msgs["other cities"], self.msgs["ad"]]))
        self.choices_provinces = self._get_reply_markup(map(self._get_province_name, self.provinces + [self.msgs["back"]]))
        self.choices_province_city = {
            province: self._get_reply_markup(map(self._get_city_name, cities + [self.msgs["other cities"]]))
            for province, cities in self.province_cities.items()
        }
        self.choices_ads = self._get_reply_markup(map(self._get_ad_name, list(self.advertises_texts.keys()) + [self.msgs["back"]]))
        
        self.bot = telebot.TeleBot(token, parse_mode="MARKDOWN")
        self.bot.message_handler(commands=["start"])(self._handle_start)
        self.bot.message_handler(content_types=["text"])(self._handle_msg)

    def run(self):
        self._log("Up and running...")
        self.bot.polling(none_stop=True)

    def _log(self, log, chat_id=None):
        if not chat_id:
            chat_id = "bot"
        dt = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        print("%s\t%s:\t%s" % (dt, chat_id, log), file=stderr, flush=True)

    def _normalize(self, text: str) -> str:
        text = text.replace("ي", "ی")
        text = text.replace("ك", "ک")
        return text

    def _get_reply_markup(self, choices: List[str]) -> telebot.types.ReplyKeyboardMarkup:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for choice in choices:
            markup.add(telebot.types.KeyboardButton(choice))
        return markup

    def _welcome(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["welcome"])

    def _tnx(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["tnx"])

    def _handle_wrong_input(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["wrong input"])
        self._select_main(chat_id)

    def _get_city_name(self, city: str) -> str:
        if city in {self.msgs["other cities"], self.msgs["ad"]}:
            return city
        return " ".join([self.msgs["city prefix"], city])

    def _get_province_name(self, province: str) -> str:
        if province == self.msgs["back"]:
            return province
        return " ".join([self.msgs["province prefix"], province])

    def _get_ad_name(self, ad: str) -> str:
        if ad == self.msgs["back"]:
            return ad
        return " ".join([self.msgs["ad prefix"], ad])

    def _select_main(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["select main"], reply_markup=self.choices_main)

    def _send_list(self, chat_id: str, city: str) -> None:
        if city not in self.city_lists:
            self._handle_wrong_input(chat_id)
            return
        caption = self.msgs["list caption pattern"] % city
        with open(self.city_lists[city], "rb") as photo:
            self.bot.send_photo(chat_id, photo, caption=caption)
        self._log("got list for %s" % city, chat_id)
        self.bot.send_message(chat_id, self.msgs["tnx"], reply_markup=telebot.types.ReplyKeyboardRemove())

    def _send_province_cities(self, chat_id: str, province: str) -> None:
        if province not in self.province_cities:
            self._handle_wrong_input(chat_id)
            return
        self.bot.send_message(chat_id, self.msgs["select city"], reply_markup=self.choices_province_city[province])

    def _send_provinces(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["select province"], reply_markup=self.choices_provinces)

    def _select_ads(self, chat_id: str) -> None:
        self.bot.send_message(chat_id, self.msgs["select ad"], reply_markup=self.choices_ads)

    def _send_ad(self, chat_id: str, ad: str) -> None:
        if ad not in self.advertises_texts:
            self._handle_wrong_input(chat_id)
            return
        with open(self.advertises_texts[ad]) as f:
            ad_text = f.read()
        caption = "\n\n".join([ad_text, self.msgs["ad suffix"]])
        with open(self.advertises_media[ad], "rb") as photo:
            self.bot.send_photo(chat_id, photo, caption=caption)
        self._log("got ad %s" % ad, chat_id)
        self._select_main(chat_id)

    def _handle_start(self, msg) -> None:
        chat_id = msg.chat.id
        self._log("started the bot", chat_id)
        self._welcome(chat_id)
        self._select_main(chat_id)

    def _handle_msg(self, msg) -> None:
        chat_id = msg.chat.id
        text = self._normalize(msg.text)
        self._log(text, chat_id)
        splitted = text.split()
        prefix = splitted[0]
        entity = " ".join(splitted[1:])

        if text == self.msgs["other cities"]:
            self._send_provinces(chat_id)
        elif text == self.msgs["back"]:
            self._select_main(chat_id)
        elif text == self.msgs["ad"]:
            self._select_ads(chat_id)
        elif prefix == self.msgs["city prefix"]:
            self._send_list(chat_id, entity)
        elif prefix == self.msgs["province prefix"]:
            self._send_province_cities(chat_id, entity)
        elif prefix == self.msgs["ad prefix"]:
            self._send_ad(chat_id, entity)
        elif text in self.city_lists:
            self._send_list(chat_id, text)
        elif text in self.province_cities:
            self._send_list(chat_id, text)
        else:
            self._handle_wrong_input(chat_id)
