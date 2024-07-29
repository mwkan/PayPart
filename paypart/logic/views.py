from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from . import forms


def start_payment_process(request):
    total_amount = 2000.0
    if request.method == 'POST':
        split_form = forms.SplitForm(request.POST, prefix='split')
        split_choice_form = forms.SplitChoiceForm(request.POST, prefix='choice')

        if split_form.is_valid():
            num_people = split_form.cleaned_data['num_people']
            request.session['total_amount'] = total_amount
            request.session['num_people'] = num_people

        if split_choice_form.is_valid():
            split_type = split_choice_form.cleaned_data['split_type']
            if split_type == 'even':
                return redirect('even_split')
            elif split_type == 'custom':
                return redirect('custom_split')

    else:
        split_form = forms.SplitForm(prefix='split')
        split_choice_form = forms.SplitChoiceForm(prefix='choice')

    return render(request, 'logic/start_payment_process.html', {
        'split_form': split_form,
        'split_choice_form': split_choice_form,
        'total_amount': total_amount
    })


def choose_split(request):
    if request.method == 'POST':
        form = forms.SplitChoiceForm(request.POST)
        if form.is_valid():
            split_type = form.cleaned_data['split_type']
            if split_type == 'even':
                return redirect('even_split')
            elif split_type == 'custom':
                return redirect('custom_split')
    else:
        form = forms.SplitChoiceForm()
    return render(request, 'logic/start_payment_process.html', {'form1': form})


def even_split(request):
    total_amount = request.session.get('total_amount')
    num_people = request.session.get('num_people')
    if total_amount and num_people:
        amount_per_person = total_amount / num_people
        request.session['split_amount'] = {'amount_per_person': amount_per_person}
        return render(request, 'logic/even_split.html', {'amount_per_person': amount_per_person})
    return redirect('start_payment_process')


def custom_split(request):
    num_people = request.session.get('num_people')
    if request.method == 'POST':
        # handle custom split data
        # save and process custom split data
        return redirect('confirm_emails')
    else:
        return render(request, 'logic/custom_split.html', {'num_people': num_people})


def get_username(request):
    return  # username


def process_payments(request):  # MWK
    # calling all the stages of the API and iterate through each username to do it for each person
    return  # true or false


def holding_page(request):
    # hold time for 10mins
    return


def success_page(request):
    return
