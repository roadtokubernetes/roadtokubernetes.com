from articles.models import Article
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views import generic

from .models import Profile


class ProfileView(generic.ListView):
    paginate_by = 10
    template_name = "articles/article_list.html"

    def get_queryset(self):
        return Article.objects.filter(
            user__username=self.kwargs.get("username")
        ).published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get("username")
        profile = get_object_or_404(
            Profile, user__username=username, user__is_active=True
        )
        name = profile.get_full_name()
        context["title"] = f"{name}'s Articles"
        return context
