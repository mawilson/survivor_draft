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

window.addEventListener("DOMContentLoaded", themeSelectorInitialize);