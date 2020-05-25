from django.http import JsonResponse, Http404
from django.core import serializers

from common.util.querrys import get_client
from .forms import SearchClientForm


def search_user(request):
    if request.is_ajax and request.method == 'POST':
        form = SearchClientForm(request.POST or None)
        if form.is_valid():
            user = get_client(form.cleaned_data['document'])
            if user:
                return JsonResponse({'document': user.document, 'id': user.id,
                                     'ok': True, 'name': user.get_full_name()}, status=200)
            else:
                return JsonResponse({
                    'error': {'document': ['No se encontro un cliente con esa cedula']},
                    'ok': False}, status=400)
        return JsonResponse({'error': form.errors}, status=400)
    raise Http404()
