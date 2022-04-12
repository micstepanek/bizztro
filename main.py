#!/usr/bin/env python3.10

from bs4 import BeautifulSoup
import csv
import logging
import requests
import time

# local module
import data_checker

"""
Scrapes all entries from all Bizztro pages and saves them to csv

'asyncio' is not used to avoid triggering possible bot protection. It is possible to try asyncio later if speed will
be important.
'dataclasses' are not used, would be overkill
"""


class BizztroScraper:
    def __init__(self):
        self.url_base = 'https://www.bizztreat.com/bizztro?p1400='
        self.output = 'mnamky.csv'
        self.csv_writer = None

    def scrape(self):
        page_1 = self.get_parsed_page(1)
        page_count = int(self.get_page_count(page_1))
        with open(self.output, 'w') as csv_file:
            self.csv_writer = csv.writer(csv_file)
            # this file is open for the whole run of the scraper.scrape()
            # it may be reworked to save some RAM and lose some speed
            self.name_columns_in_csv()
            self.extract_from_pages(1, page_count + 1)

    @staticmethod
    def get_page_count(page):
        page_count = int(page.find_all(class_='pagination-link')[-1].get_text())
        logging.info(f'pages to process synchronously: {page_count}')
        return page_count

    def get_parsed_page(self, page_number):
        response = requests.get(''.join([self.url_base, str(page_number)]))
        return BeautifulSoup(response.text, 'html.parser')

    def extract_from_pages(self, start, end):
        for i in range(start, end):
            logging.info(f'{time.asctime()}:running')
            page = self.get_parsed_page(i)
            entries = page.find_all(class_='entry-inner')
            for entry in entries:
                self.extract_entry(entry)

    def extract_entry(self, entry):
        logging.debug(entry)
        heading_element = entry.find(['h2', 'h3', 'h4', 'h5', 'h6'])
        # this might be slightly more future-proof than
        # heading_element = entry.find(class_='entry-title')
        title = heading_element.get_text().strip()
        summary = entry.find('p').get_text().strip()
        url = heading_element.find('a')['href']
        try:
            # last link is to a big image, which I wanted
            img_url = entry.find('img')['data-srcset'].rsplit(' ', 2)[-2]
        except KeyError:
            img_url = entry.find('img')['src']
        self.csv_writer.writerow([title, summary, url, img_url])

    def name_columns_in_csv(self):
        self.csv_writer.writerow(['title', 'summary', 'url', 'img_url'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper = BizztroScraper()
    scraper.scrape()
    data_checker.check(scraper.output)

