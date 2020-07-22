function drawCharts() {
  drawPieChart(
    window.total,
    "Financiaciones",
    document.getElementById("totalChart")
  )
  drawBarChart(
    window.totalAmount,
    "Dinero total",
    document.getElementById("totalAmountChart")
  )
  drawBarChart(
    window.avgAmount,
    "Dinero promedio",
    document.getElementById("avgAmountChart")
  )
  drawBarChart(
    window.allLoans,
    "Préstamos",
    document.getElementById("allLoansChart")
  )
  drawBarChart(
    window.allInvestment,
    "Inversiónes",
    document.getElementById("allInvestmentChart")
  )
  drawPieChart(
    window.approvedLoans,
    "Préstamos aprobados",
    document.getElementById("approvedLoansChart")
  )
  drawPieChart(
    window.approvedInvestment,
    "Inversiones aprobadas",
    document.getElementById("approvedInvestmentChart")
  )
  drawLineChart(
    loadGroupedMonthData(),
    "Financiaciones por mes",
    document.getElementById("groupedMonthChart")
  )
}

const compare = (a, b) => (a > b ? 1 : a == b ? 0 : -1)

function verify(data) {
  data = data ? data : []
  s = 0
  data.forEach((e) => (s += e[1]))
  if (s === 0) {
    return []
  }
  return data
}
function drawBarChart(data, title, container, h = ["Tipo", "Cantidad"]) {
  data = verify(data)
  let options = { chart: { title }, legend: { position: "none" } }
  let dataTable = google.visualization.arrayToDataTable([h, ...data])
  let chart = new google.charts.Bar(container)
  chart.draw(dataTable, options)
}

function drawPieChart(data, title, container, h = ["Tipo", "Cantidad"]) {
  data = verify(data)
  let options = { title, legend: { position: "none" } }
  let dataTable = google.visualization.arrayToDataTable([h, ...data])
  let chart = new google.visualization.PieChart(container)
  chart.draw(dataTable, options)
}

function drawLineChart(data, title, container, options = {}) {
  options = {
    chart: { title },
    theme: "material",
    legend: { position: "bottom" },
    selectionMode: "multiple",
    tooltip: { trigger: "selection" },
    ...options,
  }
  let dataTable = google.visualization.arrayToDataTable(data)
  let chart = new google.charts.Line(container)
  google.visualization.events.addListener(chart, "error", (googleError) => {
    google.visualization.errors.removeError(googleError.id)
    document.getElementById("groupedMonthChartError").textContent =
      "Error al generar el gráfico, puede que no haya datos en las fechas especificadas"
  })
  chart.draw(dataTable, google.charts.Line.convertOptions(options))
}

function assing(obj, element, index) {
  if (!obj.hasOwnProperty(element.month)) {
    obj[element.month] = [0, 0, 0, 0]
  }
  obj[element.month][index] = element.count
  return obj
}
function loadGroupedMonthData() {
  let tmpObj = {}
  window.groupedMonth.loan.application.forEach((element) =>
    assing(tmpObj, element, 0)
  )
  window.groupedMonth.loan.approved.forEach((element) =>
    assing(tmpObj, element, 1)
  )
  window.groupedMonth.investment.application.forEach((element) =>
    assing(tmpObj, element, 2)
  )
  window.groupedMonth.investment.approved.forEach((element) =>
    assing(tmpObj, element, 3)
  )
  let l = []
  let startDate = stringToDate(findGetParameter("start_month"))
  let endDate = stringToDate(findGetParameter("end_month"))
  if (startDate) {
    document.getElementById(
      "start_month"
    ).value = startDate.toISOString().split("-").slice(0, 2).join("-")
    startDate.setMonth(startDate.getMonth() - 1)
  }
  if (endDate) {
    document.getElementById("end_month").value = endDate
      .toISOString()
      .split("-")
      .slice(0, 2)
      .join("-")
    endDate.setMonth(endDate.getMonth() + 1)
  }
  for (const key in tmpObj) {
    if (tmpObj.hasOwnProperty(key)) {
      const element = tmpObj[key]
      let d = stringToDate(key)
      if ((!startDate || d > startDate) && (!endDate || d < endDate))
        l.push([d, ...element])
    }
  }
  l.sort((a, b) => compare(a[0], b[0]))
  let l2
  if (l.length != 0) {
    l2 = []
    let prev = null
    for (let index = 0; index < l.length; index++) {
      const element = l[index]
      let wPrev = prev ? new Date(prev.toISOString()) : null
      while (wPrev && wPrev < element[0]) {
        if (wPrev.toDateString() != prev.toDateString())
          l2.push([wPrev, 0, 0, 0, 0])
        let tmp = new Date(wPrev.toISOString())
        tmp.setMonth(tmp.getMonth() + 1)
        wPrev = new Date(tmp.toISOString())
      }
      l2.push(element)
      prev = new Date(element[0].toISOString())
    }
  } else {
    l2 = l
  }
  l2.unshift([
    "Mes",
    "Solicitudes de préstamo",
    "Préstamos aprobados",
    "Solicitudes de inversión",
    "Inversiónes aprobadas",
  ])
  return l2
}

function stringToDate(str) {
  if (!str) return null
  let values = str.split("-")
  values[1] -= 1
  let d = new Date(...values)
  if (d instanceof Date && !isNaN(d)) return d
  return null
}

function findGetParameter(parameterName) {
  var result = null,
    tmp = []
  location.search
    .substr(1)
    .split("&")
    .forEach(function (item) {
      tmp = item.split("=")
      if (tmp[0] === parameterName) result = decodeURIComponent(tmp[1])
    })
  return result
}

google.charts.load("current", {
  packages: ["corechart", "bar", "line", "controls"],
})
google.charts.setOnLoadCallback(drawCharts)

document.getElementById("filter-month-form").addEventListener("submit", (e) => {
  let start = document.getElementById("start_month")
  let end = document.getElementById("end_month")
  if (start.value && end.value && start.value > end.value) {
    let tmp = start.value
    start.value = end.value
    end.value = tmp
  }
})
