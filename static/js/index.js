var mainWindow = document.getElementById("mainWindow")
var spotifyWindow = document.getElementById("spotifyWindow")

function showSpotifyWindow() {
    mainWindow.setAttribute("hidden", "true");
    spotifyWindow.removeAttribute("hidden");
}

function showMainWindow() {
    spotifyWindow.setAttribute("hidden", "true");
    mainWindow.removeAttribute("hidden");
}