import { request, getToken, clearToken, friendlyError } from "./api.js";

const app = document.querySelector("#app");

const state = {
  age: Number(localStorage.getItem("child_age")) || 4,
  user: null,
  recommendation: null,
  activity: null,
  story: null,
};

const svg = (path, extra = "") =>
  `<svg class="icon ${extra}" viewBox="0 0 24 24" aria-hidden="true">${path}</svg>`;

const icons = {
  home: svg('<path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1z"/>'),
  search: svg('<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/>'),
  saved: svg('<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5.6-7 10-7 10z"/>'),
  profile: svg('<circle cx="12" cy="8" r="3.2"/><path d="M5.5 19.2a6.5 6.5 0 0 1 13 0"/>'),
  back: svg('<path d="M15 5 8 12l7 7"/>', "icon-lg"),
  arrow: svg('<path d="M9 6l6 6-6 6"/>'),
  chevron: svg('<path d="M6 9l6 6 6-6"/>', "icon-sm"),
  child: svg('<circle cx="12" cy="8" r="3"/><path d="M6 19c.6-3 3-5 6-5s5.4 2 6 5"/>'),
  moon: svg('<path d="M16 13.5A6 6 0 0 1 10.5 5 6.5 6.5 0 1 0 19 14.8 6 6 0 0 1 16 13.5z"/>'),
  zap: svg('<path d="M13 3 5 13h7l-1 8 8-10h-7z"/>'),
  user: svg('<circle cx="12" cy="8" r="3"/><path d="M5 19c1-3.2 3.4-5 7-5s6 1.8 7 5"/>'),
  flame: svg('<path d="M12 3s5 4.2 5 8.2A5 5 0 0 1 7 11c0-1.8 1.2-3.6 2.4-4.6C10 9 11 10 12 10c0-2.4.6-5 0-7z"/>'),
  shield: svg('<path d="M12 3 5 6v6c0 4.2 3 7.2 7 9 4-1.8 7-4.8 7-9V6z"/>'),
  more: svg('<circle cx="6" cy="12" r="1.4" class="filled"/><circle cx="12" cy="12" r="1.4" class="filled"/><circle cx="18" cy="12" r="1.4" class="filled"/>'),
  shop: svg('<path d="M5 9h14l-1 11H6L5 9z"/><path d="M8 9V7a4 4 0 0 1 8 0v2"/>'),
  street: svg('<path d="M4 20 10 4h4l6 16"/><path d="M12 9v3m0 3v2"/>'),
  playground: svg('<circle cx="8" cy="16" r="3"/><circle cx="16" cy="16" r="3"/><path d="M8 13V6h8v7"/>'),
  guest: svg('<path d="M4 20V9l8-5 8 5v11"/><path d="M10 20v-6h4v6"/>'),
  car: svg('<path d="M5 17h14l-1-6H6z"/><path d="m7 11 1.5-4h7L17 11M8 17v2m8-2v2"/><circle cx="8" cy="17" r="1"/><circle cx="16" cy="17" r="1"/>'),
  clock: svg('<circle cx="12" cy="12" r="8"/><path d="M12 8v5l3 2"/>'),
  quote: svg('<path d="M8 8h4v6H8zM14 8h4v6h-4z" opacity=".2"/><path d="M8 17c-2-1-3-3-3-5V8h6v5H8c0 1.4.8 2.6 3 4zm8 0c-2-1-3-3-3-5V8h6v5h-3c0 1.4.8 2.6 3 4z"/>'),
  avoid: svg('<circle cx="12" cy="12" r="8"/><path d="M7 7l10 10"/>'),
  bookmark: svg('<path d="M7 4h10v16l-5-3-5 3z"/>'),
  copy: svg('<rect x="8" y="8" width="11" height="11" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>'),
  heart: svg('<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2 4 4 0 0 1 7 2c0 5.6-7 10-7 10z"/>', "filled"),
  spark: svg('<path d="M12 3v4M12 17v4M4.5 12h4M15.5 12h4M6.5 6.5l2.5 2.5M15 15l2.5 2.5M17.5 6.5 15 9M9 15l-2.5 2.5"/>'),
  check: svg('<path d="M5 12.5 9.5 17 19 7"/>'),
  edit: svg('<path d="m4 16.5-.7 3.7 3.7-.7L18 8.5 15.5 6z"/><path d="m14.5 7 2.5 2.5"/>'),
  trash: svg('<path d="M4 7h16M10 11v6m4-6v6M8 7l1-3h6l1 3m-9 0 1 14h10l1-14"/>'),
  info: svg('<circle cx="12" cy="12" r="9"/><path d="M12 10v6m0-9h.01"/>'),
};

