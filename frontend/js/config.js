// js/config.js
// Конфигурация приложения и описание сущностей БД

export const CONFIG = {
  appName: "Ремонт Климатического Оборудования",
  apiBase: "",

  // Описание сущностей (таблиц БД)
  entities: {

    // === ЗАЯВКИ ===
    requests: {
      label: "Заявки",
      apiPath: "/api/requests",
      primaryKey: "request_id",

      // ДОСТУП ПО РОЛЯМ (если убрать — будет доступно всем)
      rolesAllowed: ["Оператор", "Специалист", "Менеджер", "Менеджер по качеству", "admin"],

      fields: [
        { key: "request_id", label: "№", type: "text", readonly: true, showInTable: true },
        { key: "start_date", label: "Дата", type: "date", required: true, showInTable: true },
        { key: "climate_tech_type", label: "Оборудование", type: "text", required: true, showInTable: true },
        { key: "climate_tech_model", label: "Модель", type: "text", required: true, showInTable: true },
        { key: "problem_description", label: "Описание проблемы", type: "textarea", showInTable: false },
        {
          key: "request_status",
          label: "Статус",
          type: "select",
          options: ["Новая заявка", "В процессе ремонта", "Готова к выдаче", "Ожидание комплектующих", "Выполнена"],
          showInTable: true
        },
        { key: "master_id", label: "Ответственный (ID)", type: "number", showInTable: false },
        { key: "client_id", label: "Клиент (ID)", type: "number", showInTable: false },
        { key: "repair_parts", label: "Запчасти/Неисправности", type: "text", showInTable: false },
        { key: "completion_date", label: "Дата завершения", type: "date", showInTable: false },
      ]
    },

    // === СТАТИСТИКА (специальная вкладка без CRUD) ===
    statistics: {
      label: "Статистика",
      type: "custom", // Не таблица, а кастомный рендер
      renderFunction: "renderStatistics", // Какую функцию вызывать

      // ДОСТУП ПО РОЛЯМ
      rolesAllowed: ["Менеджер", "Менеджер по качеству", "admin"]
    },

    // === КАЧЕСТВО (специальная вкладка) ===
    quality: {
      label: "Качество",
      type: "custom",
      renderFunction: "renderQuality",

      // ДОСТУП ПО РОЛЯМ
      rolesAllowed: ["Менеджер по качеству", "admin"]
    },

    // === ПОЛЬЗОВАТЕЛИ ===
    users: {
      label: "Пользователи",
      apiPath: "/api/users",
      primaryKey: "user_id",
      rolesAllowed: ["Менеджер", "Менеджер по качеству", "admin"],

      fields: [
        { key: "user_id", label: "ID", type: "text", readonly: true, showInTable: true },
        { key: "full_name", label: "ФИО", type: "text", required: true, showInTable: true },
        { key: "login", label: "Логин", type: "text", required: true, showInTable: true },
        { key: "phone", label: "Телефон", type: "tel", showInTable: true },
        {
          key: "user_type",
          label: "Роль",
          type: "select",
          options: ["Менеджер", "Специалист", "Оператор", "Заказчик", "Менеджер по качеству"],
          required: true,
          showInTable: true
        },
        { key: "password", label: "Пароль", type: "password", showInTable: false }
      ]
    }
  }
};
