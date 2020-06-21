function createFilterFormData(financing_type, financing_state, page = 1) {
  // financing_type = (0, 'loan'), (1, 'investment')
  // financing_state = (0, 'to check'), (1, 'approved'), (2, 'not approved')
  if (![0, 1].includes(financing_type) || ![0, 1, 2].includes(financing_state)) {
    return null
  }
  let formData = new FormData()
  formData.append('financing_type', financing_type)
  formData.append('financing_state', financing_state)
  formData.append('page', page)
  return formData
}

function createReq(data) {
  return fetch(document.urls.filter_financing, {
    method: 'POST',
    body: data,
    headers: {
      'X-CSRFToken': Cookies.get('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
      'credentials': 'include',
    },
  })
}

function createT(label, value, extra = '') {
  let $p = document.createElement('p')
  $p.appendChild(document.createTextNode(`${label}: ${value}${extra}`))
  return $p
}

function createModalCard(data) {
  const $container = document.createElement('div')
  $container.appendChild(createT('Código', data.pk))
  $container.appendChild(createT('Monto', data.fields.amount))
  $container.appendChild(createT('Fecha de solicitud', data.fields.application_date))
  $container.appendChild(createT('Fecha de aprobación', data.fields.approval_date))
  $container.appendChild(createT('Cliente', data.fields.client))
  $container.appendChild(createT('Numero de cuotas', data.fields.installments_number))
  $container.appendChild(createT('Tasa de interes', data.fields.interest_rate * 100, '%'))
  $container.appendChild(createT('Fecha de inicio', data.fields.start_date))
  $container.appendChild(createT('Fecha final', data.fields.end_date))
  if (data.model == 'financing.investment') {
    $container.appendChild(createT('Cuenta bancaria', data.fields.bank_account))
  } else if (data.model == 'financing.loan') {
    $container.appendChild(createT('Fiador', data.fields.guarantor))
    $container.appendChild(createT('Garantia', data.fields.guarantee))
  }
  return $container
}

function createFormToSubmit(approve, pk, model) {
  $form = document.getElementById('approve-form')
  $form.method = 'POST'
  $input = document.createElement('input')
  $input.name = 'approve'
  $input.value = approve
  $form.appendChild($input)
  $pk = document.createElement('input')
  $pk.name = 'financing'
  $pk.value = pk
  $form.appendChild($pk)
  $model = document.createElement('input')
  $model.name = 'model'
  $model.value = model
  $form.appendChild($model)
  return $form
}

function launchModal(data) {
  let modal = new tingle.modal({
    footer: true,
    stickyFooter: true,
    closeMethods: ['overlay', 'button', 'escape'],
    closeLabel: 'Cancelar',
  })
  modal.setContent(createModalCard(data))
  if (!data.fields.checked){
    modal.addFooterBtn('Aprobar', 'tingle-btn tingle-btn--primary', _ => { createFormToSubmit('1', data.pk, data.model).submit() })
    modal.addFooterBtn('Rechazar', 'tingle-btn tingle-btn--danger', _ => { createFormToSubmit('0', data.pk, data.model).submit() })
    modal.addFooterBtn('Dejar para despues', 'tingle-btn tingle-btn--default', _ => modal.close())
  } else {
    modal.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--default', _ => modal.close())
  }
  modal.open()
}

function createContent(data, $container) {
  let li = document.createElement('li')
  li.classList.add('btn')
  li.classList.add('list-group-item')
  let document_span = document.createElement('span')
  let code_span = document.createElement('span')
  code_span.appendChild(document.createTextNode(data.pk))
  document_span.appendChild(document.createTextNode(data.fields.application_date))
  li.appendChild(code_span)
  li.appendChild(document.createElement('br'))
  li.appendChild(document_span)
  li.addEventListener('click', e => launchModal(data))
  $container.appendChild(li)
}

function getNewData(data, $container) {
  createReq(data)
    .then(r => r.json())
    .then(j => {
      if (j.ok) {
        j.financing_list.forEach(element => {
          createContent(element, $container)
        })
      }
    })
    .catch(e => console.error(e))
}

document.addEventListener('DOMContentLoaded', function () {
  getNewData(createFilterFormData(1, 0), document.getElementById('investment-toCheck').firstElementChild.firstElementChild)
  getNewData(createFilterFormData(1, 1), document.getElementById('investment-approved').firstElementChild.firstElementChild)
  getNewData(createFilterFormData(1, 2), document.getElementById('investment-rejected').firstElementChild.firstElementChild)
  getNewData(createFilterFormData(0, 0), document.getElementById('loan-toCheck').firstElementChild.firstElementChild)
  getNewData(createFilterFormData(0, 1), document.getElementById('loan-approved').firstElementChild.firstElementChild)
  getNewData(createFilterFormData(0, 2), document.getElementById('loan-rejected').firstElementChild.firstElementChild)
})