const categories = [
  ["Истерика / сильный плач", "tantrum", "heart"],
  ["Не хочет что-то делать", "refusal", "moon"],
  ["Злится / психует", "anger", "flame"],
  ["Бьёт / кусается", "aggression", "shield"],
  ["Не слушается / делает наоборот", "not_listening", "user"],
  ["Другая ситуация", "other", "more"],
];

const subcategories = {
  tantrum: [
    ["Запретили что-то", "forbidden", "shield"],
    ["Забрали игрушку", "toy_taken", "heart"],
    ["Отказали в просьбе", "denied_request", "more"],
    ["Нужно уходить", "leave", "arrow"],
    ["Нужно одеваться", "dressing", "user"],
    ["Причина непонятна", "unknown", "more"],
  ],
  refusal: [
    ["Не хочет спать", "sleep", "moon"],
    ["Не хочет есть", "eat", "heart"],
    ["Не хочет одеваться", "dress", "user"],
    ["Не хочет чистить зубы", "brush_teeth", "spark"],
    ["Не хочет убирать", "clean_up", "more"],
    ["Не хочет уходить", "leave", "arrow"],
    ["Не хочет купаться", "bath", "more"],
  ],
  anger: [
    ["Раздражён", "irritated", "flame"],
    ["Плачет от злости", "crying", "heart"],
    ["Кричит", "shouting", "zap"],
    ["Спорит", "arguing", "more"],
    ["Бросает вещи", "throws_things", "more"],
    ["Хочет ударить", "wants_to_hit", "shield"],
    ["Причина непонятна", "unknown", "more"],
  ],
  aggression: [
    ["Бьёт взрослого", "hits_adult", "user"],
    ["Бьёт другого ребёнка", "hits_child", "user"],
    ["Кусается", "bites", "more"],
    ["Пинается", "kicks", "arrow"],
    ["Толкается", "pushes", "arrow"],
    ["Бросает вещи", "throws_things", "more"],
    ["Другое", "other", "more"],
  ],
  not_listening: [
    ["Игнорирует просьбу", "ignores_request", "more"],
    ["Отвечает «нет»", "says_no", "more"],
    ["Делает наоборот", "does_opposite", "arrow"],
    ["Спорит", "argues", "more"],
    ["Убегает", "runs_away", "arrow"],
    ["Не хочет переключаться", "transition", "spark"],
  ],
};

const places = [
  ["Дома", "home", "home"],
  ["В магазине", "shop", "shop"],
  ["На улице", "street", "street"],
  ["На площадке", "playground", "playground"],
  ["В гостях", "guest", "guest"],
  ["В машине", "car", "car"],
  ["Другое", "other", "more"],
];

function esc(value = "") {
  const div = document.createElement("div");
  div.textContent = String(value);
  return div.innerHTML;
}

function route(name) {
  location.hash = `#/${name}`;
}

function page(content, { nav = true } = {}) {
  app.innerHTML = `<section class="phone"><div class="screen ${nav ? "" : "no-nav"}">${content}</div>${nav ? bottomNav() : ""}</section>`;
  bindCommon();
}

function bottomNav() {
  const current = (location.hash || "#/home").split("/")[1];
  const items = [
    ["home", "Главная", "home"],
    ["search", "Поиск", "search"],
    ["saved", "Сохранённое", "saved"],
    ["profile", "Профиль", "profile"],
  ];
  return `<nav class="bottom-nav" aria-label="Основная навигация">${items
    .map(([key, label, icon]) =>
      `<button type="button" class="nav-item ${current === key ? "active" : ""}" data-route="${key}">${icons[icon]}<span class="nav-label">${label}</span></button>`
    ).join("")}</nav>`;
}

function back(to = "home") {
  return `<button type="button" class="icon-button back" data-route="${to}" aria-label="Назад">${icons.back}</button>`;
}

function agePicker() {
  return `<label class="age-select">${icons.child}<span>${state.age} ${years(state.age)}</span><select id="age" aria-label="Возраст ребёнка">${Array.from({ length: 16 }, (_, i) => `<option ${i + 1 === state.age ? "selected" : ""}>${i + 1}</option>`).join("")}</select>${icons.chevron}</label>`;
}

