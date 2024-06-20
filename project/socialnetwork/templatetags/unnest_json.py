from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _unnnest_json(textinput):
    ret = textinput["label"]
    if textinput["parent_expertise_area"] is not None:
        ret += (
            " &nbsp; <i class='fa-solid fa-arrow-right'></i> &nbsp; "
            + _unnnest_json(textinput["parent_expertise_area"])
        )

    return ret


@register.filter()
def unnnest_json(textinput):
    """Unnest the JSON object and return the label of the expertise area.
    Used to flatten hierarchical expertise areas.
    """
    s = _unnnest_json(textinput)
    return mark_safe(s)
