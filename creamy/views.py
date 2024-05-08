import razorpay

from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth.models import User


from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import authentication,permissions
from rest_framework.views import APIView
from rest_framework import status


from creamy.serializers import UserSerializer,CakeSerializer,BasketSerializer,BasketItemSerializer,OrderSerializer
from creamy.forms import RegistrationForm,LoginForm
from creamy.models import Cake,BasketItem,Weight,Order,OrderItems,Category,Type
from creamy.decorators import signin_required,owner_permission_required

KEY_ID="rzp_test_7O76WKtMptBPfv"
KEY_SECRET="06SLBzFxYEJEueqPBjP2fLLM"

# url:localhost:8000/register/
# method:get,post
# form_class:RegistrationForm

class SignUpView(View):


    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("signin")
        return render(request,"login.html",{"form":form})
    
# url:localhost:8000/
# method:get,post
# form_class:LoginForm
    
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("index")
        messages.error(request,"invalid credentials")
        return render(request,"login.html",{"form":form})


@method_decorator([signin_required,never_cache],name="dispatch")    
class IndexView(View):
    def get(self,request,*args,**kwargs):
        qs=Cake.objects.all()
        categories=Category.objects.all()
        selected_category=request.GET.get("category")
        if selected_category:
            qs=qs.filter(category_object__name=selected_category)
        
        return render(request,"index.html",{"data":qs,"categories":categories})
    
    def post(self,request,*args,**kwargs):

        tag_name=request.POST.get("tag")
        qs=Cake.objects.filter(tag_objects__name=tag_name)
        return render(request,"index.html",{"data":qs})



@method_decorator([signin_required,never_cache],name="dispatch")    
class CakeDetailView(View):
    
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Cake.objects.get(id=id)
        return render(request, "cake_detail.html",{"data":qs})
    


@method_decorator([signin_required,never_cache],name="dispatch")    
class AddToBasketView(View):

    def post(self,request,*args,**kwargs):
        weight=request.POST.get("weight")
        weight_obj=Weight.objects.get(name=weight)
        qty=request.POST.get("qty")
        id=kwargs.get("pk")
        cake_obj=Cake.objects.get(id=id)
        BasketItem.objects.create(
            weight_object=weight_obj,
            qty=qty,
            cake_object=cake_obj,
            basket_object=request.user.cart
        )
        return redirect("index")


@method_decorator([signin_required,never_cache],name="dispatch")       
class BasketItemListView(View):

    def get(self,request,*args,**kwargs):
        qs=request.user.cart.cartitem.filter(is_order_placed=False)
        return render(request,"cart-list.html",{"data":qs})
    

@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")        
class BasketItemRemoveView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)
        basket_item_object.delete()
        return redirect("basket-item")
    

@method_decorator([signin_required,owner_permission_required,never_cache],name="dispatch")        
class CartItemUpdateQuantityView(View):

    def post(self,request,*args,**kwargs):
        action=request.POST.get("counterbutton")
        print(action)
        id=kwargs.get("pk")
        basket_item_object=BasketItem.objects.get(id=id)

        if action=="+":
            basket_item_object.qty+=1
            basket_item_object.save()
        else:
            basket_item_object.qty-=1
            basket_item_object.save()
            
        return redirect("basket-item")

@method_decorator([signin_required,never_cache],name="dispatch")       
class CheckOutView(View):
    
    def get(self,request,*args,**kwargs):
        return render(request,"checkout.html")
    
    def post(self,request,*args,**kwargs):

        message=request.POST.get("message")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")
        payment_method=request.POST.get("payment")
        

        # creating order_instance

        order_obj=Order.objects.create(
            user_object=request.user,
            message=message,
            delivery_address=address,
            phone=phone,
            email=email,
            total=request.user.cart.basket_total,
            payment=payment_method
        )

        # creating order_item_instance

        try:
            basket_items=request.user.cart.cart_items
            for bi in basket_items:
                OrderItems.objects.create(
                    order_object=order_obj,
                    basket_item_object=bi

                )
                bi.is_order_placed=True
                bi.save()
                # print("text block 1")

            
        except:
            order_obj.delete()

        finally:
            # print("text block 2")
            print(payment_method)
            print(order_obj)
            if payment_method=="online" and order_obj:
                # print("text block 3")
                client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

                data = { "amount": order_obj.get_order_total*100, "currency": "INR", "receipt": "order_rcptid_11" }

                payment = client.order.create(data=data)        

                order_obj.order_id=payment.get("id")
                order_obj.save()

                print("payment initiate",payment)
                context={
                    "key":KEY_ID,
                    "order_id":payment.get("id"),
                    "amount":payment.get("amount")
                }
                return render(request,"payment.html",{"context":context})

            return redirect("index")
        