function years(n) {
  return n === 1 ? "год" : n < 5 ? "года" : "лет";
}

function hero(type) {
  const assets = {
    problem: ["assets/images/situation-girl.png", "Девочка с игрушечным зайцем"],
    activity: ["assets/images/activity-kit.png", "Карандаши, кисточка и игрушечный домик"],
    story: ["assets/images/story-moon.png", "Спящий месяц и звёзды"],
  };
  const [src, alt] = assets[type];
  return `<div class="card-art ${type}"><img src="${src}" alt="${alt}"></div>`;
}

function chip(label, value, selected = false, group = "", iconName = "") {
  return `<button type="button" class="chip ${selected ? "selected" : ""}" data-choice="${group}" data-value="${esc(value)}">${iconName ? icons[iconName] : ""}<span>${esc(label)}</span></button>`;
}

function message(text, kind = "error") {
  return text ? `<p class="notice ${kind}">${esc(text)}</p>` : "";
}

function rateLimitMessage() {
  return `<div class="notice notice-limit">
    <strong>Бесплатный лимит исчерпан</strong>
    <span>Для продолжения войдите в аккаунт. Зарегистрированным пользователям эти гостевые ограничения не применяются.</span>
    <button type="button" class="notice-action" data-route="login">Войти или зарегистрироваться</button>
  </div>`;
}

function validationMessage(text) {
  return `<p class="notice notice-warning">${esc(text)}</p>`;
}

function home() {
  page(`<header class="brand"><div><h1>Рядом</h1><p>Больше спокойных<br>дней вместе</p></div><button type="button" class="avatar" data-route="profile" aria-label="Профиль">${icons.profile}</button></header>
    <h2 class="home-title">Чем помочь сейчас?</h2>
    ${agePicker()}
    <div class="cards">
      <button type="button" class="feature-card peach" data-route="recommendation">${hero("problem")}<div class="copy"><strong>Сложная<br>ситуация</strong><p>Получите поддержку<br>и рекомендации от AI</p></div><span class="card-go">${icons.arrow}</span></button>
      <button type="button" class="feature-card green" data-route="activity">${hero("activity")}<div class="copy"><strong>Занятие</strong><p>Идеи для развития,<br>игры и творчества</p></div><span class="card-go">${icons.arrow}</span></button>
      <button type="button" class="feature-card lavender" data-route="story">${hero("story")}<div class="copy"><strong>Сказка</strong><p>Уютные истории<br>для спокойного сна</p></div><span class="card-go">${icons.arrow}</span></button>
    </div>
    <p class="kindness">${icons.heart}<span>Вы делаете большое дело<br>Рядом — когда это важно</span></p>`);
}

function recommendationForm() {
  const draft = state.recommendationDraft || {};
  const selectedCategory = draft.category || "";
  const selectedSubcategory = draft.subcategory || "";
  const category = categories.find((x) => x[1] === selectedCategory);
  const subitems = selectedCategory && selectedCategory !== "other" ? (subcategories[selectedCategory] || []) : [];
  const showPlace = selectedCategory === "other" || Boolean(selectedSubcategory);

  page(`<div class="top-bar">${back()}<header class="screen-title"><h2>Сложная ситуация</h2></header></div>
    <div class="support-illustration">
      <div class="support-art"><img src="assets/images/situation-girl.png" alt="Девочка с игрушечным зайцем"></div>
      <p class="support-note">Вы не одни.<br>Мы поможем разобраться<br>и найти решение</p>
    </div>
    <form id="recommendation-form">
      <h3>Что происходит?</h3>
      <div class="choice-grid situations">${categories.map((x) => chip(x[0], x[1], x[1] === selectedCategory, "category", x[2])).join("")}</div>
      ${selectedCategory ? `
        <h3>${selectedCategory === "other" ? "Опишите ситуацию" : `Что именно происходит?`}</h3>
        ${selectedCategory === "other"
          ? `<textarea id="other-situation" name="other_situation" rows="4" maxlength="500" placeholder="Например: ребёнок не хочет садиться в машину и начинает плакать...">${esc(draft.description || "")}</textarea>`
          : `<div class="choice-grid">${subitems.map((x) => chip(x[0], x[1], x[1] === selectedSubcategory, "subcategory", x[2])).join("")}</div>`}
      ` : ""}
      ${showPlace ? `
        <h3>Где вы сейчас?</h3>
        <div class="choice-grid">${places.map((x) => chip(x[0], x[1], x[1] === draft.place, "place", x[2])).join("")}</div>
        <button class="cta" type="submit">Получить совет</button>
      ` : ""}
      <div class="form-notice" aria-live="polite"></div>
    </form>`);

  const otherInput = document.querySelector("#other-situation");
  otherInput?.addEventListener("input", (e) => {
    state.recommendationDraft.description = e.target.value;
  });
}

