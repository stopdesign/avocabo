from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from django.conf import settings
from django.views.decorators.debug import sensitive_post_parameters

from rest_auth.app_settings import (TokenSerializer, JWTSerializer, create_token)
from rest_auth.models import TokenModel
from rest_auth.utils import jwt_encode

from .auth_serializers import RegisterSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test(request):
    print('request.auth', request.auth)
    print('request.user', request.user)

    username = request.user.username

    return Response({'user': username}, status=HTTP_200_OK)


@permission_classes([AllowAny])
class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    token_model = TokenModel
    token = None

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': user,
                'token': self.token
            }
            return JWTSerializer(data).data
        else:
            return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        print('request.data', request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save()
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(user)
        else:
            create_token(self.token_model, user, serializer)
        return user
