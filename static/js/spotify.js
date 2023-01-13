var spotifyWindow = document.getElementById("spotifyWindow")
var spotifyImagesWindow = document.getElementById("spotifyImagesWindow")
var spotifyImageWindow = document.getElementById("spotifyImageWindow")
var tabList = document.getElementById("tabList")
var articles = document.getElementById("articles")

function sendSongUrl(button) {
    button.setAttribute("disabled", true)
    var e = document.getElementById("songurl");
    var text = e.value;
    var type = text.substring(text.indexOf(".com/") + 5, text.lastIndexOf("/"))
    var id = text.substring(
        text.lastIndexOf("/") + 1,
        text.indexOf("?") != -1 ? text.indexOf("?") : text.length
    );
    if (["track", "album", "artist", "playlist", "user"].indexOf(type) != -1) {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/spotify");
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                showSpotifyImagesWindow(JSON.parse(xhr.responseText));
            } else if (xhr.readyState === 4 && xhr.status === 429) {
                alert("Too many requests, try again later.");
            } else if (xhr.readyState === 4) {
                alert("Something went wrong. Please try again later")
            }
        };
        xhr.send(JSON.stringify({ "id": id, "type": type }));
    } else {
        alert("Wrong url format.")
    }
    button.removeAttribute("disabled");
}

function showSpotifyImagesWindow(images) {
    if ("error" in images) {
        alert(images["error"]["message"])
    } else {
        var num = 0;
        var element = images["data"][0];
        var id = num
        tabList.insertAdjacentHTML("beforeend", `<button class="DELETEME" onclick="changeTab(this)" aria-selected="true" aria-controls="${id}">${id}</button>`)
        articles.insertAdjacentHTML("beforeend", `<article class="DELETEME" role="tabpanel" id="${id}"><img id="img${id}" src="${element.url}" style="max-height: 80vh; max-width: 80vw;"/><p id="size${id}" class="pixelatedText">Original size: ${element.width}x${element.height}</p><p class="pixelatedText">Source: <a href="${element.url}">${element.url}</a></p></article>`)
        var img = document.getElementById(`img${id}`);
        img.onload = function () {
            console.log(`Original size: ${this.width}x${this.height}`)
            document.getElementById(`size${id}`).innerText = `Original size: ${this.width}x${this.height}`
        }
        num++;
        for (var element of images["data"]) {
            if (element == images["data"][0]) continue;
            var id = num;
            tabList.insertAdjacentHTML("beforeend", `<button class="DELETEME" onclick="changeTab(this)" aria-selected="false" aria-controls="${id}">${id}</button>`)
            articles.insertAdjacentHTML("beforeend", `<article class="DELETEME" role="tabpanel" hidden id="${id}"><img id="img${id}" src="${element.url}" style="max-height: 80vh; max-width: 80vw;"/><p id="size${id}" class="pixelatedText">Original size: ${element.width}x${element.height}</p><p class="pixelatedText">Source: <a href="${element.url}">${element.url}</a></p></article>`)
            var img = document.getElementById(`img${id}`);
            img.onload = function () {
                console.log(`Original size: ${this.width}x${this.height}`)
                document.getElementById(`size${id}`).innerText = `Original size: ${this.width}x${this.height}`
            }
            num++;
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