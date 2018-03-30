from django.db import models
from rbac.models import User as RbacUser
import datetime
class UserInfo(models.Model):
    nickname = models.CharField(max_length=16)
    user = models.OneToOneField(RbacUser, on_delete='')

    def __str__(self):
        return self.nickname
class Order(models.Model):
    """
    报障单
    """
    title = models.CharField(verbose_name='标题',max_length=32)
    detail = models.TextField(verbose_name='详细')
    create_user = models.ForeignKey(UserInfo,related_name='aaa', on_delete='')
    # ctime = models.DateTimeField(auto_now_add=True,default=datetime.datetime.now)
    ctime = models.DateTimeField(auto_now_add=True)
    status_choice = (
        (1,'未处理'),
        (2,'处理中'),
        (3,'已处理')
    )
    status = models.IntegerField(choices=status_choice,default=1)
    processor = models.ForeignKey(UserInfo,related_name='bbb',null=True,blank=True, on_delete='')
    solution = models.TextField(null=True,blank=True)
    ptime = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.title