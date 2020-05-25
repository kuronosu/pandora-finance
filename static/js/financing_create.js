
function toggleForms() {
  document.getElementById('create-financing-form').classList.toggle('d-none')
  document.getElementById('serach-client-form').classList.toggle('d-none')
}
document.addEventListener('DOMContentLoaded', function () {

  const headers = {
    'X-CSRFToken': Cookies.get('csrftoken'),
    'X-Requested-With': 'XMLHttpRequest',
  }

  document.getElementById('serach-client-form').addEventListener('submit', e => {
    e.preventDefault()
    fetch(e.srcElement.action, {
      method: e.srcElement.method,
      body: new FormData(e.srcElement),
      headers
    })
      .then(r => r.json())
      .then(j => {
        let modal = new tingle.modal({
          footer: true,
          stickyFooter: true,
          closeMethods: ['overlay', 'button', 'escape'],
          closeLabel: 'No',
        })
        if (j.ok == true) {
          document.getElementById('id_client').value = j.id
          let formData = new FormData()
          formData.append('id', j.id)
          fetch(document.urls.user_guarantees, {
            method: 'POST',
            body: formData,
            headers
          })
            .then(r => r.json())
            .then(j => {
              let $select = document.getElementById('id_guarantee')
              JSON.parse(j.guarantees).forEach(element => {
                let opt = document.createElement('option')
                opt.appendChild(document.createTextNode(element.fields.name))
                opt.value = element.pk
                $select.appendChild(opt)
              })
            })
            .catch(e => console.log(e))
          document.getElementById('h2_title').textContent += ` para ${j.name}`
          toggleForms()
        } else if (j.ok == false) {
          modal.setContent('<h1>Cliente no registrado</br>¿Desea registrarlo?</h1>')
          modal.addFooterBtn('Si', 'tingle-btn tingle-btn--primary', _ => {
            window.open(document.urls.signup_client, 'Registrar cliente',
              `width=700,height=600,left=${(screen.width / 2) - 350}`)
            modal.close()
          })
          modal.addFooterBtn('No', 'tingle-btn tingle-btn--danger', _ => modal.close())
          modal.open()
        } else {
          console.log(j.error)
          modal.setContent(`<h1>${j.error.document.join('</br>')}</h1>`)
          modal.addFooterBtn('Cerrar', 'tingle-btn tingle-btn--danger', _ => modal.close())
          modal.open()
        }
      })
      .catch(e => alert(`Error en la peticion\n${e}`))
  })

  if (document.getElementById('id_client').value) {
    document.getElementById('create-financing-form').classList.remove('d-none')
    document.getElementById('serach-client-form').classList.add('d-none')
  } else {
    document.getElementById('create-financing-form').classList.add('d-none')
    document.getElementById('serach-client-form').classList.remove('d-none')
  }
})