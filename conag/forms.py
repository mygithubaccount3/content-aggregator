from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100, required=False, error_messages={'max_length': 'Max query length: 100'},
                            widget=forms.TextInput(attrs={'class': 'form-control me-2', 'type': 'search', 'placeholder': 'Search', 'aria-label': 'Search', 'style': 'width: 44%'}))
                            
    page = forms.IntegerField(max_value=50, min_value=1, required=False)
