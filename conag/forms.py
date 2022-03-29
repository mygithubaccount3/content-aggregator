from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=False, error_messages={'max_length': 'Max query length: 100'},
                            widget=forms.TextInput(attrs={'class': 'form-control me-2', 'type': 'search', 'placeholder': 'Search', 'aria-label': 'Search', 'style': 'width: 44%'}))

    page = forms.IntegerField(max_value=50, min_value=1, required=False)

    def search(self, sport_news_html_tags):
        articles = []

        for tag in sport_news_html_tags:
            article = {
                'title': '',
                'summary': '',
                'tag': '',
                'time': ''
            }
            article_title_tag = tag.select_one(
                '.gs-c-promo-heading__title')
            article_summary_tag = tag.select_one('.gs-c-promo-summary')
            article_tag_tag = tag.select_one('.qa-section-tag a')
            article_time_tag = tag.select_one('.gs-u-vh')

            
            if article_title_tag is not None:
                if ((self.cleaned_data.get('query') in article_title_tag.get_text())):
                    article.update(title=article_title_tag.get_text())
                else:
                    continue
            else:
                continue

            if article_summary_tag is not None:
                if ((self.cleaned_data.get('query') in article_summary_tag.get_text())):
                    article.update(summary=article_summary_tag.get_text())

            if article_tag_tag is not None:
                article.update(tag=article_tag_tag.get_text())

            if article_time_tag is not None and 'ago' in article_time_tag.get_text():
                article.update(time=article_time_tag.get_text())

            articles.append(article)

        return articles
