from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings
import random,string
from django.core.cache import cache
from .models import EmailVerification
from .serializers import RegisterSerializer
from django.views.decorators.csrf import csrf_exempt
import traceback
from django.contrib.auth.hashers import make_password
from core.auth import AccountJWTAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from .models import ActivityType, BluetoothDeviceType, DeviceConnectionLog
from .serializers import (
    ActivityTypeSerializer, BluetoothDeviceTypeSerializer, 
    DeviceConnectionLogSerializer
)
from django.utils import timezone
from .models import SensorData

from .models import (
    Account, Users, Devices, SensorData, Annotations, 
    UserSettings, HealthScores, Notifications, SyncLogs
)
from .serializers import (
    AccountSerializer, RegisterSerializer, UserSerializer, SensorDataSerializer, 
    DeviceSerializer, AnnotationSerializer, 
    UserSettingsSerializer, HealthScoresSerializer, NotificationsSerializer, SyncLogsSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@csrf_exempt
@api_view(['POST'])
def register_account(request):
    email = request.data.get('email')
    code = request.data.get('code')

    try:
        verification = EmailVerification.objects.get(email=email)
        if verification.code != code:
            return Response({'error': '验证码不正确'}, status=status.HTTP_400_BAD_REQUEST)
    except EmailVerification.DoesNotExist:
        return Response({'error': '请先获取验证码'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            verification.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(traceback.format_exc())  # 强制输出错误日志
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    print(serializer.errors)  # 如果验证失败，也输出错误信息
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login_account(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        account = Account.objects.get(email=email)
        if account.password == password:
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found.'}, status=404)

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@authentication_classes([AccountJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_users(request):
    if request.method == 'GET':
        # 获取当前登录账号的所有用户
        users = Users.objects.filter(account=request.user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 自动将新用户绑定到当前登录账号
        data = request.data.copy()
        data['account'] = request.user.id

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
# 暂时注释掉权限验证
# @permission_classes([IsAuthenticated])
def upload_sensor_data(request):
    print("\n==== 传感器数据上传请求 ====")
    print("✅ 请求已到达后端")
    print("📄 请求头:", request.headers)
    print("📦 请求体:", request.data)
    
    data = request.data.copy()
    user_id = request.data.get('user')
    
    try:
        user = Users.objects.get(id=user_id)
        print("✅ 用户存在:", user.id)
    except Users.DoesNotExist:
        print("❌ 用户不存在:", user_id)
        return Response({"user": ["无效的用户ID"]}, status=400)
    
    # 处理设备关联
    device_identifier = data.get('device_identifier')
    device_instance = None
    if device_identifier:
        try:
            device_instance = Devices.objects.get(bluetooth_mac=device_identifier)
            print("✅ 匹配到设备:", device_instance.id)
        except Devices.DoesNotExist:
            print("❌ 没有找到对应的设备:", device_identifier)
            # 如果设备不存在，尝试创建新设备
            device_type = data.get('device_type', 'unknown')
            device_instance = Devices.objects.create(
                user=user,
                device_id=f"auto_{device_identifier}",
                device_type=device_type,
                bluetooth_mac=device_identifier,
                paired_at=timezone.now()
            )
            print("✅ 自动创建设备:", device_instance.id)
        
    serializer = SensorDataSerializer(data=data)
    if serializer.is_valid():
        sensor_data = serializer.save(user=user, device=device_instance)
        print("✅ 数据保存成功")
        return Response(SensorDataSerializer(sensor_data).data, status=201)
    else:
        print("❌ 数据验证失败:", serializer.errors)
        return Response(serializer.errors, status=400)
    
@api_view(['GET', 'POST'])
def get_devices(request):
    if request.method == 'GET':
        devices = Devices.objects.all()
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_annotation_data(request):
    serializer = AnnotationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_health_scores(request):
    serializer = HealthScoresSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_notifications(request):
    serializer = NotificationsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def upload_sync_logs(request):
    serializer = SyncLogsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_sensor_data(request):
    user_id = request.GET.get('user')
    data = SensorData.objects.filter(user_id=user_id) if user_id else SensorData.objects.all()
    serializer = SensorDataSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_health_scores(request):
    user_id = request.GET.get('user')
    scores = HealthScores.objects.filter(user_id=user_id) if user_id else HealthScores.objects.all()
    serializer = HealthScoresSerializer(scores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_all_devices(request):
    user_id = request.GET.get('user')
    devices = Devices.objects.filter(user_id=user_id) if user_id else Devices.objects.all()
    serializer = DeviceSerializer(devices, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_user_settings(request):
    user_id = request.GET.get('user')
    settings = UserSettings.objects.filter(user_id=user_id) if user_id else UserSettings.objects.all()
    serializer = UserSettingsSerializer(settings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_notifications(request):
    user_id = request.GET.get('user')
    notifications = Notifications.objects.filter(user_id=user_id) if user_id else Notifications.objects.all()
    serializer = NotificationsSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_sync_logs(request):
    user_id = request.GET.get('user')
    logs = SyncLogs.objects.filter(user_id=user_id) if user_id else SyncLogs.objects.all()
    serializer = SyncLogsSerializer(logs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': 'success！', 'user_id': request.user.id})

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# 发送验证码到邮箱
@api_view(['POST'])
def send_verification_code(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    code = generate_code()

    # 保存到数据库（存在则更新）
    EmailVerification.objects.update_or_create(email=email, defaults={'code': code})

    # 发送邮件
    send_mail(
        'Your Verification Code',
        f'Your verification code is: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return Response({'message': 'Verification code sent!'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user  # 自动获取当前登录用户
    new_password = request.data.get('new_password')

    if not new_password:
        return Response({"detail": "New password is required."}, status=400)

    user.password = make_password(new_password)
    user.save()
    return Response({"message": "Password changed successfully."})

@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
        user.delete()
        return Response({'message': 'User deleted'}, status=200)
    except Users.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    
@api_view(['GET'])
def get_activity_types(request):
    activity_types = ActivityType.objects.all()
    serializer = ActivityTypeSerializer(activity_types, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def test_endpoint(request):
    print("\n==== 测试端点被访问 ====")
    print("📄 请求头:", request.headers)
    return Response({"message": "测试成功", "time": timezone.now().isoformat()}, status=200)

# 新增：蓝牙设备类型管理
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bluetooth_device_types(request):
    """
    获取或创建蓝牙设备类型
    """
    if request.method == 'GET':
        device_types = BluetoothDeviceType.objects.all()
        serializer = BluetoothDeviceTypeSerializer(device_types, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BluetoothDeviceTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 修改：蓝牙设备管理
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bluetooth_devices(request):
    """
    获取或注册蓝牙设备
    """
    if request.method == 'GET':
        user_id = request.query_params.get('user_id')
        if user_id:
            # 如果指定了用户ID，只显示该用户的设备
            devices = Devices.objects.filter(user_id=user_id)
            
            # 验证该用户是否属于当前账户
            try:
                user = Users.objects.get(id=user_id)
                if user.account_id != request.user.id:
                    return Response(
                        {"error": "您没有权限查看此用户的设备"}, 
                        status=403
                    )
            except Users.DoesNotExist:
                return Response({"error": "用户不存在"}, status=404)
        else:
            # 如果没有指定用户ID，显示当前账户下所有用户的所有设备
            users = Users.objects.filter(account=request.user)
            devices = Devices.objects.filter(user__in=users)
        
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # 检查用户是否属于当前账户
        user_id = request.data.get('user')
        if user_id:
            try:
                user = Users.objects.get(id=user_id)
                if user.account_id != request.user.id:
                    return Response(
                        {"error": "您没有权限为此用户添加设备"}, 
                        status=403
                    )
            except Users.DoesNotExist:
                return Response({"error": "用户不存在"}, status=400)
        
        # 检查设备是否已存在
        device_id = request.data.get('device_id')
        try:
            # 如果指定了用户ID，查找该用户的设备
            if user_id:
                device = Devices.objects.get(device_id=device_id, user_id=user_id)
            else:
                # 如果没有指定用户ID，查找当前账户下任何用户的该设备
                users = Users.objects.filter(account=request.user)
                device = Devices.objects.get(device_id=device_id, user__in=users)
            
            # 更新设备信息
            serializer = DeviceSerializer(device, data=request.data, partial=True)
        except Devices.DoesNotExist:
            # 创建新设备
            serializer = DeviceSerializer(data=request.data)
        
        if serializer.is_valid():
            device = serializer.save()
            
            # 记录连接日志
            DeviceConnectionLog.objects.create(
                device=device,
                user_id=user_id,
                connection_status='registered',
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 新增：单个蓝牙设备管理
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def bluetooth_device_detail(request, device_id):
    """
    获取、更新或删除单个蓝牙设备
    """
    try:
        device = Devices.objects.get(id=device_id)
        
        # 验证设备归属权
        users = Users.objects.filter(account=request.user)
        if device.user not in users:
            return Response({"error": "您没有权限操作此设备"}, status=403)
            
    except Devices.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DeviceSerializer(device)
        return Response(serializer.data)
        
    
    elif request.method == 'PUT':
        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# 新增：设备连接记录
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def device_connection(request):
    """
    记录设备连接状态变化
    """
    # 验证设备和用户归属权
    device_id = request.data.get('device')
    user_id = request.data.get('user')
    
    try:
        device = Devices.objects.get(id=device_id)
        user = Users.objects.get(id=user_id)
        
        # 验证用户是否属于当前账户
        if user.account_id != request.user.id:
            return Response({"error": "您没有权限记录此用户的设备连接"}, status=403)
            
    except Devices.DoesNotExist:
        return Response({"error": "设备不存在"}, status=404)
    except Users.DoesNotExist:
        return Response({"error": "用户不存在"}, status=404)
    
    serializer = DeviceConnectionLogSerializer(data=request.data)
    if serializer.is_valid():
        # 检查是否是断开连接的请求
        if request.data.get('connection_status') == 'disconnected':
            # 查找最近的连接记录并更新断开时间
            try:
                log = DeviceConnectionLog.objects.filter(
                    device_id=device_id,
                    user_id=user_id,
                    connection_status='connected',
                    disconnected_at__isnull=True
                ).latest('connected_at')
                
                log.disconnected_at = timezone.now()
                log.connection_status = 'disconnected'
                log.save()
                
                serializer = DeviceConnectionLogSerializer(log)
                return Response(serializer.data)
            except DeviceConnectionLog.DoesNotExist:
                pass
        
        # 创建新的连接记录
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 新增：获取设备连接历史
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_connection_history(request, device_id):
    """
    获取设备的连接历史记录
    """
    # 验证设备归属权
    try:
        device = Devices.objects.get(id=device_id)
        users = Users.objects.filter(account=request.user)
        if device.user not in users:
            return Response({"error": "您没有权限查看此设备的连接历史"}, status=403)
    except Devices.DoesNotExist:
        return Response({"error": "设备不存在"}, status=404)
    
    logs = DeviceConnectionLog.objects.filter(device_id=device_id).order_by('-connected_at')
    
    # 支持分页
    limit = int(request.query_params.get('limit', 20))
    offset = int(request.query_params.get('offset', 0))
    
    logs = logs[offset:offset+limit]
    serializer = DeviceConnectionLogSerializer(logs, many=True)
    return Response(serializer.data)

# 新增：从蓝牙设备上传传感器数据批量接口
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_bulk_sensor_data(request):
    """
    批量上传传感器数据
    """
    print("\n==== 批量传感器数据上传请求 ====")
    print("✅ 请求已到达后端")
    print("📦 请求体大小:", len(str(request.data)))
    
    user_id = request.data.get('user_id')
    device_id = request.data.get('device_id')
    data_points = request.data.get('data_points', [])
    
    if not user_id or not device_id or not data_points:
        return Response({"error": "必须提供user_id、device_id和data_points"}, status=400)
    
    # 验证用户归属权
    try:
        user = Users.objects.get(id=user_id)
        if user.account_id != request.user.id:
            return Response({"error": "您没有权限为此用户上传数据"}, status=403)
    except Users.DoesNotExist:
        return Response({"error": "用户不存在"}, status=400)
    
    try:
        device = Devices.objects.get(device_id=device_id)
    except Devices.DoesNotExist:
        # 自动创建设备
        device = Devices.objects.create(
            user=user,
            device_id=device_id,
            device_type=request.data.get('device_type', 'unknown'),
            paired_at=timezone.now()
        )
    
    # 批量创建数据点
    created_count = 0
    errors = []
    
    for data_point in data_points:
        try:
            # 设置必要字段
            data_point['user'] = user.id
            data_point['device'] = device.id
            
            # 确保有记录时间
            if 'recorded_at' not in data_point:
                data_point['recorded_at'] = timezone.now()
            
            serializer = SensorDataSerializer(data=data_point)
            if serializer.is_valid():
                serializer.save()
                created_count += 1
            else:
                errors.append({"data": data_point, "errors": serializer.errors})
        except Exception as e:
            errors.append({"data": data_point, "exception": str(e)})
    
    response_data = {
        "message": f"成功创建 {created_count} 条数据点，失败 {len(errors)} 条",
        "total": len(data_points),
        "created": created_count,
        "failed": len(errors)
    }
    
    if errors:
        response_data["errors"] = errors[:10]  
        if len(errors) > 10:
            response_data["errors_truncated"] = True
    
    return Response(response_data, status=status.HTTP_201_CREATED if created_count > 0 else status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_data_status(request):
    user_ids = SensorData.objects.filter(user__isnull=False).values_list('user_id', flat=True).distinct()
    return Response({'users_with_data': list(user_ids)})

CURRENT_CONFIG = {}

@csrf_exempt
def save_config(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            CURRENT_CONFIG.update(data)
            print("✅ 已保存配置:", CURRENT_CONFIG)
            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

def get_config(request):
    return JsonResponse(CURRENT_CONFIG, status=200)