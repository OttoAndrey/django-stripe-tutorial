from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductLendingPageView.as_view(), name='landing-page'),
    path('cancel/', views.CancelPageView.as_view(), name='cancel-page'),
    path('success/', views.SuccessPageView.as_view(), name='success-page'),
    path(
        'create-checkout-session/<pk>/',
        views.CreateCheckoutSessionView.as_view(),
        name='create-checkout-session',
    ),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
]
