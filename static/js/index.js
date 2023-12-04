const mainWindow = document.getElementById("mainWindow"),
    spotifyWindow = document.getElementById("spotifyWindow"),
    youtubeWindow = document.getElementById("youtubeWindow"),
    languageWindow = document.getElementById("languageWindow");

function showSpotifyWindow() {
    mainWindow.setAttribute("hidden", "true");
    spotifyWindow.removeAttribute("hidden");
    window.history.replaceState(null, null, window.location.protocol + "//" + window.location.host + "/spotify");
}

function showYoutubeWindow() {
    mainWindow.setAttribute("hidden", "true");
    youtubeWindow.removeAttribute("hidden");
    window.history.replaceState(null, null, window.location.protocol + "//" + window.location.host + "/youtube");
}

function hideYoutubeWindow() {
    youtubeWindow.setAttribute("hidden", "true")
    mainWindow.removeAttribute("hidden")
    window.history.replaceState(null, null, window.location.protocol + "//" + window.location.host + "/");
}

function hideSpotifyWindow() {
    spotifyWindow.setAttribute("hidden", "true")
    mainWindow.removeAttribute("hidden")
    window.history.replaceState(null, null, window.location.protocol + "//" + window.location.host + "/");
}

function showLanguageWindow() {
    mainWindow.setAttribute("hidden", "true")
    languageWindow.removeAttribute("hidden")
}

function hideLanguageWindow() {
    languageWindow.setAttribute("hidden", "true")
    mainWindow.removeAttribute("hidden")
}