import asyncio
import aiohttp
import logging
from tqdm import tqdm

import pandas as pd
import os
import json

from dotenv import load_dotenv

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler("SMADIMO-GP-2/logs/parser.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()


def make_market_dict(df, other_currency: set):
    market_dict = {}
    for market, currency in zip(df["Маркет"], df["Дефолтная валюта"]):
        market_dict[market] = other_currency | {currency.lower()}
    return market_dict


async def fetch_tickets(session, sem, url, headers, query, currency_rate, columns, max_retries=3):
    for attempt in range(max_retries + 1):
        async with sem:
            try:
                async with session.get(url, headers=headers, params=query) as response:
                    if response.status == 429:
                        if attempt < max_retries:
                            logger.warning(
                                "429 Too Many Requests | query=%s | retry=%s/%s | пауза 10 сек",
                                query,
                                attempt + 1,
                                max_retries,
                            )
                            await asyncio.sleep(10)
                            continue
                        else:
                            logger.error(
                                "429 Too Many Requests | query=%s | превышен лимит ретраев",
                                query,
                            )
                            return []

                    response.raise_for_status()
                    data = await response.json()
                    tickets = data.get("data", [])

                    if not tickets: logger.debug("Пустой ответ для query=%s", query); return []

                    rows = []
                    for item in tickets:
                        row = {col: item.get(col) for col in columns}
                        row["market"] = query["market"]
                        row["currency"] = query["currency"]
                        row["rate"] = currency_rate.get(query["currency"])
                        rows.append(row)

                    await asyncio.sleep(1)
                    return rows

            except Exception as e:
                logger.exception("Непредвиденная ошибка | query=%s | msg=%s", query, str(e))
                return []


async def main():
    logger.info("Старт программы")
    load_dotenv()

    url = "http://api.travelpayouts.com/v2/prices/month-matrix"
    token = os.getenv("TOKEN")

    headers = {"X-Access-Token": token}

    OTHER_CURRENCIES = {"rub", "usd", "eur", "cny"}
    
    df_iata = pd.read_csv("SMADIMO-GP-2/data/_api/cities_prepared.csv")
    IATA_CODES = df_iata["IATA_code"].to_list()

    with open("SMADIMO-GP-2/data/_api/currency.json", "r", encoding="utf-8") as f:
        currency_rate = json.load(f)

    columns = [
        "depart_date",
        "origin",
        "destination",
        "gate",
        "trip_class",
        "value",
        "duration",
        "distance"
    ]

    market_df = pd.read_csv("SMADIMO-GP-2/data/_api/market_prepared.csv")
    market_dict = make_market_dict(market_df, OTHER_CURRENCIES)

    sem = asyncio.Semaphore(5)
    timeout = aiohttp.ClientTimeout(total=60)

    all_rows = []
    tasks = []
    task_batch_size = 5

    pause_every_batches = 5
    pause_seconds = 7.5

    processed_batches = 0
    batches_since_pause = 0

    queries = []
    for destination in IATA_CODES:
        for market, currencies in market_dict.items():
            for currency in currencies:
                queries.append(
                    {
                        "origin": "MOW",
                        "month": "2026-06-01",
                        "destination": destination,
                        "show_to_affiliates": "false",
                        "one_way": "true",
                        "direct": "true",
                        "market": market,
                        "currency": currency,
                    }
                )

    total_queries = len(queries)
    logger.info("Всего запросов: %s", total_queries)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        with tqdm(total=total_queries, desc="Requests", unit="req") as bar:
            for query in queries:
                tasks.append(
                    fetch_tickets(
                        session=session,
                        sem=sem,
                        url=url,
                        headers=headers,
                        query=query,
                        currency_rate=currency_rate,
                        columns=columns,
                    )
                )

                if len(tasks) >= task_batch_size:
                    logger.info(
                        "Запуск батча: %s задач | всего строк: %s | всего батчей: %s | с последней паузы батчей: %s",
                        len(tasks),
                        len(all_rows),
                        processed_batches,
                        batches_since_pause,
                    )

                    results = await asyncio.gather(*tasks)
                    bar.update(len(tasks))
                    tasks = []

                    batch_rows = [row for batch in results for row in batch]
                    all_rows.extend(batch_rows)

                    processed_batches += 1
                    batches_since_pause += 1

                    logger.info(
                        "Батч завершен | всего строк: %s | всего батчей: %s | с последней паузы батчей: %s",
                        len(all_rows),
                        processed_batches,
                        batches_since_pause,
                    )

                    if batches_since_pause >= pause_every_batches:
                        logger.warning(
                            "Пауза %s сек, причина: с последней паузы обработано батчей: %s",
                            pause_seconds,
                            batches_since_pause
                        )
                        await asyncio.sleep(pause_seconds)
                        batches_since_pause = 0

                        logger.info("Счётчики после паузы сброшены")

            if tasks:
                logger.info("Запуск финального батча: %s задач", len(tasks))
                results = await asyncio.gather(*tasks)
                bar.update(len(tasks))

                batch_rows = [row for batch in results for row in batch]
                all_rows.extend(batch_rows)

                processed_batches += 1
                batches_since_pause += 1

                logger.info(
                    "Финальный батч завершен | добавлено строк: %s | всего строк: %s | всего батчей: %s | с последней паузы батчей: %s",
                    len(batch_rows),
                    len(all_rows),
                    processed_batches,
                    batches_since_pause,
                )

                if batches_since_pause >= pause_every_batches:
                    logger.warning(
                        "Пауза %s сек, причина: с последней паузы обработано батчей: %s",
                        pause_seconds,
                        batches_since_pause
                    )
                    await asyncio.sleep(pause_seconds)

                    batches_since_pause = 0

                    logger.info("Счётчики после паузы сброшены")

    df_tickets = pd.DataFrame(all_rows)
    df_tickets.to_csv("SMADIMO-GP-2/data/_api/tickets.csv", index=False)

    logger.info("Файл сохранен")
    logger.info("Итоговое количество строк: %s", len(df_tickets))


if __name__ == "__main__":
    asyncio.run(main())
