import os
from random import choice, sample
import requests
import datetime 
from functools import lru_cache

from django.shortcuts import render, redirect
from django.core.cache import cache
from django.contrib import messages


def index(request):

    tag_name = request.POST.get('tag_name', '')
    print(tag_name)

    if request.POST.get('type') == 'random':
      if tag_name == '':
        return redirect('random')
      else:
        return redirect('random', tag_name=tag_name)
    elif request.POST.get('type') == 'refresh':
      refresh(tag_name)
      messages.info(request, 'article list has been updated!')
    else:
      pass

    COUNT = 5

    key_name = os.environ.get('ACCESS_TOKEN') + '$' + tag_name

    if cache.get(key_name):
      article_list = cache.get(key_name)
    else:
      article_list = []
    
    articles = []
    if article_list == []:
      messages.info(request, 'hit refresh to update articles & make sure you\'re using a correct tag')
      return render(request, 'index.html', {'articles': [], 'tag_name': tag_name})

    for article in sample(list(article_list.values()), COUNT):
      articles.append({
        'item_id': article['item_id'],
        'given_title': article['given_title'],
        'given_url': article['given_url'],
        'time_added': datetime.datetime.fromtimestamp(int(article['time_added'])).strftime('%d/%m/%Y'),
        'excerpt': article['excerpt'],
        'time_to_read': article.get('time_to_read', '?')
      })

    return render(request, 'index.html', {
      'articles': articles,
      'tag_name': tag_name
    })


def random(request, tag_name=''):

    key_name = os.environ.get('ACCESS_TOKEN') + '$' + tag_name

    if cache.get(key_name):
      article_list = cache.get(key_name)
    else:
      article_list = []

    if article_list == []:
      return redirect('/')

    article = choice(list(article_list.values()))
    return redirect(article['given_url'], permanent=True)

# ============== HELPERS =============


def refresh(tag_name=''):

    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    key_name = os.environ.get('ACCESS_TOKEN') + '$' + tag_name

    archive_link = f'https://getpocket.com/v3/get?consumer_key={CONSUMER_KEY}&access_token={ACCESS_TOKEN}&state=archive&tag={tag_name}'
    response = requests.get(archive_link)
    article_list = response.json()['list']
    cache.set(key_name, article_list)