function recommendationResult() {
  const r = state.recommendation;
  if (!r) return route("recommendation");
  page(`<div class="result-head">${back("recommendation")}<header class="screen-title"><h2>${esc(r.title)}</h2><p>Такое бывает. Вот что может помочь в вашей ситуации.</p></header></div>
    <section class="result-card plan"><h3>${icons.check} Пошаговый план</h3>${(r.steps || []).map((step, i) => `<div class="step"><b>${i + 1}</b><p>${esc(step)}</p></div>`).join("")}</section>
    <section class="result-card phrase"><h3>${icons.quote} Что сказать</h3><p>«${esc(r.phrase || "")}»</p></section>
    <section class="result-card avoid"><h3>${icons.avoid} Лучше избегать</h3><ul>${(r.avoid || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></section>
    <section class="if-help"><h3>Если не помогло</h3><p>${esc(r.if_not_helped || "")}</p></section>
    <div class="result-actions">
      <button type="button" class="soft-cta" id="copy-recommendation">${icons.copy} Скопировать</button>
      <button type="button" class="secondary-cta" data-route="recommendation">Попробовать другую ситуацию</button>
    </div>`);
}

function activityForm() {
  page(`<div class="top-bar">${back()}<header class="screen-title"><h2>Идея на сейчас</h2><p>Подберём простое занятие для вашего ребёнка.</p></header></div>
    <div class="form-illustration green"><img src="assets/images/activity-kit.png" alt="Материалы для игры"></div>
    <form id="activity-form">
      <h3>Сколько есть времени?</h3>
      <div class="choice-grid wide">${[5, 10, 15, 30, 60].map((x, i) => chip(`${x} минут`, String(x), i === 2, "time", "clock")).join("")}</div>
      <h3>Где будете заниматься?</h3>
      <div class="choice-grid">${places.map((x, i) => chip(x[0], x[1], i === 0, "activity-place", x[2])).join("")}</div>
      <h3>Что есть под рукой?</h3>
      <div class="choice-grid wide">${["Бумага", "Карандаши", "Игрушки", "Кубики", "Ничего"].map((x) => chip(x, x, false, "item")).join("")}</div>
      <button class="cta" type="submit">Придумать занятие</button>
      <div class="form-notice" aria-live="polite"></div>
    </form>`);
}

function activityResult() {
  const r = state.activity;
  if (!r) return route("activity");
  page(`<div class="top-bar">${back("activity")}<header class="screen-title"><h2>Идея на ${esc(r.duration)} минут</h2><p>Простое занятие для счастливого детства каждый день.</p></header></div>
    <div class="hero-art green"><span class="duration-badge">${icons.clock} ${esc(r.duration)} минут</span><img src="assets/images/activity-kit.png" alt="Материалы для занятия"></div>
    <article class="activity-result">
      <h2>${esc(r.title)}</h2>
      <p>${esc(r.description)}</p>
      <ol>${(r.steps || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ol>
      <div class="result-actions">
        <button type="button" class="soft-cta" data-route="activity">Придумать ещё ${icons.arrow}</button>
      </div>
    </article>`);
}

function storyForm() {
  page(`<div class="top-bar">${back()}<header class="screen-title"><h2>Время для сказки</h2><p>Создадим уютную историю именно для вас.</p></header></div>
    <div class="form-illustration lavender"><img src="assets/images/story-moon.png" alt="Луна и звёзды"></div>
    <form id="story-form">
      <label>Имя ребёнка <span class="optional">необязательно</span><input name="name" maxlength="100" placeholder="Например, Миша"></label>
      <h3>Настроение</h3>
      <div class="choice-grid wide">${chip("Весёлая", "funny", true, "mood", "spark")}${chip("Спокойная", "calm", false, "mood", "moon")}${chip("Приключенческая", "adventure", false, "mood", "zap")}</div>
      <label>Главный герой <span class="optional">необязательно</span><input name="character" maxlength="150" placeholder="Например, маленький лисёнок"></label>
      <h3>Продолжительность</h3>
      <div class="choice-grid wide">${chip("Короткая", "short", true, "duration", "clock")}${chip("Средняя", "medium", false, "duration")}${chip("Длинная", "long", false, "duration")}</div>
      <button class="cta" type="submit">Создать сказку</button>
      <div class="form-notice" aria-live="polite"></div>
    </form>`);
}

