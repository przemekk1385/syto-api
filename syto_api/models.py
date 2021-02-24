from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class MyUserManage(BaseUserManager):
    def create_user(
        self,
        email,
        first_name,
        last_name,
        is_new,
        evidence_number,
        birth_date,
        password=None,
    ):
        if not email:
            raise ValueError("Użytkownik musi mieć email")
        if not first_name:
            raise ValueError("Użytkownik musi podać imię")
        if not last_name:
            raise ValueError("Użytkownik musi podać nazwisko")
        if not is_new:
            raise ValueError("Użytkownik musi zaznaczyć")
        if not evidence_number:
            raise ValueError("Użytkownik musi podać numer pesel")
        if not birth_date:
            raise ValueError("Użytkownik musi podać date urodzenia")

        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            is_new=is_new,
            evidence_number=evidence_number,
            birth_date=birth_date,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):

        user = self.create_user(
            email,
            password=password,
            birth_date=None,
            first_name=None,
            last_name=None,
            is_new=None,
            evidence_number=None,
        )
        user.is_admin = True
        user.is_superuser = (True,)
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_new = models.BooleanField(default=False)
    evidence_number = models.IntegerField(max_length=11)
    birth_date = models.DateField(
        auto_created=False, auto_now=False, auto_now_add=False
    )

    STATIONARY_WORKER = 1
    HOME_WORKER = 2

    ROLE_CHOICE = (
        (STATIONARY_WORKER, "Pracownik stacjonarny"),
        (HOME_WORKER, "Pracownik chałupniczy"),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True)

    object = MyUserManage()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "is_new",
        "evidence_number",
        "birth_date",
    ]

    def __str__(self):
        return self.email + " " + self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
