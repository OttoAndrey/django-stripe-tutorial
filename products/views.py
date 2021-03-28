import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from products.models import Product

DOMAIN = settings.STRIPE_DOMAIN
endpoint_secret = settings.STRIPE_SECRET_WEBHOOK
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session['customer_details']['email']
        product_id = session['metadata']['product_id']

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=(
                f"Thanks for your purchase. "
                f"Here is the product you ordered."
            ),
            recipient_list=[customer_email],
            from_email="admin@localhost",
        )

    # Passed signature verification
    return HttpResponse(status=200)


class SuccessPageView(TemplateView):
    template_name = 'products/success.html'


class CancelPageView(TemplateView):
    template_name = 'products/cancel.html'


class ProductLendingPageView(TemplateView):
    template_name = 'products/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product = Product.objects.get(name='test')
        context.update({
            'product': product,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs['pk']
        product = get_object_or_404(Product, pk=product_id)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.name,
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                'product_id': product.id,
            },
            mode='payment',
            success_url=DOMAIN + '/success/',
            cancel_url=DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id,
        })


