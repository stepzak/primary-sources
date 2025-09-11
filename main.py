import asyncio
import sys
from hashlib import sha256
import aiohttp
from bs4 import BeautifulSoup
import os
import logging
import dateutil.parser as parser
from dotenv import load_dotenv


LOG_FILE = os.getenv("LOG_FILE", "logs.log")
logging.basicConfig(
    #filename=LOG_FILE,
    #level=logging.DEBUG,
    level = logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

load_dotenv()

RETRIES = int(os.getenv("RETRIES"))
UA = os.getenv("UA")
HEADERS = {"User-Agent": UA}


async def request(url: str, ret_text: bool = False,) -> str | dict:
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for i in range(RETRIES):
            resp = await session.get(url)
            code = resp.status
            if code == 200:
                return await resp.text() if ret_text else await resp.json()
        ex = await resp.text()

    logging.exception(f"Could not extract text for url: {url}, {ex}")
    raise ValueError


async def get_voyager_launch_date() -> str:
    URL = os.getenv("VOYAGER_URL", "https://science.nasa.gov/mission/voyager/voyager-1/") #офиц сайт наса
    t = await request(URL, True)


    soup = BeautifulSoup(t, "html.parser")
    grid = soup.find('div', attrs={'class': 'mission-single-meta'})
    el = grid.find_all("div", attrs={"class": "grid-col-12"})[-1]
    for i in el.children:
        text = i.text.replace("\n", "")
        if "launch" in text:
            return parser.parse(text.split("launch")[1]).strftime("%Y%m%d")

async def get_rfc_date() -> str:
    URL = os.getenv("RFC_URL", "https://datatracker.ietf.org/doc/rfc1149/doc.json") # IETF Datatracker

    r = await request(URL)
    return parser.parse(r["rev_history"][0]["published"]).strftime("%Y%m%d")

async def get_unicode() -> str:
    s = "🧠"
    URL = os.getenv("UNICODE_URL", "https://unicode.org/emoji/charts-12.0/emoji-ordering.txt") #офиц сайт юникода
    t = await request(URL, ret_text=True)
    for i in t.split("\n"):
        if s in i:
            ret = i.split(";")[0]
            return ret.replace("U+", '').rstrip()

async def get_btc_generic_block_date() -> str:
    URL = os.getenv("BTC_URL", "https://web.archive.org/web/20140212034805/http://blockexplorer.com/block/000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f") #blockexplorer archive
    t = await request(URL, ret_text=True)
    soup = BeautifulSoup(t, "html.parser")
    els = soup.find_all("li")
    for el in els:
        if "Time" in el.text:
            #print(el.text)
            return parser.parse(el.text.split(":")[1]).strftime("%Y%m%d")

async def get_kr2_isbn10() -> str:
    URL = os.getenv("KR2_ISBN10_URL", "https://openlibrary.org/books/OL2030445M.json") #open library
    r = await request(URL)
    return r["isbn_10"][1]


async def gather_tasks():
    tasks = [get_voyager_launch_date(), get_rfc_date(), get_unicode(), get_btc_generic_block_date(), get_kr2_isbn10()]

    res = await asyncio.gather(*tasks)




    flag = "FLAG{" + res[0]+"-"+res[1]+"-"+res[2]+"-"+res[3]+"-"+res[4]+"}"
    logging.info(f"{flag=}")
    logging.info(f"SHA256: {sha256(flag.encode('utf-8')).hexdigest()}")

if __name__ == "__main__":
    asyncio.run(gather_tasks())