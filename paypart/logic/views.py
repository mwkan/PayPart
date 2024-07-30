import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import forms
from .api import get_access_token, VRP_consent, get_consent, exchange_code_for_token, confirm_funds, submit_payment
import re
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
        amount_per_person = total_amount / num_people
        if request.method == 'POST':
            forms1 = [forms.UsernameForm(request.POST, prefix=str(i)) for i in range(num_people)]
            if all(form.is_valid() for form in forms1):
                usernames = [form.cleaned_data['username'] for form in forms1]
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
            amounts = [form.cleaned_data['amount'] for form in forms2]
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

'''
# Main function to initiate payment processing
def process():
    usernames = ["user1", "user2", "user3", "user4", "user5"]
    amount_to_pay_per_user = 50.0  # Define the amount to be paid per user
    process_payments(usernames, amount_to_pay_per_user)


# Run the main function
if __name__ == "__main__":
    process()
'''


def holding_page(request):
    usernames = request.session.get('usernames', [])
    amounts = request.session.get('amounts', [])
    results = process_payments(usernames, amounts)
    request.session['results'] = results
    return render(request, 'logic/holding_page.html', {'results': results})


def success_page(request):
    return render(request, 'logic/success_page.html')


def process_payments(request):
    # usernames = ['user1', 'user2', 'user3']
    # amounts = [50.0, 75.0, 100.0]
    usernames = request.session.get('usernames', [])
    amounts = request.session.get('amounts', [])

    results = []
    for username, amount in zip(usernames, amounts):
        user_result = {'username': username, 'status': 'Pending'}

        access_token_call = get_access_token(scope="payments")
        access_token = access_token_call.json().get('access_token')
        if access_token_call.status_code != 200 or not access_token:
            user_result['status'] = 'Failed'
            results.append(user_result)
            continue

        consent_call = VRP_consent(access_token=access_token, amount_to_pay_per_user=amount)
        consent_id = consent_call.json().get('Data', {}).get('ConsentId')
        if consent_call.status_code != 201 or not consent_id:
            user_result['status'] = 'Failed'
            results.append(user_result)
            continue

        authorization_code = get_consent(authorization="APPROVED", consent_id=consent_id, username=username)
        redirecturi_response = authorization_code.json().get('redirectUri')
        get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
        consent_code = get_code.group(1) if get_code else None
        if authorization_code.status_code != 200 or not consent_code:
            user_result['status'] = 'Failed'
            results.append(user_result)
            continue

        vrp_exchange = exchange_code_for_token(code=consent_code)
        new_access_token = vrp_exchange.json().get('access_token')
        if vrp_exchange.status_code != 200 or not new_access_token:
            user_result['status'] = 'Failed'
            results.append(user_result)
            continue

        confirm_funds_call = confirm_funds(access_token=new_access_token, consent_id=consent_id, amount=amount)
        if confirm_funds_call.status_code != 200 or confirm_funds_call.json().get('Data', {}).get(
                'FundsAvailableResult', {}).get('FundsAvailable') != 'Available':
            user_result['status'] = 'Failed'
            results.append(user_result)
            continue

        submit_payment_call = submit_payment(access_token=new_access_token, consent_id=consent_id, amount=amount)
        if submit_payment_call.status_code == 201:
            user_result['status'] = 'Success'
        else:
            user_result['status'] = 'Failed'

        results.append(user_result)

    return results


def process_payments_view(request):
    usernames = request.session.get('usernames')
    amounts = request.session.get('amounts')

    if not usernames or not amounts:
        # return error message and redirect to an error page
        messages.error(request, "Invalid entry. Please try again.")
        return redirect('start_payment_process')  # redirect to start payment

    results = process_payments(usernames, amounts)

    return render(request, 'logic/process_payments.html', {'results': results})

# # Function to process payments for an array of users
# def process_payments(usernames, amount_to_pay_per_user):
#     for username in usernames:
#         # print(f"Processing payment for user: {username}")
#
#         # Obtain initial access token
#         access_token_call = get_access_token(scope="payments")
#         access_token = access_token_call.json()['access_token']  ## access token that is passed through next function
#         access_api_status = access_token_call.status_code
#         if access_api_status != 200:
#             continue
#
#         # Create VRP consent
#         consent_call = VRP_consent(access_token=access_token, amount_to_pay_per_user=amount_to_pay_per_user)
#         consent_id = consent_call.json()['Data']['ConsentId']
#         consent_api_status = consent_call.status_code
#         if consent_api_status != 201:
#             continue
#
#         # Get customer authorization
#         authorization_code = get_consent(authorization="APPROVED", consent_id=consent_id, username=username)
#         redirecturi_response = authorization_code.json()['redirectUri']
#         get_code = re.search(r'code=([a-f0-9-]+)', redirecturi_response)
#         consent_code = get_code.group(1)
#         authorization_api_status = authorization_code.status_code
#         if authorization_api_status != 200:
#             continue
#
#         # Exchange authorization code for VRP access token
#         vrp_exchange = exchange_code_for_token(code=consent_code)
#         new_access_token = vrp_exchange.json()['access_token']
#         exchange_api_status = vrp_exchange.status_code
#         if exchange_api_status != 200:
#             continue
#
#         # Confirm available funds
#         confirm_funds_call = confirm_funds(access_token=new_access_token, consent_id=consent_id,
#                                            amount=amount_to_pay_per_user)
#         funds_status = confirm_funds_call.json()['Data']['FundsAvailableResult']['FundsAvailable']
#         funds_api_status = confirm_funds_call.status_code
#         if funds_api_status != 'Available' & funds_status != 'Available':
#             continue
#
#         # Submit the payment
#         submit_payment_call = submit_payment(access_token=new_access_token, consent_id=consent_id,
#                                              amount=amount_to_pay_per_user)
#         submit_api_status = submit_payment_call.status_code
#         if submit_api_status == 201:
#             return True
#             # print(f"Payment successful for user: {username}")
#         else:
#             return False
#             # print(f"Payment failed for user: {username}")
