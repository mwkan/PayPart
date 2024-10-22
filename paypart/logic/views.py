import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import forms
from .api import get_access_token, VRP_consent, get_consent, exchange_code_for_token, confirm_funds, submit_payment
import re
import time
from django.contrib import messages
# from django.core.cache import cache
# from time import sleep



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


def even_split(request):
    total_amount = request.session.get('total_amount')
    num_people = request.session.get('num_people')
    if total_amount and num_people:
        amount_per_person = round(total_amount / num_people, 2)
        if request.method == 'POST':
            forms1 = [forms.UsernameForm(request.POST, prefix=str(i)) for i in range(num_people)]
            if all(form.is_valid() for form in forms1):
                usernames = [form.cleaned_data['username'] for form in forms1]
                amounts = [amount_per_person] * num_people
                #save to session
                request.session['usernames'] = usernames
                request.session['amounts'] = amounts
                return redirect('process_payments')
        else:
            forms1 = [forms.UsernameForm(prefix=str(i)) for i in range(num_people)]
        return render(request, 'logic/even_split.html', {
            'forms': forms1,
            'amount_per_person': amount_per_person
        })
    return redirect('start_payment_process')


def custom_split(request):
    num_people = request.session.get('num_people')
    if request.method == 'POST':
        forms2 = [forms.UsernameForm(request.POST, prefix=str(i)) for i in range(num_people)]
        if all(form.is_valid() for form in forms2):
            usernames = [form.cleaned_data['username'] for form in forms2]
            amounts = [float(form.cleaned_data['amount']) for form in forms2]
            request.session['usernames'] = usernames
            request.session['amounts'] = amounts
            # Process usernames and custom amounts
            return redirect('process_payments')  # Or the next step
    else:
        forms2 = [forms.UsernameForm(prefix=str(i)) for i in range(num_people)]
    return render(request, 'logic/custom_split.html', {'forms': forms2})


'''
API Calls

Each call will be done per customer

1. Obtain an access token
a. Expires in 600 (seconds)
b. SUCCESSFUL RESPONSE CODE: 200

2. Create a VRP Consent:
a. here we define how much the payment is for, variable = amount_to_pay_per_user
b. SUCCESSFUL RESPONSE CODE: 201

3. Get customer authorisation:
a. this is where we take the customer inputs, we will use variable = username
b. it will be default approved so we wont model the user approving, it will be forced
c. SUCCESSFUL RESPONSE CODE: 200

4. Exchange Authorisation Code for Access Token Specific to the VRP Request
a. Expires in 600 (seconds)
b. SUCCESSFUL RESPONSE CODE: 200

5. Confirm Customer has Available funds prior to submitting VRP Payment
a. SUCCESSFUL RESPONSE CODE: 201

6. Submit the payment against the VRP Request
a. SUCCESSFUL RESPONSE CODE: 201
'''

def holding_page(request):
    results = request.session.get('payment_results', [])
    if request.method == 'POST':
        time.sleep(300)
        return redirect('start_payment_process')
    return render(request, 'logic/holding_page.html', {'results': results})



def success_page(request):
    results = request.session.get('payment_results', [])
    return render(request, 'logic/success_page.html', {'results': results})

