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
                alert(MS["too_many_requests"]);
            } else if (xhr.readyState === 4) {
                var json = JSON.parse(xhr.responseText)
                if (typeof json === 'string' || json instanceof String) {
                    await showVideoWindow(id, type, json)
                } else if (json == null) {
                    alert(MS["cant_download"])
                }
                else {
                    await showLoadingWindow(id, type)
                }
            }
        };
        xhr.send(JSON.stringify({ "id": id, "type": parseInt(type, 10) }));
    } else {
        alert(MS["wrong_url"])
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
            if (typeof json === 'string' || json instanceof String) {
                done = true;
                filename = json;
            } else if (json == null) {
                alert(MS["cant_download"]);
                done = null;
            }
        } else if (xhr.readyState === 4) {
            alert(MS["error"]);
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
        await showVideoWindow(id, type, filename);
    } else {
        loadingWindow.setAttribute("hidden", "true");
        youtubeWindow.removeAttribute("hidden")
    }
}

async function showVideoWindow(id, type, filename) {
    youtubeWindow.setAttribute("hidden", "true");
    loadingWindow.setAttribute("hidden", "true");
    youtubeVideoWindow.removeAttribute("hidden")
    a = document.getElementById("aForButton")
    a.setAttribute("href", `/youtube/${filename}?id=${id}&type=${type}`)
    var element = document.getElementById("urlForDownloading");
    element.innerText = `https://holy-coder.ru/youtube/${filename}?id=${id}&type=${type}`
    element.setAttribute("href", `/youtube/${filename}?id=${id}&type=${type}`)
}

function hideVideoWindow() {
    youtubeVideoWindow.setAttribute("hidden", "true");
    youtubeWindow.removeAttribute("hidden");
}