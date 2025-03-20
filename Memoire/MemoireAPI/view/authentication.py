from rest_framework.views import Response
from rest_framework.decorators import api_view
from ..serializers import SignUpSerializer, LoginSerializer
from rest_framework import status
from base.models import User

@api_view(['post'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        request.session['userid'] = str(user.userid)
        request.session['email'] = user.email
        request.session['name'] = user.name
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session['userid'] = str(user.userid)
                request.session['email'] = user.email
                request.session['name'] = user.name
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post'])
def logout(request):
    request.session.flush()
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_detail(request):
    if 'userid' in request.session:
        return Response({
            "userid": request.session['userid'],
            "name": request.session['name'],
            "email": request.session['email'],
        }, status=status.HTTP_200_OK)
    return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)