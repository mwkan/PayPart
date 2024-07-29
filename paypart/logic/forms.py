from django import forms


class SplitForm(forms.Form):
    num_people = forms.IntegerField(min_value=1, label='Number of people splitting payment')

class SplitChoiceForm(forms.Form):
    SPLIT_CHOICES = [
        ('even', 'Even Split'),
        ('custom', 'Custom Split'),
    ]
    split_type = forms.ChoiceField(choices=SPLIT_CHOICES, widget=forms.RadioSelect)
