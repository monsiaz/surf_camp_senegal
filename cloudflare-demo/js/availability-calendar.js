/**
 * Availability Calendar — interactive date picker with live pricing.
 * Fetches from /api/availability and lets users pick check-in / check-out.
 * Zero dependencies.
 */
(function () {
  'use strict';

  var API = '/api/availability';
  var MONTHS_AHEAD = 4;
  var cache = {};
  var checkin = null;
  var checkout = null;
  var hovDate = null;
  var currentMonth = new Date();
  currentMonth.setDate(1);
  var roomFilter = 'dormitory';
  var container = null;
  var onDatesSelected = null;

  var MONTH_NAMES = {
    en: ['January','February','March','April','May','June','July','August','September','October','November','December'],
    fr: ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
    es: ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    it: ['Gennaio','Febbraio','Marzo','Aprile','Maggio','Giugno','Luglio','Agosto','Settembre','Ottobre','Novembre','Dicembre'],
    de: ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
    nl: ['Januari','Februari','Maart','April','Mei','Juni','Juli','Augustus','September','Oktober','November','December'],
    ar: ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'],
  };
  var DAY_NAMES = {
    en: ['Mo','Tu','We','Th','Fr','Sa','Su'],
    fr: ['Lu','Ma','Me','Je','Ve','Sa','Di'],
    es: ['Lu','Ma','Mi','Ju','Vi','Sá','Do'],
    it: ['Lu','Ma','Me','Gi','Ve','Sa','Do'],
    de: ['Mo','Di','Mi','Do','Fr','Sa','So'],
    nl: ['Ma','Di','Wo','Do','Vr','Za','Zo'],
    ar: ['اث','ثل','أر','خم','جم','سب','أح'],
  };

  var LABELS = {
    en: { checkin: 'Check-in', checkout: 'Check-out', nights: 'nights', from: 'From', perNight: '/night', available: 'available', full: 'Full', select: 'Select dates above', dormitory: 'Dormitory', single: 'Single Room', double: 'Double Room', total: 'Estimated total' },
    fr: { checkin: 'Arrivée', checkout: 'Départ', nights: 'nuits', from: 'Dès', perNight: '/nuit', available: 'dispo', full: 'Complet', select: 'Sélectionnez vos dates', dormitory: 'Dortoir', single: 'Chambre Single', double: 'Chambre Double', total: 'Total estimé' },
    es: { checkin: 'Llegada', checkout: 'Salida', nights: 'noches', from: 'Desde', perNight: '/noche', available: 'disp.', full: 'Completo', select: 'Selecciona fechas', dormitory: 'Dormitorio', single: 'Habitación Single', double: 'Habitación Doble', total: 'Total estimado' },
    it: { checkin: 'Arrivo', checkout: 'Partenza', nights: 'notti', from: 'Da', perNight: '/notte', available: 'disp.', full: 'Completo', select: 'Seleziona le date', dormitory: 'Dormitorio', single: 'Camera Singola', double: 'Camera Doppia', total: 'Totale stimato' },
    de: { checkin: 'Anreise', checkout: 'Abreise', nights: 'Nächte', from: 'Ab', perNight: '/Nacht', available: 'verf.', full: 'Voll', select: 'Datum wählen', dormitory: 'Schlafsaal', single: 'Einzelzimmer', double: 'Doppelzimmer', total: 'Geschätzt' },
    nl: { checkin: 'Aankomst', checkout: 'Vertrek', nights: 'nachten', from: 'Vanaf', perNight: '/nacht', available: 'besch.', full: 'Vol', select: 'Selecteer data', dormitory: 'Slaapzaal', single: 'Eenpersoonskamer', double: 'Tweepersoonskamer', total: 'Geschat totaal' },
    ar: { checkin: 'الوصول', checkout: 'المغادرة', nights: 'ليالي', from: 'من', perNight: '/ليلة', available: 'متاح', full: 'ممتلئ', select: 'اختر التواريخ', dormitory: 'مهجع', single: 'غرفة فردية', double: 'غرفة مزدوجة', total: 'المجموع التقديري' },
  };

  var lang = document.documentElement.lang?.slice(0, 2) || 'en';
  if (!LABELS[lang]) lang = 'en';
  var L = LABELS[lang];
  var mNames = MONTH_NAMES[lang] || MONTH_NAMES.en;
  var dNames = DAY_NAMES[lang] || DAY_NAMES.en;

  function ds(d) { return d.toISOString().slice(0, 10); }
  function parseD(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }

  function fetchAvailability(fromDate, cb) {
    var key = ds(fromDate);
    if (cache[key]) return cb(cache[key]);
    var url = API + '?from=' + key + '&months=' + MONTHS_AHEAD;
    fetch(url).then(function (r) { return r.json(); }).then(function (data) {
      cache[key] = data.days || {};
      cb(cache[key]);
    }).catch(function () { cb({}); });
  }

  function getDayData(dateStr, days) {
    var d = days[dateStr];
    if (!d || !d[roomFilter]) return null;
    return d[roomFilter];
  }

  function daysBetween(a, b) {
    return Math.round((b - a) / 86400000);
  }

  function isInRange(dateStr) {
    if (!checkin || !hovDate) return false;
    var d = parseD(dateStr), ci = parseD(checkin);
    var end = checkout ? parseD(checkout) : parseD(hovDate);
    return d > ci && d < end;
  }

  function ensureDataAndRender() {
    var key = ds(currentMonth);
    if (cache[key]) { render(cache[key]); return; }
    container.innerHTML = '<div class="ac-loading">Loading…</div>';
    fetchAvailability(currentMonth, function(days) { render(days); });
  }

  function render(days) {
    if (!container) return;
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var m = currentMonth.getMonth(), y = currentMonth.getFullYear();
    var firstDay = new Date(y, m, 1);
    var startDow = (firstDay.getDay() + 6) % 7;
    var daysInMonth = new Date(y, m + 1, 0).getDate();

    var html = '<div class="ac-header">';
    html += '<button class="ac-nav ac-prev" aria-label="Previous">‹</button>';
    html += '<span class="ac-month">' + mNames[m] + ' ' + y + '</span>';
    html += '<button class="ac-nav ac-next" aria-label="Next">›</button>';
    html += '</div>';

    html += '<div class="ac-room-tabs">';
    html += '<button class="ac-tab' + (roomFilter === 'dormitory' ? ' active' : '') + '" data-room="dormitory">🛏 ' + L.dormitory + '</button>';
    html += '<button class="ac-tab' + (roomFilter === 'single' ? ' active' : '') + '" data-room="single">🚪 ' + L.single + '</button>';
    html += '<button class="ac-tab' + (roomFilter === 'double' ? ' active' : '') + '" data-room="double">🛌 ' + L.double + '</button>';
    html += '</div>';

    html += '<div class="ac-grid">';
    for (var i = 0; i < 7; i++) html += '<div class="ac-dow">' + dNames[i] + '</div>';
    for (var e = 0; e < startDow; e++) html += '<div class="ac-empty"></div>';

    for (var day = 1; day <= daysInMonth; day++) {
      var date = new Date(y, m, day);
      var dateStr = ds(date);
      var isPast = date < today;
      var info = getDayData(dateStr, days);
      var avail = info ? info.available : 0;
      var price = info ? info.price : 0;
      var cls = 'ac-day';
      if (isPast) cls += ' ac-past';
      else if (!info || avail <= 0) cls += ' ac-full';
      else if (avail <= 1) cls += ' ac-low';
      else cls += ' ac-ok';

      if (dateStr === checkin) cls += ' ac-checkin';
      if (dateStr === checkout) cls += ' ac-checkout';
      if (checkin && isInRange(dateStr)) cls += ' ac-range';

      var tooltip = '';
      if (!isPast && info) {
        tooltip = avail > 0
          ? price + '€' + L.perNight + ' · ' + avail + ' ' + L.available
          : L.full;
      }

      html += '<div class="' + cls + '" data-date="' + dateStr + '" title="' + tooltip + '">';
      html += '<span class="ac-num">' + day + '</span>';
      if (!isPast && info && avail > 0) {
        html += '<span class="ac-price">' + price + '€</span>';
      }
      html += '</div>';
    }
    html += '</div>';

    html += '<div class="ac-summary">';
    if (checkin && checkout) {
      var nights = daysBetween(parseD(checkin), parseD(checkout));
      var totalPrice = 0, allAvail = true;
      var d = parseD(checkin);
      for (var n = 0; n < nights; n++) {
        var di = getDayData(ds(d), days);
        if (di && di.available > 0) totalPrice += di.price;
        else allAvail = false;
        d.setDate(d.getDate() + 1);
      }
      html += '<div class="ac-dates">';
      html += '<div class="ac-dt"><span class="ac-dt-lbl">' + L.checkin + '</span><span class="ac-dt-val">' + checkin + '</span></div>';
      html += '<div class="ac-dt-arrow">→</div>';
      html += '<div class="ac-dt"><span class="ac-dt-lbl">' + L.checkout + '</span><span class="ac-dt-val">' + checkout + '</span></div>';
      html += '</div>';
      html += '<div class="ac-total">' + nights + ' ' + L.nights + (allAvail ? ' · ' + L.total + ': <strong>' + totalPrice + ' €</strong>' : '') + '</div>';
    } else if (checkin) {
      html += '<div class="ac-hint">' + L.checkin + ': ' + checkin + ' — ' + L.checkout + '?</div>';
    } else {
      html += '<div class="ac-hint">' + L.select + '</div>';
    }
    html += '</div>';

    container.innerHTML = html;
    bindEvents(days);
  }

  function bindEvents(days) {
    container.querySelector('.ac-prev').onclick = function () {
      var now = new Date(); now.setDate(1);
      if (currentMonth > now) {
        currentMonth.setMonth(currentMonth.getMonth() - 1);
        ensureDataAndRender();
      }
    };
    container.querySelector('.ac-next').onclick = function () {
      var max = new Date();
      max.setMonth(max.getMonth() + 12);
      if (currentMonth < max) {
        currentMonth.setMonth(currentMonth.getMonth() + 1);
        ensureDataAndRender();
      }
    };

    container.querySelectorAll('.ac-tab').forEach(function (btn) {
      btn.onclick = function () {
        roomFilter = btn.dataset.room;
        ensureDataAndRender();
      };
    });

    container.querySelectorAll('.ac-day:not(.ac-past):not(.ac-full)').forEach(function (cell) {
      cell.onclick = function () {
        var d = cell.dataset.date;
        if (!checkin || checkout) {
          checkin = d; checkout = null;
        } else if (d > checkin) {
          checkout = d;
          if (onDatesSelected) onDatesSelected(checkin, checkout, roomFilter);
        } else {
          checkin = d; checkout = null;
        }
        render(days);
      };
      cell.onmouseenter = function () {
        if (checkin && !checkout) {
          hovDate = cell.dataset.date;
          render(days);
        }
      };
    });
  }

  window.initAvailabilityCalendar = function (el, opts) {
    container = typeof el === 'string' ? document.getElementById(el) : el;
    if (!container) return;
    if (opts && opts.onDatesSelected) onDatesSelected = opts.onDatesSelected;
    if (opts && opts.room) roomFilter = opts.room;
    container.innerHTML = '<div class="ac-loading">Loading…</div>';
    var today = new Date(); today.setDate(1);
    fetchAvailability(today, function (days) { render(days); });
  };
})();
