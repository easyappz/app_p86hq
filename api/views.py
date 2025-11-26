from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .serializers import (
    MessageSerializer,
    MemberSerializer,
    RegisterSerializer,
    LoginSerializer
)
from .models import Member


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: MessageSerializer}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        serializer = MessageSerializer(data)
        return Response(serializer.data)


class RegisterView(APIView):
    """
    API endpoint for user registration.
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: MemberSerializer,
            400: dict
        },
        description="Register a new user account"
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member = serializer.save()
        member_serializer = MemberSerializer(member)
        
        return Response(
            {
                "message": "User registered successfully",
                "user": member_serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    API endpoint for user login.
    Sets HttpOnly cookie for session authentication.
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: MemberSerializer,
            400: dict,
            401: dict
        },
        description="Login user with email and password"
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Invalid credentials",
                    "details": {"non_field_errors": serializer.errors.get('non_field_errors', ['Invalid email or password'])}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member = serializer.validated_data['member']
        
        # Store member ID in session
        request.session['member_id'] = member.id
        request.session.save()
        
        member_serializer = MemberSerializer(member)
        
        response = Response(
            {
                "message": "Login successful",
                "user": member_serializer.data
            },
            status=status.HTTP_200_OK
        )
        
        return response


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Clears the session cookie.
    """

    @extend_schema(
        responses={
            200: dict,
            401: dict
        },
        description="Logout current user"
    )
    def post(self, request):
        member_id = request.session.get('member_id')
        
        if not member_id:
            return Response(
                {
                    "error": "Authentication required",
                    "details": {}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Clear session
        request.session.flush()
        
        response = Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK
        )
        
        return response


class CurrentUserView(APIView):
    """
    API endpoint to get current authenticated user information.
    """

    @extend_schema(
        responses={
            200: MemberSerializer,
            401: dict
        },
        description="Get current authenticated user"
    )
    def get(self, request):
        member_id = request.session.get('member_id')
        
        if not member_id:
            return Response(
                {
                    "error": "Authentication required",
                    "details": {}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            request.session.flush()
            return Response(
                {
                    "error": "Authentication required",
                    "details": {}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
