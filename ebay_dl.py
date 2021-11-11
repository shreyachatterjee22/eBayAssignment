import argparse
from typing import Text
import requests
from bs4 import BeautifulSoup
import json 
import csv

def parse_itemssold(text):
    numbers =''
    for char in text:
        if char in '1234567890':
            numbers += char
    if 'sold' in text:
        return int(numbers)
    else:
        return 0

def parse_price(text):
    numbers = ''
    price = ''
    dollar_index = text.find('$')
    space_index = text.find(' ')
    if dollar_index == -1:
        return 0
    if space_index != -1:
        price_text = text[dollar_index:space_index]
    else:
        price_text = text[dollar_index:]
    for char in price_text:
        if char in '1234567890':
            numbers += char
    return int(numbers)



parser = argparse.ArgumentParser(description='download information from ebay and convert to jsaon')
parser.add_argument('search_term')
parser.add_argument('--num_pages', default=10)
args = parser.parse_args()
print('args.search_term = ', args.search_term)

items =[]
for page_number in range(1, int(args.num_pages)+1):
    url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw='
    url += args.search_term
    url += '&_sacat=0&_pgn='
    url += str(page_number)
    url += '&rt=nc'
    print ('url = ', url)
    
    r = requests.get(url)
    status = r.status_code
    print('status = ', status)
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')

    tags_items = soup.select('.s-item')
    for tag_item in tags_items:

        tags_name = tag_item.select('.s-item__title')
        name = None
        for tag in tags_name:
            status = tag.text
        
        tags_status = tag_item.select('.SECONDARY_INFO')
        status = None
        for tag in tags_status:
            status = tag.text
        
        price_sold = None
        tags_price = tag_item.select('.s-item__price')
        for tag in tags_price:
            price_sold = parse_price(tag.text)
        
        freereturns = False
        tags_freereturns = tag_item.select('.s-item__free-returns')
        for tag in tags_freereturns:
            freereturns = True

        items_sold = None
        tags_itemssold = tag_item.select('.s-item__hotness')
        for tag in tags_itemssold:
            items_sold = parse_itemssold(tag.text)

        shipping = 0
        tags_shipping = tag_item.select('.s-item__shipping')
        for tag in tags_shipping:
            shipping = parse_price(tag.text)
        
        item = {
            'name' : name,
            'freereturns' : freereturns,
            'status' : status,
            'price' : price_sold,
            'items_sold' : items_sold,
            'shipping' : shipping
        }
        items.append(item)

    print('len(tag_items) = ', (len(tags_items)))
    print('len(items) = ', (len(items)))

    filename = args.search_term + '.json'
    with open(filename, 'w', encoding = 'ascii') as f:
        f.write(json.dumps(items))
