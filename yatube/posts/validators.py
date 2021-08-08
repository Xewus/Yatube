from django.core.exceptions import ValidationError


def validate_not_repeat( value):
    if value == user:
        raise ValidationError(
            'Любишь себя?', params={'value': value},
        )
