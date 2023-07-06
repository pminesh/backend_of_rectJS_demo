import json, os, razorpay
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import  APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import Transaction, BillingDetail, Plan, Coupon, UserPackage
from .serializers import PaymentSerializer, PlanSerializer, CouponSerializer, CouponDeleteSerializer, BillingDetailSerializer, TransactionSerializer
from .utils import check_coupon, get_expiry_date, date_has_expired
# from .permissions import IsUser, UserIsOwnerOrReadOnly
from django.http import HttpResponse

# from .emails import send_payment_success_email
_public_key = ""
_secret_key = ""


STRIPE_PUBLISHABLE_KEY = ''
STRIPE_SECRET_KEY = ''

# Payment Start
# Reference : https://blog.learncodeonline.in/how-to-integrate-razorpay-payment-gateway-with-django-rest-framework-and-reactjs
class PaymentStart(APIView):
    def post(self, request):
        """
        [create razorpay order]
        The amount will come in 'paise' that means if we pass 50 amount will become 0.5 rupees that means 50 paise so we have to convert it in rupees. So, we will mumtiply it by 100 so it will be 50 rupees.

        We are saving an order with is_paid=False because we've just initialized the order we haven't received the money we will handle the payment success in next.

        Returns:
            [payment]: [Data from Razorpay],
            [transaction]: [id, payment_id],
        """  
        try:
            # request.data is coming from frontend
            bill_id = request.data['bill_id']
            bill_currency = request.data['currency']
            bill = get_object_or_404(BillingDetail, id=int(bill_id))
        except Exception:
            return Response({'message': 'Invalid Request'}, status=status.HTTP_403_FORBIDDEN)


        # Check the plan status
        if not bill.plan.status:
            return Response({'message': 'The plan is not activated select another plan to continue'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Check user generate bill if already paid
        if not bill.status:
            return Response({'message': 'User\'s bill has been expired generate a new bill to pay'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Check if user has already a activated plan
        user_package = UserPackage.objects.filter(user=bill.user, status=True).last()
        if user_package and not date_has_expired(user_package.expiry_date):                
            return Response({'message': 'User already has a activated plan.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Plan Pricing
        # plan_discount = bill.plan.discount or 0
        # plan_price = (int(bill.plan.price) - int(plan_discount))
        '''
        print('========Plan========')
        print('Plan Name = ', bill.plan)
        print('Plan Price = ', bill.plan.price)
        print("Plan Discount = ", plan_discount)
        print("Plan Net = ", plan_price)
        print('========Plan========')
        '''
        if coupon := bill.coupon:
            # Check Coupon Properties And Calculate Price
            response = check_coupon(coupon, bill.plan.final_price)
            if response == 'not_activated':
                return Response({'message': 'Coupon is not activated'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if response == 'code_expired':
                return Response({'message': 'Coupon has been expired'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if response == 'limit_exceeded':
                return Response({'message': 'Coupon limit exceeded'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                # Coupon is Valid
                final_amount = response
        else:
            # When Coupon is Not Available                
            final_amount = bill.plan.final_price    

        # setup razorpay client this is the client to whome user is paying money that's you
        client = razorpay.Client(auth=(_public_key, _secret_key))

        # IF Currency is Not INR
        if bill_currency.upper() != 'INR':
            final_amount = int(final_amount) // 74

        payment = client.order.create({"amount": int(final_amount) * 100, "currency": bill_currency, "payment_capture": "1"})

        transaction = Transaction.objects.create(bill=bill, amount=final_amount, currency=bill_currency, order_id=payment['id'])

        serializer = PaymentSerializer(transaction)

        """
            Transaction response will be 
            {'id': 17, 
            'order_date': '23 January 2021 03:28 PM', 
            'order_product': '**product name from frontend**', 
            'order_amount': '**product amount from frontend**', 
            'order_payment_id': 'order_G3NhfSWWh5UfjQ', # it will be unique everytime
            'is_paid': False}
        """

        data = {
            "payment": payment,
            "transaction": serializer.data
        }
        return Response(data, status=status.HTTP_201_CREATED)
    
# Payment Success
class PaymentSuccess(APIView):
    def post(self, request):
        # request.data is coming from frontend
        try:
            res = json.loads(request.data["response"])
        except Exception:
            return Response({'message': 'Unauthorized payment'}, status=status.HTTP_401_UNAUTHORIZED)

        """
        response will be:
        {
        'razorpay_payment_id': 'pay_G3NivgSZLx7I9e', 
        'razorpay_order_id': 'order_G3NhfSWWh5UfjQ', 
        'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
        this will come from frontend which we will use to validate and confirm the payment
        """

        ord_id = ""
        raz_pay_id = ""
        raz_signature = ""

        # res.keys() will give us list of keys in res
        for key in res.keys():

            if key == 'razorpay_order_id':
                ord_id = res[key]
            elif key == 'razorpay_payment_id':
                raz_pay_id = res[key]
            elif key == 'razorpay_signature':
                raz_signature = res[key]

        # get transaction by payment_id which we've created earlier with is_paid=False
        transaction = Transaction.objects.get(order_id=ord_id)

        # Get Bill Object
        bill = BillingDetail.objects.filter(user=transaction.bill.user).last()

        # we will pass this whole data in razorpay client to verify the payment
        data = {
            'razorpay_order_id': ord_id,
            'razorpay_payment_id': raz_pay_id,
            'razorpay_signature': raz_signature
        }

        client = razorpay.Client(auth=(_public_key, _secret_key))

        # checking if the transaction is valid or not by passing above data dictionary in 
        # razorpay client if it is "valid" then check will return None
        check = client.utility.verify_payment_signature(data)

        if check is not None:
            # print("Redirect to error url or error page")
            return Response({'error': 'Error occurred, Please contact our support team!'}, status=status.HTTP_401_UNAUTHORIZED)

        # if payment is successful that means check is None then we will turn is_paid=True
        transaction.is_paid = True
        transaction.payment_id = raz_pay_id
        transaction.save()

        # Bill Status True to False so User can't make payment for a same bill again
        bill.status = False
        bill.save()

        # Coupon Used Number Update
        if bill.coupon:
            bill.coupon.coupon_used += 1
            bill.coupon.save()

        # After Complete Payment Create a Package For User
        expiry_date = get_expiry_date(int(transaction.bill.plan.validity))
        UserPackage.objects.create(user=transaction.bill.user, plan=transaction.bill.plan, transaction=transaction, expiry_date=expiry_date)
        # Send a confirmation mail to subscriber
        # res = send_payment_success_email(transaction.bill.user, transaction, expiry_date)

        res_data = {
            'message': 'payment successfully received!'
        }

        return Response(res_data, status=status.HTTP_202_ACCEPTED)

# All Plans View
class PlansView(ListAPIView):  
    queryset = Plan.objects.filter(status=True)
    serializer_class = PlanSerializer

# All Plans Details View
class PlansDetailView(RetrieveAPIView):
    queryset = Plan.objects.filter(status=True)
    serializer_class = PlanSerializer
    lookup_field = 'slug'

# All Coupons View
class CouponCheckView(APIView):
    serializer_class = CouponSerializer
    # permission_classes = [permissions.IsAuthenticated, UserIsOwnerOrReadOnly]

    def post(self, request):
        """
        Check Coupon 
        Args:
            code ([str]): [Case sensitive coupon code]
            bill_id ([int]): [valid user generated bill id]

        Returns:
            coupon_data: {},
            price: int,
            price_after_discount: int,
        """        
        try:
            code = request.data['code']
            bill_id = request.data['bill_id']
        except Exception:
            return Response({'message': 'Requirement doesn\'t satisfied'}, status=status.HTTP_400_BAD_REQUEST)

        coupon = get_object_or_404(Coupon, code=code)
        bill = get_object_or_404(BillingDetail, id=int(bill_id))

        # Check the bill status
        if not bill.status:
            return Response({'message': 'Already received payment for this bill'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Check the coupon status
        response = check_coupon(coupon, bill.plan.final_price)

        if response == 'not_activated':
            return Response({'message': 'Coupon is not activated'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if response == 'code_expired':
            return Response({'message': 'Coupon has been expired'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if response == 'limit_exceeded':
            return Response({'message': 'Coupon limit exceeded'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Coupon is Valid
        final_amount = response

        # Update coupon to the bill
        bill.coupon = coupon
        bill.save()

        # Serialize Coupon Data
        serializer = self.serializer_class(coupon)

        # Response
        data = {
            'coupon_data' : serializer.data, 
            'price': bill.plan.final_price,
            'price_after_discount': final_amount
        }
        return Response(data, status=status.HTTP_200_OK)

# Coupon Delete View
class CouponDeleteView(GenericAPIView):
    serializer_class = CouponDeleteSerializer
    # permission_classes = [permissions.IsAuthenticated, UserIsOwnerOrReadOnly]
    def post(self, request):
        try:
            bill_id = request.data['bill_id']
        except Exception:
            return Response({'message': 'Invalid Url'}, status=status.HTTP_400_BAD_REQUEST)
        bill = get_object_or_404(BillingDetail, id=int(bill_id))

        # Check the bill status
        if not bill.status:
            return Response({'message': 'Invalid Bill'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if bill.coupon:
            bill.coupon = None
            bill.save()
            return Response({'message': 'Coupon has been deleted.'}, status=status.HTTP_200_OK)

        return Response({'message': 'Bill does not have any coupon.'}, status=status.HTTP_400_BAD_REQUEST)
        
# Bill Generate View
class BillView(ModelViewSet):
    http_method_names = ['get', 'post']
    serializer_class = BillingDetailSerializer
    # queryset = BillingDetail.objects.filter(status=True)
    queryset = BillingDetail.objects.all()
    # permission_classes = (permissions.IsAuthenticated, UserIsOwnerOrReadOnly)

    def create(self, request, *args, **kwargs):
        previous_pack  =  UserPackage.objects.filter(user=self.request.user, status=True).last()
        
        # Return user if user has a activated plan
        if previous_pack and not previous_pack.is_expired:
            current_plan = {
                'plan_name': previous_pack.plan.name,
                'expiry': f"{previous_pack.expiry_date.day}-{previous_pack.expiry_date.month}-{previous_pack.expiry_date.year}",
            }
            return Response({'message' : 'You already have a activated plan!', 'current_plan': current_plan, 'status': status.HTTP_406_NOT_ACCEPTABLE}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Delete the previous bill take only two records
        previous_bills = BillingDetail.objects.filter(user = self.request.user, status=True)
        if previous_bills.count() >= 2:
            for count_loop, bill in enumerate(previous_bills):
                if count_loop == 0:
                    bill.delete()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user = self.request.user, status=True)
        return Response({**serializer.data, 'status': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        
        # return Response({'message' : 'You already have a active plan'}, status=status.HTTP_201_CREATED)
        
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # def perform_create(self, serializer):
        #     # Delete All Previous Bills
        #     profile  =  UserPackage.objects.filter(user=self.request.user).last()
        #     previous_bills = BillingDetail.objects.filter(user = self.request.user)
        #     print(profile)
        #     raise serializer.ValidationError('foo limit reached.') 
        # if previous_bills:
        #     for bill in previous_bills:
        #         bill.delete()
        # return serializer.save(user = self.request.user, status=True)

    def get_queryset(self):        
        if getattr(self, "swagger_fake_view", False): # Added for swagger warning due to AnonymousUser
            return BillingDetail.objects.none()
        return self.queryset.filter(user = self.request.user).order_by('-id')

# User Transaction View
class TransactionView(ListAPIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    # permission_classes = (permissions.IsAuthenticated, IsUser,)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): # Added for swagger warning for AnonymousUser
            return Transaction.objects.none()
        return self.queryset.filter(bill__user = self.request.user).order_by('-id')

# from django.views.decorators.csrf import csrf_exempt
# import stripe

# stripe.api_key = STRIPE_SECRET_KEY

# @csrf_exempt
# def test_payment(request):
#     session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[
#             {
#                 'price_data': {
#                     'currency': 'inr',
#                     'product_data': {
#                         'name': 'Intro to Django Course',
#                     },
#                     'unit_amount': 10000,
#                 },
#                 'quantity': 1,
#             }
#         ],
#         mode='payment',
#         success_url='http://localhost:3000/user',
#         cancel_url='http://localhost:3000/dashboard',
#     )
#     return HttpResponse({'message' : f'{session.id} - session id'})

