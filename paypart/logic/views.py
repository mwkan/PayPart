from django.shortcuts import render
from django.http import HttpResponse

# total cost = x
# Split number = y (number of people the user wants to split the cost between)
# Amount per person = x/y
# Ask for input y times:
# Full name:
# amount to pay: (editable)
# Bank (option set):
# Any other questions from API:

# Front end should show difference between total and amount input on each person

# API takes info from this and inputs it y times to each user and returns true or false for each user

# if all true, then return success page
# if not all true, then return fail page


def start_payment_process(request): #MA
    #landing page, payment = £2000, asks for how many splitting between & asks user whether they want to split or use custom
    return HttpResponse("Welcome to Paypart")

def choose_split(request):
    # take the payment amount and split it between number of users
    return #amount

def choose_custom(request):
    #taking the custom value from the input
    return #amount

def get_username(request):
    return #username

def process_payments(request): #MWK
    #calling all the stages of the API and iterate through each username to do it for each person
    return #true or false

def holding_page(request):
    #hold time for 10mins
    return

def success_page(request):
    return

