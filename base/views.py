from django.shortcuts import render
from django.http import HttpResponse
from .models import Clothing

# Create your views here.
def home(request):
    extracted = Clothing.objects.order_by('-rating')

    context = {'clothing': extracted}
    for item in extracted:
        print(item.name)

    return render(request, 'base/home.html', context)

