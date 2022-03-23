import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .forms import SearchForm


def get_bs4_instance(html_document: str, parser: str) -> BeautifulSoup:
    response = requests.get(html_document)
    return BeautifulSoup(response.text, parser)


def bbc(request, page=1):
    if request.GET.get('page') or page:
        articles = []
        page_obj = {}
        form = SearchForm(request.GET)
        is_form_valid = form.is_valid()
        cleaned_query = form.cleaned_data.get('query')
        soup = get_bs4_instance('https://bbc.com/sport', 'lxml')
        sport_news_html_tags = soup.select('.gs-c-promo-body')
        del sport_news_html_tags[-25:]

        for tag in sport_news_html_tags:
            article = {
                'title': '',
                'summary': '',
                'tag': '',
                'time': ''
            }
            article_title_tag = tag.select_one('.gs-c-promo-heading__title')
            article_summary_tag = tag.select_one('.gs-c-promo-summary')
            article_tag_tag = tag.select_one('.qa-section-tag a')
            article_time_tag = tag.select_one('.gs-u-vh')

            if article_title_tag is not None:
                if ((is_form_valid and cleaned_query in article_title_tag.get_text())):
                    article.update(title=article_title_tag.get_text())
                else:
                    continue
            else:
                continue

            if article_summary_tag is not None:
                if ((cleaned_query in article_summary_tag.get_text())):
                    article.update(summary=article_summary_tag.get_text())

            if article_tag_tag is not None:
                article.update(tag=article_tag_tag.get_text())

            if article_time_tag is not None and 'ago' in article_time_tag.get_text():
                article.update(time=article_time_tag.get_text())

            articles.append(article)

        paginator = Paginator(articles, 10)
        page_number = request.GET.get('page') or page #escape GET
        page_obj = paginator.get_page(page_number)

        return render(request, 'conag/index.html', {'page_obj': page_obj, 'form': form})
    else:
        return redirect('conag:bbc', permanent=True, page=1)


def cnn(request):
    articles = []
    service = Service(executable_path=ChromeDriverManager().install())
    # chrome_options = webdriver.ChromeOptions()
    # # chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(service=service)

    # browser.set_window_size(950, 800)

    browser.get("https://edition.cnn.com/health")
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.find('h2', string='Latest').find_next_siblings('li')

    for tag in tags:
        articles.append(tag.find_next(
            'span', class_='cd__headline-text').get_text())

    # browser.close()
    # driver.quit()

    return render(request, 'conag/index.html', {'articles': articles})
