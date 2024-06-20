from django import template
from django.utils.safestring import mark_safe

register = template.Library()

import re


@register.filter()
def highlight(textinput, keyword):
    """Highlight the keyword in the textinput. Return the textinput with the keyword highlighted.
    Args:
        textinput: The text to be highlighted.
        keyword: The keyword to be highlighted.
    Returns:
        if textinput is None, otherwise the textinput with the keyword highlighted.
    """
    if textinput:
        src_str = re.compile(keyword, re.IGNORECASE)
        str_replaced = src_str.sub(
            f'<span class="highlight">{keyword}</span>', str(textinput)
        )
    else:
        str_replaced = ""

    return mark_safe(str_replaced)
