from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .serializers import (
    MessageSerializer,
    MessageCreateSerializer,
    MemberSerializer,
    RegisterSerializer,
    LoginSerializer,
    ProfileUpdateSerializer
)
from .models import Member, Message


class HelloView(APIView):
    """
    A simple API endpoint that returns a greeting message.
    """

    @extend_schema(
        responses={200: dict}, description="Get a hello world message"
    )
    def get(self, request):
        data = {"message": "Hello!", "timestamp": timezone.now()}
        return Response(data)


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


class ProfileView(APIView):
    """
    API endpoint to get and update current user profile.
    """

    def get_authenticated_member(self, request):
        """Helper method to get authenticated member."""
        member_id = request.session.get('member_id')
        
        if not member_id:
            return None
        
        try:
            return Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            request.session.flush()
            return None

    @extend_schema(
        responses={
            200: MemberSerializer,
            401: dict
        },
        description="Get current user profile"
    )
    def get(self, request):
        member = self.get_authenticated_member(request)
        
        if not member:
            return Response(
                {
                    "error": "Authentication required",
                    "details": {}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProfileUpdateSerializer,
        responses={
            200: MemberSerializer,
            400: dict,
            401: dict
        },
        description="Update current user profile"
    )
    def put(self, request):
        member = self.get_authenticated_member(request)
        
        if not member:
            return Response(
                {
                    "error": "Authentication required",
                    "details": {}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = ProfileUpdateSerializer(member, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save()
        response_serializer = MemberSerializer(member)
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MessagesPagination(PageNumberPagination):
    """Custom pagination for messages."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessagesListView(APIView):
    """
    API endpoint to get paginated list of messages.
    """

    @extend_schema(
        responses={
            200: dict,
            401: dict
        },
        description="Get paginated list of chat messages"
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
        
        messages = Message.objects.all().select_related('author')
        
        paginator = MessagesPagination()
        paginated_messages = paginator.paginate_queryset(messages, request)
        
        serializer = MessageSerializer(paginated_messages, many=True)
        
        return paginator.get_paginated_response(serializer.data)


class MessageCreateView(APIView):
    """
    API endpoint to create a new message.
    """

    @extend_schema(
        request=MessageCreateSerializer,
        responses={
            201: MessageSerializer,
            400: dict,
            401: dict
        },
        description="Create a new chat message"
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
        
        serializer = MessageCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "error": "Validation failed",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message = serializer.save(author=member)
        response_serializer = MessageSerializer(message)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
