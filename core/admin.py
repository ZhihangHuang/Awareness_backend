from django.contrib import admin
from .models import (
    Account, Users, Devices, SensorData, Annotations, UserSettings, 
    HealthScores, Notifications, SyncLogs, ActivityType, 
    BluetoothDeviceType, DeviceConnectionLog
)

admin.site.register(Account)
admin.site.register(Users)

# 设备管理
class DevicesAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'device_type', 'user', 'paired_at', 'is_active')
    list_filter = ('device_type', 'is_active')
    search_fields = ('device_id', 'device_type')

admin.site.register(Devices, DevicesAdmin)

# 传感器数据管理
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'value', 'unit', 'user', 'recorded_at', 'device')
    list_filter = ('data_type', 'activity')
    search_fields = ('data_type',)
    date_hierarchy = 'recorded_at'

admin.site.register(SensorData, SensorDataAdmin)

# 活动类型管理
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_default', 'icon_name')
    list_filter = ('is_default',)
    search_fields = ('name',)

admin.site.register(ActivityType, ActivityTypeAdmin)

# 蓝牙设备类型管理
class BluetoothDeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'description')
    search_fields = ('name', 'identifier')

admin.site.register(BluetoothDeviceType, BluetoothDeviceTypeAdmin)

# 设备连接日志管理
class DeviceConnectionLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'user', 'connection_status', 'connected_at', 'disconnected_at')
    list_filter = ('connection_status',)
    search_fields = ('device__device_id', 'user__name')
    date_hierarchy = 'connected_at'

admin.site.register(DeviceConnectionLog, DeviceConnectionLogAdmin)

# 其他模型保持不变
admin.site.register(Annotations)
admin.site.register(UserSettings)
admin.site.register(HealthScores)
admin.site.register(Notifications)
admin.site.register(SyncLogs)