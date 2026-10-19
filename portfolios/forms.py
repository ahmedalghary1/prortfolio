from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
import re

from .models import DEFAULT_SKILLS, Portfolio, Project


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="البريد الإلكتروني")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class PortfolioForm(forms.ModelForm):
    skills = forms.CharField(
        label="المهارات", required=False,
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": "HTML\nCSS\nBootstrap\nJavaScript"}),
        help_text="اكتب كل مهارة في سطر، أو افصل بينها بفاصلة. عند تركها فارغة ستُستخدم مهارات القالب.",
    )

    class Meta:
        model = Portfolio
        fields = ("name", "role", "tagline", "about", "email", "location", "skills", "photo")
        labels = {
            "name": "الاسم", "role": "المسمى المهني",
            "tagline": "نبذة قصيرة", "about": "عني", "email": "بريد التواصل",
            "location": "الموقع", "skills": "المهارات", "photo": "الصورة الشخصية",
        }
        widgets = {"about": forms.Textarea(attrs={"rows": 5}), "tagline": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.initial["skills"] = self.instance.skills.replace(", ", "\n")

    def clean_skills(self):
        value = self.cleaned_data.get("skills", "")
        skills = [item.strip() for item in re.split(r"[,،\n\r]+", value) if item.strip()]
        result = ", ".join(dict.fromkeys(skills)) or DEFAULT_SKILLS
        if len(result) > 500:
            raise forms.ValidationError("قائمة المهارات طويلة جدًا. اختصرها إلى 500 حرف.")
        return result


ProjectFormSet = inlineformset_factory(
    Portfolio, Project, fields=("title", "description", "url", "image"),
    extra=3, can_delete=True, max_num=10, validate_max=True,
    widgets={"description": forms.Textarea(attrs={"rows": 2})},
    labels={"title": "اسم المشروع", "description": "وصف المشروع", "url": "رابط المشروع", "image": "صورة المشروع"},
)
