var youtubeWindow = document.getElementById("youtubeWindow");
var loadingWindow = document.getElementById("loadingWindow");
var youtubeVideoWindow = document.getElementById("youtubeVideoWindow");

function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s * 1000));
}


async function startDownloadingVideo(button) {
    button.setAttribute("disabled", true)
    var e = document.getElementById("videoUrl");
    var text = e.value;
    var type = document.querySelector('input[name="type"]:checked').value;
    if (text.includes("youtube.com/watch?v=")) {
        var id = text.substring(text.indexOf("v=") + 2, text.length)
    } else if (text.includes("youtu.be/")) {
        var id = text.substring(text.indexOf(".be/") + 4, text.length)
    } else {
        var id = "";
    }
    if (id.length == 11) {
        let xhr = new XMLHttpRequest();
        xhr.open("POST", "/youtube");
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");

        xhr.onreadystatechange = async function () {
            if (xhr.readyState === 4 && xhr.status === 429) {
                alert("Too many requests, try again later.");
            } else if (xhr.readyState === 4) {
                var json = JSON.parse(xhr.responseText)
                if (json == true) {
                    await showVideoWindow(id, type)
                } else if (json == null) {
                    alert("Sorry I can't download this video")
                }
                else {
                    await showLoadingWindow(id, type)
                }
            }
        };
        xhr.send(JSON.stringify({ "id": id, "type": parseInt(type, 10) }));
    } else {
        alert("Wrong url format.")
    }
    button.removeAttribute("disabled");
}

async function showLoadingWindow(id, type) {
    youtubeWindow.setAttribute("hidden", "true");
    loadingWindow.removeAttribute("hidden")
    let xhr = new XMLHttpRequest();
    var done = false;
    xhr.onreadystatechange = async function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var json = JSON.parse(xhr.responseText)
            if (json == true) {
                done = true;
            } else if (json == null) {
                alert("Sorry I can't download this video");
                done = null;
            }
        } else if (xhr.readyState === 4) {
            alert("Something went wrong. Please try again later");
            done = null;
        }
    }
    while (true) {
        await sleep(4);
        xhr.open("GET", `/youtube?id=${id}&type=${type}`);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(null);
        await sleep(1);
        if (done != false) break;
    };
    if (done == true) {
        await showVideoWindow(id, type);
    } else {
        loadingWindow.setAttribute("hidden", "true");
        youtubeWindow.removeAttribute("hidden")
    }
}

async function showVideoWindow(id, type) {
    youtubeWindow.setAttribute("hidden", "true");
    loadingWindow.setAttribute("hidden", "true");
    youtubeVideoWindow.removeAttribute("hidden")
    a = document.getElementById("aForButton")
    a.setAttribute("href", `/youtube/download?id=${id}&type=${type}`)
    element = document.getElementById("urlForDownloading");
    element.innerHTML = `https://holy-coder.ru/youtube/download?id=${id}&type=${type}`
    element.setAttribute("href", `/youtube/download?id=${id}&type=${type}`)
}

function hideVideoWindow() {
    youtubeVideoWindow.setAttribute("hidden", "true");
    youtubeWindow.removeAttribute("hidden");
}