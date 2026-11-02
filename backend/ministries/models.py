from django.conf import settings
from django.db import models

from members.models import Member


class Ministry(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    coordinator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='coordinated_ministries')
    members = models.ManyToManyField(Member, through='MinistryMembership', related_name='ministries')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class MinistryMembership(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='ministry_memberships')
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('ministry', 'member'), name='unique_ministry_member')]
