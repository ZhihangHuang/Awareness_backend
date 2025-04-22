from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView

urlpatterns = [
    path('register/', views.register_account),
    path('register_user/', views.register_user),
    path('users/', views.get_users),

    path('sensor_data/', views.upload_sensor_data, name='upload_sensor_data'),  
    path('get_sensor_data/', views.get_sensor_data),                            

    path('upload_device/', views.get_devices),
    path('devices/', views.get_all_devices),

    path('bluetooth_devices/', views.bluetooth_devices, name='bluetooth-devices'),
    path('bluetooth_devices/<int:device_id>/', views.bluetooth_device_detail, name='bluetooth-device-detail'),
    path('bluetooth_device_types/', views.bluetooth_device_types, name='bluetooth-device-types'),
    path('device_connection/', views.device_connection, name='device-connection'),
    path('device_connections/<int:device_id>/', views.device_connection_history, name='device-connection-history'),

    path('upload_annotation/', views.upload_annotation_data),
    path('upload_health_scores/', views.upload_health_scores),
    path('upload_notifications/', views.upload_notifications),
    path('upload_sync_logs/', views.upload_sync_logs),
    path('user_data_status/', views.user_data_status),

    path('user_settings/', views.get_user_settings),
    path('health_scores/', views.get_health_scores),
    path('notifications/', views.get_notifications),
    path('sync_logs/', views.get_sync_logs),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('protected/', views.protected_view),
    path('send-code/', views.send_verification_code),
    path('change-password/', views.change_password, name='change-password'),
    path('delete_user/<int:user_id>/', views.delete_user),
    path('activity_types/', views.get_activity_types),
    path('test/', views.test_endpoint, name='test_endpoint'),
    path("save-config/", views.save_config),
    path("get-config/", views.get_config),
    path('sensor_data/by_session/', views.get_data_by_session),
    path('public-config/', views.get_public_config),
]