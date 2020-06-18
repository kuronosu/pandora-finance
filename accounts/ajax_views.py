import json
from django.contrib.auth import get_user_model
from django.http import JsonResponse, Http404
from django.core import serializers
from common.util.querrys import get_client
from .forms import SearchClientDocumentForm, SearchClientNameForm

UserModel = get_user_model()


def search_user_by_document(form):
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


def search_user(request):
    if request.is_ajax and request.method == 'POST':
        form = SearchClientDocumentForm(request.POST or None)
        return search_user_by_document(form)
    raise Http404()
