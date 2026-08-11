from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers import python
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
import re

from .models import (
    ContactMessage,
    PrayerRequest,
    Testimony,
    NewsletterSubscriber,
)

from .models import (
    ContactMessage,
    PrayerRequest,
    Testimony,
    NewsletterSubscriber,
    Devotional,
    Leadership,
    Event,
)
class BootstrapFormMixin:
    """
    Mixin to apply Bootstrap 5 styling to all form fields.
    Adds form-control, form-control-lg, premium-input, etc.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Skip if widget is already customized
            if field.widget.attrs.get('class'):
                continue

            # Determine widget class based on field type
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select form-select-lg'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control form-control-lg premium-input'
                if field.widget.attrs.get('rows') is None:
                    field.widget.attrs['rows'] = 5
            else:
                field.widget.attrs['class'] = 'form-control form-control-lg premium-input'

            # Add placeholder from label if not present
            if not field.widget.attrs.get('placeholder') and field.label:
                field.widget.attrs['placeholder'] = str(field.label)


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        labels = {
            'full_name': _('Your Full Name'),
            'email': _('Your Email Address'),
            'phone': _('Phone Number (optional)'),
            'subject': _('Subject'),
            'message': _('Your Message'),
        }

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        return email

    def clean_subject(self):
        return self.cleaned_data['subject'].strip()

    def clean_message(self):
        return self.cleaned_data['message'].strip()


class PrayerRequestForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = ['full_name', 'email', 'phone', 'urgency', 'request_details', 'confidential']
        labels = {
            'full_name': _('Your Full Name'),
            'email': _('Your Email (optional)'),
            'phone': _('Phone Number (optional)'),
            'urgency': _('Urgency Level'),
            'request_details': _('Prayer Request Details'),
            'confidential': _('Keep this request confidential'),
        }
        widgets = {
            'confidential': forms.CheckboxInput(),
        }

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_request_details(self):
        return self.cleaned_data['request_details'].strip()


class FirstVisitForm(BootstrapFormMixin, forms.Form):
    planned_date = forms.DateField(
        label=_('Planned Visit Date'),
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Select date'}),
        help_text=_('When do you plan to visit us?'),
    )
    number_of_guests = forms.IntegerField(
        label=_('Number of Guests'),
        min_value=1,
        initial=1,
        help_text=_('How many people are coming?'),
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 2'}),
    )
    children = forms.BooleanField(
        label=_('Bringing Children?'),
        required=False,
        help_text=_('Check if you will bring children'),
    )
    notes = forms.CharField(
        label=_('Additional Notes'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Any special needs or questions...'}),
    )

    def clean_number_of_guests(self):
        value = self.cleaned_data.get('number_of_guests')
        if value and value < 1:
            raise ValidationError(_('Please enter at least 1 guest.'))
        return value

    def clean_planned_date(self):
        date = self.cleaned_data.get('planned_date')
        if date and date < timezone.now().date():
            raise ValidationError(_('The visit date cannot be in the past.'))
        return date


class TestimonyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Testimony
        fields = ['full_name', 'email', 'photo', 'title', 'story']
        labels = {
            'full_name': _('Your Full Name'),
            'email': _('Your Email Address'),
            'photo': _('Your Photo (optional)'),
            'title': _('Testimony Title'),
            'story': _('Share Your Story'),
        }
        help_texts = {
            'photo': _('Upload a photo (JPEG, PNG) - optional'),
        }

    def clean_full_name(self):
        return self.cleaned_data['full_name'].strip()

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()

    def clean_title(self):
        return self.cleaned_data['title'].strip()

    def clean_story(self):
        return self.cleaned_data['story'].strip()


class NewsletterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['name', 'email']
        labels = {
            'name': _('Your Name (optional)'),
            'email': _('Your Email Address'),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip().lower()
            # Check for duplicate active subscribers
            if NewsletterSubscriber.objects.filter(email__iexact=email, active=True).exists():
                raise ValidationError(_('This email is already subscribed to our newsletter.'))
        return email

    def clean_name(self):
        return self.cleaned_data.get('name', '').strip()


class SearchForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search sermons, devotionals, events...'),
            'aria-label': _('Search'),
        }),
    )

    def clean_q(self):
        return self.cleaned_data.get('q', '').strip()

class DevotionalForm(forms.ModelForm):
    class Meta:
        model = Devotional
        fields = [
            'title',
            'scripture',
            'author',
            'featured_image',
            'excerpt',
            'content',      # ← THIS MUST EXIST
            'published',
            'featured',
            'meta_title',
            'meta_description',
            'meta_keywords',
        ]
    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean_scripture(self):
        return self.cleaned_data["scripture"].strip()

    def clean_author(self):
        return self.cleaned_data["author"].strip()

    def clean_excerpt(self):
        return self.cleaned_data["excerpt"].strip()


class LeadershipForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Leadership
        fields = [
            "name",
            "position",
            "photo",
            "biography",
            "quote",
            "display_order",
            "show_on_homepage",
            "facebook",
            "instagram",
            "email",
            "phone",
        ]
        labels = {
            "name": _("Full Name"),
            "position": _("Position / Title"),
            "photo": _("Profile Photo"),
            "biography": _("Biography"),
            "quote": _("Personal Quote"),
            "display_order": _("Display Order"),
            "show_on_homepage": _("Show on Homepage"),
            "facebook": _("Facebook Profile"),
            "instagram": _("Instagram Profile"),
            "email": _("Email Address"),
            "phone": _("Phone Number"),
        }
        widgets = {
            "quote": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Enter a quote from this leader..."
            }),
        }

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_position(self):
        return self.cleaned_data["position"].strip()

    def clean_quote(self):
        return self.cleaned_data["quote"].strip()


class EventForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "banner",
            "event_type",
            "description",
            "venue",
            "start_date",
            "end_date",
            "registration_link",
            "google_maps_link",
            "featured",
            "published",
        ]
        labels = {
            "title": _("Event Title"),
            "banner": _("Event Banner"),
            "event_type": _("Event Type"),
            "description": _("Event Description"),
            "venue": _("Venue"),
            "start_date": _("Start Date & Time"),
            "end_date": _("End Date & Time"),
            "registration_link": _("Registration Link"),
            "google_maps_link": _("Google Maps Link"),
            "featured": _("Featured Event"),
            "published": _("Published"),
        }
        widgets = {
            "start_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local"
                }
            ),
            "end_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local"
                }
            ),
        }

    def clean_title(self):
        return self.cleaned_data["title"].strip()

    def clean_venue(self):
        return self.cleaned_data["venue"].strip()

    def clean(self):
        cleaned_data = super().clean()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                _("End date cannot be before the start date.")
            )

        return cleaned_data
