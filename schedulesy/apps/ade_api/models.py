from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import generate_uuid


class Resource(models.Model):
    ext_id = models.CharField(max_length=25, unique=True, db_index=True)
    fields = JSONField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', blank=True, null=True, related_name='children',
        on_delete=models.CASCADE)
    events = JSONField(blank=True, null=True)

    class Meta:
        verbose_name = _('Resource')
        verbose_name_plural = _('Resources')

    def __str__(self):
        return '{0.ext_id}'.format(self)


class Fingerprint(models.Model):
    ext_id = models.CharField(max_length=25)
    method = models.CharField(max_length=50)
    fingerprint = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Fingerprint')
        verbose_name_plural = _('Fingerprints')

    def __str__(self):
        return '{0.ext_id} - {0.method}'.format(self)


class DisplayType(models.Model):
    name = models.CharField(_('Name'), max_length=256, unique=True)

    class Meta:
        verbose_name = _('Display type')
        verbose_name_plural = _('Display types')

    def __str__(self):
        return '{0.name}'.format(self)


class AdeConfig(models.Model):

    ade_url = models.URLField(_('ADE URL'))
    parameters = JSONField(_('Parameters'))

    class Meta:
        verbose_name = _('ADE config')
        verbose_name_plural = _('ADE config')

    def __str__(self):
        return str(_('ADE config'))

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class LocalCustomization(models.Model):
    """
    Local customization. It contains mirror data from the ADE model for
    standalone usage.
    """
    customization_id = models.IntegerField(unique=True)
    directory_id = models.CharField(
        max_length=32, db_column='uds_directory_id')
    username = models.CharField(
        max_length=32, db_column='uid', blank=True, unique=True)
    resources = models.ManyToManyField(Resource)

    class Meta:
        verbose_name = _('Local Customization')
        verbose_name_plural = _('Local Customizations')

    def __str__(self):
        return '{0.username}'.format(self)


class Access(models.Model):

    key = models.CharField(
        max_length=36, unique=True, default=generate_uuid)
    creation_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=256)
    customization = models.ForeignKey(
        'ade_api.LocalCustomization', related_name='accesses',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Access')
        verbose_name_plural = _('Accesses')
        unique_together = ('name', 'customization')

    def __str__(self):
        return '{0.key} ({0.name})'.format(self)
