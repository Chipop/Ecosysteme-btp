from django import template
register = template.Library()


@register.filter
def verbose_name(obj):
    return obj._meta.verbose_name


@register.filter
def verbose_name_plural(obj):
    return obj._meta.verbose_name_plural


@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()
