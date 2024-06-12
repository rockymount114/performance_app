from django.template.defaulttags import register


from django.template.defaultfilters import slugify


@register.filter
def unslugify(value):
    return ' '.join(word.capitalize() for word in slugify(value).split('-'))