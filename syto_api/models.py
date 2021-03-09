from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import ExpressionWrapper, F
from django.utils.translation import gettext_lazy as _
from phonenumber_field import modelfields


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

    def create_user(
        self,
        email,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # based on django.contrib.auth.models.AbstractUser
    first_name = models.CharField(
        _("first name"), max_length=150, blank=True, null=True
    )
    last_name = models.CharField(_("last name"), max_length=150, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    # extra fields
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = modelfields.PhoneNumberField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __repr__(self):
        return "<User email={} groups=[{}]>".format(
            self.email, ", ".join(self.groups.values_list("name", flat=True))
        )

    def __str__(self):
        return self.email


class AvailabilityHours(models.Model):

    day = models.DateField()
    hours = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __repr__(self):
        return "<AvailabilityHours day={} hours={}>".format(self.day, self.hours)

    def __str__(self):
        return _("{}, {} hours").format(self.day, self.hours)


class AvailabilityPeriodQuerySet(models.QuerySet):
    def with_timedelta(self):
        timedelta_expression = ExpressionWrapper(
            F("end") - F("start"), output_field=models.DurationField()
        )
        return self.annotate(timedelta=timedelta_expression)


class AvailabilityPeriod(models.Model):

    objects = AvailabilityPeriodQuerySet.as_manager()

    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __repr__(self):
        return "<AvailabilityPeriod start={} end={}>".format(self.start, self.end)

    def __str__(self):
        return "{}-{}".format(
            self.start.strftime("%Y-%m-%d %H:%M"), self.end.strftime("%H:%M")
        )
