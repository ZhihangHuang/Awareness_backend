from rest_framework import serializers
from .models import (
    Account, Users, Devices, SensorData, Annotations, UserSettings, 
    HealthScores, Notifications, SyncLogs, ActivityType, 
    BluetoothDeviceType, DeviceConnectionLog
)
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'password', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'password', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Account with this email does not exist.")
        if not check_password(password, account.password):
            raise serializers.ValidationError("Incorrect password.")

        data.update({
            'account_id': account.id,
            'email': account.email,
        })
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'account', 'name', 'gender', 'avatar']
        extra_kwargs = {'account': {'required': False, 'allow_null': True}}

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Devices
        fields = [
            'id', 'user', 'device_id', 'device_type', 'paired_at',
            'bluetooth_mac', 'is_active', 'manufacturer', 'model_number', 'firmware_version'
        ]

# ✅ 活动类型序列化器 - 更新字段
class ActivityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityType
        fields = ['id', 'name', 'description', 'is_default', 'icon_name']

# ✅ 修改：SensorData序列化器 - 添加新字段
class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = [
            'id', 'user', 'activity', 'data_type', 'value', 'unit', 
            'recorded_at', 'synced_at', 'time_index', 'device', 
            'raw_data', 'quality'
        ]
        extra_kwargs = {
            'activity': {'required': False, 'allow_null': True},
            'recorded_at': {'required': False, 'allow_null': True},
            'synced_at': {'required': False, 'allow_null': True},
            'device': {'required': False, 'allow_null': True},
        }

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotations
        fields = ['user', 'status', 'synced_at', 'details']

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['user', 'language', 'unit_system', 'dark_mode', 'synced_at']

class HealthScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthScores
        fields = ['user', 'score_type', 'score_value', 'calculated_at']

class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['user', 'language', 'unit_system', 'dark_mode']

class SyncLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLogs
        fields = ['user', 'status', 'synced_at', 'details']

# 新增：蓝牙设备类型序列化器
class BluetoothDeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BluetoothDeviceType
        fields = ['id', 'name', 'identifier', 'description', 'supported_data_types']

# 新增：设备连接日志序列化器
class DeviceConnectionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConnectionLog
        fields = ['id', 'device', 'user', 'connected_at', 'disconnected_at', 'connection_status', 'error_message']
        read_only_fields = ['id', 'connected_at']