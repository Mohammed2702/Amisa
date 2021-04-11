from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model

import datetime

from Amisacb import utils


User = get_user_model()


class CodeGroup(models.Model):
    code_batch_number = models.CharField(max_length=100, blank=False, unique=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Code Group'
        verbose_name_plural = 'Code Groups'

    def __str__(self):
        return self.code_batch_number

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code_batch_number)
        super().save(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('codes:code_batch_sheet', args=[self.slug])

    def create_codes(self, **kwargs):
        EXISTING_CODES = Code.objects.values_list('code')

        batch_number = CodeGroup.objects.get(code_batch_number=kwargs['code_batch_number'])
        number_of_codes = kwargs['number_of_codes']
        amount_per_code = kwargs['amount_per_code']
        expiry_date = kwargs['expiry_date']
        date = expiry_date.split(' ')[0].split('/')
        day = int(date[1])
        month = int(date[0])
        year = int(date[2])
        time = expiry_date.split(' ')[1].split(' ')[0].split(':')
        hour = int(time[0])
        minute = int(time[1])

        meridian = expiry_date.split(' ')[1]

        if meridian == 'PM':
            if hour >= 12:
                hour += 12

            if hour == 24:
                hour = 0

        expiry_date = datetime.datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute
        )

        for _ in range(int(number_of_codes)):
            code = utils.generate_code(EXISTING_CODES)
            new_code = Code.objects.create(
                code_group=batch_number,
                code=code,
                amount=amount_per_code,
                expiry_date=expiry_date
            )
            new_code.save()


class Code(models.Model):
    code_group = models.ForeignKey(CodeGroup, on_delete=models.CASCADE)
    code = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
    )
    amount = models.PositiveIntegerField(default=100, blank=False)
    status = models.BooleanField(default=True)
    used_by = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=20, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Code'
        verbose_name_plural = 'Codes'

    def __str__(self):
        return self.code

    def is_expired(self):
        if timezone.now() >= self.expiry_date:
            return True
        else:
            return False

    def get_serial_number(self):
        return f'AC-{self.id}'

    def get_used_by(self):
        user = None

        if not self.status:
            if len(self.used_by) > 0:
                user = User.objects.get(username=self.used_by)

        return user

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
    
        super().save(*args, **kwargs)