function storyResult() {
  const r = state.story;
  if (!r) return route("story");
  const paragraphs = esc(r.story || "").split(/\n+/).filter(Boolean);
  page(`<div class="top-bar">${back("story")}<header class="screen-title"><h2>Ваша сказка</h2></header></div>
    <article class="story-reading">
      <div class="hero-art lavender"><img src="assets/images/story-moon.png" alt="Спящий месяц и звёзды"></div>
      <h1>${esc(r.title)}</h1>
      ${paragraphs.map((x) => `<p>${x}</p>`).join("")}
      <button type="button" class="soft-cta" data-route="story">Создать ещё одну ${icons.arrow}</button>
    </article>`);
}

function login({ clearFields = false } = {}) {
  page(`<section class="auth">
    <div class="auth-hero">${icons.moon}</div>
    <h1>С возвращением</h1>
    <p>Войдите, чтобы продолжить быть рядом.</p>
    <form id="login-form" autocomplete="off">
      <label>Email<input name="email" type="email" required autocomplete="off"></label>
      <label>Пароль<input name="password" type="password" required minlength="8" autocomplete="off"></label>
      <button class="cta" type="submit">Войти</button>
      <div class="form-notice" aria-live="polite"></div>
    </form>
    <p class="auth-switch">Нет аккаунта? <button type="button" data-route="register">Зарегистрироваться</button></p>
    <button type="button" class="text-button" data-route="home">Продолжить без входа</button>
  </section>`, { nav: false });

  if (clearFields) {
    requestAnimationFrame(() => {
      const form = document.querySelector("#login-form");
      if (form) form.reset();
      form?.querySelectorAll("input").forEach((input) => { input.value = ""; });
    });
  }
}

function register() {
  page(`<section class="auth">
    <div class="top-bar">${back("login")}</div>
    <div class="auth-hero">${icons.heart}</div>
    <h1>Давайте знакомиться</h1>
    <p>Пара деталей — и вы с нами.</p>
    <form id="register-form">
      <label>Ваше имя<input name="name" required maxlength="100" autocomplete="name"></label>
      <label>Ваш возраст<input name="age" type="number" required min="18" max="120" autocomplete="bday"></label>
      <label>Email<input name="email" type="email" required autocomplete="email"></label>
      <label>Пароль<input name="password" type="password" required minlength="8" autocomplete="new-password"></label>
      <button class="cta" type="submit">Создать аккаунт</button>
      <div class="form-notice" aria-live="polite"></div>
    </form>
    <p class="auth-switch">Уже есть аккаунт? <button type="button" data-route="login">Войти</button></p>
  </section>`, { nav: false });
}

function profile(editing = false) {
  if (!getToken()) return login();

  page(`<section class="profile-loading"><span class="spinner dark"></span><p>Загружаем профиль…</p></section>`);

  request("/users/me", { auth: true })
    .then((user) => {
      state.user = user;
      localStorage.setItem("profile_email", user.email || localStorage.getItem("profile_email") || "");
      renderProfile(editing);
    })
    .catch((error) => {
      if (error.status === 401) {
        clearToken();
        localStorage.removeItem("profile_email");
        login();
        setTimeout(() => {
          const form = document.querySelector(".auth form");
          if (form) showFormError(form, friendlyError(error));
        }, 0);
        return;
      }
      page(`<section class="empty"><div class="empty-icon">${icons.zap}</div><h2>Не удалось загрузить профиль</h2><p>${esc(friendlyError(error))}</p><button type="button" class="soft-cta" data-route="profile">Повторить</button></section>`);
    });
}