@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):
        
        client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))
        data=request.POST
        try:

            client.utility.verify_payment_signature(data)
            print(data)
            order_obj=Order.objects.get(order_id=data.get("razorpay_order_id"))
            order_obj.is_paid=True
            order_obj.save()
            print("******transaction completed*****")
        except:
            print("!!!!!!!!!!Transaction Failed!!!!!!!!")

        return render(request,"success.html")




@method_decorator([signin_required,never_cache],name="dispatch")       
class SignOutView(View):
    
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
    


class OrderSummaryView(View):

    def get(self,request,*args,**kwargs):
        qs=Order.objects.filter(user_object=request.user).exclude(status="cancelled")
        return render(request,"order_summary.html",{"data":qs})
    
class OrderItemRemoveView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        OrderItems.objects.get(id=id).delete()
        return redirect("order-summary")
    





# ---------- api ---------- 

class SignUpApiView(CreateAPIView):

    serializer_class=UserSerializer
    queryset=User.objects.all()


class CakeListApiView(ListAPIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    serializer_class=CakeSerializer
    queryset=Cake.objects.all()


class CakeDetailApiView(RetrieveAPIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    serializer_class=CakeSerializer
    queryset=Cake.objects.all()


class AddToCartApiView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def post(self,request,*args,**kwargs):

        basket_object=request.user.cart
        
        id=kwargs.get("pk")
        cake_object=Cake.objects.get(id=id)

        weight_name=request.data.get("weight")
        weight_object=Weight.objects.get(name=weight_name)

        quantity=request.data.get("qty")

        BasketItem.objects.create(
            basket_object=basket_object,
            cake_object=cake_object,
            weight_object=weight_object,
            qty=quantity
        )

        return Response(data={"message":"created"})
    

class CartListApiView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def get(self,request,*args,**kwargs):

        qs=request.user.cart
        serializer_instance=BasketSerializer(qs)

        return Response(data=serializer_instance.data)
    

class CartItemUpdateApiView(UpdateAPIView,DestroyAPIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    serializer_class=BasketItemSerializer
    queryset=BasketItem.objects.all()

    def perform_update(self, serializer):
        
        weight_name=self.request.data.get("weight_object")
        weight_object=Weight.objects.get(name=weight_name)

        serializer.save(weight_object=weight_object)


class CheckOutApiView(APIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    def post(self,request,*args,**kwargs):

        user_obj=request.user
        delivery_address=request.data.get("delivery_address")
        phone=request.data.get("phone")
        email=request.data.get("email")
        payment_method=request.data.get("payment")

        order_instance=Order.objects.create(
            user_object=user_obj,
            delivery_address=delivery_address,
            phone=phone,
            email=email,
            payment=payment_method
        )

        cart_item=request.user.cart.cart_items

        for bi in cart_item:
            order_instance.basket_item_object.add(bi)
            bi.is_order_placed=True
            bi.save()

        if payment_method=="cod":
            order_instance.save()
            return Response(data={"message":"created"})

        elif payment_method=="online" and order_instance:

            client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))
            data = { "amount": order_instance.get_order_total*100, "currency": "INR", "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)
            print(payment)

            order_id=payment.get("id")
            key_id=KEY_ID
            order_total=payment.get("amount")
            user=request.user.username

            data={
                "order_id":order_id,
                "key_id":key_id,
                "order_total":order_total,
                "user":user,
                "phone":phone
            }
            order_instance.order_id=order_id
            order_instance.save()
            return Response(data=data,status=status.HTTP_201_CREATED)
        

class OrderSummaryApiView(ListAPIView):

    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    serializer_class=OrderSerializer
    queryset=Order.objects.all

    def get_queryset(self):
        return Order.objects.filter(user_object=self.request.user)
    

class PaymentVerificationApiView(APIView):

    def post(self,request,*args,**kwargs):

        data=request.data

        client=razorpay.Client(auth=(KEY_ID,KEY_SECRET))

        try:
            client.utility.verify_payment_signature(data)
            order_id=data.get("razorpay_order_id")
            order_object=Order.objects.get(order_id=order_id)
            order_object.is_paid=True
            order_object.save()
            return Response(data={"message":"payment success"},status=status.HTTP_200_OK)
        
        except:
            return Response(data={"message":"payment failed"},status=status.HTTP_400_BAD_REQUEST)
