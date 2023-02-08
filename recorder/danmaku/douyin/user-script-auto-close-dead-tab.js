// ==UserScript==
// @name         Auto close dead douyin danmaku tab
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  try to take over the world!
// @author       You
// @match        https://live.douyin.com/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function () {
  'use strict';

  console.log('Auto close dead douyin danmaku tab running...');

  setInterval(() => {
    if (window.is_danmaku_dead) {
      window.close();
    }
  }, 1000);
})();
