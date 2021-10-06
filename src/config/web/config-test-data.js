/* Used only for testing purpose */

let config = {
  "providers": [
    {
      "name": "Insta",
      "url": "https://instagram.com/{}"
    },
    {
      "name": "LinkedIn",
      "url": "https://linkedin.com/{}"
    }
  ],
  "groups": [
    {
      "name": "Others",
      "providerList": [
        "Insta",
        "LinkedIn"
      ]
    }
  ],
  "keepBrowserOpened": true,
  "browserAlwaysOnTop": false,
  "useSystemBrowser": false,
  "menuShortcut": "Ctrl+Shift+B",
  "repeatShortcut": "F10",
  "filteredWords": [],
  "initialBrowserSize": "850x500",
  "enableDarkReader": true
}

loadConfig(config);