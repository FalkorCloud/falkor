from django import template, conf
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def raw_include(path):
    import os.path

    filepath = None
    for template_dir in conf.settings.TEMPLATES[0]['DIRS']:
        filepath = '%s/%s' % (template_dir, path)
        if os.path.isfile(filepath):
            break

    fp = open(filepath, 'r')
    output = fp.read()
    fp.close()
    return mark_safe(output)