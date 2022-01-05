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
    },
    {
      "name": "Insta2",
      "url": "https://instagram2.com/{}"
    },
    {
      "name": "Insta3",
      "url": "https://instagram4.com/{}"
    },
    {
      "name": "Insta4",
      "url": "https://instagram4.com/{}"
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