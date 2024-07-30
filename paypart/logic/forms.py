from django import forms


class SplitForm(forms.Form):
    num_people = forms.IntegerField(min_value=1, label='Number of people splitting payment')


class SplitChoiceForm(forms.Form):
    SPLIT_CHOICES = [
        ('even', 'Split Evenly'),
        ('custom', 'Split by Custom Amount'),
    ]
    split_type = forms.ChoiceField(choices=SPLIT_CHOICES, widget=forms.RadioSelect)


class UsernameForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    amount = forms.DecimalField(label='Amount', required=False, min_value=0)
