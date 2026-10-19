from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


DEFAULT_SKILLS = "HTML, CSS, Bootstrap, JavaScript"
DEFAULT_PROJECTS = (
    ("Student System", "A simple system for managing student records."),
    ("Personal Website", "A personal website to introduce skills and work."),
    ("Online Store", "A simple online store with product cards."),
)


class Portfolio(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolios")
    slug = models.SlugField(max_length=60, unique=True, blank=True, allow_unicode=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    tagline = models.CharField(max_length=220)
    about = models.TextField(max_length=1200)
    email = models.EmailField()
    location = models.CharField(max_length=100, blank=True)
    skills = models.CharField(max_length=500, blank=True, default=DEFAULT_SKILLS)
    photo = models.ImageField(upload_to="profiles/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("portfolio_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)[:60].strip("-") or "portfolio"
            candidate = base
            number = 2
            while Portfolio.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                suffix = f"-{number}"
                candidate = f"{base[:60 - len(suffix)].rstrip('-')}{suffix}"
                number += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def skill_list(self):
        return [skill.strip() for skill in (self.skills or DEFAULT_SKILLS).split(",") if skill.strip()]


class Project(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
