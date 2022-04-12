import csv
import logging

image_extensions = ('.png', '.jpg', '.jpeg')
page_extensions = ('.html', '.htm', '.asp', '.aspx')


def check(file_name):
    with open(file_name, 'r') as csv_file:
        # this file is open for the whole run of the scraper.scrape()
        # it may be reworked to save some RAM and lose some speed
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            check_row(row)


def check_row(row):
    if 'Mňamk' not in row['title']:
        logging.warning(f'"Mňamk" not in title: {row["title"]}')
    if len(row['summary']) < 100:
        logging.warning(f'Seems too short for summary: {row["summary"]}')
    if not row['url'].startswith('http'):
        logging.warning(f'Url is not starting with http: {row["url"]}')
    if '.' in row['url'].rsplit('/', 1)[-1]:
        if not row['url'].endswith(page_extensions):
            logging.warning(f'Period in last part of url: {row["url"]}')
    if not row['img_url'].endswith(image_extensions):
        logging.warning(f'Image url is not ending with {" or ".join(image_extensions)}: {row["img_url"]}')


if __name__ == '__main__':
    check('mnamky.csv')

