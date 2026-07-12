from django import template

register = template.Library()

@register.filter
def is_doctor(user):
    """Return True if user belongs to Doctor group."""
    return user.groups.filter(name="Doctor").exists()

@register.filter
def is_patient(user):
    """Return True if user belongs to Patient group."""
    return user.groups.filter(name="Patient").exists()


# @register.filter
# def is_doctor(user):
#     """Return True if user belongs to Doctor group."""
#     if user and user.is_authenticated:
#         return user.groups.filter(name__iexact="Doctor").exists()
#     return False

# @register.filter
# def is_patient(user):
#     """Return True if user belongs to Patient group."""
#     if user and user.is_authenticated:
#         return user.groups.filter(name__iexact="Patient").exists()
#     return False
