from django.db import OperationalError
from django.contrib import messages
from django.shortcuts import redirect
import logging
from django.urls import reverse_lazy


logger = logging.getLogger(__name__)


def validate_profile_update(request, instance, user_form_class, profile_form_class, success_url_name):
  
    try:
        user_form = user_form_class(request.POST, instance=instance.user)
        profile_form = profile_form_class(request.POST, instance=instance)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            username = instance.user.username
            logger.info(f'[{instance.__class__.__name__}] [{username}] updated their profile successfully.')
            messages.success(request, "Profile updated successfully!")
            return redirect(success_url_name)
        
        else:
            return {
                'user_form': user_form,
                'profile_form': profile_form,
            }

    except OperationalError as e:
        logger.error(f'Failed updating profile due to database operational error: {e}')
        messages.error(request, "There was a problem while updating your profile. Please try again later.")
        return redirect('main:home')
    
    except Exception as e:
        logger.exception(f'An unexpected error while updating profile: {e}')
        messages.error(request, "An unexpected error. Please try again later.")
        return redirect('main:home')
