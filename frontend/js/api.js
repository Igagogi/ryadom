export const API_BASE_URL = window.RYADOM_API_URL || "http://127.0.0.1:8000";
export const API_TIMEOUT_MS = 45000;

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function clearToken() {
  localStorage.removeItem("access_token");
}

export async function request(path, { method = "GET", body, auth = false } = {}) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 401 && auth) clearToken();

      let detail = data.detail || "Не удалось выполнить запрос.";
      if (Array.isArray(detail)) {
        detail = detail.map((item) => item.msg || "Проверьте поле.").join(" ");
      }

      throw new ApiError(response.status, detail);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) throw error;

    if (error.name === "AbortError") {
      throw new ApiError(
        408,
        "Сервер отвечает слишком долго. Попробуйте ещё раз."
      );
    }

    throw new ApiError(
      0,
      "Не удалось подключиться к серверу. Проверьте, что backend запущен."
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export function friendlyError(error) {
  if (error.status === 400) return error.message || "Проверьте данные и попробуйте ещё раз.";
  if (error.status === 401) return "Неверный email или пароль.";
  if (error.status === 408) return error.message;
  if (error.status === 422) return error.message || "Проверьте, пожалуйста, заполненные поля.";
  if (error.status === 429) return error.message || "Лимит запросов исчерпан.";
  if (error.status === 503) return error.message || "Сервис временно недоступен. Попробуйте немного позже.";
  return error.message || "Что-то пошло не так. Попробуйте ещё раз.";
}
