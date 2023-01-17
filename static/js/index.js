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

function hideYoutubeWindow() {
    youtubeWindow.setAttribute("hidden", "true")
    mainWindow.removeAttribute("hidden")
}

function hideSpotifyWindow() {
    spotifyWindow.setAttribute("hidden", "true")
    mainWindow.removeAttribute("hidden")
}