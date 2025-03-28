from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ShoppingCartForm, ShoppingCartItemForm, OrderAddressForm, OrderItemForm
from .models import ShoppingCart, ShoppingCartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, View, FormView
from django.urls import reverse_lazy
from restaurant.models import MenuItem
from user.models import User
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
import logging
from django.db import OperationalError



logger = logging.getLogger(__name__)




class CreateShoppingCartView(LoginRequiredMixin, CreateView):
    model = ShoppingCart
    form_class = ShoppingCartForm


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer'] = self.request.user.customer
        return kwargs
    

    def form_valid(self, form):
        try:
            customer = self.request.user.customer
            restaurant = form.cleaned_data['restaurant']
            if not restaurant:
            
                raise ValueError("Restaurant must be specified")
        
            existing_cart, created = ShoppingCart.objects.get_or_create(
                customer=customer, restaurant=restaurant
            )
            
            logger.info(f'ShoppingCart created successfully for user [{customer}] at restaurant [{restaurant}]')
            return redirect('order:detail_shopping_cart', pk=existing_cart.pk)
            
        except OperationalError as e:
            logger.error(f'Failed creating shopping cart for user [{self.request.user}]: {e}')
            messages.error(self.request, "There was a problem creating your shopping cart. Please try again later.")
            return redirect('main:home')
        
        except Exception as e:
            logger.exception(f'Error creating ShoppingCart for user [{self.request.user}]: {e}')
            messages.error(self.request, "An unexpected error. Please try again later.")
            return redirect('main:home')


    def form_invalid(self, form):
        logger.warning(f'ShoppingCart creation failed for user [{self.request.user}]. Errors: {form.errors}')
        messages.error(self.request, "There was a problem with your shopping cart. Please check the form and try again.")
        return super().form_invalid(form)
    



class ListShoppingCartView(LoginRequiredMixin, ListView):
    model = ShoppingCart
    template_name = 'shopping_cart/shopping_cart_list.html'

    def get_queryset(self):
        user = self.request.user
        carts = ShoppingCart.objects.filter(customer=self.request.user)
        
        logger.info(f"User [{self.request.user.username}] accessed their shopping cart list.")

        return carts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.request.user  
        return context
    



class DetailShoppingCartView(LoginRequiredMixin, DetailView):
    model = ShoppingCart
    template_name = 'shopping_cart/shoppingcart_detail.html'

    
    def get_queryset(self):
        return ShoppingCart.objects.filter(pk=self.kwargs.get('pk'), customer=self.request.user)
    
    
    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        cart = get_object_or_404(queryset)
        return cart
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_price'] = self.object.get_total_price()
        context['restaurant_name'] = self.object.restaurant.name
        return context
    
    



class DeleteShoppingCartView(LoginRequiredMixin, DeleteView):
    model = ShoppingCart
    template_name = 'restaurant/confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('order:shopping_cart_list')




class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        try:
            item = get_object_or_404(MenuItem, pk=item_id)
            restaurant = item.category.restaurant

            cart, created = ShoppingCart.objects.get_or_create(customer=request.user, restaurant=restaurant)

            shopping_cart_item, item_created = ShoppingCartItem.objects.get_or_create(cart=cart, menu_item=item)
            
            if not item_created:
                shopping_cart_item.quantity += 1
                shopping_cart_item.save()

                logger.info(f'User [{request.user.username}] increased quantity of item "{item.name}" (ID: {item.pk}) in cart (ID: {cart.pk}) to {shopping_cart_item.quantity}.')

            else:
                logger.info(f"User [{request.user.username}] added item '{item.name}' (ID: {item.pk}) to cart (ID: {cart.pk}).")

            return redirect(self.get_success_url(cart.pk))

        except Exception as e:
            logger.exception(f'Error adding item to cart: {e}')
            messages.error(request, "An unexpected error while adding item to cart. Please try again later.")
            return redirect('main:home')
        

    def get_success_url(self, cart_pk):
        return reverse_lazy('order:detail_shopping_cart', kwargs={'pk': cart_pk})
        
        
        



