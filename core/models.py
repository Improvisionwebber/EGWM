from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, URLValidator
from django_ckeditor_5.fields import CKEditor5Field
import os
from .imgbb_storage import ImgBBStorage

# ---------- Abstract Base Models ----------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("created at"), default=timezone.now, editable=False)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SEOModel(models.Model):
    meta_title = models.CharField(_("meta title"), max_length=255, blank=True, help_text=_("SEO title (max 255 chars)"))
    meta_description = models.TextField(_("meta description"), max_length=500, blank=True, help_text=_("SEO description (max 500 chars)"))
    meta_keywords = models.CharField(_("meta keywords"), max_length=255, blank=True, help_text=_("Comma-separated keywords"))
    og_image = models.ImageField(
        _("Open Graph image"),
        upload_to="seo/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    canonical_url = models.URLField(_("canonical URL"), blank=True, help_text=_("Override canonical URL if needed"))

    class Meta:
        abstract = True


# ---------- Singleton Settings Helpers ----------
class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------- Church Settings ----------
class ChurchSettings(SingletonModel, TimeStampedModel):
    church_name = models.CharField(_("church name"), max_length=255, default="Embassy of God's Word Ministry")
    short_name = models.CharField(_("short name"), max_length=100, blank=True)
    tagline = models.CharField(_("tagline"), max_length=255, blank=True)
    mission = models.TextField(_("mission"), blank=True)
    vision = models.TextField(_("vision"), blank=True)
    motto = models.CharField(_("motto"), max_length=255, blank=True)
    address = models.TextField(_("address"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=30, blank=True)
    alternate_phone = models.CharField(_("alternate phone"), max_length=30, blank=True)
    google_maps_embed = models.TextField(_("Google Maps embed"), blank=True, help_text=_("Full iframe embed code or URL"))
    logo = models.ImageField(
        _("logo"),
        upload_to="settings/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )

    favicon = models.ImageField(
        _("favicon"),
        upload_to="settings/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )

    hero_default_image = models.ImageField(
        _("default hero image"),
        upload_to="settings/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    youtube_live_url = models.URLField(_("YouTube Live URL"), blank=True)
    livestream_enabled = models.BooleanField(_("livestream enabled"), default=False)

    service_times_text = models.TextField(_("service times text"), blank=True, help_text=_("HTML or plain text summary"))

    # Social links (quick access in settings)
    facebook = models.URLField(_("Facebook"), blank=True)
    instagram = models.URLField(_("Instagram"), blank=True)
    youtube = models.URLField(_("YouTube"), blank=True)
    tiktok = models.URLField(_("TikTok"), blank=True)
    whatsapp = models.URLField(_("WhatsApp"), blank=True)
    telegram = models.URLField(_("Telegram"), blank=True)

    office_hours = models.CharField(_("office hours"), max_length=255, blank=True)
    copyright_text = models.CharField(_("copyright text"), max_length=255, blank=True)

    def __str__(self):
        return self.church_name

    class Meta:
        verbose_name = _("Church Settings")
        verbose_name_plural = _("Church Settings")


# ---------- Homepage Settings ----------
class HomepageSettings(SingletonModel, TimeStampedModel):
    hero_title = models.CharField(_("hero title"), max_length=255, blank=True)
    hero_subtitle = models.TextField(_("hero subtitle"), blank=True)
    hero_button_text = models.CharField(_("hero button text"), max_length=50, blank=True)
    hero_button_link = models.CharField(_("hero button link"), max_length=255, blank=True, help_text=_("URL or path"))

    welcome_title = models.CharField(_("welcome title"), max_length=255, blank=True)
    welcome_message = models.TextField(_("welcome message"), blank=True)

    featured_sermon = models.ForeignKey(
        "Sermon", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("featured sermon")
    )
    featured_devotional = models.ForeignKey(
        "Devotional", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("featured devotional")
    )
    featured_testimony = models.ForeignKey(
        "Testimony", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("featured testimony")
    )
    featured_event = models.ForeignKey(
        "Event", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", verbose_name=_("featured event")
    )

    show_gallery = models.BooleanField(_("show gallery"), default=True)
    show_events = models.BooleanField(_("show events"), default=True)
    show_testimonies = models.BooleanField(_("show testimonies"), default=True)
    show_devotionals = models.BooleanField(_("show devotionals"), default=True)
    show_sermons = models.BooleanField(_("show sermons"), default=True)
    show_ministries = models.BooleanField(_("show ministries"), default=True)
    show_statistics = models.BooleanField(_("show statistics"), default=True)

    def __str__(self):
        return "Homepage Settings"

    class Meta:
        verbose_name = _("Homepage Settings")
        verbose_name_plural = _("Homepage Settings")


# ---------- Hero Slide ----------
class HeroSlide(TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    subtitle = models.TextField(_("subtitle"), blank=True)
    image = models.ImageField(
        _("image"),
        upload_to="hero/",
        storage=ImgBBStorage()
    )
    video_file = models.FileField(_("video file"), upload_to="hero/videos/", blank=True, null=True, help_text=_("Optional video file (MP4)"))
    youtube_url = models.URLField(_("YouTube URL"), blank=True, help_text=_("Alternative YouTube video URL"))
    button_text = models.CharField(_("button text"), max_length=50, blank=True)
    button_link = models.CharField(_("button link"), max_length=255, blank=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0, help_text=_("Lower numbers appear first"))
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = _("Hero Slide")
        verbose_name_plural = _("Hero Slides")

    def __str__(self):
        return self.title


# ---------- Announcement ----------
class Announcement(TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    content = CKEditor5Field(_("content"), config_name="extends")
    is_active = models.BooleanField(_("active"), default=True)
    display_until = models.DateTimeField(_("display until"), blank=True, null=True,
                                         help_text=_("Leave blank to show indefinitely"))
    display_order = models.PositiveIntegerField(_("display order"), default=0)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")

    def __str__(self):
        return self.title

    def is_displayable(self):
        if not self.is_active:
            return False
        if self.display_until and timezone.now() > self.display_until:
            return False
        return True


# ---------- Service Schedule ----------
class ServiceSchedule(TimeStampedModel):
    DAY_CHOICES = (
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    )
    day = models.IntegerField(_("day"), choices=DAY_CHOICES)
    name = models.CharField(_("service name"), max_length=100, default=_("Main Service"))
    start_time = models.TimeField(_("start time"))
    end_time = models.TimeField(_("end time"))
    venue = models.CharField(_("venue"), max_length=255, blank=True)
    description = models.TextField(_("description"), blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0)

    class Meta:
        ordering = ["day", "start_time", "display_order"]
        verbose_name = _("Service Schedule")
        verbose_name_plural = _("Service Schedules")

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time} - {self.name}"


# ---------- Social Link ----------
class SocialLink(TimeStampedModel):
    PLATFORM_CHOICES = (
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("youtube", "YouTube"),
        ("tiktok", "TikTok"),
        ("whatsapp", "WhatsApp"),
        ("telegram", "Telegram"),
        ("twitter", "Twitter/X"),
        ("linkedin", "LinkedIn"),
        ("other", "Other"),
    )
    platform = models.CharField(_("platform"), max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(_("URL"))
    icon_class = models.CharField(_("icon class"), max_length=100, blank=True,
                                  help_text=_("CSS class for icon (e.g., fab fa-facebook)"))
    display_order = models.PositiveIntegerField(_("display order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["display_order"]
        verbose_name = _("Social Link")
        verbose_name_plural = _("Social Links")

    def __str__(self):
        return f"{self.get_platform_display()}"


# ---------- Leadership ----------
class Leadership(TimeStampedModel, SEOModel):
    name = models.CharField(_("name"), max_length=255)
    position = models.CharField(_("position"), max_length=255)
    photo = models.ImageField(
        _("photo"),
        upload_to="leadership/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    biography = CKEditor5Field(_("biography"), blank=True, config_name="extends")
    quote = models.TextField(_("quote"), blank=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0)
    show_on_homepage = models.BooleanField(_("show on homepage"), default=False)

    facebook = models.URLField(_("Facebook"), blank=True)
    instagram = models.URLField(_("Instagram"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=30, blank=True)

    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("Leadership")
        verbose_name_plural = _("Leadership")

    def __str__(self):
        return f"{self.name} - {self.position}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Leadership.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("leadership_detail", kwargs={"slug": self.slug})


# ---------- Ministry ----------
class Ministry(TimeStampedModel, SEOModel):
    name = models.CharField(_("name"), max_length=255)
    leader = models.CharField(_("leader"), max_length=255, blank=True)
    image = models.ImageField(
        _("image"),
        upload_to="ministries/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    description = CKEditor5Field(_("description"), config_name="extends")
    meeting_day = models.CharField(_("meeting day"), max_length=50, blank=True)
    meeting_time = models.CharField(_("meeting time"), max_length=50, blank=True)
    meeting_venue = models.CharField(_("meeting venue"), max_length=255, blank=True)
    display_order = models.PositiveIntegerField(_("display order"), default=0)
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("Ministry")
        verbose_name_plural = _("Ministries")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Ministry.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("ministry_detail", kwargs={"slug": self.slug})


# ---------- Sermon Category ----------
class SermonCategory(TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name = _("Sermon Category")
        verbose_name_plural = _("Sermon Categories")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while SermonCategory.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("sermon_category_detail", kwargs={"slug": self.slug})


# ---------- Sermon ----------
class Sermon(TimeStampedModel, SEOModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)
    category = models.ForeignKey(SermonCategory, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="sermons", verbose_name=_("category"))
    speaker = models.CharField(_("speaker"), max_length=255)
    bible_reference = models.CharField(_("bible reference"), max_length=255, blank=True)
    series = models.CharField(_("series"), max_length=255, blank=True)
    thumbnail = models.ImageField(
        _("thumbnail"),
        upload_to="sermons/thumbnails/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    youtube_url = models.URLField(_("YouTube URL"), blank=True)
    audio_file = models.FileField(_("audio file"), upload_to="sermons/audio/", blank=True, null=True)
    pdf_notes = models.FileField(_("PDF notes"), upload_to="sermons/notes/", blank=True, null=True)
    summary = models.TextField(_("summary"), blank=True, help_text=_("Short excerpt for listings"))
    content = CKEditor5Field(_("content"), blank=True, config_name="extends")
    date_preached = models.DateTimeField(_("date preached"), default=timezone.now)
    featured = models.BooleanField(_("featured"), default=False)
    published = models.BooleanField(_("published"), default=True)
    views = models.PositiveIntegerField(_("views"), default=0)

    @property
    def reading_time(self):
        if not self.content:
            return 0
        words = len(self.content.split())
        return max(1, round(words / 200))  # approx 200 words per minute

    @property
    def youtube_embed_url(self):
        if self.youtube_url:
            # Extract video ID from various YouTube URL formats
            import re
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&?#]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, self.youtube_url)
                if match:
                    return f"https://www.youtube.com/embed/{match.group(1)}"
        return None

    class Meta:
        ordering = ["-date_preached"]
        verbose_name = _("Sermon")
        verbose_name_plural = _("Sermons")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Sermon.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("sermon_detail", kwargs={"slug": self.slug})


# ---------- Devotional ----------
class Devotional(TimeStampedModel, SEOModel):
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)
    featured_image = models.ImageField(
        _("featured image"),
        upload_to="devotionals/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    scripture = models.CharField(_("scripture"), max_length=255, blank=True, help_text=_("Bible verse reference"))
    author = models.CharField(_("author"), max_length=255, default="Pastor Kingsley Nwekwo")
    excerpt = models.TextField(_("excerpt"), blank=True, help_text=_("Short description for listings"))
    content = CKEditor5Field(_("content"), config_name="extends")
    published = models.BooleanField(_("published"), default=True)
    featured = models.BooleanField(_("featured"), default=False)
    views = models.PositiveIntegerField(_("views"), default=0)

    @property
    def reading_time(self):
        if not self.content:
            return 0
        words = len(self.content.split())
        return max(1, round(words / 200))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Devotional")
        verbose_name_plural = _("Devotionals")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Devotional.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("devotional_detail", kwargs={"slug": self.slug})


# ---------- Event ----------
class Event(TimeStampedModel, SEOModel):
    EVENT_TYPES = (
        ("service", _("Service")),
        ("conference", _("Conference")),
        ("revival", _("Revival")),
        ("outreach", _("Outreach")),
        ("prayer_meeting", _("Prayer Meeting")),
        ("bible_study", _("Bible Study")),
        ("youth", _("Youth Event")),
        ("other", _("Other")),
    )
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)
    banner = models.ImageField(
        _("banner"),
        upload_to="events/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )   
    event_type = models.CharField(_("event type"), max_length=50, choices=EVENT_TYPES, default="service")
    description = CKEditor5Field(_("description"), config_name="extends")
    venue = models.CharField(_("venue"), max_length=255)
    start_date = models.DateTimeField(_("start date"))
    end_date = models.DateTimeField(_("end date"), blank=True, null=True)
    registration_link = models.URLField(_("registration link"), blank=True)
    google_maps_link = models.URLField(_("Google Maps link"), blank=True)
    featured = models.BooleanField(_("featured"), default=False)
    published = models.BooleanField(_("published"), default=True)

    @property
    def countdown(self):
        """Returns a timedelta until start date, or None if past."""
        now = timezone.now()
        if self.start_date > now:
            return self.start_date - now
        return None

    class Meta:
        ordering = ["start_date"]
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"slug": self.slug})

class GalleryAlbum(TimeStampedModel):
    title = models.CharField(
        _("title"),
        max_length=255
    )

    description = models.TextField(
        _("description"),
        blank=True
    )

    cover_image = models.ImageField(
        _("cover image"),
        upload_to="gallery/albums/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )

    published = models.BooleanField(
        _("published"),
        default=True
    )

    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = _("Gallery Album")
        verbose_name_plural = _("Gallery Albums")

    def __str__(self):
        return self.title


class GalleryImage(TimeStampedModel):
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("album")
    )

    image = models.ImageField(
        _("image"),
        upload_to="gallery/images/",
        storage=ImgBBStorage(),
    )

    caption = models.CharField(
        _("caption"),
        max_length=255,
        blank=True
    )

    display_order = models.PositiveIntegerField(
        _("display order"),
        default=0
    )

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = _("Gallery Image")
        verbose_name_plural = _("Gallery Images")

    def __str__(self):
        return self.caption or "Gallery Image"


# ---------- Testimony ----------
class Testimony(TimeStampedModel, SEOModel):
    full_name = models.CharField(_("full name"), max_length=255)
    email = models.EmailField(_("email"), blank=True)
    photo = models.ImageField(
        _("photo"),
        upload_to="testimonies/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    title = models.CharField(_("title"), max_length=255, blank=True)
    story = CKEditor5Field(_("story"), config_name="extends")
    slug = models.SlugField(_("slug"), max_length=255, unique=True, blank=True)
    approved = models.BooleanField(_("approved"), default=False, help_text=_("Approve for public display"))
    featured = models.BooleanField(_("featured"), default=False)
    published_date = models.DateTimeField(_("published date"), default=timezone.now)

    class Meta:
        ordering = ["-published_date"]
        verbose_name = _("Testimony")
        verbose_name_plural = _("Testimonies")

    def __str__(self):
        return f"{self.full_name} - {self.title or 'Testimony'}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title or self.full_name)
            self.slug = base_slug
            original_slug = self.slug
            counter = 1
            while Testimony.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("testimony_detail", kwargs={"slug": self.slug})


# ---------- Prayer Request ----------
class PrayerRequest(TimeStampedModel):
    URGENCY_CHOICES = (
        ("low", _("Low")),
        ("medium", _("Medium")),
        ("high", _("High")),
        ("urgent", _("Urgent")),
    )
    STATUS_CHOICES = (
        ("pending", _("Pending")),
        ("prayed", _("Prayed For")),
        ("answered", _("Answered")),
        ("archived", _("Archived")),
    )
    full_name = models.CharField(_("full name"), max_length=255)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=30, blank=True)
    urgency = models.CharField(_("urgency"), max_length=20, choices=URGENCY_CHOICES, default="medium")
    request_details = models.TextField(_("request details"))
    confidential = models.BooleanField(_("confidential"), default=False,
                                       help_text=_("Keep this request private (not shown publicly)"))
    status = models.CharField(_("status"), max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_notes = models.TextField(_("admin notes"), blank=True)
    submitted_date = models.DateTimeField(_("submitted date"), default=timezone.now)

    class Meta:
        ordering = ["-submitted_date"]
        verbose_name = _("Prayer Request")
        verbose_name_plural = _("Prayer Requests")

    def __str__(self):
        return f"{self.full_name} - {self.get_urgency_display()}"


# ---------- Contact Message ----------
class ContactMessage(TimeStampedModel):
    full_name = models.CharField(_("full name"), max_length=255)
    email = models.EmailField(_("email"))
    phone = models.CharField(_("phone"), max_length=30, blank=True)
    subject = models.CharField(_("subject"), max_length=255)
    message = models.TextField(_("message"))
    read_status = models.BooleanField(_("read"), default=False)
    submitted_date = models.DateTimeField(_("submitted date"), default=timezone.now)

    class Meta:
        ordering = ["-submitted_date"]
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


# ---------- Giving Information ----------
class GivingInformation(TimeStampedModel):
    title = models.CharField(_("title"), max_length=255, default=_("Bank Transfer"))
    bank_name = models.CharField(_("bank name"), max_length=255)
    account_name = models.CharField(_("account name"), max_length=255)
    account_number = models.CharField(_("account number"), max_length=50)
    description = models.TextField(_("description"), blank=True, help_text=_("Additional details for giving"))
    qr_image = models.ImageField(
        _("QR image"),
        upload_to="giving/qr/",
        storage=ImgBBStorage(),
        blank=True,
        null=True
    )
    display_order = models.PositiveIntegerField(_("display order"), default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = _("Giving Information")
        verbose_name_plural = _("Giving Information")

    def __str__(self):
        return f"{self.title} - {self.bank_name}"


# ---------- Newsletter Subscriber ----------
class NewsletterSubscriber(TimeStampedModel):
    name = models.CharField(_("name"), max_length=255, blank=True)
    email = models.EmailField(_("email"), unique=True)
    subscribed_date = models.DateTimeField(_("subscribed date"), default=timezone.now)
    active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["-subscribed_date"]
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")

    def __str__(self):
        return f"{self.name or self.email}"