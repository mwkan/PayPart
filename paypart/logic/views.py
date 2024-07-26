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


def home(request):
    total_cost = 100
    return HttpResponse("Welcome to Paypart")

# Create your views here.
