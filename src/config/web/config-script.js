var curConfig = {}

var pages = [
    {
        "label": "Main",
        "page": "./config-misc.html",
        "loadFn": () => loadMain(),
        "storeFn": () => saveMain(),
    },
    {
        "label": "Search Providers",
        "page": "./config-providers.html",
        "loadFn": () => loadProviders(),
        "storeFn": () => saveProviders(),
    },
    {
        "label": "Search Groups",
        "page": "./config-groups.html",
        "loadFn": () => initGroupsPage(),
        "storeFn": () => saveGroups(),
    },
    {
        "label": "Pos Processing",
        "page": "./config-pos-import.html",
        "loadFn": () => loadPosProcess(),
        "storeFn": () => savePosProcess(),
    }
]

var currentPage = -1

function load(index) {
    if (currentPage > -1) {
        pages[currentPage].storeFn()
    }
    $('#lkPrevious').text('')
    $('#lkNext').text('')

    if (index >= 0 && index < pages.length) {
        let actual = pages[index]
        $( "#content" ).fadeOut("fast", function() {
            $( "#content" ).load(actual.page);
            $( "#content" ).fadeIn("slow");

            currentPage = index
            setTimeout(actual.loadFn, 150);

            if (index > 0) {
                $('#lkPrevious').text(`(${pages[index - 1].label})`)
                $('#btPrev').removeClass('disabled2')
            } else {
                $('#btPrev').addClass('disabled2')
            }
            if (index < pages.length - 1) {
                $('#lkNext').text(`(${pages[index + 1].label})`)
                $('#btNext').removeClass('disabled2')
            } else {
                $('#btNext').addClass('disabled2')
            }
        })        
    }
    
}

function init() {
    $("#mainActions").empty()
    for (i = 0; i < pages.length; i++) {
        $("#mainActions").append(createLinkForPage(pages[i], i))
    }
    load(0)
}

function createLinkForPage(pg, index) {
    return $(`<button id='lk${index}' onclick='load(${index})'>`)
        .append('<img src="../../assets/ext-link.png" />')
        .append(`<span> ${pg.label}</span>`)
}

function loadConfig(value) {
    curConfig = value;
    init()
    return "Done"
}

function save() {
    if (currentPage > -1) {
        pages[currentPage].storeFn()
    }    
}

function saveAndGetConfig() {
    save()
    return curConfig
}