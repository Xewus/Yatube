from datetime import date


def year(request):
    return {'year': str(date.today().year)}
