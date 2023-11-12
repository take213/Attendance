from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Attendance(models.Model):
    # CASCADE設定のため、ユーザーが削除されると登録内容も削除
    STATE_TYPE = [
        ('開始', '開始'),
        ('停止', '停止'),
        ('終了', '終了')
    ]
    HOUR_CANDIDATE = [(i, i) for i in range(24)]
    MINUTE_CANDIDATE = [[i]*2 for i in range(60)]
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True, blank=False)
    hour = models.IntegerField(choices=HOUR_CANDIDATE)
    minute = models.IntegerField(choices=MINUTE_CANDIDATE)
    state = models.CharField(max_length=6, choices=STATE_TYPE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user, self.state

    class Meta:
        ordering = ['hour', 'minute']