def check_funds_no_payment(usernames, amounts, request):
    print(usernames)
    print(amounts)

    results = []

    for username, amount in zip(usernames, amounts):
        user_result = {'username': username, 'status': 'Pending', 'message': ''}
        try:
            # Obtain access token
            access_token_call = get_access_token(scope="payments")
            access_token_call.raise_for_status()  # raises an httperror for a bad response
            access_token = access_token_call.json().get('access_token')
            if access_token_call.status_code != 200 or not access_token:
                raise ValueError('Access token not found')

            # Request VRP consent
            consent_call = VRP_consent(access_token=access_token, amount_to_pay_per_user=amount)
            consent_call.raise_for_status()
            consent_id = consent_call.json().get('Data', {}).get('ConsentId')
            if consent_call.status_code != 201 or not consent_id:
                raise ValueError('Consent ID not found')

            # Get Consent Authorisation code
            authorization_code = get_consent(authorization="APPROVED", consent_id=consent_id, username=username)
            authorization_code.raise_for_status()
            redirecturi_response = authorization_code.json().get('redirectUri')
            get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
            consent_code = get_code.group(1) if get_code else None
            if authorization_code.status_code != 200 or not consent_code:
                raise ValueError('Consent code not found in URI')

            vrp_exchange = exchange_code_for_token(code=consent_code)
            vrp_exchange.raise_for_status()
            new_access_token = vrp_exchange.json().get('access_token')
            if vrp_exchange.status_code != 200 or not new_access_token:
                raise ValueError('New Access Token not found')

            confirm_funds_call = confirm_funds(access_token=new_access_token, consent_id=consent_id, amount=amount)
            confirm_funds_call.raise_for_status()
            if confirm_funds_call.status_code != 200 or confirm_funds_call.json().get('Data', {}).get(
                    'FundsAvailableResult', {}).get('FundsAvailable') != 'Available':
                raise ValueError('Funds not available')

            user_result['status'] = 'Success'

        except AttributeError:
            user_result['status'] = 'Failed'
            user_result['message'] = 'Username not found'

        except (requests.HTTPError, ValueError) as e:
            user_result['status'] = 'Failed'
            user_result['message'] = str(e)

        results.append(user_result)

    #stores results in the session
    request.session['payment_results'] = results

    #check for any failed payments
    if any(result['status'] == 'Failed' for result in results):
        return redirect('holding_page')
    return process_payments(usernames, amounts, request)

def process_payments(usernames, amounts, request):
    print(usernames)
    print(amounts)

    results = []
    for username, amount in zip(usernames, amounts):
        user_result = {'username': username, 'status': 'Pending', 'message': ''}

        try:
            # Obtain access token
            access_token_call = get_access_token(scope="payments")
            access_token_call.raise_for_status()  # raises an httperror for a bad response
            access_token = access_token_call.json().get('access_token')
            if access_token_call.status_code != 200 or not access_token:
                raise ValueError('Access token not found')

            # Request VRP consent
            consent_call = VRP_consent(access_token=access_token, amount_to_pay_per_user=amount)
            consent_call.raise_for_status()
            consent_id = consent_call.json().get('Data', {}).get('ConsentId')
            if consent_call.status_code != 201 or not consent_id:
                raise ValueError('Consent ID not found')

            # Get Consent Authorisation code
            authorization_code = get_consent(authorization="APPROVED", consent_id=consent_id, username=username)
            authorization_code.raise_for_status()
            redirecturi_response = authorization_code.json().get('redirectUri')
            get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
            consent_code = get_code.group(1) if get_code else None
            if authorization_code.status_code != 200 or not consent_code:
                raise ValueError('Consent code not found in URI')

            vrp_exchange = exchange_code_for_token(code=consent_code)
            vrp_exchange.raise_for_status()
            new_access_token = vrp_exchange.json().get('access_token')
            if vrp_exchange.status_code != 200 or not new_access_token:
                raise ValueError('New Access Token not found')

            confirm_funds_call = confirm_funds(access_token=new_access_token, consent_id=consent_id, amount=amount)
            confirm_funds_call.raise_for_status()
            if confirm_funds_call.status_code != 200 or confirm_funds_call.json().get('Data', {}).get(
                    'FundsAvailableResult', {}).get('FundsAvailable') != 'Available':
                raise ValueError('Funds not available')

            submit_payment_call = submit_payment(access_token=new_access_token, consent_id=consent_id, amount=amount)
            submit_payment_call.raise_for_status()
            if submit_payment_call.status_code == 201:
                user_result['status'] = 'Success'
            else:
                raise ValueError('Payment submission failed')

            user_result['status'] = 'Success'

        except (requests.HTTPError, ValueError) as e:
            user_result['status'] = 'Failed'
            user_result['message'] = str(e)

        results.append(user_result)

    # stores results in the session
    request.session['payment_results'] = results

    # check for any failed payments
    if any(result['status'] == 'Failed' for result in results):
        return redirect('holding_page')
    return redirect('success_page')


def process_payments_view(request):
    usernames = request.session.get('usernames')
    amounts = request.session.get('amounts')

    if not usernames or not amounts:
        # return error message and redirect to an error page
        messages.error(request, "Invalid entry. Please try again.")
        return redirect('start_payment_process')  # redirect to start payment

    #calls the process payments function which handles redirection based on results
    return check_funds_no_payment(usernames, amounts, request)

