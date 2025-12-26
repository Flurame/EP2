// js/ui.js — функции рендера и утилиты для интерфейса
// Модульная версия с ES6 export

// Конфигурация темы графиков (для ApexCharts)
export const CHART_THEME = {
  mode: 'dark',
  monochrome: { enabled: false },
  background: 'transparent',
  foreColor: '#bfe8d8cc',
  fontFamily: 'inherit'
};

// Хранилище инстансов графиков
export const charts = {
  timeline: null,
  faults: null,
  spark1: null,
  spark2: null
};

// ========== УТИЛИТЫ ==========

export function uuidv4() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) => {
    const r = crypto.getRandomValues(new Uint8Array(1))[0];
    return (Number(c) ^ (r & (15 >> (Number(c) / 4)))).toString(16);
  });
}

export const ROLES = {
  admin: "Администратор",
  operator: "Оператор",
  specialist: "Специалист",
  manager: "Менеджер по качеству",

  // русские варианты (чтобы не ломаться, если backend отдаёт так)
  "Менеджер": "Менеджер",
  "Специалист": "Специалист",
  "Оператор": "Оператор",
  "Заказчик": "Заказчик",
  "Менеджер по качеству": "Менеджер по качеству",
};

export const STATUS = {
  open: "Открыта",
  in_progress: "В ремонте",
  waiting_parts: "Ожидание",
  done: "Завершена",
};

export const STATUS_BADGE = {
  open: "badge--info",
  in_progress: "badge--warn",
  waiting_parts: "badge--warn",
  done: "badge--ok",
};

export const $ = (sel) => document.querySelector(sel);

// ========== ДАТА И ВРЕМЯ ==========

export function nowLocalInputValue() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function toISOFromLocalInput(v) {
  if (!v) return null;
  const dt = new Date(v);
  return isNaN(dt.getTime()) ? null : dt.toISOString();
}

