// onChange event for the Theme form change. Cookie only gets set if setCookie provided as 'true'
function themeChange(value, setCookie) {
    let cookie, className;
    let age = (30 * 60 * 24 * 365) // half of a year lifetime
    switch(value) {
        case "unjeff":
            cookie = "survivorTheme=unjeff;samesite=lax;path=/;";
            className = "theme_unjeff";
            break;
        case "bg_blue":
            cookie = "survivorTheme=bg_blue;samesite=lax;path=/;";
            className = "theme_bg_blue";
            break;
        case "bg_grey":
            cookie = "survivorTheme=bg_grey;samesite=lax;path=/;";
            className = "theme_bg_grey";
            break;
        case "jeff_grey":
            cookie = "survivorTheme=jeff_grey;samesite=lax;path=/;";
            className = "theme_jeff_grey";
            break;
        case "jeff":
        default: 
            cookie = "survivorTheme=jeff;samesite=lax;path=/;";
            className = "theme_jeff";
    }
    cookie = cookie + "max-age=" + age + ";";
    if (setCookie) {
        document.cookie = cookie;
    }
    className = className + " survivor_cursor"; // also add torch cursor
    document.body.className = className;
}

// onLoad event for the Theme selector dropdown to properly populate on page load
function themeSelectorInitialize() {
    if (navigator.cookieEnabled) { // if cookies are enabled, use them to retrieve the last theme used & set it
        processCookies();
    } else { // if cookies are not enabled, Jeff by default
        document.getElementById("theme_selector").selectedIndex = 0;
    }
}

function processCookies() {
    let cookies = document.cookie
        .split("; "); // each cookie is delimited by a semicolon & space - the space matters, as cookie attributes are specified immediately following the semicolon
    //    .find((row) => row.startsWith("test2="))
    //    ?.split("=")[1];
    for (const _cookie of cookies) { // iterate through the cookies & do stuff with each
        let cookie = _cookie.split("=");
        if (cookie.length === 2) { // cookie is only valid for processing if it looks like key=value, split will have != 2 elements otherwise
            if (cookie[0] === "survivorTheme") {
                let themeSelector = document.getElementById("theme_selector");
                themeChange(cookie[1], set_cookie = false);
                switch (cookie[1]) {
                    case "unjeff":
                        themeSelector.selectedIndex = 1;
                        break;
                    case "jeff_grey":
                        themeSelector.selectedIndex = 2;
                        break;
                    case "bg_blue":
                        themeSelector.selectedIndex = 3;
                        break;
                    case "bg_grey":
                        themeSelector.selectedIndex = 4;
                        break;
                    case "jeff":
                    default:
                        themeSelector.selectedIndex = 0;
                }
            }
        }
    }
}

function linked_seasons_display_toggle(e) {
    let season = e.value; // should be the season ID of the linked season to display or hide
    let enabled = e.checked; // whether the box was checked or unchecked
    let linked_season_teams = document.getElementsByName("linked_season_" + season + "_team");
    for (let t of linked_season_teams) {
        if (enabled) {
            t.style.display = "";
        } else {
            t.style.display = "none";
        }
    }
}

function linked_seasons_visibility_on_load() {// function to show or hide teams on page load based on linked_seasons checkbox statuses
    let linked_season_checkboxes = document.getElementsByName("linked_seasons_checkbox"); // get all linked_seasons_checkboxes
    for (let c of linked_season_checkboxes) { // for each checkbox, will enable or disable teams with matching season values based on checked property
        linked_seasons_display_toggle(c);
    }
}

window.addEventListener("DOMContentLoaded", themeSelectorInitialize);
window.addEventListener("DOMContentLoaded", linked_seasons_visibility_on_load);

// function called to create a web socket listening on the season ID group for draft_marker updates
function createDraftWatchSocket(season_id) {
    const chatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/live_draft/'
        + season_id
        + '/'
    );
    
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let draft_marker = parseInt(data.message);
        let draft_ordering_list_items = document.querySelectorAll("li[name='draft_ordering']");
        if (draft_ordering_list_items) {
            for (const li of draft_ordering_list_items) {
                let parts = li.innerText.split(" ");
                if (parts.length > 2) {
                    let position = parseInt(parts[0].substring(0, parts[0].length - 1), 10);
                    let team_name;
                    if (parts[parts.length - 1] === "(current)") {
                        team_name = parts.slice(1, parts.length - 1).join(" ");
                    } else {
                        team_name = parts.slice(1).join(" ");
                    }
                    if (draft_marker === position) {
                        li.innerText = position + ": " + team_name + " (current)";
                        li.className = "font-bold";
                    } else {
                        li.innerText = position + ": " + team_name;
                        li.className = "";
                    }
                }
            }
            let draft_complete = document.querySelector("li[name='draft_complete']");
            if (draft_marker > draft_ordering_list_items.length) {
                draft_complete.style.display = ""; // show draft complete if draft marker is greater than number of survivors
            } else {
                draft_complete.style.display = "none"; // hide draft complete if draft marker is not beyond number of survivors
            }
        }
    };
    
    chatSocket.onclose = function(e) {
        if (e.code !== 1000) {
            console.error('Chat socket closed unexpectedly. Code, reason, wasClean: ' + e.code + ', ' + e.reason + ', ' + e.wasClean)
        }
    };
}