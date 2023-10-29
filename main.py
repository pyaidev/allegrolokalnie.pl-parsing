import requests
from bs4 import BeautifulSoup
import time
import json
import random

url = 'https://allegrolokalnie.pl/oferty/dom-i-ogrod'  # Замените на вашу ссылку
page_limit = 1  # Замените на количество страниц, которые вы хотите обработать
base_url = f'{url}?page='
blacklist_file = 'blacklist.txt'
proxy_list = [
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
    '9111.19111.1111.119:12606:5707111991',
]

# Load the existing blacklist
try:
    with open(blacklist_file, 'r') as blacklist:
        blacklist_set = set(line.strip() for line in blacklist)
except FileNotFoundError:
    blacklist_set = set()

all_links = []

for page_number in range(1, page_limit + 1):
    selected_proxy = random.choice(proxy_list)
    print(f'Прокси: 1 {selected_proxy}')
    proxies = {
        'http': selected_proxy,
    }

    response = requests.get(base_url + str(page_number), proxies=proxies)

    if response.status_code == 200:
        print(f'Обработка страницы {page_number}')
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        product_links = soup.find_all("a", class_="mlc-card mlc-itembox")
        if product_links:
            for link in product_links:
                href = link.get("href")
                full_link = f'https://allegrolokalnie.pl{href}'
                if full_link not in blacklist_set:
                    badge = link.find("li", class_="ml-badges__badge")
                    if badge and "Często sprzedaje" in badge.get_text():
                        print(badge)
                        continue  # Skip this element
                    all_links.append(full_link)
                    selected_proxy = random.choice(proxy_list)
                    proxies = {
                        'http': selected_proxy,
                    }
                    print(f'Прокси: 2 {selected_proxy}')
                    product_response = requests.get(full_link, proxies=proxies)
                    if product_response.status_code == 200:
                        product_html = product_response.text
                        product_soup = BeautifulSoup(product_html, 'html.parser')
                        seller_details_section = product_soup.find("section",
                                                                  class_="ml-normalize-section mlc-offer__seller-details")
                        data_attribute = seller_details_section['data-mlc-seller-details']
                        data = json.loads(data_attribute)
                        seller_name = data["seller"]["name"]
                        blacklist_set.add(seller_name)
                    else:
                        print(f'Ошибка при получении страницы товара. Код ответа: {product_response.status_code}')
                else:
                    print(f'Продавец {seller_name} уже в черном списке.')
        else:
            print('Нет ссылок на товары на этой странице.')
    else:
        print(f'Ошибка при получении страницы. Код ответа: {response.status_code}')
    time.sleep(1)

# Save the updated blacklist
with open(blacklist_file, 'w') as blacklist:
    for link in blacklist_set:
        blacklist.write(link + '\n')

# Save all the links
with open('products.txt', 'w') as file:
    for link in all_links:
        file.write(link + '\n')

print(f'Всего товаров: {len(all_links)}')
