from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO

import razorpay
from django.contrib import messages
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

from django.shortcuts import render, redirect, get_object_or_404

from book_store import settings
from orders.models import Order,OrderItem
from userprofile.models import Wallet,WalletTransaction

# Create your views here.
def view_order(request,orderid):
    order = Order.objects.get(id=orderid)
    # order_items = order.orderitem_set.all()
    order_items = OrderItem.objects.filter(order=order)
    current_time = timezone.now()
    fifteen_days_ago = current_time - timedelta(days=15)
    if fifteen_days_ago <= order.order_date <= current_time :
        ret = 0
    else :
        ret=1
    context ={
        'order_items':order_items,
        'order': order,
        'ret':ret
    }
    return render(request,'book_store/vieworder.html',context)


def my_orders(request):
    order = Order.objects.filter(user=request.user).order_by('-order_date')

    paginator = Paginator(order, 7)
    page = request.GET.get('page')
    order = paginator.get_page(page)
    context = {
        'orders' : order
    }
    return render(request,'book_store/myorders.html',context)

def view_orders(request,orderid):
    order = Order.objects.get(id=orderid)
    username  = order.user.username
    # order_items = order.orderitem_set.all()
    order_items = OrderItem.objects.filter(order=order)

    context ={
        'order_items':order_items,
        'order': order,
        'name' : username
    }
    return render(request,'admin_side/vieworders.html',context)

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.order_status != 'Cancelled':
        # Check if the order was paid using  or WALLET_PAY
        if order.payment_method == 'Wallet':
            user_wallet = Wallet.objects.get(user=request.user)
            # Refund the amount to the user's wallet
            refund_amount = order.price_after_discount  # Assuming you want to refund the full amount
            user_wallet.balance += Decimal(refund_amount)
            user_wallet.save()
            transaction_type = 'Debit'
            WalletTransaction.objects.create(
                wallet=user_wallet,
                amount=refund_amount,
                transaction_type=transaction_type,
            )
        if order.payment_method == 'Prepaid':
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            refund_response = client.payment.refund(order.razor_pay_payment_id, {'amount': int(order.price_after_discount * 100)})

            if refund_response['status'] == 'processed':
                order.payment_status = 'REFUNDED'
                order.save()
                messages.success(request, "Order cancelled successfully. Refund processed to your source bank account.")
            else:
                messages.error(request, "Unable to process the refund to your source bank account. Please try again later.")
                return redirect('myorder_detail', order.id)

        if order.payment_status == 'Pending':
            order.payment_status='No payment'
        else:
            order.payment_status='Refunded'
        order.order_status='Cancelled'

        order.save()

        # Restore the stock for the cancelled order items
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            variant = item.variant
            variant.stock = variant.stock + item.quantity
            variant.save()

    return redirect(request.META.get('HTTP_REFERER'))


def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    user_wallet = Wallet.objects.get(user=request.user)
    # Refund the amount to the user's wallet
    refund_amount = order.price_after_discount  # Assuming you want to refund the full amount
    user_wallet.balance += Decimal(refund_amount)
    user_wallet.save()
    transaction_type = 'Debit'
    WalletTransaction.objects.create(
        wallet=user_wallet,
        amount=refund_amount,

        transaction_type=transaction_type,
    )

    order.payment_status='Refunded'
    order.order_status='Returned'

    order.save()

    # Restore the stock for the cancelled order items
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        variant = item.variant
        variant.stock = variant.stock + item.quantity
        variant.save()

    return redirect(request.META.get('HTTP_REFERER'))

def download_invoice(request, order_id):
    order = Order.objects.get(pk=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Render HTML template to a string
    html_content = render_to_string('book_store/invoice_pdf.html', {'order': order, 'order_items': order_items})

    # Create a PDF using ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Convert HTML content to PDF
    from xhtml2pdf import pisa
    pisa_status = pisa.CreatePDF(html_content, dest=response, link_callback=None)
    if pisa_status.err:
        return HttpResponse('PDF generation error.')

    return response