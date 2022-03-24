from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label='',
                            max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control me-2', 'type': 'search', 'placeholder': 'Search', 'aria-label': 'Search', 'style': 'width: 44%'}))