class UpdateShoppingCartItemView(LoginRequiredMixin, UpdateView):
    model = ShoppingCartItem
    form_class = ShoppingCartItemForm
    template_name = 'shopping_cart/shoppingcartitem_form.html'



    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['customer'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            item = self.get_object()
            item.quantity = form.cleaned_data['quantity']
            item.save()

            logger.info(f"User [{self.request.user.username}] updated quantity of item '{item.menu_item.name}' (ID: {item.pk}) in cart (ID: {item.cart.pk}) to {item.quantity}.")
            return super().form_valid(form)
        
        except OperationalError as e:
            logger.error(f'Failed updating shopping cart item for user [{self.request.user}]: {e}')
            messages.error(self.request, "There was a problem updating your shopping cart item. Please try again later.")
            return redirect('main:home')
        
        except Exception as e:
            logger.exception(f'Error updating ShoppingCartItem for user [{self.request.user}]: {e}')
            messages.error(self.request, "An unexpected error. Please try again later.")
            return redirect('main:home')
        
    

    def form_invalid(self, form):
        logger.warning(f'ShoppingCartItem (ID: {self.get_object().pk}) update failed for user [{self.request.user}]. Errors: {form.errors}')
        return super().form_invalid(form)

    
    def get_success_url(self):
        cart_pk = self.kwargs['cart_pk']
        return reverse_lazy('order:detail_shopping_cart', kwargs={'pk': self.object.cart.pk})
        



class DeleteShoppingCartItemView(LoginRequiredMixin, DeleteView):
    model = ShoppingCartItem
    template_name = 'shopping_cart/shoppingcartitem_confirm_delete.html'


    def get_success_url(self):
        return reverse_lazy('order:shopping_cart_list')




class ListShoppingCartItemView(LoginRequiredMixin, ListView):
    model = ShoppingCartItem
    template_name = 'shopping_cart/shoppingcartitem_list.html'

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        cart = get_object_or_404(ShoppingCart, pk=cart_pk)

        logger.info(f"User [{self.request.user.username}] accessed list of items in cart (ID: {cart.pk}).")

        return ShoppingCartItem.objects.filter(cart=cart)




class DetailShoppingCartItemView(LoginRequiredMixin, DetailView):
    model = ShoppingCartItem
    template_name = 'shopping_cart/shoppingcartitem_detail.html'

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        cart = get_object_or_404(ShoppingCart, pk=cart_pk)
        return ShoppingCartItem.objects.filter(cart=cart)
    
    
        



class CheckoutShoppingCartView(LoginRequiredMixin, FormView):
    template_name = 'shopping_cart/checkout.html'
    form_class = OrderAddressForm
    success_url = reverse_lazy('order:order_confirm')
    

    def get_initial(self):
        cart_pk = self.kwargs['cart_pk']
        cart = get_object_or_404(ShoppingCart, pk=cart_pk)
        user = get_object_or_404(User, pk=self.request.user.pk)
        return {'address': user.customer.address}
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_pk = self.kwargs['cart_pk']
        cart = get_object_or_404(ShoppingCart, pk=cart_pk)
        context['cart'] = cart
        return context
    
    
    def form_valid(self, form):
        try:
            cart_pk = self.kwargs['cart_pk']
            cart = get_object_or_404(ShoppingCart, pk=cart_pk)
            user = get_object_or_404(User, pk=self.request.user.pk)
            address = form.cleaned_data['address']
            cart_items = cart.items.all()

            with transaction.atomic():
                order = Order.objects.create(customer=user.customer, restaurant=cart.restaurant, address=address)
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=item.menu_item,
                        quantity=item.quantity,
                        price=item.menu_item.price)
                order.calculate_total_price()
                cart.items.all().delete()
                cart.delete()


                subject = "Order Confirmation"
                html_message = render_to_string('shopping_cart/order_email.html', {'order': order, 'user': user})
                plain_message = strip_tags(html_message) 
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [user.email]
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message, fail_silently=False)

                logger.info(f'Order (ID: {order.pk}) created successfully for user [{user}]')

                self.success_url = reverse_lazy('order:order_confirm', kwargs={'pk': order.pk})
                return super().form_valid(form)


        except OperationalError as e:
            logger.error(f"Database error during checkout for user [{self.request.user}]: {e}")
            messages.error(self.request, "There was a problem processing your order. Please try again later.")
            return redirect('main:home')   

        except Exception as e:
            logger.exception(f"Error during checkout for user [{self.request.user}]: {e}")
            messages.error(self.request, "An unexpected error. Please try again later.")
            return redirect('main:home')  
        
                
    def form_invalid(self, form):
        logger.warning(f'Checkout failed for user [{self.request.user}]. Errors: {form.errors}')
        return super().form_invalid(form)




class OrderConfirmView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'shopping_cart/order_confirm.html'
    context_object_name = 'order'




class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'shopping_cart/order_list.html'
    context_object_name = 'object_list'
    paginate_by = 10



    def get_queryset(self):
        if hasattr(self.request.user, 'customer'):
            return Order.objects.filter(customer=self.request.user.customer).order_by('-order_date')
        else:
            return Order.objects.none()
    
    