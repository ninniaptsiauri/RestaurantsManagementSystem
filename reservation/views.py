from django.forms import BaseModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ReservationForm
from .models import Reservation, Table, Restaurant
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView, View
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db import OperationalError
import logging



logger = logging.getLogger(__name__)


class CreateReservation(PermissionRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservation/reservation_form.html'
    permission_required = 'reservation.add_reservation'
    

    def get_initial(self):
       initial = super().get_initial()
       table_id = self.kwargs.get('table_id')
       restaurant_id = self.kwargs.get('restaurant_id')
       table = get_object_or_404(Table, pk=table_id)
       restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
       initial['table'] = table
       initial['restaurant'] = restaurant
       return initial
    


    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.customer = self.request.user.customer
        reservation.table = form.cleaned_data['table']
        reservation.restaurant = form.cleaned_data['restaurant']

        if not reservation.check_availability():
            messages.error(self.request, "The selected table is not available at this time.")
            return self.form_invalid(form)
        try:
            reservation.save()

        except OperationalError as e:
            logger.error(f"Error saving reservation for user: [{self.request.user}] due to database operational error: {e}")
            messages.error(self.request, "Database error. Please try again later.")
            return redirect('main:home')
        
        except Exception as e:
            logger.exception(f"An unexpected error while creating reservation: {e}")
            messages.error(self.request, "An unexpected error. Please try again later.")

        else:
            subject = "Reservation Confirmation"
            email_context = {
                'reservation': reservation,
                'user': self.request.user,
            }
            html_message = render_to_string('reservation/reservation_email.html', email_context)
            plain_message = strip_tags(html_message) 
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [reservation.customer.user.email]

            try:
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message, fail_silently=False)

            except Exception as e:
                logger.error(f"Error sending reservation confirmation email for reservation ID: {reservation.pk}: {e}")
                messages.warning(self.request, "Reservation created, but there was a problem sending the confirmation email.")
             
            logger.info(f'Reservation created successfully for user: [{self.request.user}] for table (ID: {form.cleaned_data["table"]})')
            return super().form_valid(form)
    
       
    
    def form_invalid(self, form):
        logger.error(f'Reservation failed for user: [{self.request.user}]. Errors: {form.errors}')
        return self.render_to_response(self.get_context_data(form=form))
    

    def get_success_url(self):
        return reverse_lazy('reservation:detail', kwargs={'pk': self.object.pk})
        
    


class UpdateReservation(PermissionRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservation/reservation_form.html'
    permission_required = 'reservation.change_reservation'
    
    

    def form_valid(self, form):
        reservation = form.save(commit=False)
        if not reservation.check_availability():
            messages.error(self.request, "The selected table is not available at this time.")
            return self.form_invalid(form)
        
        try:
            reservation.save()
        
        except OperationalError as e:
            logger.error(f"Failed to update reservation due to database operational error: {e}")

        except Exception as e:
            logger.exception(f"An unexpected error while updating reservation: {e}")
            messages.error(self.request, "An unexpected error. Please try again later.")
            raise 

        else: 
            try:
                send_mail('Reservation Update', f'Hello {self.request.user.username}, you updated your reservation successfully. See details on your profile.',
                            settings.DEFAULT_FROM_EMAIL, [self.request.user.email], fail_silently=False)
            
            except Exception as e:
                logger.error(f"Error sending reservation update email for reservation (ID:{reservation.pk}): {e}")
                messages.warning(self.request, "Reservation updated, but there was a problem sending the update email.")
            
            logger.info(f'Reservation updated successfully for user: [{self.request.user}] for table ({form.cleaned_data["table"]})')
            return super().form_valid(form)
        
          
                
    
    def form_invalid(self, form):
        logger.error(f'Reservation update failed for user: [{self.request.user}]')
        return super().form_invalid(form)
    
    

    def get_success_url(self):
        return reverse_lazy('reservation:detail', kwargs={'pk': self.object.pk})

    
    

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservation/reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10
    

    def get_queryset(self):
        user = self.request.user
        reservations = Reservation.objects.filter(customer=self.request.user.customer).order_by('-reservation_date')
        return reservations


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = self.request.user  
        return context
    
    


class ReservationDetailView(LoginRequiredMixin, DetailView):
    model = Reservation
    template_name = 'reservation/reservation_detail.html'
    context_object_name = 'reservation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_future'] = self.object.is_future
        return context
        
    



class DeleteReservationView(PermissionRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'restaurant/confirm_delete.html'
    permission_required = 'reservation.delete_reservation'
    
    
    def get_success_url(self):
        return reverse_lazy('reservation:list')
    



class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        reservation = get_object_or_404(Reservation, pk=pk)
        if reservation.is_future:
            reservation.is_cancelled = True
            reservation.save()
            messages.success(request, "Reservation cancelled successfully.")

            try:
                send_mail('Cancel Reservation', f'Hello {request.user.username}, you cancelled your reservation at restaurant "{reservation.restaurant.name}" at [{reservation.reservation_date}] successfully.',
                        settings.DEFAULT_FROM_EMAIL, [reservation.customer.user.email], fail_silently=False)

            except Exception as e:
                logger.error(f"Error sending reservation cancel email for reservation (ID: {reservation.pk}): {e}")
                messages.warning(request, "Reservation cancelled, but there was a problem sending the cancel email.")
                
            logger.info(f'Reservation (ID: {reservation.pk}) cancel successful by user: [{request.user}]')

        else:
            messages.error(request, "You cannot cancel a past reservation.")
            logger.info(f'Reservation (ID: {reservation.pk}) cancel failed bu user: [{request.user}]')

        return HttpResponseRedirect(reverse_lazy('reservation:list'))