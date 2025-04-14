from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from core.models import Account

class AccountJWTAuthentication(JWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id_claim = 'user_id'  # 必须设置
        self.user_id_field = 'id'       # 默认是 id

    def get_user(self, validated_token):
        print("🟢 正在使用自定义 AccountJWTAuthentication 验证 token")

        try:
            user_id = validated_token[self.user_id_claim]
        except KeyError:
            raise AuthenticationFailed("Token 中没有用户标识字段")

        try:
            return Account.objects.get(**{self.user_id_field: user_id})
        except Account.DoesNotExist:
            raise AuthenticationFailed("用户不存在")