export function toLocalInputFromISO(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function formatDateTime(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return isNaN(d.getTime()) ? "—" : d.toLocaleString("ru-RU", {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

// ========== УВЕДОМЛЕНИЯ ==========

export function showToast(text) {
  const t = $("#toast");
  if (!t) return;
  t.textContent = text;
  t.hidden = false;
  t.style.opacity = '1';
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    t.style.opacity = '0';
    setTimeout(() => t.hidden = true, 300);
  }, 2600);
}

// ========== ЭКРАНИРОВАНИЕ ==========

export function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function roleTitle(role) {
  return ROLES[role] || role || "—";
}

export function statusBadge(status) {
  const cls = STATUS_BADGE[status] || "badge--info";
  const label = STATUS[status] || status;
  return `<span class="badge ${cls}">${escapeHtml(label)}</span>`;
}

// ========== ДОСТУП ПО РОЛЯМ ==========

// Базово (максимально просто): сравниваем строку роли 1-в-1
export function canAccessEntity(entity, currentRole) {
  const allowed = entity?.rolesAllowed;
  if (!Array.isArray(allowed) || allowed.length === 0) return true; // всем
  if (!currentRole) return false;
  return allowed.includes(currentRole);
}

// ========== ГЕНЕРАЦИЯ ВКЛАДОК ==========

export function renderTabs(config, containerId, onTabClick, currentRole) {
  const container = document.getElementById(containerId);
  if (!container) {
    showToast(`Контейнер #${containerId} не найден`);
    return [];
  }
  container.innerHTML = "";

  // Оставляем только доступные вкладки
  const entries = Object.entries(config.entities || {})
    .filter(([_, entity]) => canAccessEntity(entity, currentRole));

  if (entries.length === 0) {
    showToast("Нет доступных разделов");
    return [];
  }

  entries.forEach(([key, entity], index) => {
    const btn = document.createElement("button");
    btn.className = "tab";
    if (index === 0) btn.classList.add("is-active");
    btn.textContent = entity.label;
    btn.dataset.entity = key;
    btn.setAttribute("role", "tab");
    btn.setAttribute("aria-selected", index === 0 ? "true" : "false");

    btn.onclick = () => {
      document.querySelectorAll(".tab").forEach(b => {
        b.classList.remove("is-active");
        b.setAttribute("aria-selected", "false");
      });
      btn.classList.add("is-active");
      btn.setAttribute("aria-selected", "true");
      onTabClick(key);
    };

    container.appendChild(btn);
  });

  // Возвращаем список ключей, которые реально отрисовали
  return entries.map(([key]) => key);
}

// ========== ГЕНЕРАЦИЯ ТАБЛИЦЫ ==========

export function renderTable(entityConfig, data, containerId, onEdit, onDelete) {
  const container = document.getElementById(containerId);
  if (!container) {
    showToast(`Контейнер #${containerId} не найден`);
    return;
  }

  const visibleFields = (entityConfig.fields || []).filter(f => f.showInTable);

  const thHtml = visibleFields
    .map(f => `<th scope="col">${escapeHtml(f.label)}</th>`)
    .join("");

  let rowsHtml = "";
  if (!data || data.length === 0) {
    rowsHtml = `<tr><td class="empty" colspan="${visibleFields.length + 1}">Нет данных</td></tr>`;
  } else {
    rowsHtml = data.map((item) => {
      const tds = visibleFields.map((f) => {
        let val = item?.[f.key];

        if (f.type === "date" && val) {
          const d = new Date(val);
          val = isNaN(d.getTime()) ? val : d.toLocaleDateString("ru-RU");
        }

        return `<td>${escapeHtml(val ?? "—")}</td>`;
      }).join("");

      const id = item?.[entityConfig.primaryKey];

      const delBtn = onDelete
        ? `<button class="btn btn--ghost btn-del" type="button" title="Удалить">🗑️</button>`
        : "";

      return `
        <tr data-id="${escapeHtml(id)}">
          ${tds}
          <td class="col-actions">
            <button class="btn btn--ghost btn-edit" type="button" title="Редактировать">✏️</button>
            ${delBtn}
          </td>
        </tr>
      `;
    }).join("");
  }

  container.innerHTML = `
    <div class="cardhead">
      <h2 class="h2">${escapeHtml(entityConfig.label || "")}</h2>
      <button class="btn btn--primary" id="btnCreate" type="button">Создать</button>
    </div>

    <div class="tableWrap">
      <table class="table" aria-label="${escapeHtml(entityConfig.label || "")}">
        <thead>
          <tr>
            ${thHtml}
            <th scope="col" style="width: 140px;">Действия</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
      </table>
    </div>
  `;

  const btnCreate = container.querySelector("#btnCreate");
  if (btnCreate) btnCreate.onclick = () => onEdit?.(null);

  const editButtons = container.querySelectorAll(".btn-edit");
  editButtons.forEach((btn) => {
    btn.onclick = (e) => {
      const tr = e.target.closest("tr");
      if (!tr) return;
      const id = tr.dataset.id;
      const item = (data || []).find((i) => String(i?.[entityConfig.primaryKey]) === String(id));
      if (item) onEdit?.(item);
    };
  });

  const delButtons = container.querySelectorAll(".btn-del");
  delButtons.forEach((btn) => {
    btn.onclick = (e) => {
      const tr = e.target.closest("tr");
      if (!tr) return;
      const id = tr.dataset.id;
      const item = (data || []).find((i) => String(i?.[entityConfig.primaryKey]) === String(id));
      if (item) onDelete?.(item);
    };
  });
}

// ========== ГЕНЕРАЦИЯ ФОРМЫ ==========

export function renderForm(entityConfig, item, containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    showToast(`Контейнер #${containerId} не найден`);
    return;
  }
  container.innerHTML = "";

  (entityConfig.fields || []).forEach(field => {
    let value = item ? (item[field.key] ?? "") : "";

    if (field.type === 'date' && value) {
      const d = new Date(value);
      if (!isNaN(d)) value = d.toISOString().split('T')[0];
    }

    let inputHtml = "";
    const requiredAttr = field.required ? "required" : "";
    const readonlyAttr = (field.readonly && item) ? "readonly" : "";

    if (field.type === "select") {
      const optionsHtml = (field.options || []).map(opt => {
        const isSelected = opt === value ? "selected" : "";
        return `<option value="${escapeHtml(opt)}" ${isSelected}>${escapeHtml(opt)}</option>`;
      }).join("");
      inputHtml = `<select name="${escapeHtml(field.key)}" class="select" ${requiredAttr} ${readonlyAttr}>${optionsHtml}</select>`;

    } else if (field.type === "textarea") {
      inputHtml = `<textarea name="${escapeHtml(field.key)}" class="textarea" rows="3" ${requiredAttr} ${readonlyAttr}>${escapeHtml(value)}</textarea>`;

    } else {
      inputHtml = `<input type="${escapeHtml(field.type)}" name="${escapeHtml(field.key)}" class="input" value="${escapeHtml(value)}" ${requiredAttr} ${readonlyAttr}>`;
    }

    const html = `
      <label class="field ${field.type === 'textarea' ? 'grid__full' : ''}">
        <span class="field__label">${escapeHtml(field.label)}</span>
        ${inputHtml}
      </label>
    `;
    container.insertAdjacentHTML("beforeend", html);
  });
}

// ========== СТАТИСТИКА И ГРАФИКИ ==========

export function renderStatistics(data, containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    showToast(`Контейнер #${containerId} не найден`);
    return;
  }

  const total = (data || []).length;
  const done = (data || []).filter(r => r.request_status === 'Выполнена' || r.request_status === 'Готова к выдаче').length;
  const inProgress = (data || []).filter(r => r.request_status === 'В процессе ремонта').length;

  const completedWithTime = (data || [])
    .filter(r => (r.request_status === 'Выполнена' || r.request_status === 'Готова к выдаче') && r.completion_date && r.start_date)
    .map(r => (new Date(r.completion_date) - new Date(r.start_date)) / (1000 * 60 * 60));

  const avgVal = completedWithTime.length > 0
    ? (completedWithTime.reduce((a, b) => a + b, 0) / completedWithTime.length).toFixed(1)
    : "—";

  container.innerHTML = `
    <div class="grid grid--3">
      <div class="card card--inner kpi-card">
        <div class="kpi__label">Выполнено заявок</div>
        <div class="kpi__flex">
          <div class="kpi__value">${done}</div>
          <div id="chartSpark1" class="kpi__chart"></div>
        </div>
      </div>

      <div class="card card--inner kpi-card">
        <div class="kpi__label">В работе</div>
        <div class="kpi__flex">
          <div class="kpi__value">${inProgress}</div>
          <div id="chartSpark2" class="kpi__chart"></div>
        </div>
      </div>

      <div class="card card--inner kpi-card">
        <div class="kpi__label">Среднее время</div>
        <div class="kpi__flex">
          <div class="kpi__value">${avgVal}</div>
          <div class="kpi__hint">ч. на заявку</div>
        </div>
      </div>
    </div>

    <div class="grid grid--2" style="margin-top:12px;">
      <div class="card card--inner">
        <h3 class="h3">Динамика заявок (7 дней)</h3>
        <div id="chartTimeline" style="min-height: 280px;"></div>
      </div>

      <div class="card card--inner">
        <h3 class="h3">Типы неисправностей</h3>
        <div id="chartFaults" style="min-height: 280px; display:flex; justify-content:center; align-items:center;"></div>
      </div>
    </div>
  `;

  setTimeout(() => renderCharts(data), 100);
}

