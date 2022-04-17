#!/usr/bin/env python3.10
"""Scrapes all entries from all Bizztro pages and saves them to csv

'asyncio' is not used to avoid triggering possible bot protection. It is possible to try asyncio later if speed will
be important.
'dataclasses' are not used, would be overkill
"""

from bs4 import BeautifulSoup
import csv
import pathlib
import logging
import requests
import time

# local modules
import data_checker


class Scraper:
    def __init__(self):
        self.csv_writer = None

    @staticmethod
    def get_parsed_page(url):
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')


class BizztroScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.url_base = 'https://www.bizztreat.com/bizztro?p1400='
        self.output = 'mnamky.csv'

    def scrape(self):
        page_1 = self.get_page_by_number(1)
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

    def get_page_by_number(self, page_number):
        return self.get_parsed_page(''.join([self.url_base, str(page_number)]))

    def extract_from_pages(self, start, end):
        for i in range(start, end):
            logging.info(f'{time.asctime()}:running')
            page = self.get_page_by_number(i)
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
    logging.info(f'Data was saved to {pathlib.Path(__file__).parent / scraper.output}')