function renderProfile(editing = false) {
  const u = state.user;
  if (!u) return profile(editing);

  if (editing) {
    page(`<div class="top-bar"><button type="button" class="icon-button back" id="back-to-profile" aria-label="Назад">${icons.back}</button><header class="screen-title"><h2>Редактировать профиль</h2><p>Изменения сохранятся в аккаунте.</p></header></div>
      <form id="profile-edit-form" class="profile-edit">
        <label>Имя<input name="name" required maxlength="100" value="${esc(u.name)}"></label>
        <label>Возраст<input name="age" type="number" required min="18" max="120" value="${u.age}"></label>
        <label>Email<input name="email" type="email" value="${esc(u.email || localStorage.getItem("profile_email") || "")}" disabled></label>
        <button class="cta" type="submit">${icons.check} Сохранить изменения</button>
        <div class="form-notice" aria-live="polite"></div>
      </form>`);
    return;
  }

  page(`<div class="profile-toolbar">${back("home")}<button type="button" class="icon-button" id="edit-profile" aria-label="Редактировать">${icons.edit}</button></div>
    <header class="profile-head">
      <div class="profile-circle">${esc((u.name || "?")[0]).toUpperCase()}</div>
      <h1>${esc(u.name)}</h1>
      <p>Ваш личный уголок в «Рядом»</p>
    </header>
    <section class="profile-data">
      <p><span>Возраст</span><b>${u.age} лет</b></p>
      <p><span>Email</span><b>${esc(u.email || localStorage.getItem("profile_email") || "—")}</b></p>
    </section>
    <button type="button" class="soft-cta" id="logout">${icons.profile} Выйти из аккаунта</button>
    <button type="button" class="danger-button" id="delete-account">${icons.trash} Удалить аккаунт</button>
    <section class="about-card"><div>${icons.info}</div><p>«Рядом» помогает быстро найти идею, спокойную фразу или занятие для ребёнка. Ответы AI не заменяют консультацию врача или другого специалиста.</p></section>`);
}

function about() {
  page(`<div class="top-bar">${back("home")}<header class="screen-title"><h2>О «Рядом»</h2></header></div>
    <div class="about-hero"><img src="assets/images/situation-girl.png" alt="Иллюстрация Рядом"></div>
    <section class="about-copy">
      <h1>Больше спокойных дней вместе</h1>
      <p>«Рядом» — помощник для родителей детей примерно от 2 до 6 лет. Он помогает понять, что можно сделать прямо сейчас: коротко, спокойно и без лишней теории.</p>
      <div class="about-points">
        <article><b>${icons.zap}</b><h3>Что делать сейчас</h3><p>Пошаговый план, готовая фраза и то, чего лучше избегать.</p></article>
        <article><b>${icons.spark}</b><h3>Чем занять ребёнка</h3><p>Простые идеи игр и творчества с учётом времени и места.</p></article>
        <article><b>${icons.moon}</b><h3>Создать сказку</h3><p>Персональная история с выбранным настроением и продолжительностью.</p></article>
      </div>
      <div class="about-safety"><strong>Важно</strong><p>«Рядом» не является медицинским или диагностическим сервисом. Если ситуация связана со здоровьем или безопасностью ребёнка, обратитесь к подходящему специалисту.</p></div>
    </section>`);
}

function empty(title, text, iconName) {
  page(`<section class="empty"><div class="empty-icon">${icons[iconName] || icons.search}</div><h2>${esc(title)}</h2><p>${esc(text)}</p></section>`);
}

function render() {
  const name = (location.hash || "#/home").slice(2).replaceAll("/", "-");
  const views = {
    home,
    recommendation: recommendationForm,
    "recommendation-result": recommendationResult,
    activity: activityForm,
    "activity-result": activityResult,
    story: storyForm,
    "story-result": storyResult,
    login,
    register,
    profile,
    "profile-edit": () => profile(true),
    about,
    search: () => empty("Поиск появится позже", "Когда в API появится поиск, здесь можно будет находить советы и занятия.", "search"),
    saved: () => empty("Сохранение появится позже", "Серверного API для сохранённых материалов пока нет — поэтому мы ничего не выдаём за сохранённое.", "saved"),
  };
  (views[name] || home)();
}

function selected(group) {
  return document.querySelector(`.chip.selected[data-choice="${group}"]`)?.dataset.value;
}

function showFormError(form, text) {
  const target = form.querySelector(".form-notice") || form;
  const old = target.querySelector(".notice");
  if (old) old.remove();
  target.insertAdjacentHTML("beforeend", message(text));
}

