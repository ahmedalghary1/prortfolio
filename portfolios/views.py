from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PortfolioForm, ProjectFormSet, SignUpForm
from .models import DEFAULT_PROJECTS, Portfolio, Project


def home(request):
    return render(request, "portfolios/home.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "portfolios/signup.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "portfolios/dashboard.html", {"portfolios": request.user.portfolios.all()})


def _portfolio_form(request, portfolio=None):
    portfolio = portfolio or Portfolio(owner=request.user)
    form = PortfolioForm(request.POST or None, request.FILES or None, instance=portfolio)
    projects = ProjectFormSet(request.POST or None, request.FILES or None, instance=portfolio)
    if request.method == "POST" and form.is_valid() and projects.is_valid():
        with transaction.atomic():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            projects.instance = item
            projects.save()
            if not item.projects.exists():
                Project.objects.bulk_create([
                    Project(portfolio=item, title=title, description=description, order=index)
                    for index, (title, description) in enumerate(DEFAULT_PROJECTS)
                ])
        return redirect(item.get_absolute_url())
    return render(request, "portfolios/editor.html", {"form": form, "projects": projects, "editing": bool(portfolio.pk)})


@login_required
def portfolio_create(request):
    return _portfolio_form(request)


@login_required
def portfolio_edit(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, owner=request.user)
    return _portfolio_form(request, portfolio)


def portfolio_detail(request, slug):
    portfolio = get_object_or_404(Portfolio.objects.prefetch_related("projects"), slug=slug)
    return render(request, "portfolios/detail.html", {"portfolio": portfolio})
