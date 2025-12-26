// js/main.js — точка входа приложения
// Объединяет config, api, ui

import { CONFIG } from './config.js';
import * as API from './api.js';
import * as UI from './ui.js';

// ========== СОСТОЯНИЕ ПРИЛОЖЕНИЯ ==========
const state = {
  user: API.loadAuthFromStorage() || null,
  currentEntity: null,
  entityData: {},
};

// ========== УТИЛИТЫ ==========
function todayISODate() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

function renderLoadError(message = 'Ошибка загрузки') {
  UI.showToast(message);
  const el = document.getElementById('tabContent');
  if (el) {
    el.innerHTML = '<div class="card card--inner"><p class="muted">Ошибка загрузки</p></div>';
  }
}

// Берём роль из тех полей, которые у тебя реально могут приходить
function getCurrentRole() {
  return state.user?.user_type || state.user?.usertype || state.user?.role || null;
}

/**
 * Делает объект “двухформатным”, чтобы работать и с ключами вида:
 * - request_id / start_date / climate_tech_type
 * - requestid / startdate / climatetechtype
 */
function mapRequestsFromBackend(rawData) {
  return (rawData || []).map((item) => {
    const request_id = item.requestid ?? item.request_id;
    const start_date = item.startdate ?? item.start_date;
    const climate_tech_type = item.climatetechtype ?? item.climate_tech_type;
    const climate_tech_model = item.climatetechmodel ?? item.climate_tech_model;
    const problem_description = item.problemdescription ?? item.problem_description;
    const request_status = item.requeststatus ?? item.request_status;
    const completion_date = item.completiondate ?? item.completion_date;
    const repair_parts = item.repairparts ?? item.repair_parts;
    const master_id = item.masterid ?? item.master_id;
    const client_id = item.clientid ?? item.client_id;

    return {
      // snake_case
      request_id,
      start_date,
      climate_tech_type,
      climate_tech_model,
      problem_description,
      request_status,
      completion_date,
      repair_parts,
      master_id,
      client_id,

      // legacy keys (под UI/config, если там старые ключи)
      requestid: request_id,
      startdate: start_date,
      climatetechtype: climate_tech_type,
      climatetechmodel: climate_tech_model,
      problemdescription: problem_description,
      requeststatus: request_status,
      completiondate: completion_date,
      repairparts: repair_parts,
      masterid: master_id,
      clientid: client_id,
    };
  });
}

function mapUsersFromBackend(rawData) {
  return (rawData || []).map((item) => {
    const user_id = item.userid ?? item.user_id;
    const full_name = item.fullname ?? item.full_name;
    const user_type = item.usertype ?? item.user_type;

    return {
      // snake_case
      user_id,
      full_name,
      login: item.login,
      phone: item.phone,
      user_type,

      // legacy keys
      userid: user_id,
      fullname: full_name,
      usertype: user_type,
    };
  });
}

function normalizeRequestPayload(formObj) {
  // Приводим payload к тому, что ждёт backend requests.py:
  // climate_tech_type, climate_tech_model, problem_description, client_id, master_id
  // (start_date/request_status на создании сервер сам ставит)
  const payload = { ...formObj };

  // поддержка обоих вариантов ключей
  payload.climate_tech_type = payload.climate_tech_type ?? payload.climatetechtype;
  payload.climate_tech_model = payload.climate_tech_model ?? payload.climatetechmodel;
  payload.problem_description = payload.problem_description ?? payload.problemdescription;
  payload.request_status = payload.request_status ?? payload.requeststatus;
  payload.completion_date = payload.completion_date ?? payload.completiondate;
  payload.repair_parts = payload.repair_parts ?? payload.repairparts;
  payload.master_id = payload.master_id ?? payload.masterid;
  payload.client_id = payload.client_id ?? payload.clientid;
  payload.request_id = payload.request_id ?? payload.requestid;

  // чистим “двойные” ключи, чтобы не путаться
  delete payload.climatetechtype;
  delete payload.climatetechmodel;
  delete payload.problemdescription;
  delete payload.requeststatus;
  delete payload.completiondate;
  delete payload.repairparts;
  delete payload.masterid;
  delete payload.clientid;
  delete payload.requestid;

  // типы
  if (payload.master_id === '' || payload.master_id === undefined) delete payload.master_id;
  if (payload.master_id !== undefined && payload.master_id !== null) payload.master_id = Number(payload.master_id);

  if (payload.client_id !== undefined && payload.client_id !== null) payload.client_id = Number(payload.client_id);

  if (!payload.repair_parts) delete payload.repair_parts;
  if (!payload.completion_date) delete payload.completion_date;

  return payload;
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('appTitle').textContent = CONFIG.appName;

  // Вход
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(loginForm);
    const login = formData.get('login');
    const password = formData.get('password');

    if (!login || !password) {
      UI.showToast('Введите логин и пароль');
      return;
    }

    try {
      const user = await API.apiLogin(login, password);
      state.user = user;
      renderApp();
    } catch (err) {
      UI.showToast('Ошибка входа: ' + (err?.message || err));
    }
  });

  // Выход
  const logoutBtn = document.getElementById('logoutBtn');
  logoutBtn.addEventListener('click', () => {
    API.clearAuthStorage();
    location.reload();
  });

  // Автовход (если уже есть user в storage)
  if (state.user) {
    renderApp();
  }
});

// ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========
function renderApp() {
  document.getElementById('view-login').classList.remove('active');
  document.getElementById('view-login').hidden = true;

  document.getElementById('view-app').classList.add('active');
  document.getElementById('view-app').hidden = false;

  document.getElementById('userbar').hidden = false;

  document.getElementById('userName').textContent =
    state.user.full_name || state.user.fullname || state.user.name || state.user.login;

  // UI.roleTitle может быть заточен под англ. роли, поэтому для русских ролей показываем user_type
  document.getElementById('userRole').textContent =
    state.user.user_type || state.user.usertype || state.user.role || UI.roleTitle(state.user.role);

  const role = getCurrentRole();

  // ШАГ 3: отрисовываем вкладки по роли и получаем список доступных ключей
  const visibleTabs = UI.renderTabs(CONFIG, 'navTabs', (entityKey) => {
    state.currentEntity = entityKey;
    loadEntityData();
  }, role);

  // первая вкладка — первая доступная
  const firstEntityKey = (visibleTabs && visibleTabs.length) ? visibleTabs[0] : null;
  state.currentEntity = firstEntityKey;

  if (!state.currentEntity) {
    UI.showToast('Нет доступных разделов');
    const el = document.getElementById('tabContent');
    if (el) {
      el.innerHTML = '<div class="card card--inner"><p class="muted">Нет доступа к разделам</p></div>';
    }
    return;
  }

  loadEntityData();
}

// ========== ЗАГРУЗКА ДАННЫХ ==========
async function loadEntityData() {
  const entityKey = state.currentEntity;
  const entityConf = CONFIG.entities[entityKey];

  // Защита: если вкладка запрещена — даже не грузим данные
  const role = getCurrentRole();
  if (!UI.canAccessEntity(entityConf, role)) {
    UI.showToast('Нет доступа');
    const el = document.getElementById('tabContent');
    if (el) {
      el.innerHTML = '<div class="card card--inner"><p class="muted">Доступ запрещён</p></div>';
    }
    return;
  }

  // Кастомные вкладки
  if (entityConf.type === 'custom') {
    try {
      let requestsData = state.entityData.requests;

      if (!requestsData) {
        const resp = await API.apiFetchRequests();
        const rawData = resp.data || resp || [];
        requestsData = mapRequestsFromBackend(rawData);
        state.entityData.requests = requestsData;
      }

      if (entityConf.renderFunction === 'renderStatistics') {
        UI.renderStatistics(requestsData, 'tabContent');
      } else if (entityConf.renderFunction === 'renderQuality') {
        UI.renderQuality(requestsData, 'tabContent');
      } else {
        renderLoadError('Неизвестная вкладка');
      }
    } catch (e) {
      UI.showToast(e?.message || 'Ошибка загрузки');
      renderLoadError();
    }
    return;
  }

  // Обычные таблицы
  try {
    let data = [];

    if (entityKey === 'requests') {
      const resp = await API.apiFetchRequests();
      const rawData = resp.data || resp || [];
      data = mapRequestsFromBackend(rawData);
      state.entityData.requests = data;
    } else if (entityKey === 'users') {
      const resp = await API.apiFetchAllUsers();
      const rawData = resp.data || resp || [];
      data = mapUsersFromBackend(rawData);
      state.entityData.users = data;
    } else {
      // На будущее: другие сущности
      data = [];
    }

    state.entityData[entityKey] = data;

    UI.renderTable(
      entityConf,
      data,
      'tabContent',
      (item) => openEditModal(item),
      async (item) => {
        // удаление только заявок
        if (state.currentEntity !== 'requests') return;

        const id = item.request_id ?? item.requestid ?? item[entityConf.primaryKey];
        if (!id) {
          UI.showToast('Не найден ID заявки');
          return;
        }

        if (!confirm(`Удалить заявку #${id}?`)) return;

        try {
          // нужно, чтобы в api.js была функция API.apiDeleteRequest(id)
          await API.apiDeleteRequest(id);
          UI.showToast('Заявка удалена');

          state.entityData.requests = null;
          await loadEntityData();
        } catch (err) {
          UI.showToast(err?.message || 'Ошибка удаления');
        }
      }
    );
  } catch (e) {
    UI.showToast(e?.message || 'Ошибка загрузки');
    renderLoadError();
  }
}

