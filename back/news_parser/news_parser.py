import sqlite3

import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    'Host': 'bgaek.by',
    'User-Agent': 'Safari',
    'Accept': '*/*',
    'Accept_encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
data = []
the_last_page = []

url_pagination = 'http://bgaek.by/'
pagination_response = requests.get(url_pagination, headers=headers)
pagination_soup = BeautifulSoup(pagination_response.text, 'lxml')

pages = []
pagination = pagination_soup.find('div', class_='nav-links').findAll('a', class_='page-numbers')

for page in pagination:
    pages.append(page.text)

the_last_page = pages[-2]

for page in range(0, 11):
    url = f'http://bgaek.by/page/{page}/'
    response_news = requests.get(url, headers=headers)
    soup_news = BeautifulSoup(response_news.text, 'lxml')

    news_post = soup_news.findAll('div', class_='post-column clearfix')

    for post in news_post:
        descriptions = post.find('div', class_='entry-content entry-excerpt clearfix').text
        result = [string.replace('\n', ' ') for string in descriptions]
        posts_descriptions_list = list(filter(None, result))
        posts_descriptions_str = ''.join(posts_descriptions_list)
        if posts_descriptions_str != ' ':
            images = post.findAll('img', class_='attachment-post-thumbnail size-post-thumbnail wp-post-image')
            for img in images:
                if img.has_attr('src'):
                    posts_images = img['src']
            if post.find('h2', class_='entry-title'):
                posts_title = post.find('h2', class_='entry-title').text
            posts_date = post.find('span', class_='meta-date').text
            posts_descriptions = ''.join(posts_descriptions_list)

            data.append([posts_images, posts_title, posts_date, posts_descriptions])

        db = sqlite3.connect('db.db')
        sql = db.cursor()

        sql.execute("""CREATE TABLE IF NOT EXISTS news (
            posts_images BLOB,
            posts_title TEXT,
            posts_date TEXT,
            posts_descriptions TEXT 
        )""")

        db.commit()

        sql.execute(f'INSERT INTO news VALUES (?, ?, ?, ?)',
                    (posts_images, posts_title, posts_date, posts_descriptions))
        db.commit()

        for value in sql.execute('SELECT * FROM news'):
            print(value)

header = ['posts_images', 'posts_title', 'posts_date', 'posts_descriptions']

df = pd.DataFrame(data, columns=header)
result = df.to_json('/Users/vaniakazeko/Desktop/bgaek/back/news_parser/news.json', orient='index', force_ascii=False,
                    indent=4)
