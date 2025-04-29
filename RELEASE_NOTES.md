# Notes

**2025.04-1** | 30/Apr/25


* Edit notes (cards) directly during the review
  * It's possible to add **texts** only in the review stage
* Web Browser attached to main Window (Dock bar)
  * Instead of using a standalone window, it can be in multiple positions in the Anki Window
* Persist cookies (cookies are enabled and stored between executions)
  * This allows the user to login in sites and the session will remain in the next time using Anki
* Technical changes: 
  * Modified integration with Anki
    * The original integration is legacy. This new way aims to reduce un-expected bugs
  * Change integration with DarkReader
    * Tough still unstable

**7.2** | 17/Nov/23

* Fix issues with PyQt6 and new version of Anki
* Minor changes in blank page


**7.0** | 02/08/22

* Support base64 images (like in Google Images)
* Add image processing (reducing)
* Improve config view
* Change config to avoid losing configs between updates

**6.0** | 06/01/22

* Support Anki 2.50 / PyQt 6 (from @RisingOrange)
* Fix reading config from wrong location 

**5.0** | 11/10/21

* Introduce major feature: Search Groups 

**4.3** | 24/08/21

* Introduce new config view (prepare future features)
* Bug fixes
  - Issue #5
  - Issue #9

**4.2** | 29/08/20

* Bug fixes
  - NoneType message on close and reload
  - Issue #1
  - Broken warning message for unsupported links
* Added new shortcuts (back, forward, next / previous tab)

**4.1** | 17/04/20

* Small bug fix on *No selection option* on reviewer

**4.0** | 16/04/20

* Added support to tabs
* Added config for *Initial size*
    * Issue #50 (on previous repo: https://github.com/ssricardo/anki-plugins/issues/50)
* Fix bugs
* Added shortcuts on browser window
* Add experimental dark mode (DarkReader)

**3.0** | 18/01/20

* Added option to query without text selection
  * Type in terms or use value from Field
  * Memorize option
* On config window, added sorting for providers
  * Issues #28 and #40
* Added configuration to filter/strip set of words from the search
  * Issue #35
* Improve repeated options
  * Added *repeat operation* when assigning a value to the same field
  * Issue #37

**2.0** | 13/08/19

* Major changes on web browser window
  * Added common features: back, forward, stop, reload
  * Made possible to search with another provider within browser window
* Improve error handling
* Try to solve issues #22 and #25

**1.3** | 21/06

* Fix openLink using System browser  
  * Related issue #23
* Improve message for unaccepted links 
  * Shows the link on the message
  * Related issue #20

**1.2** | 31/05

* Improve the feedback
  * Shows message when the importing action is not available
  * Related issue #18
* Add shortcuts
  * Show web browser menu
  * Search again with same provider (skip menu)

**1.1** | 21/02/19

* Issues #5, #8 and #9
* Option to use the system web browser

**1.0**

* Initial version
  * Internal Web browser
  * Look up selected word
  * Import images and text







