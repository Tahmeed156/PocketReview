from django.shortcuts import render, redirect
import os
from random import choice
import requests
import datetime 
from functools import lru_cache

def index(request):

    # TODO paginate or allow count selection

    print(request.POST)

    tag_name = request.POST.get('tag_name', '')

    if request.POST.get('random'):
      return redirect ('random', tag_name=tag_name)

    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    COUNT = 5

    archive_link = f'https://getpocket.com/v3/get?consumer_key={CONSUMER_KEY}&access_token={ACCESS_TOKEN}&state=archive&count={COUNT}&tag={tag_name}'

    response = requests.get(archive_link)
    article_list = response.json()['list']
    
    articles = []
    if article_list == []:
      return render(request, 'index.html', {'articles': []})

    for article in article_list.values():
      articles.append({
        'item_id': article['item_id'],
        'given_title': article['given_title'],
        'given_url': article['given_url'],
        'time_added': datetime.datetime.fromtimestamp(int(article['time_added'])).strftime('%d/%m/%Y'),
        'excerpt': article['excerpt'],
        'time_to_read': article['time_to_read']
      })

    return render(request, 'index.html', {
      'articles': articles,
      'tag_name': tag_name
    })

@lru_cache
def random(request, tag_name=''):

    # TODO add caching
    # TODO refresh list

    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')

    archive_link = f'https://getpocket.com/v3/get?consumer_key={CONSUMER_KEY}&access_token={ACCESS_TOKEN}&state=archive&tag={tag_name}'

    response = requests.get(archive_link)
    article_list = response.json()['list']
    
    try:
      article = choice(list(article_list.values()))
      return redirect(article['given_url'], permanent=True)
    except AttributeError:
      return redirect('/')