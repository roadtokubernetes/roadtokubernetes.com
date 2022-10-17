from django.shortcuts import render

# Create your views here.

def console_view(request):
    return render(request, "console/view.html", {})
