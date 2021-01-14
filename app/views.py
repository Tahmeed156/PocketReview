import os
from random import choice, sample
import requests
import datetime 

from django.shortcuts import render, redirect
from django.core.cache import cache
from django.contrib import messages


def index(request):

  if request.session.get('token') is None:
    return redirect('auth-user')

  tag_name = request.POST.get('tag_name', '')
  print(tag_name)

  if request.POST.get('type') == 'random':
    if tag_name == '':
      return redirect('random')
    else:
      return redirect('random', tag_name=tag_name)
  elif request.POST.get('type') == 'refresh':
    refresh(request.session.get('token'), tag_name)
    messages.info(request, 'article list has been updated!')
  elif request.POST.get('type') == 'logout':
    return redirect('auth-user')
  else:
    pass

  COUNT = 5

  key_name = request.session.get('token') + '$' + tag_name

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

  if request.session.get('token') is None:
    return redirect('auth-user')

  key_name = request.session.get('token') + '$' + tag_name

  if cache.get(key_name):
    article_list = cache.get(key_name)
  else:
    article_list = []

  if article_list == []:
    return redirect('/')

  article = choice(list(article_list.values()))
  return redirect(article['given_url'], permanent=True)


def auth_user(request):
  
  if os.environ.get('DJANGO_DEBUG'):
    redirect_uri = 'http://localhost:8000/auth/app/'
  else:
    redirect_uri = 'https://pocket-review.herokuapp.com/auth/app/'

  request_token_link = f"https://getpocket.com/v3/oauth/request?consumer_key={os.environ.get('CONSUMER_KEY')}&redirect_uri={redirect_uri}"
  response = requests.get(request_token_link)
  
  request_token = response.text.split('=')[1]
  request.session['token'] = request_token
  redirect_user_link = f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={redirect_uri}"

  return redirect(redirect_user_link)


def auth_app(request):
  
  request_token_link = f"https://getpocket.com/v3/oauth/authorize?consumer_key={os.environ.get('CONSUMER_KEY')}&code={request.session.get('token')}"
  response = requests.get(request_token_link).text.split('&')
  
  request.session['username'] = response[1].split('=')[1]
  request.session['token'] = response[0].split('=')[1]
  messages.info(request, f"Login Successful! Welcome {request.session['username']}.")

  refresh(request.session.get('token'))

  return redirect('home')


# ============== HELPERS =============


def refresh(token, tag_name=''):

    ACCESS_TOKEN = token
    CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    key_name = token + '$' + tag_name

    archive_link = f'https://getpocket.com/v3/get?consumer_key={CONSUMER_KEY}&access_token={ACCESS_TOKEN}&state=archive&tag={tag_name}'
    response = requests.get(archive_link)
    article_list = response.json()['list']
    cache.set(key_name, article_list)
