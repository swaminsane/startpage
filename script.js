/* ===== CLOCK ===== */
function updateTime() {
    const now = new Date();
    document.getElementById("time").innerText =
        now.toLocaleTimeString();

    let h = now.getHours();
    let g = "Good evening...";
    if (h < 12) g = "Good morning...";
    else if (h < 18) g = "Good afternoon...";
    document.getElementById("greeting").innerText = g;
}
setInterval(updateTime, 1000);
updateTime();

/* ===== WEATHER ===== */
async function loadWeather() {
    try {
        let res = await fetch("https://wttr.in/Nawada?format=j1");
        let data = await res.json();

        let temp = data.current_condition[0].temp_C;
        let desc = data.current_condition[0].weatherDesc[0].value;

        document.getElementById("weather").innerHTML =
            `${desc} ${temp}°C<br>Nawada`;

    } catch {
        document.getElementById("weather").innerText =
            "weather unavailable";
    }
}
loadWeather();
setInterval(loadWeather, 600000);

/* ===== SEARCH MODE ===== */
let mode = "web";

document.getElementById("toggle").onclick = () => {
    mode = mode === "web" ? "file" : "web";
    document.getElementById("toggle").innerText =
        "Mode: " + (mode === "web" ? "Web" : "Files");
};

/* ===== SMART SEARCH ===== */
document.getElementById("search").addEventListener("keydown", async e => {
    if (e.key === "Enter") {
        let q = e.target.value.trim();

        if (!q) return;

        let parts = q.split(" ");
        let cmd = parts[0];
        let rest = parts.slice(1).join(" ");

        /* ===== SHORTCUTS ===== */
        let shortcuts = {
            yt: "https://invidious.nerdvpn.de/search?q=",
            arc: "https://archive.org/search?query=",
            wiki: "https://en.wikipedia.org/wiki/"
        };

        // If shortcut matched
        if (shortcuts[cmd]) {
            let target = rest || cmd; // fallback if no extra text
            window.location.href =
                shortcuts[cmd] + encodeURIComponent(target);
            return;
        }

        /* ===== NORMAL SEARCH ===== */
        if (mode === "web") {
            window.location.href =
                "https://duckduckgo.com/?q=" + encodeURIComponent(q);
        } else {
            let res = await fetch("/search?q=" + encodeURIComponent(q));
            let files = await res.json();
            showResults(files);
        }
    }
});

/* ===== FILE RESULTS ===== */
function showResults(files) {
    let div = document.getElementById("results");
    div.innerHTML = "";

    files.forEach(f => {
        let a = document.createElement("a");
        a.innerText = f;
        a.href = "file://" + f;
        a.style.display = "block";
        a.style.color = "#aaa";
        div.appendChild(a);
    });
}

/* ===== BOOKMARKS (MANUAL ONLY) ===== */
let bookmarks = {
    dev: [
        { name: "GitHub", url: "https://github.com/swaminsane" },
        { name: "Site", url: "https://swaminsane.github.io"}
    ],
    social: [
        { name: "Archive", url: "https://archive.org/details/@swami_vivekanand712/collections"}
    ],
    media: [],
    tools: [
        { name: "Syncthing", url: "http://localhost:8384"}
    ]
};

/* ===== RENDER ===== */
function render() {
    let container = document.getElementById("bookmarks");
    container.innerHTML = "";

    Object.keys(bookmarks).forEach(cat => {
        let card = document.createElement("div");
        card.className = "card";

        let html = "<b>" + cat + "</b>";

        bookmarks[cat].forEach(b => {
            html += `<a href="${b.url}" target="_blank">${b.name}</a>`;
        });

        card.innerHTML = html;
        container.appendChild(card);
    });
}

/* ===== AUTO FOCUS SEARCH (nice UX) ===== */
document.getElementById("search").focus();

 /* ===== MPD ===== */
async function loadMPD() {
    try {
        let res = await fetch("/mpd");
        let data = await res.json();

        document.getElementById("song").innerText = data.song;
        document.getElementById("progress").style.width =
            data.progress + "%";

    } catch {
        document.getElementById("song").innerText = "mpd offline";
    }
}

// refresh every 2 sec (smooth progress)
setInterval(loadMPD, 2000);
loadMPD();

/* INIT */
render();
