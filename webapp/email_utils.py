import textwrap
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def format_changes(changes):
    formatted_changes = []
    for field, change in changes.items():
        formatted_changes.append(f"{field.capitalize()}:\n    Old: {change['old']}\n    New: {change['new']}")
    return "\n".join(formatted_changes)

def send_approval_request_cobj(objective, supervisor_email, action, changes=None):
    subject = f"Objective {action.capitalize()} - Pending Approval"
    
    message = textwrap.dedent(f"""
    An objective has been {action}d and requires your approval:

    Objective: {objective.name}
    Department: {objective.department}
    {'Created' if action == 'create' else 'Modified'} by: {objective.created_by if action == 'create' else objective.modified_by}
    """).strip()

    if changes:
        changes_text = format_changes(changes)
        message += "\n\nChanges made:\n" + textwrap.indent(changes_text, '    ')

    message += "\n\nPlease review and approve this objective."

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [supervisor_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Email sent successfully for objective {objective.id}")
    except Exception as e:
        logger.error(f"Failed to send email for objective {objective.id}: {str(e)}")

def send_approval_request_measure(measure, supervisor_email, action, changes=None):
    subject = f"Measure {action.capitalize()} - Pending Approval"
    
    message = textwrap.dedent(f"""
    A measure has been {action}d and requires your approval:

    Measure: {measure.title}
    Department: {measure.department}
    Objective: {measure.objective}
    {'Created' if action == 'create' else 'Modified'} by: {measure.created_by if action == 'create' else measure.modified_by}
    """).strip()

    if changes:
        changes_text = format_changes(changes)
        message += "\n\nChanges made:\n" + textwrap.indent(changes_text, '    ')

    message += "\n\nPlease review and approve this measure."

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [supervisor_email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        logger.info(f"Email sent successfully for measure {measure.id}")
    except Exception as e:
        logger.error(f"Failed to send email for measure {measure.id}: {str(e)}")