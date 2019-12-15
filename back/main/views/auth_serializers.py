from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` must be implemented.')

    # TODO(gregory): валидирует ли set_password?
    # def validate_password(self, password):
    #     raise serializers.ValidationError('The two password fields didn't match.')
    #     return validate_password(password)

    def validate(self, data):
        print('validate', data)
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')

        print('validated_data', validated_data)

        user_model = get_user_model()
        user = user_model(**validated_data)
        user.set_password(password)

        # Run model validations
        try:
            user.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        user.save()

        return user
