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

for page in range(0, int(the_last_page)+1):
    url = f'http://bgaek.by/page/{page}/'
    response_news = requests.get(url, headers=headers)
    soup_news = BeautifulSoup(response_news.text, 'lxml')

    news_post = soup_news.findAll('div', class_='post-column clearfix')

    for post in news_post:
        images = post.findAll('img', class_='attachment-post-thumbnail size-post-thumbnail wp-post-image')
        for img in images:
            if img.has_attr('src'):
                posts_images = img['src']
        if post.find('h2', class_='entry-title'):
            posts_title = post.find('h2', class_='entry-title').text
        posts_date = post.find('span', class_='meta-date').text
        posts_descriptions = post.find('div', class_='entry-content entry-excerpt clearfix').text

        data.append([posts_images, posts_title, posts_date, posts_descriptions])

header = ['posts_images', 'posts_title', 'posts_date', 'posts_descriptions']

df = pd.DataFrame(data, columns=header)
result = df.to_json('/Users/vaniakazeko/Desktop/bgaek/back/news_parser/news.json', orient='index', force_ascii=False, indent=4)
