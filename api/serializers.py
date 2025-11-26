from rest_framework import serializers
from .models import Member, Message


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for Member model - used for displaying user data."""
    
    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Member
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'username': {
                'min_length': 3,
                'max_length': 150
            },
            'email': {
                'required': True
            }
        }

    def validate_username(self, value):
        """Check if username already exists."""
        if Member.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username already exists")
        return value

    def validate_email(self, value):
        """Check if email already exists."""
        if Member.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        """Create a new member with hashed password."""
        password = validated_data.pop('password')
        member = Member(**validated_data)
        member.set_password(password)
        member.save()
        return member


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate email and password."""
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required")

        try:
            member = Member.objects.get(email=email)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not member.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        attrs['member'] = member
        return attrs


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = Member
        fields = ['username', 'email']
        extra_kwargs = {
            'username': {
                'required': False,
                'max_length': 150
            },
            'email': {
                'required': False
            }
        }

    def validate_username(self, value):
        """Check if username already exists for other users."""
        instance = self.instance
        if Member.objects.filter(username=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("User with this username already exists")
        return value

    def validate_email(self, value):
        """Check if email already exists for other users."""
        instance = self.instance
        if Member.objects.filter(email=value).exclude(id=instance.id).exists():
            raise serializers.ValidationError("This email is already in use")
        return value


class MessageAuthorSerializer(serializers.ModelSerializer):
    """Serializer for message author information."""
    
    class Meta:
        model = Member
        fields = ['id', 'username']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    author = MessageAuthorSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'author', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate_text(self, value):
        """Validate message text."""
        if not value or not value.strip():
            raise serializers.ValidationError("This field is required")
        if len(value) > 5000:
            raise serializers.ValidationError("Message text is too long")
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    class Meta:
        model = Message
        fields = ['text']
        extra_kwargs = {
            'text': {
                'required': True,
                'min_length': 1,
                'max_length': 5000
            }
        }

    def validate_text(self, value):
        """Validate message text."""
        if not value or not value.strip():
            raise serializers.ValidationError("This field is required")
        return value
