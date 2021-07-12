import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import mysql.connector

dawn_r1 = requests.get('https://www.dawn.com/trends/coronavirus')
coverpage_dawn = dawn_r1.content
soap_dawn = BeautifulSoup(coverpage_dawn,'html5lib')
all_cover_articles = soap_dawn.find_all('h2',{'data-layout':'story'})

#scrap only 5 articles
number_of_articles = 5

#empty list
title_dawn = []
author_dawn = []
links_dawn = []
articles_dawn = []
all_publish_date = []

for n in np.arange(0,number_of_articles):
    #getting the links
    link = all_cover_articles[n].find('a')['href']
    links_dawn.append(link)

    #getting the tiles
    title = all_cover_articles[n].find('a').get_text()
    title_dawn.append(title)

    #go to inside the detail view of news
    article = requests.get(link)
    coverpage_sub_articles = article.content
    soap_sub_article = BeautifulSoup(coverpage_sub_articles, 'html5lib')
    body = soap_sub_article.find_all('div', class_='story__content')
    x = body[0].find_all('p')

    # Unifying the paragraphs
    list_paragraphs = []
    for p in np.arange(0, len(x)):
        paragraph = x[p].get_text()
        list_paragraphs.append(paragraph)
        final_article = " ".join(list_paragraphs)

    articles_dawn.append(final_article)

    #extract author name
    author_baseline = soap_sub_article.find_all('span', class_='story__byline')
    author_dawn.append(author_baseline[0].get_text())

    #publish date
    date_publish_baseline = soap_sub_article.find_all('span', class_='timestamp--date')
    all_publish_date.append(date_publish_baseline[0].get_text())

    # saving data to Mysql Database
    db = mysql.connector.connect(user="root", database="research_ms")
    cursor = db.cursor()

    add_news = ("INSERT INTO covid_articles"
                "(news_title, links, author, publish_date, article,source) "
                "VALUES (%s, %s, %s, %s, %s , %s)")
    data_news = (title, link, author_baseline[0].get_text(), date_publish_baseline[0].get_text(), final_article, 'Dawn')

    #insertion
    cursor.execute(add_news,data_news)

    db.commit()
    cursor.close()
    db.close()

# For export to csv uncomment the below code
#dictionary = {'title':title_dawn , 'links':links_dawn , 'author':author_dawn, 'article':articles_dawn , 'publish_date':all_publish_date,'source':'dawn'}
#df = pd.DataFrame (dictionary)
#to_csv = df.to_csv ('C:/Users/smile/Desktop/dawn_news_data.csv')


