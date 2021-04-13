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

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

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

    @property
    def is_foreman(self):
        return self.groups.filter(name="foreman").exists()

    @property
    def is_cottage_worker(self):
        return self.groups.filter(name="cottage_worker").exists()

    @property
    def is_stationary_worker(self):
        return self.groups.filter(name="stationary_worker").exists()

    def __repr__(self):
        return "<User email={} groups=[{}]>".format(
            self.email, ", ".join(self.groups.values_list("name", flat=True))
        )

    def __str__(self):
        return self.email


class Slot(models.Model):

    day = models.DateField(primary_key=True)
    stationary_workers_limit = models.IntegerField(blank=True, null=True)
    is_open_for_cottage_workers = models.BooleanField(blank=True, null=True)

    @property
    def _is_open_for_cottage_workers(self):
        return False if self.is_open_for_cottage_workers is None else True

    @property
    def _stationary_workers_limit(self):
        return 0 if not self.stationary_workers_limit else self.stationary_workers_limit

    def __repr__(self):
        return (
            "<Slot day={} stationary_workers_limit={} is_open_for_cottage_workers={}>"
        ).format(
            self.day, self._stationary_workers_limit, self._is_open_for_cottage_workers
        )

    def __str__(self):
        return _("{}, stationary workers limit {}{}").format(
            self.day,
            self._stationary_workers_limit,
            _(", open for cottage workers")
            if self._is_open_for_cottage_workers
            else "",
        )


class AvailabilityHours(models.Model):

    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    hours = models.IntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = _("Availability hours")

    def __repr__(self):
        return "<AvailabilityHours user={} day={} hours={}>".format(
            self.user, self.slot.day, self.hours
        )

    def __str__(self):
        return _("{}, {}, {} hours").format(self.user, self.slot.day, self.hours)


class AvailabilityPeriodQuerySet(models.QuerySet):
    def with_timedelta(self):
        timedelta_expression = ExpressionWrapper(
            F("end") - F("start"), output_field=models.DurationField()
        )
        return self.annotate(timedelta=timedelta_expression)


class AvailabilityPeriod(models.Model):

    objects = AvailabilityPeriodQuerySet.as_manager()

    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __repr__(self):
        return "<AvailabilityPeriod user={} start={} end={}>".format(
            self.user,
            self.start.strftime(DATETIME_FORMAT),
            self.end.strftime(DATETIME_FORMAT),
        )

    def __str__(self):
        return _("{}, from {} to {}").format(
            self.user,
            self.start.strftime(DATETIME_FORMAT),
            self.end.strftime(DATETIME_FORMAT),
        )
