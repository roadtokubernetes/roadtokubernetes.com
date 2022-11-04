# Create your views here.
from django.shortcuts import render


# Create your views here.
def books_view(request):
    return render(request, "books/index.html", {})