function showRateLimit(form) {
  const target = form.querySelector(".form-notice") || form;
  const old = target.querySelector(".notice");
  if (old) old.remove();
  target.insertAdjacentHTML("beforeend", rateLimitMessage());
  target.querySelector("[data-route=\"login\"]")?.addEventListener("click", () => route("login"));
}

function showValidation(form, text) {
  const target = form.querySelector(".form-notice") || form;
  const old = target.querySelector(".notice");
  if (old) old.remove();
  target.insertAdjacentHTML("beforeend", validationMessage(text));
}

function loading(button, label) {
  if (!button) return;
  button.disabled = true;
  button.dataset.original = button.innerHTML;
  button.innerHTML = `<span class="spinner"></span>${label}`;
}

function restore(button) {
  if (!button) return;
  button.disabled = false;
  button.innerHTML = button.dataset.original || button.innerHTML;
}

function validateChoice(form, choices, messageText) {
  if (!choices) {
    showValidation(form, messageText);
    return false;
  }
  return true;
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    area.remove();
    return ok;
  }
}

function recommendationCopyText() {
  const r = state.recommendation;
  return [
    r.title,
    "",
    "Пошаговый план:",
    ...(r.steps || []).map((x, i) => `${i + 1}. ${x}`),
    "",
    `Что сказать: «${r.phrase || ""}»`,
    "",
    "Лучше избегать:",
    ...(r.avoid || []).map((x) => `• ${x}`),
    "",
    `Если не помогло: ${r.if_not_helped || ""}`,
  ].join("\n");
}

