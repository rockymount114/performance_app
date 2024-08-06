# Get changes

def get_changes(old_instance, new_instance):
    changes = {}
    for field in new_instance._meta.fields:
        old_value = getattr(old_instance, field.name)
        new_value = getattr(new_instance, field.name)
        if old_value != new_value:
            changes[field.name] = {
                'old': old_value,
                'new': new_value
            }
    return changes