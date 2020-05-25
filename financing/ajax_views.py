import json
from django.core import serializers
from django.http import JsonResponse, Http404
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage

from .forms import ApproveFilterForm
from .models import Guarantee, Investment, Loan


def user_guarantees(request):
    if request.is_ajax and request.method == 'POST':
        client_id = request.POST.get('id', None)
        if client_id:
            guarantees = Guarantee.objects.filter(client__id=client_id)
            return JsonResponse({'guarantees': serializers.serialize('json', guarantees),
                                 'client': client_id}, status=200)
        return JsonResponse({
            'error': {'client': ['No se proporcionó el id del cliente']}}, status=400)
    raise Http404()


def filter_financing(request):
    if not request.user.is_authenticated and not request.user.can_approve:
        return HttpResponseForbidden()
    if request.is_ajax and request.method == 'POST':
        form = ApproveFilterForm(request.POST or None)
        if form.is_valid():
            model = Loan if form.cleaned_data['financing_type'] == '0' else Investment
            # (0, 'to check'), (1, 'approved'), (2, 'not approved')
            if form.cleaned_data['financing_state'] == '0':
                queryset = model.get_to_check()
            elif form.cleaned_data['financing_state'] == '1':
                queryset = model.get_approved()
            else:
                queryset = model.get_not_approved()
            paginator = Paginator(queryset, 20)
            try:
                page = paginator.page(form.cleaned_data['page'])
                return JsonResponse({
                    'financing_list': json.loads(serializers.serialize(
                        'json', page.object_list)),
                    'ok': True
                }, status=200)
            except EmptyPage:
                return JsonResponse({
                    'error': {'page': ['El numero de pagina debe ser menor o igual a '
                                       f'{paginator.num_pages}']
                              },
                    'ok': False}, status=400)
        return JsonResponse({'error': form.errors, 'ok': False}, status=400)
    raise Http404()