// ========== МОДАЛКА СОЗДАНИЯ/РЕДАКТИРОВАНИЯ ==========
function openEditModal(item) {
  const entityConf = CONFIG.entities[state.currentEntity];
  const modal = document.getElementById('dynamicModal');
  const form = document.getElementById('dynamicForm');

  document.getElementById('modalTitle').textContent = item
    ? `Редактирование: ${entityConf.label}`
    : `Создание: ${entityConf.label}`;

  UI.renderForm(entityConf, item, 'modalFields');

  // небольшие UX-правки для заявки
  if (!item && state.currentEntity === 'requests') {
    // если в конфиге есть start_date/startdate — проставим
    const start1 = form.querySelector('[name="start_date"]');
    const start2 = form.querySelector('[name="startdate"]');
    if (start1 && !start1.value) start1.value = todayISODate();
    if (start2 && !start2.value) start2.value = todayISODate();

    // скрыть client_id (он берётся из токена/юзера)
    const client1 = form.querySelector('[name="client_id"]');
    const client2 = form.querySelector('[name="clientid"]');
    if (client1) client1.closest('.field')?.style && (client1.closest('.field').style.display = 'none');
    if (client2) client2.closest('.field')?.style && (client2.closest('.field').style.display = 'none');

    // скрыть request_id (автоинкремент)
    const rid1 = form.querySelector('[name="request_id"]');
    const rid2 = form.querySelector('[name="requestid"]');
    if (rid1) rid1.closest('.field')?.style && (rid1.closest('.field').style.display = 'none');
    if (rid2) rid2.closest('.field')?.style && (rid2.closest('.field').style.display = 'none');
  }

  form.onsubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const raw = Object.fromEntries(formData.entries());

    try {
      if (state.currentEntity === 'requests') {
        // Приводим payload к формату backend
        const payload = normalizeRequestPayload(raw);

        // client_id берём из авторизованного пользователя
        const uid = state.user.user_id ?? state.user.userid ?? state.user.id;
        if (uid !== undefined && uid !== null) payload.client_id = Number(uid);

        // простая валидация (что ждёт backend)
        if (!payload.climate_tech_type || String(payload.climate_tech_type).trim() === '') {
          UI.showToast('Укажите тип техники');
          return;
        }
        if (!payload.climate_tech_model || String(payload.climate_tech_model).trim() === '') {
          UI.showToast('Укажите модель');
          return;
        }
        if (!payload.problem_description || String(payload.problem_description).trim() === '') {
          UI.showToast('Опишите проблему');
          return;
        }

        const id = payload.request_id;
        if (item) {
          const pk = item.request_id ?? item.requestid ?? item[entityConf.primaryKey];
          await API.apiUpdateRequest(pk, payload);
          UI.showToast('Заявка обновлена');
        } else {
          // request_id не отправляем при создании
          delete payload.request_id;
          await API.apiCreateRequest(payload);
          UI.showToast('Заявка создана');
        }

        state.entityData.requests = null;
        modal.close();
        await loadEntityData();
        return;
      }

      if (state.currentEntity === 'users') {
        // Тут у тебя в исходнике использовался apiFetch напрямую.
        // Оставляем совместимость:
        const pk = item ? (item.user_id ?? item.userid ?? item[entityConf.primaryKey]) : null;

        if (item) {
          await API.apiFetch(`api/users/${pk}`, {
            method: 'PUT',
            body: JSON.stringify(raw),
          });
          UI.showToast('Пользователь обновлён');
        } else {
          await API.apiFetch('api/users', {
            method: 'POST',
            body: JSON.stringify(raw),
          });
          UI.showToast('Пользователь создан');
        }

        state.entityData.users = null;
        modal.close();
        await loadEntityData();
        return;
      }

      UI.showToast('Неизвестная сущность');
    } catch (err) {
      UI.showToast(err?.message || 'Ошибка сохранения');
    }
  };

  modal.showModal();
}
