from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)


from Amisacb import utils
from Amisacb.data import user_location
from .manager import (
    UserManager
)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True, blank=False)
    email = models.EmailField(max_length=50, blank=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)
    last_updated = models.DateField(auto_now_add=True)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        user = User.objects.get(username=self.username)

        profile_created, profile = Profile.objects.get_or_create(user=user)
        wallet_created, wallet = Wallet.objects.get_or_create(
            user=user
        )

        if not profile_created:
            profile.save()

        if not wallet_created:
            wallet.save()

    def __str__(self):
        return self.username

    def get_full_name(self):
        if len(self.first_name) > 0 and len(self.last_name) > 0:
            return f'{self.first_name} {self.last_name}'
        else:
            return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reference_id = models.CharField(max_length=100, blank=True, unique=True)
    state = models.CharField(max_length=15, choices=user_location, default='N/A')
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=12, blank=True, default='N/A')

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.reference_id:
            exisiting_refs = Profile.objects.values_list('reference_id')

            self.reference_id = utils.generate_referrence_id(exisiting_refs)
        super().save(*args, **kwargs)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_balance = models.FloatField(blank=True)
    wallet_status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return self.user.username

password_reset_exp = timezone.now() + timezone.timedelta(minutes=5)

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link_slug = models.CharField(max_length=100, unique=True)
    verification_code = models.CharField(max_length=6, unique=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def is_expired(self):
        if timezone.now() >= password_reset_exp:
            return True
        else:
            return False
