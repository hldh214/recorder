// ==UserScript==
// @name         douyin-danmaku
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Detect if still recording and send danmaku to ws-server, otherwise reload the page.
// @author       You
// @match        https://live.douyin.com/590890573
// @icon         https://www.google.com/s2/favicons?sz=64&domain=douyin.com
// @grant        none
// ==/UserScript==

(function () {
  'use strict';

  setInterval(() => {
    if (window.ws_rpc_last_send_time) {
      const now = Date.now();
      // if no danmaku in 60s, reload the page
      if (now - window.ws_rpc_last_send_time > 1000 * 60) {
        location.reload();
      }
    } else {
      // if no danmaku yet, reload the page
      location.reload();
    }
  }, 1000 * 10)
})();
