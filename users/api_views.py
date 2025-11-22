from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserProfileSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    user = request.user
    from store.models import CartItem, Order
    from store.serializers import OrderSerializer
    
    cart_count = CartItem.objects.filter(user=user).count()
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    return Response({
        'user': UserProfileSerializer(user).data,
        'cart_count': cart_count,
        'recent_orders': OrderSerializer(recent_orders, many=True).data
    })