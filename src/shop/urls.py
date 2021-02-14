from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name="shophome" ),
    path('about/', views.about , name="AboutUs" ),
    path('contact/', views.contect , name="ContactUs" ),
    path('tracker/', views.tracker , name="TrakingStatus" ),
    path('search/', views.search , name="Search" ),
    path('products/<int:myid>', views.prodView , name="productview" ),
    path('checkout/', views.checkout , name="Checkout" ),
    path('invoice/', views.GeneratePDF , name="GeneratePDF" ),
    path('manfashion/', views.manfashion , name="manfashion" ),
    path('girlfashion/', views.girlfashion , name="girlfashion" ),
    path('computer/', views.computer , name="computer" ),
    path('electronic/', views.electronic , name="electronic" ),
    path('process_payment/', views.process_payment , name="process_payment" ),
    path('payment_done/', views.payment_done , name="payment_done" ),
    path('payment_cancelled/', views.payment_cancelled, name="payment_cancelled" ),
   path('signup/', views.handleSignup , name="handleSignup" ),
   path('login/', views.handleLogin , name="handleLogin" ),
   path('logout/', views.handleLogout , name="handleLogout" ),
]
