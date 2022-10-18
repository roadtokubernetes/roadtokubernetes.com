from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(redirect_field_name=None)
def console_view(request):
    return render(request, "console/view.html", {})
