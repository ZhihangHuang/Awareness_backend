from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.contrib.auth import get_user_model

# 用户管理器
class AccountManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('用户必须有邮箱')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# 自定义账户模型
class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # 添加这个字段
    is_superuser = models.BooleanField(default=False)

    objects = AccountManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = 'account'
class Users(models.Model):
    account = models.ForeignKey(Account, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=6, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'users'

class Devices(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    device_id = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    paired_at = models.DateTimeField(blank=True, null=True)
    
    # 新增字段：设备蓝牙MAC地址
    bluetooth_mac = models.CharField(max_length=20, blank=True, null=True)
    # 新增字段：设备状态
    is_active = models.BooleanField(default=True)
    # 新增字段：设备制造商
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    # 新增字段：设备型号
    model_number = models.CharField(max_length=100, blank=True, null=True)
    # 新增字段：固件版本
    firmware_version = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.device_type} - {self.device_id}"

    class Meta:
        db_table = 'devices'

# ✅ 现有：活动类型表
class ActivityType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # 新增字段：活动描述
    description = models.TextField(blank=True, null=True)
    
    # 新增字段：默认活动
    is_default = models.BooleanField(default=False)
    # 新增字段：活动图标
    icon_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'activity_type'

# ✅ 修改：SensorData 使用 ActivityType 外键
class SensorData(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    activity = models.ForeignKey(ActivityType, models.SET_NULL, blank=True, null=True)
    data_type = models.CharField(max_length=100, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    recorded_at = models.DateTimeField(blank=True, null=True)
    synced_at = models.DateTimeField(blank=True, null=True)
    time_index = models.FloatField(null=True, blank=True)  # 现有，记录数据点的时间索引
    session_id = models.CharField(max_length=100, blank=True, null=True)
    # 新增字段：设备外键
    device = models.ForeignKey(Devices, models.SET_NULL, blank=True, null=True, related_name="sensor_data")
    # 新增字段：原始数据JSON
    raw_data = models.JSONField(blank=True, null=True)
    # 新增字段：数据质量等级（例如：优 good、中 fair、差 poor）
    quality = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.data_type}: {self.value} {self.unit or ''} - {self.recorded_at}"

    class Meta:
        db_table = 'sensor_data'
        # 新增索引提高查询性能
        indexes = [
            models.Index(fields=['user', 'data_type', 'recorded_at']),
            models.Index(fields=['device', 'recorded_at']),
            models.Index(fields=['activity', 'recorded_at']),
        ]

# 其余模型保持不变
class Annotations(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    synced_at = models.DateTimeField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'annotations'

class UserSettings(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    unit_system = models.CharField(max_length=50, blank=True, null=True)
    dark_mode = models.IntegerField(blank=True, null=True)
    synced_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'user_settings'

class HealthScores(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    score_type = models.CharField(max_length=50, blank=True, null=True)
    score_value = models.FloatField(blank=True, null=True)
    calculated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'health_scores'

class Notifications(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    unit_system = models.CharField(max_length=50, blank=True, null=True)
    dark_mode = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'notifications'

class SyncLogs(models.Model):
    user = models.ForeignKey(Users, models.DO_NOTHING, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    synced_at = models.DateTimeField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sync_logs'

class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.email} - {self.code}'

# 新增：蓝牙设备类型模型
class BluetoothDeviceType(models.Model):
    name = models.CharField(max_length=100)
    identifier = models.CharField(max_length=50, unique=True)  # 例如: 'embracePlus', 'e4Wristband'
    description = models.TextField(blank=True, null=True)
    supported_data_types = models.JSONField(default=list)  # 支持的数据类型列表
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'bluetooth_device_type'

# 新增：设备连接历史
class DeviceConnectionLog(models.Model):
    device = models.ForeignKey(Devices, on_delete=models.CASCADE, related_name='connection_logs')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(blank=True, null=True)
    connection_status = models.CharField(max_length=50)  # 例如: 'connected', 'disconnected', 'failed'
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.device} - {self.connection_status} at {self.connected_at}"
    
    class Meta:
        db_table = 'device_connection_log'