function bindCommon() {
  document.querySelectorAll("[data-route]").forEach((el) =>
    el.addEventListener("click", () => route(el.dataset.route))
  );

  document.querySelector("#age")?.addEventListener("change", (e) => {
    state.age = Number(e.target.value);
    localStorage.setItem("child_age", state.age);
    render();
  });

  document.querySelectorAll(".chip").forEach((el) =>
    el.addEventListener("click", () => {
      const group = el.dataset.choice;
      if (group === "item") {
        el.classList.toggle("selected");
      } else {
        document.querySelectorAll(`.chip[data-choice="${group}"]`).forEach((x) => x.classList.remove("selected"));
        el.classList.add("selected");
      }
    })
  );

  document.querySelectorAll('.chip[data-choice="category"]').forEach((el) =>
    el.addEventListener("click", () => {
      const current = state.recommendationDraft?.category || "";
      if (current === el.dataset.value) {
        state.recommendationDraft = {};
      } else {
        state.recommendationDraft = {
          category: el.dataset.value,
          subcategory: "",
          place: "",
          description: "",
        };
      }
      recommendationForm();
    })
  );

  document.querySelectorAll('.chip[data-choice="subcategory"]').forEach((el) =>
    el.addEventListener("click", () => {
      const current = state.recommendationDraft?.subcategory || "";
      if (current === el.dataset.value) {
        state.recommendationDraft = {
          ...(state.recommendationDraft || {}),
          subcategory: "",
          place: "",
        };
      } else {
        state.recommendationDraft = {
          ...(state.recommendationDraft || {}),
          subcategory: el.dataset.value,
          place: "",
        };
      }
      recommendationForm();
    })
  );

  document.querySelector("#recommendation-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;

    const category = selected("category");
    const subcategory = selected("subcategory");
    const place = selected("place");
    const description = document.querySelector("#other-situation")?.value.trim() || "";

    if (!validateChoice(form, category, "Выберите ситуацию.")) return;
    if (category === "other") {
      if (!description) {
        showValidation(form, "Опишите, пожалуйста, что происходит.");
        document.querySelector("#other-situation")?.focus();
        return;
      }
    } else if (!validateChoice(form, subcategory, "Выберите, что именно происходит.")) {
      return;
    }
    if (!validateChoice(form, place, "Выберите место.")) return;

    loading(button, "Подбираем решение…");

    try {
      state.recommendation = await request("/recommendations", {
        method: "POST",
        body: {
          age: state.age,
          category,
          subcategory: category === "other" ? description : subcategory,
          place,
        },
      });

      route("recommendation/result");
    } catch (err) {
      restore(button);
      if (err.status === 429) showRateLimit(form);
      else showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#activity-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;

    const time = selected("time");
    const place = selected("activity-place");

    if (!validateChoice(form, time, "Выберите, сколько времени есть.")) return;
    if (!validateChoice(form, place, "Выберите место для занятия.")) return;

    loading(button, "Придумываем занятие…");

    try {
      state.activity = await request("/activities", {
        method: "POST",
        body: {
          age: state.age,
          time: Number(time),
          place,
          available_items: [...document.querySelectorAll('.chip.selected[data-choice="item"]')].map((x) => x.dataset.value),
        },
      });
      route("activity/result");
    } catch (err) {
      restore(button);
      if (err.status === 429) showRateLimit(form);
      else showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#story-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;

    const mood = selected("mood");
    const duration = selected("duration");

    if (!validateChoice(form, mood, "Выберите настроение сказки.")) return;
    if (!validateChoice(form, duration, "Выберите продолжительность.")) return;

    loading(button, "Пишем сказку…");

    try {
      const data = new FormData(form);
      state.story = await request("/stories", {
        method: "POST",
        body: {
          age: state.age,
          name: data.get("name") || null,
          mood,
          character: data.get("character") || null,
          duration,
        },
      });
      route("story/result");
    } catch (err) {
      restore(button);
      if (err.status === 429) showRateLimit(form);
      else showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#login-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;
    loading(button, "Входим…");

    try {
      const data = new FormData(form);
      const payload = Object.fromEntries(data);
      const res = await request("/auth/login", { method: "POST", body: payload });
      localStorage.setItem("access_token", res.access_token);
      localStorage.setItem("profile_email", payload.email);
      form.reset();
      state.user = null;
      restore(button);
      route("home");
    } catch (err) {
      restore(button);
      showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#register-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;
    loading(button, "Создаём аккаунт…");

    try {
      const data = Object.fromEntries(new FormData(form));
      data.age = Number(data.age);
      await request("/auth/register", { method: "POST", body: data });

      form.querySelector(".form-notice").innerHTML = message("Аккаунт создан. Теперь войдите.", "success");
      setTimeout(() => route("login"), 700);
    } catch (err) {
      restore(button);
      showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#edit-profile")?.addEventListener("click", () => route("profile/edit"));
  document.querySelector("#back-to-profile")?.addEventListener("click", () => route("profile"));

  document.querySelector("#profile-edit-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.currentTarget;
    const button = e.submitter;
    loading(button, "Сохраняем…");

    const data = Object.fromEntries(new FormData(form));
    data.age = Number(data.age);

    try {
      state.user = await request(`/users/${state.user.id}`, {
        method: "PUT",
        body: { name: data.name, age: data.age },
        auth: true,
      });
      if (state.user.email) localStorage.setItem("profile_email", state.user.email);
      restore(button);
      route("profile");
    } catch (err) {
      restore(button);
      if (err.status === 401) {
        clearToken();
        return login();
      }
      showFormError(form, friendlyError(err));
    }
  });

  document.querySelector("#delete-account")?.addEventListener("click", async () => {
    const confirmed = window.confirm(
      "Удалить аккаунт? Это действие нельзя отменить."
    );
    if (!confirmed) return;

    const button = document.querySelector("#delete-account");
    loading(button, "Удаляем…");

    try {
      await request(`/users/${state.user.id}`, { method: "DELETE", auth: true });
      clearToken();
      localStorage.removeItem("profile_email");
      state.user = null;
      route("home");
    } catch (err) {
      restore(button);
      const notice = document.querySelector(".profile-data");
      if (notice) notice.insertAdjacentHTML("afterend", message(friendlyError(err)));
    }
  });

  document.querySelector("#logout")?.addEventListener("click", () => {
    clearToken();
    localStorage.removeItem("profile_email");
    state.user = null;
    route("login");
    setTimeout(() => {
      const form = document.querySelector("#login-form");
      if (!form) return;
      form.reset();
      form.querySelectorAll("input").forEach((input) => { input.value = ""; });
    }, 100);
  });

  document.querySelector("#copy-recommendation")?.addEventListener("click", async (e) => {
    const button = e.currentTarget;
    const ok = await copyText(recommendationCopyText());
    const original = button.innerHTML;
    button.innerHTML = ok ? `${icons.check} Скопировано` : `${icons.copy} Не удалось скопировать`;
    if (ok) setTimeout(() => { button.innerHTML = original; }, 1800);
  });
}

window.addEventListener("hashchange", render);
render();
