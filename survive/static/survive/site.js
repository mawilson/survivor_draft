// onChange event for the Theme form change
function themeChange(value) {
    switch(value) {
        case "unjeff":
            document.cookie = "survivorTheme=unjeff;samesite=lax";
            document.body.className = "theme_unjeff";
            break;
        case "bg_blue":
            document.cookie = "survivorTheme=bg_blue;samesite=lax";
            document.body.className = "theme_bg_blue";
            break;
        case "bg_grey":
            document.cookie = "survivorTheme=bg_grey;samesite=lax";
            document.body.className = "theme_bg_grey";
            break;
        case "jeff_grey":
            document.cookie = "survivorTheme=jeff_grey;samesite=lax";
            document.body.className = "theme_jeff_grey";
            break;
        case "jeff":
        default: 
            document.cookie = "survivorTheme=jeff;samesite=lax";
            document.body.className = "theme_jeff";
    }
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
                themeChange(cookie[1]);
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