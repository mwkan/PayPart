from django import forms


class SplitForm(forms.Form):
    num_people = forms.IntegerField(min_value=1, label='Number of people splitting payment')
