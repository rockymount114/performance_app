from functools import wraps
from django.conf import settings
from .email_utils import *
import logging

logger = logging.getLogger(__name__)

def send_approval_email(object_type, action):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            logger.debug(f"Entering decorator for {object_type} {action}")
            response = view_func(request, *args, **kwargs)
            
            logger.debug(f"After view function. Method: {request.method}, Status: {response.status_code}")
            
            if request.method == 'POST' and response.status_code == 302:
                logger.debug(f"Conditions met for sending email")
                try:
                    if object_type == 'objective':
                        obj = getattr(request, 'objective', None)
                    elif object_type == 'measure':
                        obj = getattr(request, 'measure', None)
                    else:
                        raise ValueError(f"Invalid object_type: {object_type}")

                    logger.debug(f"Object retrieved: {obj}")

                    if obj is None:
                        raise ValueError(f"No {object_type} found on request")
                    
                    changes = getattr(request, 'changes', None)  # Get changes from request

                    supervisor_email = settings.PERFORMANCE_OFFICER_EMAIL
                    if object_type == 'objective':
                        send_approval_request_cobj(obj, supervisor_email, action,changes)
                    else:
                        send_approval_request_measure(obj, supervisor_email, action,changes)
                    logger.info(f"Approval email sent for {object_type} {obj.id}")
                except Exception as e:
                    logger.error(f"Failed to send approval email for {action} {object_type}: {str(e)}")
            else:
                logger.debug(f"Conditions not met for sending email")
                    
            return response
        return _wrapped_view
    return decorator