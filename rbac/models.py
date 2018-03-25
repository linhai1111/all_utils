from django.db import models


class User(models.Model):
    """
    用户表
    """
    username = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    email = models.EmailField(verbose_name='邮箱')

    def __str__(self):
        return self.username


class Role(models.Model):
    """
    角色表
    """
    caption = models.CharField(verbose_name='角色', max_length=32)

    def __str__(self):
        return self.caption


class User2Role(models.Model):
    """
    用户角色关系表
    """
    user = models.ForeignKey(User, verbose_name='用户', related_name='roles')
    role = models.ForeignKey(Role, verbose_name='角色', related_name='users')

    def __str__(self):
        return '%s-%s' % (self.user.username, self.role.caption,)


class Menu(models.Model):
    """
    菜单表
    """
    caption = models.CharField(verbose_name='菜单名称', max_length=32)
    parent = models.ForeignKey('self', verbose_name='父菜单', related_name='p', null=True, blank=True)

    def __str__(self):
        prev = ""
        parent = self.parent
        while True:
            if parent:
                prev = prev + '-' + str(parent.caption)
                parent = parent.parent
            else:
                break
        return '%s-%s' % (prev, self.caption,)


class Permission(models.Model):
    """
    权限
    """
    caption = models.CharField(verbose_name='权限', max_length=32)
    url = models.CharField(verbose_name='URL正则', max_length=128)
    menu = models.ForeignKey(Menu, verbose_name='所属菜单', related_name='permissions',null=True,blank=True)

    def __str__(self):
        return "%s-%s" % (self.caption, self.url,)


class Action(models.Model):
    """
    操作：增删改查
    """
    caption = models.CharField(verbose_name='操作标题', max_length=32)
    code = models.CharField(verbose_name='方法', max_length=32)

    def __str__(self):
        return self.caption


class Permission2Action2Role(models.Model):
    """
    权限操作关系表
    """
    permission = models.ForeignKey(Permission, verbose_name='权限URL', related_name='actions')
    action = models.ForeignKey(Action, verbose_name='操作', related_name='permissions')
    role = models.ForeignKey(Role, verbose_name='角色', related_name='p2as')

    class Meta:
        unique_together = (
            ('permission', 'action', 'role'),
        )

    def __str__(self):
        return "%s-%s-%s" % (self.permission, self.action, self.role,)