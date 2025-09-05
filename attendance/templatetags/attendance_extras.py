from django import template

register = template.Library()

@register.filter
def duration_format(timedelta_obj):
    """Format a timedelta object to hours and minutes"""
    if not timedelta_obj:
        return "0h 0m"
    
    total_seconds = int(timedelta_obj.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"