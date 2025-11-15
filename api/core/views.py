"""healthcheck view"""

from django.db import connection
from django.http import HttpResponse


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return HttpResponse(status=200)
    except Exception:  # pylint: disable=broad-except
        return HttpResponse(status=500)
