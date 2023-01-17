var mainWindow = document.getElementById("mainWindow"),
    spotifyWindow = document.getElementById("spotifyWindow"),
    youtubeWindow = document.getElementById("youtubeWindow");

function showSpotifyWindow() {
    mainWindow.setAttribute("hidden", "true");
    spotifyWindow.removeAttribute("hidden");
}

function showYoutubeWindow() {
    mainWindow.setAttribute("hidden", "true");
    youtubeWindow.removeAttribute("hidden");
}

function showMainWindow(window) {
    window.setAttribute("hidden", "true");
    mainWindow.removeAttribute("hidden");
}