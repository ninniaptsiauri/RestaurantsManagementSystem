from django.shortcuts import redirect
from django.contrib import messages
from django.db import OperationalError
import logging

logger = logging.getLogger(__name__)

def handle_error(request, e, action: str):
    if isinstance(e, OperationalError):
        logger.error(f'Failed {action} due to database error: {e}')
        messages.error(request, f"There was a problem {action}. Please try again later.")

    else:
        logger.exception(f"An unexpected error while {action}: {e}")
        messages.error(request, "An unexpected error. Please try again later.")
        
    return redirect('main:home')
