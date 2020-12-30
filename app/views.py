from django.shortcuts import render
import requests


def index(request):

    ACCESS_TOKEN = ''
    CONSUMER_KEY = ''
    COUNT = 5

    response = requests.get(f'https://getpocket.com/v3/get?consumer_key={CONSUMER_KEY}&access_token={ACCESS_TOKEN}&state=archive&count={COUNT}')
    article_list = response.json()['list']
    
    articles = []
    for article in article_list.values():
      articles.append(article['given_title'])

    return render(request, 'index.html', {'articles': articles})
