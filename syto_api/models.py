from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import ExpressionWrapper, F
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(self.normalize_email(email), **extra_fields)
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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    # based on django.contrib.auth.models.AbstractUser
    first_name = models.CharField(_("first name"), max_length=150, null=True)
    last_name = models.CharField(_("last name"), max_length=150, null=True)
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
    evidence_number = models.CharField(max_length=11, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __repr__(self):
        return "<{} groups=[{}]>".format(
            self.email, ", ".join(self.groups.values_list("name", flat=True))
        )

    def __str__(self):
        return self.email


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class AvailabilityHours(models.Model):

    day = models.DateField()
    hours = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
