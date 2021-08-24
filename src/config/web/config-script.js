var curConfig = {}

var pages = [
    {
        "label": "Main",
        "page": "./config-misc.html",
        "loadFn": () => loadMain(),
        "storeFn": () => saveMain(),
    },
    {
        "label": "Providers",
        "page": "./config-providers.html",
        "loadFn": () => loadProviders(),
        "storeFn": () => saveProviders(),
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
                $('#btPrev').removeClass('disabled')
            } else {
                $('#btPrev').addClass('disabled')
            }
            if (index < pages.length - 1) {
                $('#lkNext').text(`(${pages[index + 1].label})`)
                $('#btNext').removeClass('disabled')
            } else {
                $('#btNext').addClass('disabled')
            }
        })        
    }
    
}

function init() {
    load(0)
}

function loadConfig(value) {
    curConfig = value;
    init()
    return "Done"
}

function next() {
    if (currentPage < pages.length - 1) {
        load(currentPage + 1)
    }
}

function previous() {
    if (currentPage > 0) {
        load(currentPage - 1)
    } 
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