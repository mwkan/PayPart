from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import SplitForm


def start_payment_process(request):
    if request.method == 'POST':
        form = SplitForm(request.POST)
        if form.is_valid():
            num_people = form.cleaned_data['num_people']
            request.session['total_amount'] = 2000.0
            request.session['num_people'] = num_people
            return redirect('collect_user_amounts')
    else:
        form = SplitForm()

    return render(request, 'logic/start_payment_process.html', {'form': form})

def collect_user_amounts(request):
    return HttpResponse("This is the collect_user_amounts page, which is yet to be implemented.")
def choose_split(request):
    # enables the user to choose which split they want to go for
    return #amount

def even_split(request):
    return

def custom_split(request):
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

