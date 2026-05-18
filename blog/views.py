from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

from .forms import CommentForm
from .models import Post


class IndexView(generic.ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "post_list"
    paginate_by = 5


class PostDetailView(generic.DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    form_class = CommentForm

    def get__success_url(self) -> str:
        return reverse("blog:post-detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related(
            "user",
        ).order_by("-created_time")
        if "form" not in context:
            context["form"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.is_authenticated:
            return redirect("login")

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.save()
            return redirect(
                reverse("blog:post-detail", kwargs={"pk": self.object.pk})
            )
        else:
            return self.render_to_response(self.get_context_data(form=form))
