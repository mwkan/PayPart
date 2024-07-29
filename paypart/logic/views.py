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


# Function to process payments for an array of users
def process_payments(usernames, amount_to_pay_per_user):
    for username in usernames:
        #print(f"Processing payment for user: {username}")

        # Obtain initial access token
        access_token = obtain_access_token()
        if access_token != 200:
            continue

        # Create VRP consent
        consent_id = create_vrp_consent(access_token, amount_to_pay_per_user)
        if consent_id != 201:
            continue

        # Get customer authorization
        authorization_code = get_customer_authorization(username)
        if authorization_code != 200:
            continue

        # Exchange authorization code for VRP access token
        vrp_access_token = exchange_authorization_code(authorization_code)
        if vrp_access_token != 200
            continue

        # Confirm available funds
        if confirm_available_funds(vrp_access_token) != 201:
            continue

        # Submit the payment
        if submit_payment(vrp_access_token) == 201:
            return True
            #print(f"Payment successful for user: {username}")
        else:
            return False
            #print(f"Payment failed for user: {username}")

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
>>>>>>> 3ae2579 (add process payment function)

def holding_page(request):
    # hold time for 10mins
    return


def success_page(request):
    return
