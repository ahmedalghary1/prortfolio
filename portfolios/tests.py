from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Portfolio, Project


class PortfolioFlowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other = User.objects.create_user(username="other", password="StrongPass123!")

    def test_create_public_portfolio_with_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("portfolio_create"), {
            "name": "Sample Person", "role": "Developer",
            "tagline": "I build useful websites", "about": "About my work",
            "email": "sample@example.com", "location": "Cairo", "skills": "Python\nDjango",
            "projects-TOTAL_FORMS": "3", "projects-INITIAL_FORMS": "0",
            "projects-MIN_NUM_FORMS": "0", "projects-MAX_NUM_FORMS": "10",
            "projects-0-title": "My app", "projects-0-description": "A sample app",
            "projects-0-url": "https://example.com", "projects-0-order": "0",
        })
        self.assertRedirects(response, "/p/sample-person/")
        portfolio = Portfolio.objects.get(slug="sample-person")
        self.assertEqual(portfolio.owner, self.owner)
        self.assertEqual(portfolio.skill_list, ["Python", "Django"])
        self.assertEqual(Project.objects.get(portfolio=portfolio).title, "My app")
        self.client.logout()
        public = self.client.get(portfolio.get_absolute_url())
        self.assertContains(public, "Sample Person")
        self.assertContains(public, "My app")
        self.assertNotContains(public, "default-profile.jpeg")
        self.assertNotContains(public, "project-image")

    def test_other_user_cannot_edit(self):
        portfolio = Portfolio.objects.create(
            owner=self.owner, slug="private-editor", name="Owner", role="Designer",
            tagline="Hello", about="About", email="owner@example.com", skills="Design",
        )
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("portfolio_edit", args=[portfolio.pk])).status_code, 404)

    def test_arabic_slug_collision_and_default_content(self):
        self.client.force_login(self.owner)
        payload = {
            "name": "أحمد علي", "role": "مطور", "tagline": "أبني مواقع",
            "about": "نبذة", "email": "ahmed@example.com", "skills": "",
            "projects-TOTAL_FORMS": "3", "projects-INITIAL_FORMS": "0",
            "projects-MIN_NUM_FORMS": "0", "projects-MAX_NUM_FORMS": "10",
        }
        first = self.client.post(reverse("portfolio_create"), payload)
        self.assertEqual(first.status_code, 302)
        first_portfolio = Portfolio.objects.get(slug="أحمد-علي")
        self.assertEqual(first_portfolio.skill_list, ["HTML", "CSS", "Bootstrap", "JavaScript"])
        self.assertEqual(first_portfolio.projects.count(), 3)
        self.assertContains(self.client.get(first_portfolio.get_absolute_url()), "Student System")
        second = self.client.post(reverse("portfolio_create"), payload)
        self.assertEqual(second.status_code, 302)
        self.assertTrue(Portfolio.objects.filter(slug="أحمد-علي-2").exists())