export function renderCharts(data) {
  if (!window.ApexCharts) {
    showToast("ApexCharts не подключен, графики не будут отображаться");
    return;
  }

  // SPARKLINE 1
  const sparkData1 = [4, 3, 5, 7, 6, 8, 9, 12, 14, 15];
  const spark1El = document.querySelector("#chartSpark1");
  if (spark1El) {
    if (!charts.spark1) {
      charts.spark1 = new ApexCharts(spark1El, {
        series: [{ data: sparkData1 }],
        chart: { type: 'area', height: 50, width: 100, sparkline: { enabled: true } },
        stroke: { curve: 'smooth', width: 2 },
        fill: { opacity: 0.2 },
        colors: ['#30d6a0'],
        tooltip: { fixed: { enabled: false }, x: { show: false }, marker: { show: false } }
      });
      charts.spark1.render();
    } else {
      charts.spark1.updateSeries([{ data: sparkData1 }]);
    }
  }

  // SPARKLINE 2
  const sparkData2 = [2, 4, 3, 5, 4, 6, 5, 4, 3, 2];
  const spark2El = document.querySelector("#chartSpark2");
  if (spark2El) {
    if (!charts.spark2) {
      charts.spark2 = new ApexCharts(spark2El, {
        series: [{ data: sparkData2 }],
        chart: { type: 'bar', height: 50, width: 100, sparkline: { enabled: true } },
        colors: ['#ffc14f'],
        plotOptions: { bar: { borderRadius: 3, columnWidth: '60%' } },
        tooltip: { fixed: { enabled: false }, x: { show: false } }
      });
      charts.spark2.render();
    } else {
      charts.spark2.updateSeries([{ data: sparkData2 }]);
    }
  }

  // TIMELINE
  const days = {};
  const today = new Date();
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(today.getDate() - i);
    const key = d.toISOString().split('T')[0];
    days[key] = 0;
  }

  (data || []).forEach(r => {
    if (!r.start_date) return;
    const key = String(r.start_date).split('T')[0];
    if (days[key] !== undefined) days[key]++;
  });

  const timelineData = Object.keys(days).map(date => ({
    x: new Date(date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }),
    y: days[date]
  }));

  const timelineEl = document.querySelector("#chartTimeline");
  if (timelineEl) {
    if (!charts.timeline) {
      charts.timeline = new ApexCharts(timelineEl, {
        series: [{ name: 'Заявок', data: timelineData }],
        chart: { type: 'area', height: 280, background: 'transparent', toolbar: { show: false }, animations: { enabled: true } },
        colors: ['#10b981'],
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 100] } },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        xaxis: { type: 'category', axisBorder: { show: false }, axisTicks: { show: false } },
        yaxis: { show: false },
        grid: { borderColor: '#1e5b46', strokeDashArray: 4 },
        theme: CHART_THEME
      });
      charts.timeline.render();
    } else {
      charts.timeline.updateSeries([{ data: timelineData }]);
    }
  }

  // DONUT
  const faultMap = {};
  (data || []).forEach(r => {
    const t = r.repair_parts || "Не указано";
    faultMap[t] = (faultMap[t] || 0) + 1;
  });

  let sorted = Object.entries(faultMap).sort((a, b) => b[1] - a[1]);
  if (sorted.length === 0) sorted = [["Нет данных", 1]];
  else if (sorted.length > 5) {
    const top = sorted.slice(0, 5);
    const other = sorted.slice(5).reduce((acc, cur) => acc + cur[1], 0);
    sorted = [...top, ["Прочее", other]];
  }

  const faultLabels = sorted.map(x => x[0]);
  const faultValues = sorted.map(x => x[1]);

  const faultsEl = document.querySelector("#chartFaults");
  if (faultsEl) {
    if (!charts.faults) {
      charts.faults = new ApexCharts(faultsEl, {
        series: faultValues,
        labels: faultLabels,
        chart: { type: 'donut', height: 280, background: 'transparent' },
        colors: ['#10b981', '#30d6a0', '#ffc14f', '#ff4f6d', '#8d99ae'],
        plotOptions: {
          pie: {
            donut: {
              size: '70%',
              labels: {
                show: true,
                total: {
                  show: true,
                  label: 'Всего',
                  color: '#eafff6',
                  formatter: (w) => w.globals.seriesTotals.reduce((a, b) => a + b, 0)
                }
              }
            }
          }
        },
        stroke: { show: false },
        dataLabels: { enabled: false },
        legend: { position: 'bottom', horizontalAlign: 'center', fontSize: '13px' },
        theme: CHART_THEME
      });
      charts.faults.render();
    } else {
      charts.faults.updateOptions({ labels: faultLabels });
      charts.faults.updateSeries(faultValues);
    }
  }
}

