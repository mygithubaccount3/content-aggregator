from datetime import datetime
from typing import Any, Dict
from django.shortcuts import render
from django.core.paginator import InvalidPage
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .forms import SearchForm


class IndexView(TemplateView):
    template_name = 'conag/greeting.html'
    http_method_names = ['get']

    def http_method_not_allowed(self, request):
        message = 'Request method not allowed. Allowed methods: '

        for method in self.http_method_names:
            message += f'{method.upper()} '

        return render(request, 'conag/method_not_allowed.html', {'message': message})


class BbcView(ListView):
    template_name = 'conag/index.html'
    http_method_names = ['get']
    form_class = SearchForm
    paginate_by = 10
    context_object_name = 'articles'

    def get_queryset(self):
        form = self.form_class(self.request.GET)

        if form.is_valid():
            soup = self.__get_bs4_instance('https://bbc.com/sport', 'lxml')
            sport_news_html_tags = soup.select('ul > li > div > div > div')
            del sport_news_html_tags[-25:]

            articles = form.search(sport_news_html_tags, 'bbc')

            if 'query' in self.request.GET:
                self.__log(form.cleaned_data.get('query'))

            return articles

        return []

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(
            page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page)
        except ValueError:
            page_number = 1

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            page_number = paginator.num_pages
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)

        return context

    def http_method_not_allowed(self, request):
        message = 'Request method not allowed. Allowed methods: '

        for method in self.http_method_names:
            message += f'{method.upper()} '

        return render(request, 'conag/method_not_allowed.html', {'message': message})

    def __get_bs4_instance(self, html_document: str, parser: str) -> BeautifulSoup:
        response = requests.get(html_document)
        return BeautifulSoup(response.text, parser)

    def __log(self, message):
        with open('./logs.txt', 'a') as file:
            file.write(
                f"[{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}] {message}\n")


class CnnView(ListView):
    template_name = 'conag/index.html'
    http_method_names = ['get']
    form_class = SearchForm
    paginate_by = 10
    context_object_name = 'articles'

    def get_queryset(self):
        form = self.form_class(self.request.GET)

        if form.is_valid():
            service = Service(
                executable_path=ChromeDriverManager().install())
            browser = webdriver.Chrome(service=service)
            browser.get("https://edition.cnn.com/health")
            html = browser.page_source

            soup = BeautifulSoup(html, 'lxml')
            tags = soup.find(
                'h2', string='Latest').find_next_siblings('li')

            articles = form.search(tags, 'cnn')
            return articles

        return []

    def paginate_queryset(self, queryset, page_size):
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(
            page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page)
        except ValueError:
            page_number = 1

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
            page_number = paginator.num_pages
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(self.request.GET)

        return context

    def http_method_not_allowed(self, request):
        message = 'Request method not allowed. Allowed methods: '

        for method in self.http_method_names:
            message += f'{method.upper()} '
        return render(request, 'conag/method_not_allowed.html', {'message': message})
