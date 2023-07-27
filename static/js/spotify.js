var spotifyWindow = document.getElementById("spotifyWindow")
var spotifyImagesWindow = document.getElementById("spotifyImagesWindow")
var tabList = document.getElementById("tabList")
var articles = document.getElementById("articles")

function sendSongUrl(button) {
    button.setAttribute("disabled", true)
    var e = document.getElementById("songurl");
    var text = e.value;
    if (text.includes("open.spotify.com/")) {
        var type = text.substring(text.indexOf(".com/") + 5, text.lastIndexOf("/"))
        var id = text.substring(
            text.lastIndexOf("/") + 1,
            text.indexOf("?") != -1 ? text.indexOf("?") : text.length
        );
    } else if (text.includes("spotify:")) {
        var type = text.substring(8, text.lastIndexOf(":"))
        var id = text.substring(
            text.lastIndexOf(":") + 1,
            text.length
        );
    }
    if (["track", "album", "artist", "playlist", "user"].indexOf(type) != -1 && id.length == 22) {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/spotify");
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 429) {
                alert(MS["too_many_requests"]);
            } else if (xhr.readyState === 4 && xhr.status === 200) {
                showSpotifyImagesWindow(JSON.parse(xhr.responseText));
            } else if (xhr.readyState === 4) {
                alert(MS["error"])
            }
        };
        xhr.send(JSON.stringify({ "id": id, "type": type }));
    } else {
        alert(MS["wrong_url"])
    }
    button.removeAttribute("disabled");
}

function showSpotifyImagesWindow(images) {
    if ("error" in images) {
        alert(images["error"]["message"]);
    } else {
        var id = 0;
        var url = images["data"][0];
        tabList.insertAdjacentHTML("beforeend", `<button class="DELETEME" onclick="changeTab(this)" aria-selected="true" aria-controls="${id}">${id}</button>`)
        articles.insertAdjacentHTML("beforeend", `<article class="DELETEME" role="tabpanel" id="${id}"><img src="${url}" style="max-height: 80vh; max-width: 80vw;"/><p class="pixelatedText">Source: <a href="${url}">${url}</a></p></article>`)
        id++;
        for (var url of images["data"]) {
            if (url == images["data"][0]) continue;
            tabList.insertAdjacentHTML("beforeend", `<button class="DELETEME" onclick="changeTab(this)" aria-selected="false" aria-controls="${id}">${id}</button>`)
            articles.insertAdjacentHTML("beforeend", `<article class="DELETEME" role="tabpanel" hidden id="${id}"><img src="${url}" style="max-height: 80vh; max-width: 80vw;"/><p class="pixelatedText">Source: <a href="${url}">${url}</a></p></article>`)
            id++;
        }
        spotifyWindow.setAttribute("hidden", true);
        spotifyImagesWindow.removeAttribute("hidden");
    }
}

function hideSpotifyImagesWindow() {
    spotifyImagesWindow.setAttribute("hidden", true);
    spotifyWindow.removeAttribute("hidden");
    const elements = document.getElementsByClassName("DELETEME");
    while (elements.length > 0) {
        elements[0].parentNode.removeChild(elements[0]);
    }
}



function changeTab(element) {
    var id = element.getAttribute("aria-controls");
    var elements = tabList.getElementsByTagName("button");
    for (var e of elements) {
        e.setAttribute("aria-selected", false)
        document.getElementById(e.getAttribute("aria-controls")).setAttribute("hidden", true)
    }
    element.setAttribute("aria-selected", true);
    document.getElementById(id).removeAttribute("hidden");
}