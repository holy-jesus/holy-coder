function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

var userLang = getCookie("language") || navigator.language || navigator.userLanguage;
const ENGLISH = {
    "too_many_requests": "Too many requests. Please try again later.",
    "error": "Something went wrong. Please try again later.",
    "wrong_url": "Wrong url format.",
    "cant_download": "Sorry I can't download this video.",
}

const RUSSIAN = {
    "too_many_requests": "Слишком много запросов. Попробуйте позже.",
    "error": "Что-то пошло не так, попробуйте позже.",
    "wrong_url": "Неверный формат ссылки.",
    "cant_download": "Я не могу скачать это видео.",
}
if (userLang.startsWith("en")) {
    const MS = ENGLISH
} else if (userLang.startsWith("ru")) {
    const MS = RUSSIAN
}

function russianLanguage() {
    document.cookie = "language=ru; path=/; expires=Tue, 19 Jan 2100 03:14:07 GMT"
    location.reload()
}

function englishLanguage() {
    document.cookie = "language=en; path=/; expires=Tue, 19 Jan 2100 03:14:07 GMT"
    location.reload()
}