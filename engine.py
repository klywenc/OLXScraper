import os
import requests
from lxml import html
import re
from collections import Counter
import asyncio
from concurrent.futures import ProcessPoolExecutor
from urllib.parse import urljoin
import redis
import json
import pika

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='scrape_task_queue', durable=True)


async def download_olx_page(page_num, keyword):
    filename = f'pages/olx_{keyword}_page_{page_num}.html'

    if os.path.exists(filename):
        print(f"Plik {filename} istnieje")
        return

    url = f"https://www.olx.pl/oferty/q-{keyword}/?page={page_num}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Zjebales cos {url}")
        return

    with open(filename, 'wb') as f:
        f.write(response.content)

    print(f"Saved: {filename}")


async def download_olx_pages(keyword, num_pages=10):
    if not os.path.exists('pages'):
        os.makedirs('pages')

    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(executor, download_olx_page, page_num, keyword) for page_num in
                 range(1, num_pages + 1)]
        await asyncio.gather(*tasks)


def scrape_olx(filename):
    if filename != 'pages/concatenated.html':
        return

    if filename is None:
        return

    tree = html.parse(filename)

    prices = tree.xpath('//p[@data-testid="ad-price"]/text()')

    if not prices:
        print("Not found.")
        return

    prices = [int(''.join(re.findall(r'\d+', price))) for price in prices if re.search(r'\d+', price)]

    if not prices:
        print("Cooked.")
        return

    lowest_price = min(prices)

    price_counter = Counter(prices)
    most_common_price, most_common_count = price_counter.most_common(1)[0]

    most_common_price_links = []
    for i, price in enumerate(prices):
        if price == most_common_price:
            link = tree.xpath(f'(//a[@class="linkWithHash"]/@href)[{i + 1}]')
            if link:
                most_common_price_links.extend(link)

    first_offer_links = tree.xpath('//a[@class="linkWithHash"]/@href')
    first_offer_link = first_offer_links[0] if first_offer_links else "Brak dostępnych ofert"

    data = {
        'average_price': sum(prices) / len(prices),
        'lowest_price': lowest_price,
        'most_common_price': most_common_price,
        'most_common_count': most_common_count,
        'most_common_price_links': ', '.join(
            most_common_price_links) if most_common_price_links else 'Brak dostępnych ofert',
        'first_offer_link': first_offer_link
    }
    serialized_data = json.dumps(data)

    redis_db.hset("scraped", filename, serialized_data)

    print(f"Results {filename}:")
    print(f"Srednia: {sum(prices) / len(prices)} zł")
    print(f"Lowesr: {lowest_price} zł")
    print(f"najczestsza: {most_common_price} zł (wystąpiła {most_common_count} razy)")


async def concatenate_and_scrape(keyword, num_pages=10):
    if not os.path.exists('pages'):
        os.makedirs('pages')

    html_files = []

    for page_num in range(1, num_pages + 1):
        filename = f'pages/olx_{keyword}_page_{page_num}.html'
        if os.path.exists(filename):
            html_files.append(filename)
        else:
            await download_olx_page(page_num, keyword)
            html_files.append(filename)

    concatenated_html = ''
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            concatenated_html += f.read()

    with open('pages/concatenated.html', 'w', encoding='utf-8') as f:
        f.write(concatenated_html)

    scrape_olx('pages/concatenated.html')

    os.remove('pages/concatenated.html')


async def callback(ch, method, properties, body):
    print("Received message")
    data = json.loads(body)
    keyword = data.get('keyword')
    num_pages = data.get('num_pages')
    if num_pages:
        num_pages = int(num_pages)
    await concatenate_and_scrape(keyword, num_pages)

def callback_blocking(ch, method, properties, body):
    asyncio.run(callback(ch, method, properties, body))


channel.basic_consume(queue='scrape_task_queue', on_message_callback=callback_blocking, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
