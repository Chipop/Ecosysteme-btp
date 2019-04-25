from django import template
register = template.Library()


def urlize_targetblank(text):
    return text.replace('<a ', '<a class="st_content_url" target="_blank" ')


url_target_blank = register.filter(urlize_targetblank, is_safe = True)