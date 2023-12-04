// ==UserScript==
// @name         Auto close dead douyin danmaku tab
// @namespace    http://tampermonkey.net/
// @version      1.1.0
// @description  try to take over the world!
// @author       You
// @match        https://live.douyin.com/*
// @grant        window.close
// @run-at       document-end
// ==/UserScript==

(function () {
  'use strict';

  if (!('is_danmaku_dead' in unsafeWindow)) {
    return;
  }

  console.log('Auto close dead douyin danmaku tab running...');

  let path = window.location.pathname;
  // key: douyin-danmaku-path-timestamp
  let storageKeyPrefix = 'douyin-danmaku-' + path;
  let storageKey = storageKeyPrefix + '-' + Date.now();

  localStorage.setItem(storageKey, 'alive');

  setInterval(() => {
    if (unsafeWindow.is_danmaku_dead) {
      window.close();
    }

    let pageList = [];
    for (let i = 0; i < localStorage.length; i++) {
      let key = localStorage.key(i);
      if (key.startsWith(storageKeyPrefix)) {
        let ts = key.split('-').pop();
        pageList.push({
          key,
          ts,
        });
      }
    }
    if (pageList.length > 1) {
      console.log('More than one page alive, close the oldest one.')
      console.log('pageList', pageList)
      pageList.sort((a, b) => a.ts - b.ts);
      let key = pageList[0].key;
      localStorage.removeItem(key);
      if (key === storageKey) {
        window.close();
      }
    }

  }, 1000);
})();
