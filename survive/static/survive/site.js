// onChange event for the Theme form change
function themeChange(value) {
    switch(value) {
        case "unjeff": 
            document.body.className = "theme_unjeff";
            break;
        case "bg_blue": 
            document.body.className = "theme_bg_blue";
            break;
        case "bg_grey":
            document.body.className = "theme_bg_grey";
            break;
        case "jeff_grey":
            document.body.className = "theme_jeff_grey";
            break;
        case "jeff":
        default: 
        document.body.className = "theme_jeff";
    }
}

// onLoad event for the Theme selector dropdown to properly populate on page load
function themeSelect() {
    document.getElementById("themeSelector").selectedIndex = 0;
}