// ========== ВКЛАДКА КАЧЕСТВА ==========

export function renderQuality(data, containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    showToast(`Контейнер #${containerId} не найден`);
    return;
  }

  container.innerHTML = `
    <div class="card card--inner">
      <h2 class="h2">Качество / QR‑код</h2>
      <div class="grid grid--2">
        <div>
          <h3 class="h3">Оценка качества</h3>
          <p class="muted">QR‑код ведёт на форму опроса качества обслуживания.</p>
          <div class="qrBlock" style="margin-top: 20px;">
            <img src="/qr/feedback" alt="QR‑код формы обратной связи" style="max-width: 200px;" />
            <button id="feedbackBtn" class="btn btn--primary" type="button" style="margin-top: 10px;">Открыть форму обратной связи</button>
          </div>
        </div>
        <div>
          <h3 class="h3">Инструменты менеджера</h3>
          <p class="muted">Доступно менеджеру по качеству.</p>
          <div class="alert alert--info" style="margin-top: 20px;">
            Менеджер по качеству может:
            <ul style="margin-top: 10px;">
              <li>просматривать отзывы клиентов;</li>
              <li>инициировать доп. диагностику;</li>
              <li>согласовывать изменение сроков.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  `;

  const feedbackBtn = document.getElementById("feedbackBtn");
  if (feedbackBtn) {
    feedbackBtn.onclick = () => {
      window.open(
        "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform?usp=sf_link",
        "_blank"
      );
    };
  }
}
