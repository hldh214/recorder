"use strict";

console.log("======================== Recorder hook start ========================");
window.is_danmaku_dead = false;
window.danmaku_reload_interval = setInterval(() => {
  if (window.ws_rpc_last_send_time) {
    const now = Date.now();
    // if no danmaku in 60s
    if (now - window.ws_rpc_last_send_time > 1000 * 60) {
      console.log("======================== Recorder hook dead ========================");
      window.is_danmaku_dead = true;
      clearInterval(window.danmaku_reload_interval);
    }
  } else {
    // if no danmaku yet
    console.log("======================== Recorder hook dead ========================");
    window.is_danmaku_dead = true;
    clearInterval(window.danmaku_reload_interval);
  }
}, 1000 * 60);

(self.__LOADABLE_LOADED_CHUNKS__ = self.__LOADABLE_LOADED_CHUNKS__ || []).push([[5285], {
  75570: (e,t,n)=>{
    n.d(t, {
      Z: ()=>l
    });
    var r, o, i = n(44503);
    function a() {
      return a = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        a.apply(this, arguments)
    }
    const l = function(e) {
      return i.createElement("svg", a({
        width: 22,
        height: 9,
        viewBox: "0 0 22 9",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = i.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M5.483 1.137C4.923.379 4.113 0 3.055 0 2.187 0 1.461.284.876.853.292 1.413 0 2.128 0 2.996c0 .853.249 1.543.746 2.072.521.561 1.208.841 2.06.841.435 0 .822-.083 1.161-.248a2.32 2.32 0 00.912-.782h.06v.107c0 .797-.167 1.464-.498 2-.348.57-.81.853-1.386.853-.829 0-1.33-.402-1.504-1.207H.166C.379 8.21 1.338 9 3.043 9c1.003 0 1.8-.438 2.393-1.314.584-.869.876-2.01.876-3.423 0-1.326-.276-2.368-.83-3.126zm-3.612.556c.316-.347.726-.52 1.232-.52.497 0 .904.157 1.22.473.307.316.461.75.461 1.303 0 .56-.146 1.002-.438 1.326-.3.324-.714.486-1.243.486-.521 0-.932-.162-1.232-.486-.308-.316-.462-.742-.462-1.279 0-.529.154-.963.462-1.303zM12.754 1.137C12.194.379 11.384 0 10.326 0c-.868 0-1.594.284-2.179.853-.584.56-.876 1.275-.876 2.143 0 .853.249 1.543.746 2.072.521.561 1.208.841 2.06.841.435 0 .822-.083 1.161-.248a2.32 2.32 0 00.912-.782h.06v.107c0 .797-.167 1.464-.498 2-.348.57-.81.853-1.386.853-.829 0-1.33-.402-1.504-1.207H7.437C7.65 8.21 8.609 9 10.315 9c1.002 0 1.8-.438 2.392-1.314.584-.869.876-2.01.876-3.423 0-1.326-.276-2.368-.83-3.126zm-3.612.556c.316-.347.726-.52 1.232-.52.497 0 .904.157 1.22.473.307.316.461.75.461 1.303 0 .56-.146 1.002-.438 1.326-.3.324-.714.486-1.243.486-.521 0-.932-.162-1.232-.486-.308-.316-.462-.742-.462-1.279 0-.529.154-.963.462-1.303z",
        fill: "#fff"
      })), o || (o = i.createElement("path", {
        d: "M19.181 1.654h-1.137V4.14h-2.498v1.15h2.498v2.486h1.137V5.289h2.487V4.14H19.18V1.654z",
        fill: "#fff"
      })))
    }
  }
  ,
  76953: (e,t,n)=>{
    n.d(t, {
      Z: ()=>a
    });
    var r, o = n(44503);
    function i() {
      return i = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        i.apply(this, arguments)
    }
    const a = function(e) {
      return o.createElement("svg", i({
        width: 20,
        height: 32,
        viewBox: "0 0 12 12",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = o.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M.6 5.684C.6 2.874 3.02.6 6 .6c2.982 0 5.4 2.273 5.4 5.084 0 2.81-2.418 5.084-5.4 5.084 0 0-1.308.076-1.84.2-.35.076-.944.276-1.309.399a.42.42 0 01-.562-.292c-.054-.225-.034-.756-.018-1.166.011-.289.02-.518-.001-.537C1.249 8.44.6 7.132.6 5.684zm6.814 1.095a.684.684 0 11.394 1.31l-.004.001-.01.003-.032.009a7.48 7.48 0 01-.503.118c-.317.063-.756.13-1.209.13-.453 0-.892-.067-1.208-.13a7.485 7.485 0 01-.504-.118l-.032-.01-.01-.002h-.003l-.002-.002a.683.683 0 01-.462-.85.69.69 0 01.858-.46l.003.002.02.005.085.023a6.1 6.1 0 00.317.071c.269.054.61.103.938.103.328 0 .67-.05.938-.103a6.1 6.1 0 00.402-.094l.02-.005.004-.001z",
        fill: "#2F3035",
        fillOpacity: .9
      })))
    }
  }
  ,
  79757: (e,t,n)=>{
    n.d(t, {
      Z: ()=>a
    });
    var r, o = n(44503);
    function i() {
      return i = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        i.apply(this, arguments)
    }
    const a = function(e) {
      return o.createElement("svg", i({
        width: 20,
        height: 32,
        viewBox: "0 0 16 16",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = o.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M9.063 1.563a1.063 1.063 0 00-2.126 0v.606A5.964 5.964 0 002.03 8.038v4.504h-.05a1.062 1.062 0 100 2.125h12.042a1.063 1.063 0 000-2.125h-.067V8.038a5.964 5.964 0 00-4.892-5.867v-.608zm-2.126 14.52a1.063 1.063 0 000 2.125h2.125a1.063 1.063 0 000-2.125H6.938z",
        fill: "#2F3035",
        fillOpacity: .9
      })))
    }
  }
  ,
  59304: (e,t,n)=>{
    n.d(t, {
      uH: ()=>j,
      yP: ()=>G,
      S: ()=>X,
      Lf: ()=>K
    });
    var r = n(30673)
      , o = n(32781)
      , i = n(65146)
      , a = n(88438)
      , l = n.n(a)
      , s = n(94610)
      , c = n.n(s)
      , u = n(84578)
      , d = n.n(u)
      , m = n(92012)
      , v = n.n(m)
      , f = n(79705)
      , h = n.n(f)
      , p = n(44503)
      , g = n(35913)
      , y = n(72302)
      , w = n(27063);
    const _ = "xpbnjqXa"
      , E = "DBVNu1Yo"
      , k = "L1m4jyWo"
      , x = "OhjN0KNR"
      , b = "QI_g4_k6"
      , C = "JBAFnypq"
      , N = "i4vdvOF5"
      , T = "L8o4Hyg1"
      , Z = "LFbb1oon"
      , S = "R6NHkCAw"
      , I = "WUYWjT8q"
      , L = "NQ5SUMaK"
      , D = "eMehXMtB"
      , M = "uN5UCaPA"
      , B = "cTANKPmO"
      , A = "QCfRJhpK"
      , P = "uoSgVxqA"
      , O = "GUqKWZi6"
      , V = "lFvnFfVZ"
      , W = "qEOFp17k"
      , R = "DhFyQEaz"
      , F = "pedvPIfF"
      , U = "vbTjf9Q0";
    var H, G, j;
    !function(e) {
      e[e.AUDIO_1V8 = 0] = "AUDIO_1V8",
        e[e.AUDIO_GRID = 1] = "AUDIO_GRID",
        e[e.VIDEO_1V6 = 2] = "VIDEO_1V6",
        e[e.VIDEO_GRID = 3] = "VIDEO_GRID",
        e[e.VIDEO_DYNAMIC = 4] = "VIDEO_DYNAMIC",
        e[e.VIDEO_6V6 = 5] = "VIDEO_6V6"
    }(G || (G = {})),
      function(e) {
        e[e.NONE = 0] = "NONE",
          e[e.ORDER_SING = 1] = "ORDER_SING"
      }(j || (j = {}));
    var K = (0,
      i.Z)({}, G.VIDEO_6V6, 6)
      , q = (H = {},
      (0,
        i.Z)(H, G.AUDIO_1V8, 50.4),
      (0,
        i.Z)(H, G.AUDIO_GRID, 42),
      (0,
        i.Z)(H, G.VIDEO_1V6, 42.5),
      (0,
        i.Z)(H, G.VIDEO_DYNAMIC, 63.56),
      (0,
        i.Z)(H, G.VIDEO_GRID, 62.45),
      (0,
        i.Z)(H, G.VIDEO_6V6, 61),
      H)
      , Y = 16 / 9
      , X = function(e) {
      var t, n = e.layout, a = e.renderElement, s = e.count, u = e.className, m = e.isTheaterOn, f = e.renderPK, H = p.useRef(), j = p.useState(Y), K = (0,
        o.Z)(j, 2), X = K[0], z = K[1], Q = (0,
        y.n)().player, J = p.useCallback((function() {
          var e, t, n = null == Q || null === (e = Q.root) || void 0 === e ? void 0 : e.clientWidth, r = null == Q || null === (t = Q.root) || void 0 === t ? void 0 : t.clientHeight;
          return n && r ? n / r : Y
        }
      ), []), $ = p.useCallback((function() {
          clearTimeout(H.current),
            H.current = l()((function() {
                var e = J();
                z(e)
              }
            ), 50)
        }
      ), []);
      p.useEffect((function() {
          return null == Q || Q.on(g.FULLSCREEN_CHANGE, $),
            function() {
              null == Q || Q.off(g.FULLSCREEN_CHANGE, $)
            }
        }
      ), []);
      var ee = p.useCallback((function() {
          var e = J();
          z(e)
        }
      ), []);
      p.useEffect((function() {
          return window.addEventListener("resize", ee),
            function() {
              window.removeEventListener("resize", ee)
            }
        }
      ), []),
        p.useEffect((function() {
            $()
          }
        ), [m]);
      var te = p.useMemo((function() {
          return "".concat(q[n] * Y / X, "%")
        }
      ), [X, n])
        , ne = p.useMemo((function() {
          var e;
          return p.createElement("div", {
            className: E,
            style: {
              width: te
            }
          }, c()(e = (0,
            r.Z)(Array(3))).call(e, (function(e, t) {
              var n, o;
              return p.createElement("div", {
                className: k,
                key: t
              }, c()(n = d()(o = (0,
                r.Z)(Array(3))).call(o, 0, 3)).call(n, (function(e, n) {
                  var r;
                  return p.createElement("div", {
                    className: x,
                    key: v()(r = "".concat(t, "_")).call(r, n)
                  }, a(n + 3 * t))
                }
              )))
            }
          )))
        }
      ), [a, te])
        , re = p.useMemo((function() {
          var e;
          return p.createElement("div", {
            className: E,
            style: {
              width: te
            }
          }, p.createElement("div", {
            className: b
          }, a(0)), c()(e = (0,
            r.Z)(Array(2))).call(e, (function(e, t) {
              var n, o;
              return p.createElement("div", {
                className: k,
                key: t
              }, c()(n = d()(o = (0,
                r.Z)(Array(4))).call(o, 0, 4)).call(n, (function(e, n) {
                  var r;
                  return p.createElement("div", {
                    className: b,
                    key: v()(r = "".concat(t, "_")).call(r, n)
                  }, a(n + 4 * t + 1))
                }
              )))
            }
          )))
        }
      ), [a, te])
        , oe = p.useMemo((function() {
          var e;
          return p.createElement("div", {
            className: h()(C, "theaterGridContainer"),
            style: {
              width: te
            }
          }, c()(e = (0,
            r.Z)(Array(3))).call(e, (function(e, t) {
              var n, o;
              return p.createElement("div", {
                className: k,
                key: t
              }, c()(n = d()(o = (0,
                r.Z)(Array(3))).call(o, 0, 3)).call(n, (function(e, n) {
                  var r;
                  return p.createElement("div", {
                    className: h()(N, "videoItem"),
                    key: v()(r = "".concat(t, "_")).call(r, n)
                  }, a(n + 3 * t))
                }
              )))
            }
          )))
        }
      ), [a, te])
        , ie = p.useMemo((function() {
          var e;
          return p.createElement("div", {
            className: T,
            style: {
              width: te
            }
          }, p.createElement("div", {
            className: Z
          }, a(0)), p.createElement("div", {
            className: S
          }, c()(e = (0,
            r.Z)(Array(6))).call(e, (function(e, t) {
              return p.createElement("div", {
                className: h()(N, "videoItem"),
                key: t
              }, a(t + 1))
            }
          ))))
        }
      ), [a, te])
        , ae = p.useMemo((function() {
          var e, t = (0,
            w.Aw)(s), n = t.col, o = t.row, i = 1 / n, l = 1 / o, u = .5 * (1 - s % n * i);
          return p.createElement("div", {
            className: h()(I, "theaterGridContainer"),
            style: {
              flexDirection: 3 === s ? "column" : void 0,
              width: te
            }
          }, c()(e = (0,
            r.Z)(Array(s))).call(e, (function(e, t) {
              return p.createElement("div", {
                key: t,
                className: h()(N, "videoItem"),
                style: {
                  width: "".concat(100 * i, "%"),
                  height: "".concat(0 === t && 3 === s ? 100 : 100 * l, "%")
                }
              }, a(t))
            }
          )), s % n != 0 && 3 !== s && p.createElement(p.Fragment, null, p.createElement("div", {
            className: h()(L, D),
            style: {
              width: "".concat(100 * u, "%"),
              height: "".concat(100 * l, "%")
            }
          }), p.createElement("div", {
            className: h()(L, M),
            style: {
              width: "".concat(100 * u, "%"),
              height: "".concat(100 * l, "%")
            }
          })))
        }
      ), [s, a, te])
        , le = p.useMemo((function() {
          var e;
          return p.createElement("div", {
            className: B
          }, p.createElement("div", {
            className: A
          }), p.createElement("div", {
            className: h()(O, "theaterGridContainer"),
            style: {
              width: te
            }
          }, p.createElement("div", {
            className: h()(V)
          }, f && f()), p.createElement("div", {
            className: h()(_)
          }, c()(e = (0,
            r.Z)(Array(2))).call(e, (function(e, t) {
              var n;
              return p.createElement("div", {
                className: h()(0 === t ? W : R),
                key: t
              }, c()(n = (0,
                r.Z)(Array(3))).call(n, (function(e, n) {
                  var o, i, l;
                  return p.createElement("div", {
                    className: k,
                    key: v()(o = "".concat(t, "_")).call(o, n)
                  }, c()(i = d()(l = (0,
                    r.Z)(Array(2))).call(l, 0, 2)).call(i, (function(e, r) {
                      var o, i;
                      return p.createElement("div", {
                        className: h()(N, "videoItem"),
                        key: v()(o = v()(i = "".concat(t, "_")).call(i, n, "_")).call(o, r)
                      }, a(r + 2 * n + 6 * t))
                    }
                  )))
                }
              )))
            }
          )))), p.createElement("div", {
            className: P
          }))
        }
      ), [a, te, f]);
      return p.createElement("div", {
        className: h()(_, u, (t = {},
          (0,
            i.Z)(t, F, n === G.AUDIO_1V8 || n === G.AUDIO_GRID),
          (0,
            i.Z)(t, U, n === G.VIDEO_6V6),
          t))
      }, n === G.AUDIO_1V8 && re, n === G.AUDIO_GRID && ne, n === G.VIDEO_1V6 && ie, n === G.VIDEO_DYNAMIC && ae, n === G.VIDEO_GRID && oe, n === G.VIDEO_6V6 && le)
    }
  }
  ,
  3505: (e,t,n)=>{
    n.d(t, {
      G: ()=>E
    });
    var r, o, i, a, l, s, c = n(30906), u = n(32781), d = n(67161), m = n(75403), v = n(80212), f = n(79705), h = n.n(f), p = n(58256), g = n(44503), y = n(51333);
    !function(e) {
      e[e.DEFAULT = 0] = "DEFAULT",
        e[e.NONE_DEFAULT = 1] = "NONE_DEFAULT"
    }(r || (r = {})),
      function(e) {
        e[e.DEFAULT = 0] = "DEFAULT",
          e[e.NONE_DEFAULT = 1] = "NONE_DEFAULT"
      }(o || (o = {})),
      function(e) {
        e[e.RECOMMEND = 1] = "RECOMMEND",
          e[e.NOT_RECOMMEND = 0] = "NOT_RECOMMEND"
      }(i || (i = {})),
      function(e) {
        e[e.LOGIN = 1] = "LOGIN",
          e[e.NOT_LOGIN = 0] = "NOT_LOGIN"
      }(a || (a = {})),
      function(e) {
        e.VERTICAL = "vertical",
          e.HORIZONTAL = "horizontal"
      }(l || (l = {})),
      function(e) {
        e[e.UNK_NOWN = 0] = "UNK_NOWN",
          e[e.LIVE = 1] = "LIVE",
          e[e.FIRST_LIVE = 2] = "FIRST_LIVE",
          e[e.RECORD_LIVE = 3] = "RECORD_LIVE"
      }(s || (s = {}));
    var w = function(e) {
      window.collectEvent("livesdk_second_tab_click", (0,
        c.Z)((0,
        c.Z)({}, {
        url: location.href,
        url_path: location.pathname
      }), {}, {
        tab_name: "live"
      }, e))
    }
      , _ = ["href", "children", "style", "className", "passParamKeys", "spa", "onClick", "passParams", "firstTabName", "onClickLog", "title"]
      , E = function(e) {
      var t = e.href
        , n = e.children
        , r = e.style
        , o = e.className
        , i = e.passParamKeys
        , a = void 0 === i ? [] : i
        , l = e.spa
        , s = e.onClick
        , f = e.passParams
        , E = void 0 === f ? {} : f
        , k = e.firstTabName
        , x = e.onClickLog
        , b = e.title
        , C = (0,
        d.Z)(e, _)
        , N = g.useState(t)
        , T = (0,
        u.Z)(N, 2)
        , Z = T[0]
        , S = T[1];
      g.useEffect((function() {
          S(t)
        }
      ), [t]);
      var I = g.useCallback((function(e) {
          if (s && s(e),
            t) {
            x && w({
              category_name: k,
              more_detail: b,
              enter_from: "hot_hover"
            });
            var n = t.split("?", 2)
              , r = (0,
              u.Z)(n, 2)
              , o = r[0]
              , i = r[1]
              , l = []
              , d = m.U(a)
              , v = (0,
              c.Z)((0,
              c.Z)((0,
              c.Z)({}, window.__INVISIBLE_QUERY__ || {}), d), E)
              , f = (0,
              p.stringify)(v);
            f && l.push(f),
            i && l.push(i),
              l.length > 0 ? S([o, l.join("&")].join("?")) : S(o)
          }
        }
      ), [t, a, s, E]);
      return l ? g.createElement(y.rU, (0,
        c.Z)((0,
        c.Z)({
        to: Z || "",
        style: r,
        className: h()(o),
        onClick: I
      }, C), {}, {
        target: v.f() ? "_self" : C.target
      }), n) : g.createElement("a", (0,
        c.Z)((0,
        c.Z)({
        href: globalThis.getFilterXss().filterUrl(Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: o,
        style: r,
        onClick: I
      }, C), {}, {
        target: v.f() ? "_self" : C.target
      }), n)
    }
  }
  ,
  7968: (e,t,n)=>{
    n.d(t, {
      E: ()=>r
    });
    var r = n(44503).createContext({
      player: {}
    })
  }
  ,
  72302: (e,t,n)=>{
    n.d(t, {
      n: ()=>i
    });
    var r = n(44503)
      , o = n(7968)
      , i = function() {
      return {
        player: r.useContext(o.E).player
      }
    }
  }
  ,
  27063: (e,t,n)=>{
    n.d(t, {
      Aw: ()=>d,
      KR: ()=>m,
      BM: ()=>v,
      Gm: ()=>f
    });
    var r = n(10081)
      , o = n.n(r)
      , i = n(34246)
      , a = n.n(i)
      , l = n(92012)
      , s = n.n(l)
      , c = n(12035)
      , u = n.n(c)
      , d = function(e) {
      for (var t = 2, n = 1, r = 1; r <= 3; r++)
        if (e <= r * r) {
          t = r,
            n = Math.ceil(e / t);
          break
        }
      return {
        col: t,
        row: n
      }
    }
      , m = function e(t) {
      var n = o()(t).call(t, "{");
      if (-1 !== n) {
        var r = a()(t).call(t, "}") + 1
          , i = t.substring(n, r);
        try {
          return JSON.parse(i)
        } catch (l) {
          return e(t.substring(n + 1))
        }
      }
    }
      , v = function(e) {
      return e <= 999 ? "".concat(e) : e > 999 ? "999" : ""
    }
      , f = function() {
      var e, t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 0;
      if (t <= 0)
        return "00:00";
      var n = String(Math.floor(t / 60))
        , r = String(t % 60);
      return s()(e = "".concat(u()(n, 2, "0"), ":")).call(e, u()(r, 2, "0"))
    }
  }
  ,
  85722: (e,t,n)=>{
    n.d(t, {
      C7: ()=>R,
      yw: ()=>re
    });
    var r = n(64408)
      , o = n(19049)
      , i = n(95508)
      , a = n(65146)
      , l = n(81711)
      , s = n.n(l)
      , c = n(21805)
      , u = n.n(c)
      , d = n(90823)
      , m = n.n(d)
      , v = n(5594)
      , f = n.n(v)
      , h = n(32781)
      , p = n(80051)
      , g = n.n(p)
      , y = n(57617)
      , w = n.n(y)
      , _ = n(36539)
      , E = n(14484)
      , k = n(76659)
      , x = function() {
      var e = (0,
        r.Z)(f().mark((function e() {
          var t, r, o, i, a, l, s, c, u, d, m, v = arguments;
          return f().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return r = v.length > 0 && void 0 !== v[0] ? v[0] : "",
                      o = v.length > 1 ? v[1] : void 0,
                      i = o.websocketKey,
                      a = void 0 === i ? [] : i,
                      e.next = 4,
                      g().all([Promise.all([n.e(3558), n.e(1370), n.e(7073), n.e(2192), n.e(5813), n.e(5407), n.e(2806), n.e(8718), n.e(8053), n.e(4439), n.e(9154), n.e(2851), n.e(7595), n.e(3345), n.e(225), n.e(8261), n.e(5250), n.e(7308), n.e(6200), n.e(9010), n.e(8711)]).then(n.bind(n, 96169)), Promise.all([n.e(3558), n.e(1370), n.e(7073), n.e(2192), n.e(5813), n.e(5407), n.e(2806), n.e(8718), n.e(8053), n.e(4439), n.e(9154), n.e(2851), n.e(7595), n.e(3345), n.e(225), n.e(8261), n.e(5250), n.e(7821)]).then(n.bind(n, 77821))]);
                  case 4:
                    return l = e.sent,
                      s = (0,
                        h.Z)(l, 2),
                      c = s[0].default,
                      u = s[1].liveIMModules,
                      d = "" === r ? "/webcast/im/fetch/" : r,
                      m = new c({
                        host: E.Pe(),
                        aid: "6383",
                        live_id: 1,
                        app_name: "douyin_web",
                        did_rule: 3,
                        modules: u,
                        debug: !1,
                        endpoint: "live_pc",
                        support_wrds: 1,
                        im_path: d,
                        websocket_key: a,
                        user_unique_id: null == _ || null === (t = k.Es()) || void 0 === t ? void 0 : t.user_unique_id
                      }),
                      e.abrupt("return", m);
                  case 11:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , b = function() {
      var e = (0,
        r.Z)(f().mark((function e(t, r) {
          var o, i, a;
          return f().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      Promise.all([n.e(3558), n.e(1370), n.e(7073), n.e(2192), n.e(5813), n.e(5407), n.e(2806), n.e(8718), n.e(8053), n.e(4439), n.e(9154), n.e(2851), n.e(7595), n.e(3345), n.e(225), n.e(8261), n.e(5250), n.e(7821)]).then(n.bind(n, 77821));
                  case 2:
                    i = e.sent,
                      a = i.liveIMModules,
                      s()(o = w()(a)).call(o, (function(e) {
                          t.on(e, r)
                        }
                      ));
                  case 5:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t, n) {
        return e.apply(this, arguments)
      }
    }()
      , C = n(3493)
      , N = n.n(C)
      , T = n(56402)
      , Z = n.n(T)
      , S = n(9267)
      , I = n.n(S)
      , L = n(56493);
    var D = function(e) {
      return (t = Z()(e, "payload.common.msgId", (0,
        L.Z)())) ? "string" == typeof t ? t : "number" == typeof t ? "".concat(t) : I().fromBits(t.low, t.high, t.unsigned).toString() : "";
      var t
    }
      , M = n(57038)
      , B = n(29529)
      , A = n(47776)
      , P = n.n(A)
      , O = n(94610)
      , V = n.n(O);
    function W(e) {
      if (P()(e))
        return V()(e).call(e, (function(e) {
            return "object" === (0,
              B.Z)(e) && null !== e ? W(e) : e
          }
        ));
      if ("object" === (0,
        B.Z)(e) && null !== e) {
        var t, n = w()(e);
        s()(t = n || []).call(t, (function(t) {
            var n = e[t]
              , r = /List$/
              , o = t.replace(r, "");
            P()(n) && r.test(t) && void 0 === e[o] && (e[o] = n),
              W(n)
          }
        ))
      }
      return e
    }
    var R, F = n(30906), U = n(88438), H = n.n(U), G = n(92637), j = n.n(G), K = n(10081), q = n.n(K), Y = n(92012), X = n.n(Y), z = n(32383), Q = n.n(z), J = n(9120), $ = n.n(J), ee = ["WebcastRoomDataSyncMessage"], te = (0,
      i.Z)((function e(t) {
        var i = this;
        (0,
          o.Z)(this, e),
          (0,
            a.Z)(this, "ee", void 0),
          (0,
            a.Z)(this, "messageService", void 0),
          (0,
            a.Z)(this, "messageMap", {}),
          (0,
            a.Z)(this, "queue", []),
          (0,
            a.Z)(this, "init", (function() {
              i.messageService.subscribe(ee.join(","), i.receive)
            }
          )),
          (0,
            a.Z)(this, "subscribe", (function(e, t) {
              return i.ee.on(e, t),
                H()((function() {
                    var t, n;
                    s()(t = j()(n = i.ee.eventNames()).call(n, (function(t) {
                        return new RegExp(t).test(e)
                      }
                    ))).call(t, (function(e) {
                        i.messageMap[e] && i.ee.emit(e, [i.messageMap[e].payload])
                      }
                    ))
                  }
                )),
                function() {
                  i.ee.off(e, t)
                }
            }
          )),
          (0,
            a.Z)(this, "unsubscribe", (function(e, t) {
              i.ee.off(e, t)
            }
          )),
          (0,
            a.Z)(this, "receive", function() {
            var e = (0,
              r.Z)(f().mark((function e(t) {
                var r, o;
                return f().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          return e.next = 2,
                            Promise.all([n.e(3558), n.e(1370), n.e(7073), n.e(5879)]).then(n.bind(n, 25879));
                        case 2:
                          r = e.sent,
                            o = r.liveIMModules,
                            s()(t).call(t, (function(e) {
                                var t, n, r;
                                if (e && e.payload && -1 !== q()(ee).call(ee, e.method)) {
                                  var a = e.payload
                                    , l = a.bizlogid
                                    , s = a.payload
                                    , c = a.common
                                    , u = a.synckey
                                    , d = a.version
                                    , m = D(e);
                                  if (o[u]) {
                                    var v = null === (t = (n = o[u]).deserializeBinary) || void 0 === t || null === (r = t.call(n, s)) || void 0 === r ? void 0 : r.toObject()
                                      , f = {
                                      method: u,
                                      msgId: m,
                                      payload: W((0,
                                        F.Z)({
                                        common: c,
                                        version: d,
                                        bizlogid: l
                                      }, v))
                                    };
                                    i.messageMap[u] = {
                                      bizlogid: l,
                                      msgId: m,
                                      version: d,
                                      payload: f
                                    },
                                      i.queue.push(f)
                                  } else
                                    ;
                                }
                              }
                            )),
                            i.publish();
                        case 6:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            )));
            return function(t) {
              return e.apply(this, arguments)
            }
          }()),
          (0,
            a.Z)(this, "publish", (function() {
              var e, t;
              s()(e = Q()($()(t = i.queue).call(t, (function(e, t) {
                  var n, r;
                  return (0,
                    F.Z)((0,
                    F.Z)({}, e), {}, (0,
                    a.Z)({}, t.method, X()(n = null !== (r = e[t.method]) && void 0 !== r ? r : []).call(n, t)))
                }
              ), {}))).call(e, (function(e) {
                  var t = (0,
                    h.Z)(e, 2)
                    , n = t[0]
                    , r = t[1];
                  i.ee.emit(n, r)
                }
              )),
                i.queue = []
            }
          )),
          this.ee = new (N()),
          this.messageService = t
      }
    ));
    !function(e) {
      e[e.ASYNC = 0] = "ASYNC",
        e[e.SYNC = 1] = "SYNC"
    }(R || (R = {}));
    var ne = function() {
      function e() {
        (0,
          o.Z)(this, e),
          (0,
            a.Z)(this, "wrds", void 0),
          (0,
            a.Z)(this, "room_id_str", ""),
          (0,
            a.Z)(this, "timer", void 0),
          (0,
            a.Z)(this, "ee", void 0),
          (0,
            a.Z)(this, "eeSync", void 0),
          (0,
            a.Z)(this, "msgIdSets", {}),
          (0,
            a.Z)(this, "msgIdSetsSync", {}),
          (0,
            a.Z)(this, "queue", []),
          (0,
            a.Z)(this, "liveIMInstance", null),
          (0,
            a.Z)(this, "imRequestPath", "/webcast/im/fetch/"),
          (0,
            a.Z)(this, "websocketKey", []),
          this.ee = new (N()),
          this.eeSync = new (N()),
          this.wrds = new te(this)
      }
      var t;
      return (0,
        i.Z)(e, [{
        key: "sdkInit",
        value: (t = (0,
            r.Z)(f().mark((function e(t) {
              var n = this;
              return f().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        if (e.prev = 0,
                          this.liveIMInstance) {
                          e.next = 5;
                          break
                        }
                        return e.next = 4,
                          x(this.imRequestPath, {
                            websocketKey: this.websocketKey
                          });
                      case 4:
                        this.liveIMInstance = e.sent;
                      case 5:
                        return this.liveIMInstance.start({
                          identity: M.nN.Audience,
                          room_id: this.room_id_str
                        }),
                          e.next = 8,
                          b(this.liveIMInstance, (function(e) {
                              var t, r, o = e.toObject(), i = {
                                method: null == o || null === (t = o.common) || void 0 === t ? void 0 : t.method,
                                msgId: null == o || null === (r = o.common) || void 0 === r ? void 0 : r.msgId,
                                payload: W(o)
                              };

                              // ======================== recorder modification start ========================
                              if (!window.is_danmaku_dead) {
                                window.data_n = i;
                                // get room_id from url
                                window.data_n.room_id = (new URL(window.location.href)).pathname.split('/')[1];
                                (() => {
                                  // pause video player
                                  if (document.querySelector('.xgplayer-play').getAttribute('data-state') === 'play') {
                                    document.querySelector('.xgplayer-play').click();
                                  }
                                  // disable danmaku display on video player
                                  if (document.querySelector('.danmu-icon').getAttribute('data-state') === 'active') {
                                    document.querySelector('.danmu-icon').click();
                                  }
                                  // disable gift display on video player
                                  if (document.querySelectorAll('.fHknbHHl')[2].querySelectorAll('div')[0].innerHTML === '屏蔽礼物特效') {
                                    document.querySelectorAll('.fHknbHHl')[2].querySelectorAll('div')[1].click();
                                  }

                                  if (window.ws_rpc_client && window.ws_rpc_client.readyState !== WebSocket.CLOSED) {
                                    if (window.ws_rpc_client.readyState === WebSocket.OPEN) {
                                      window.ws_rpc_client.send(JSON.stringify(window.data_n));
                                      window.ws_rpc_last_send_time = Date.now();
                                    }
                                  } else {
                                    window.ws_rpc_client = new WebSocket('ws://localhost:18964');
                                  }
                                })();
                              }
                              // ======================== recorder modification end ========================

                              n.queuePush(i),
                                n.publishSync(i)
                            }
                          ));
                      case 8:
                        e.next = 12;
                        break;
                      case 10:
                        e.prev = 10,
                          e.t0 = e.catch(0);
                      case 12:
                      case "end":
                        return e.stop()
                    }
                }
              ), e, this, [[0, 10]])
            }
          ))),
            function(e) {
              return t.apply(this, arguments)
            }
        )
      }, {
        key: "publishSync",
        value: function(e) {
          var t = this
            , n = this.eeSync.eventNames();
          s()(n).call(n, (function(n) {
              var r = t.msgIdSetsSync[n]
                , o = D(e);
              u()(r).call(r, o) || (r.push(o),
              r.length > 100 && r.shift(),
              new RegExp(e.method).test(n) && t.eeSync.emit(n, [e]))
            }
          ))
        }
      }, {
        key: "publish",
        value: function(e) {
          var t = this
            , n = this.ee.eventNames();
          s()(n).call(n, (function(n) {
              var r = [];
              s()(e).call(e, (function(e) {
                  var o = D(e)
                    , i = t.msgIdSets[n];
                  u()(i).call(i, o) || (i.push(o),
                  i.length > 100 && i.shift(),
                  new RegExp(e.method).test(n) && r.push(e))
                }
              )),
              r.length && t.ee.emit(n, r)
            }
          ))
        }
      }, {
        key: "subscribe",
        value: function(e, t) {
          var n = this
            , r = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : R.ASYNC;
          return r === R.ASYNC ? (this.msgIdSets[e] = [],
            this.ee.on(e, t)) : (this.eeSync.on(e, t),
            this.msgIdSetsSync[e] = []),
            function() {
              r === R.ASYNC ? n.ee.off(e, t) : n.eeSync.off(e, t)
            }
        }
      }, {
        key: "unsubscribe",
        value: function(e, t) {
          var n = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : R.ASYNC;
          n === R.ASYNC ? this.ee.off(e, t) : this.eeSync.off(e, t)
        }
      }, {
        key: "polling",
        value: function(e) {
          var t = this
            , n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 1e3;
          this.room_id_str = e,
          e && (this.liveIMInstance && this.stop(),
            this.sdkInit(n),
            this.wrds.init(),
            this.timer = m()((function() {
                t.publish(t.queue),
                  t.queueClear()
              }
            ), n))
        }
      }, {
        key: "pause",
        value: function() {
          clearTimeout(this.timer),
            this.liveIMInstance.stop()
        }
      }, {
        key: "stop",
        value: function() {
          var e, t, n;
          clearTimeout(this.timer),
          null === (e = this.liveIMInstance) || void 0 === e || e.stop(),
          null === (t = this.ee) || void 0 === t || t.removeAllListeners(),
          null === (n = this.eeSync) || void 0 === n || n.removeAllListeners()
        }
      }, {
        key: "emitter",
        get: function() {
          return this.ee
        }
      }, {
        key: "queuePush",
        value: function() {
          var e;
          (e = this.queue).push.apply(e, arguments)
        }
      }, {
        key: "queueClear",
        value: function() {
          this.queue = []
        }
      }, {
        key: "pauseMessagePublish",
        value: function() {
          clearInterval(this.timer)
        }
      }, {
        key: "continueMessagePublish",
        value: function() {
          var e = this
            , t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 1e3;
          this.queueClear(),
            clearInterval(this.timer),
            this.timer = m()((function() {
                e.publish(e.queue),
                  e.queueClear()
              }
            ), t)
        }
      }, {
        key: "getimReponseHeader",
        value: function() {
          var e;
          return null === (e = this.liveIMInstance) || void 0 === e ? void 0 : e.imReponseHeader
        }
      }, {
        key: "setImRequestPath",
        value: function(e) {
          this.imRequestPath = e
        }
      }, {
        key: "setWebsocketKey",
        value: function(e) {
          this.websocketKey = e
        }
      }]),
        e
    }()
      , re = new ne
  }
  ,
  14001: (e,t,n)=>{
    n.d(t, {
      a: ()=>w
    });
    var r = n(30906)
      , o = n(32781)
      , i = n(67161)
      , a = n(10081)
      , l = n.n(a)
      , s = n(84578)
      , c = n.n(s)
      , u = n(44503);
    const d = "B3AsdZT9";
    var m = n(58256)
      , v = n(75403)
      , f = n(80212)
      , h = n(79705)
      , p = n.n(h)
      , g = n(51333)
      , y = ["href", "children", "style", "className", "passParamKeys", "spa", "isNeedSeoOpt", "refEl"];
    function w(e) {
      var t = e.href
        , n = void 0 === t ? "" : t
        , a = e.children
        , s = e.style
        , h = e.className
        , w = e.passParamKeys
        , _ = void 0 === w ? [] : w
        , E = e.spa
        , k = e.isNeedSeoOpt
        , x = void 0 !== k && k
        , b = e.refEl
        , C = (0,
        i.Z)(e, y)
        , N = (0,
        u.useState)("")
        , T = (0,
        o.Z)(N, 2)
        , Z = T[0]
        , S = T[1]
        , I = (0,
        u.useRef)(null);
      (0,
        u.useEffect)((function() {
          var e = v.U({
            passParamKeys: _
          })
            , t = (0,
            m.stringify)(e);
          S(t)
        }
      ), []);
      var L = (0,
        u.useMemo)((function() {
          if (n) {
            var e, t, r = l()(n).call(n, "#");
            -1 !== r ? (e = c()(n).call(n, 0, r),
              t = c()(n).call(n, r + 1)) : (e = n,
              t = "");
            var o, i, a = l()(e).call(e, "?");
            -1 !== a ? (o = c()(e).call(e, 0, a),
              i = c()(e).call(e, a + 1)) : (o = e,
              i = "");
            var s = [];
            return Z && s.push(Z),
            i && s.push(i),
              s.length > 0 ? [o, s.join("&")].join("?") + (t && "#".concat(t)) : o + (t && "#".concat(t))
          }
        }
      ), [Z, n])
        , D = L;
      if (x && !E && D) {
        var M = D.split("#")
          , B = (0,
          o.Z)(M, 2);
        D = B[0],
          B[1];
        var A = D.split("?")
          , P = (0,
          o.Z)(A, 2);
        D = P[0],
          P[1]
      }
      return E ? u.createElement(g.rU, (0,
        r.Z)({
        to: L,
        className: p()(d, h),
        style: s
      }, C), a) : u.createElement("a", (0,
        r.Z)((0,
        r.Z)({
        href: globalThis.getFilterXss().filterUrl(D, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: p()(d, h),
        style: s,
        ref: function(e) {
          I.current = e,
          b && (b.current = e)
        }
      }, C), {}, {
        target: f.f() ? "_self" : C.target,
        onClick: function(e) {
          try {
            var t;
            I.current.href = globalThis.getFilterXss().filterUrl(L, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            null == C || null === (t = C.onClick) || void 0 === t || t.call(C, e)
          } catch (n) {}
        }
      }), a)
    }
  }
  ,
  66019: (e,t,n)=>{
    n.d(t, {
      SJ: ()=>H,
      ev: ()=>G,
      zk: ()=>K,
      qR: ()=>q,
      EH: ()=>Y,
      Tz: ()=>X,
      Yx: ()=>z,
      fl: ()=>Q,
      bH: ()=>J,
      c3: ()=>$,
      Vg: ()=>ee,
      q5: ()=>te,
      u: ()=>ne,
      FT: ()=>re,
      ZP: ()=>le
    });
    var r = n(30906), o = n(32781), i = n(64408), a = n(14212), l = n.n(a), s = n(10081), c = n.n(s), u = n(88438), d = n.n(u), m = n(21805), v = n.n(m), f = n(94610), h = n.n(f), p = n(5594), g = n.n(p), y = n(44503), w = n(45489), _ = n(70676), E = n.n(_), k = n(79705), x = n.n(k), b = n(24260), C = n(52252), N = n(53607), T = n(92557), Z = n(25083), S = n(15574), I = n(47482), L = n(45627), D = n(90414), M = n(51652), B = n(90147), A = n(55861), P = n(55618), O = n(53540), V = n(95992), W = n(68378), R, F = (0,
      b.default)({
      resolved: {},
      chunkName: function() {
        return "Lottie"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(1115), n.e(8670)]).then(n.bind(n, 86256))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 86256
      }
    }, {
      ssr: !1
    }), U = !1, H = function() {
      var e = (0,
        i.Z)(g().mark((function e() {
          var t, r;
          return g().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      n.e(9853).then(n.bind(n, 79853)).then((function(e) {
                          return e.default
                        }
                      ));
                  case 2:
                    return t = e.sent,
                      e.next = 5,
                      n.e(5848).then(n.bind(n, 65848)).then((function(e) {
                          return e.default
                        }
                      ));
                  case 5:
                    if (r = e.sent,
                      !U) {
                      e.next = 8;
                      break
                    }
                    return e.abrupt("return");
                  case 8:
                    t.use(),
                      r.use(),
                      U = !0;
                  case 12:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }(), G = function() {
      return null
    }, j = C.p() ? null : N.Q, K = function(e, t) {
      return !!e && new Date(e).toDateString() === new Date(t).toDateString()
    }, q = function(e) {
      if (!C.p()) {
        var t = j && l()(j.getItem({
          sKey: e
        }), 10) || 0;
        return t && K(t, $) || !1
      }
    }, Y = "AVATAR_FULL_LOGIN_GUIDE_TIMESTAMP", X = "AVATAR_FULL_LOGIN_GUIDE_COUNT", z = "AVATAR_FULL_LOGIN_GUIDE_ITA_TIMESTAMP", Q = "AVATAR_FULL_LOGIN_GUIDE_ITA_COUNT", J = 5184e3, $ = (new Date).getTime(), ee = q(Y), te = q(z), ne = j && l()(j.getItem({
      sKey: X
    }), 10) || 0, re = j && l()(j.getItem({
      sKey: Q
    }), 10) || 0, oe = !C.p() && (c()(R = navigator.userAgent).call(R, "Window") > 0 && window.devicePixelRatio > 1), ie = function(e) {
      switch (e) {
        case "LOGIN_MOBILE_CODE":
        default:
          return "phone_sms";
        case "LOGIN_ACCOUNT_PWD":
          return "phone_password";
        case "LOGIN_SCAN_CODE":
          return "qr_code"
      }
    }, ae = "click_x";
    function le(e) {
      var t, n = e.config, a = e.destroy, s = e.text, c = e.isPage, u = e.enterMethod, m = void 0 === u ? "" : u, f = e.isCanClose, p = void 0 === f || f, _ = e.avatarAbtest, k = void 0 === _ ? 0 : _, b = e.onClose, C = void 0 === b ? null : b, N = e.loginBgImg, R = void 0 === N ? "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/login-resetpwd-bg.png" : N, U = e.scanLoginText, H = void 0 === U ? 0 : U, K = e.subTitle, J = void 0 === K ? [] : K, $ = (0,
        y.useRef)(null), le = (0,
        y.useRef)(null), se = (0,
        y.useState)(""), de = (0,
        o.Z)(se, 2), me = de[0], ve = de[1], fe = (0,
        y.useState)(!1), he = (0,
        o.Z)(fe, 2), pe = he[0], ge = he[1], ye = (0,
        y.useState)(!1), we = (0,
        o.Z)(ye, 2), _e = we[0], Ee = we[1], ke = (0,
        y.useState)(!1), xe = (0,
        o.Z)(ke, 2), be = xe[0], Ce = xe[1], Ne = "PASSWORD_RESET" === me, Te = window.DOMAIN && window.DOMAIN === B.LIVE_XIGUA_DOMAIN ? "\u76f4\u64ad\u670d\u52a1\u7531\u6296\u97f3\u63d0\u4f9b \u9700\u767b\u5f55" : "\u767b\u5f55\u540e\u6296\u97f3\u66f4\u61c2\u4f60", Ze = "PASSWORD_RESET" === me ? "\u91cd\u7f6e\u5bc6\u7801" : s || Te;
      G = function() {
        T.emit(T.EVENT.showLoginPane, !1),
          ge(!1),
          d()((function() {
              var e;
              null === (e = $.current) || void 0 === e || e.call($),
              null == a || a()
            }
          ), 200)
      }
      ;
      (0,
        y.useEffect)((function() {
          var e;
          S.Gn();
          var t = function(e) {
            e.stopPropagation()
          };
          return T.emit(T.EVENT.videoStopPlayNext),
          null === (e = document) || void 0 === e || e.addEventListener("keydown", t, !0),
            function() {
              var e;
              T.emit(T.EVENT.videoRemoveStopPlayNext),
              null === (e = document) || void 0 === e || e.removeEventListener("keydown", t, !0)
            }
        }
      ), []);
      var Se = y.useCallback(function() {
        var e = (0,
          i.Z)(g().mark((function e(t) {
            var o, i;
            return g().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      if (t) {
                        e.next = 2;
                        break
                      }
                      return e.abrupt("return");
                    case 2:
                      return T.emit(T.EVENT.showLoginPane, !0),
                        e.next = 5,
                        (0,
                          O.j1)();
                    case 5:
                      o = e.sent,
                      null !== A.n && void 0 !== A.n && A.n.loginGuideShowed && A.n.destroy(),
                        i = new o((0,
                          r.Z)((0,
                          r.Z)({}, n), {}, {
                          success: function(e) {
                            null != e && e.redirect_url ? E().get(null == e ? void 0 : e.redirect_url).then((function() {
                                var t;
                                d()(G, 500),
                                null == n || null === (t = n.success) || void 0 === t || t.call(n, e)
                              }
                            )).catch((function() {
                                G()
                              }
                            )) : G()
                          },
                          onPageChange: function(e) {
                            ve(e),
                              V.Z.sendLog("clickLoginMethod", {
                                enter_from: Z.vM(),
                                enter_method: m,
                                login_method: ie(e),
                                login_suggest_method: "qr_code"
                              })
                          },
                          getCloseFunc: function() {
                            return ae
                          },
                          ele: t
                        })),
                        $.current = i.init(),
                        i.setTeaConfig({
                          ug_source: I.Rs("ug_source"),
                          sem_keyword: I.Rs("sem_keyword"),
                          browser_is_360: L.a2() ? "1" : "0"
                        });
                    case 10:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), [m, n]);
      (0,
        y.useEffect)((function() {
          var e, t, n, r;
          D.$o(M.LocalStorageKeys.ShowPendantWearTip) || (ee = q(Y),
            te = q(z),
            ne = j && l()(j.getItem({
              sKey: X
            }), 10) || 0,
            re = j && l()(j.getItem({
              sKey: Q
            }), 10) || 0,
            1 !== k || v()(e = ["cold_start", "cold_start_full", "auto"]).call(e, m) ? 0 === k || te || v()(t = ["cold_start", "cold_start_full", "auto"]).call(t, m) ? 1 === k && v()(n = ["cold_start", "cold_start_full"]).call(n, m) ? (ne < 1 && Ce(!0),
            ne % 3 == 0 && ee || (Ee(!0),
              ce(Y),
              ue(X),
              ne = 1)) : 0 !== k && !ee && v()(r = ["cold_start", "cold_start_full"]).call(r, m) && (ne < 1 && Ce(!0),
            (3 === k && ne < 3 || (2 === k || 4 === k) && ne < 5) && Ee(!0),
              ce(Y),
              ue(X),
              ne = 1) : (re < 1 && Ce(!0),
            (3 === k && re < 3 || (2 === k || 4 === k) && re < 5) && Ee(!0),
              ce(z),
              ue(Q),
              re += 1) : (re < 1 && Ce(!0),
            re % 3 == 0 && te || (Ee(!0),
              ce(z),
              ue(Q),
              re += 1))),
            ge(!0)
        }
      ), []),
        (0,
          y.useEffect)((function() {
            0 !== k && Ne && Ce(!1)
          }
        ), [me]);
      var Ie = v()(t = ["cold_start_full", "cold_start", "auto", "navigation_bar"]).call(t, m) && !Ne && !_e
        , Le = y.createElement("div", {
        id: "login-pannel",
        className: x()({
          bigqr: !0
        }, {
          resetpwd: Ne
        }, {
          subtitle: Ie
        }, {
          scale: oe
        }, {
          avatar: _e && !Ne
        }, {
          titleanima: be && !Ne
        }, {
          scan_login_text: 2 === H
        }),
        style: {
          background: "#fff url(".concat(R, ") no-repeat"),
          backgroundSize: "100% auto"
        }
      }, y.createElement("div", {
        className: "login-pannel__header",
        onClick: function(e) {
          e.stopPropagation()
        }
      }, be && !Ne && y.createElement("div", {
        className: "login-pannel-animation"
      }, y.createElement(F, {
        ref: le,
        className: "login-pannel-animation-lottie",
        data: W,
        loop: !1,
        assetsPath: "https://lf3-static.bytednsdoc.com/obj/eden-cn/medeh7bmupenuhd/pendantPanda/"
      })), y.createElement("div", {
        className: "login-pannel__header-title"
      }, Ze), _e && !Ne && y.createElement(y.Fragment, null, y.createElement("div", {
        className: "login-pannel__header-title-avatar-disappear"
      }, "\u767b\u5f55\u540e\u83b7\u5f97\u4e13\u5c5e\u5934\u50cf\u6302\u4ef6"), y.createElement("div", {
        className: "login-pannel__header-title-avatar"
      }, "\u767b\u5f55\u540e\u83b7\u5f97\u4e13\u5c5e\u5934\u50cf\u6302\u4ef6")), Ie && 0 === J.length && y.createElement("div", {
        className: "login-pannel__header-title-desc"
      }, y.createElement("ul", null, y.createElement("li", null, "\u63a8\u8350\u66f4\u61c2\u4f60"), y.createElement("li", null, "\u641c\u7d22\u66f4\u7cbe\u5f69"), y.createElement("li", null, "\u7545\u804a\u76f4\u64ad\u95f4"), y.createElement("li", null, "\u89e3\u9501\u70b9\u8d5e\u4e92\u52a8"))), Ie && 0 !== J.length && y.createElement("div", {
        className: "login-pannel__header-title-desc"
      }, y.createElement("ul", {
        id: "sub-title"
      }, h()(J).call(J, (function(e, t) {
          return y.createElement("li", {
            key: t,
            id: "".concat((n = e,
              "\u9ad8\u6e05\u89c6\u9891\u514d\u8d39\u770b" === n ? "video" : "\u70b9\u8d5e\u8bc4\u8bba\u968f\u5fc3\u53d1" === n ? "comment" : "\u76f4\u64ad\u95f4\u7545\u804a\u6253\u8d4f" === n ? "live" : "\u670b\u53cb\u89c6\u9891\u4e00\u952e\u89c8" === n ? "friend" : "video"))
          }, e);
          var n
        }
      ))))), !c && p && y.createElement("div", {
        className: "dy-account-close",
        onClick: function(e) {
          e.stopPropagation(),
            ae = "click_x",
          null == C || C(),
            G()
        }
      }), y.createElement("div", {
        ref: Se,
        onClick: function(e) {
          e.stopPropagation()
        }
      }));
      return y.createElement(y.Fragment, null, c ? y.createElement("div", {
        className: "login-page"
      }, Le) : y.createElement(w.Kv, {
        in: pe,
        classNames: "login-mask",
        timeout: {
          enter: 400,
          exit: 150
        },
        unmountOnExit: !0,
        appear: !0
      }, y.createElement(P.T, {
        className: "screen-mask",
        onClick: function() {
          V.Z.sendLog("clickLoginOutside", {
            enter_method: m,
            enter_from: Z.vM()
          })
        }
      }, y.createElement("div", {
        className: "box-align-center"
      }, y.createElement(w.Kv, {
        in: pe,
        classNames: "login-pannel",
        timeout: {
          enter: 400,
          exit: 150
        },
        appear: !0,
        unmountOnExit: !0
      }, Le)))))
    }
    function se() {
      G()
    }
    var ce = function(e) {
      j && j.setItem(e, $.toString(), J, "/", "douyin.com", "")
    }
      , ue = function(e) {
      var t = (l()(j.getItem({
        sKey: e
      }), 10) || 0) + 1;
      j.setItem(e, t.toString(), J, "/", "douyin.com", "")
    }
  }
  ,
  53494: (e,t,n)=>{
    n.d(t, {
      o: ()=>N,
      w: ()=>C
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(5594)
      , a = n.n(i)
      , l = n(88438)
      , s = n.n(l)
      , c = n(14212)
      , u = n.n(c)
      , d = n(80051)
      , m = n.n(d)
      , v = n(44503)
      , f = n(9)
      , h = n(72983)
      , p = n(52252)
      , g = n(53607)
      , y = n(76659)
      , w = n(90414)
      , _ = n(51652)
      , E = n(83218)
      , k = n(95992)
      , x = p.p() ? null : g.Q
      , b = function(e) {
      var t = e.confirmHandler
        , n = void 0 === t ? null : t
        , r = e.cancelHandler
        , i = void 0 === r ? null : r
        , a = e.defaultHandler
        , l = void 0 === a ? null : a
        , c = e.countdown
        , u = void 0 === c ? 5 : c
        , d = (0,
        v.useRef)(null)
        , m = (0,
        v.useState)(u)
        , f = (0,
        o.Z)(m, 2)
        , h = f[0]
        , p = f[1]
        , g = function() {
        clearTimeout(d.current)
      };
      return (0,
        v.useEffect)((function() {
          return d.current = s()((function() {
              null == l || l()
            }
          ), 1e3 * u),
            function() {
              clearTimeout(d.current)
            }
        }
      ), []),
        (0,
          v.useEffect)((function() {
            s()((function() {
                h > 0 && p(h - 1)
              }
            ), 1e3)
          }
        ), [h]),
        v.createElement("div", {
          className: "trust-login-dialog-mask"
        }, v.createElement("div", {
          className: "trust-login-dialog-content"
        }, v.createElement("div", {
          className: "trust-login-dialog-title"
        }, "\u662f\u5426\u4fdd\u5b58\u767b\u5f55\u4fe1\u606f\uff1f\uff08".concat(h, "\uff09")), v.createElement("div", {
          className: "trust-login-dialog-info"
        }, "\u4fdd\u5b58\u540e\u4e0b\u6b21\u767b\u5f55\u514d\u9a8c\u8bc1\uff0c\u53ef\u5728\u4e2a\u4eba\u4e2d\u5fc3\u8bbe\u7f6e"), v.createElement("div", {
          className: "trust-login-dialog-button"
        }, v.createElement("div", {
          className: "trust-login-dialog-button-confirm",
          onClick: function() {
            g(),
            null == n || n()
          }
        }, "\u4fdd\u5b58"), v.createElement("div", {
          className: "trust-login-dialog-button-cancel",
          onClick: function() {
            g(),
            null == i || i()
          }
        }, "\u53d6\u6d88"))))
    }
      , C = function(e) {
      var t, n = e.confirmHandler, r = void 0 === n ? null : n, o = e.cancelHandler, i = void 0 === o ? null : o, a = e.countdown, l = void 0 === a ? 5 : a, s = e.showWay, c = void 0 === s ? "" : s, u = document.createElement("div");
      u.setAttribute("id", "trust-logout-dialog"),
        document.body.appendChild(u),
        k.Z.sendLog("loginInfoPopupShow", {
          popup_type: c,
          params_for_special: "uc_login",
          device_id: null === (t = y.Es()) || void 0 === t ? void 0 : t.user_unique_id
        }),
        f.render(v.createElement(b, {
          confirmHandler: function() {
            var e, t;
            k.Z.sendLog("loginInfoPopupResult", {
              popup_type: c,
              status: "save",
              params_for_special: "uc_login",
              device_id: null === (e = y.Es()) || void 0 === e ? void 0 : e.user_unique_id
            }),
              k.Z.sendLog("loginInfoPopupClose", {
                popup_type: c,
                method: "click",
                params_for_special: "uc_login",
                device_id: null === (t = y.Es()) || void 0 === t ? void 0 : t.user_unique_id
              });
            try {
              (0,
                E.dg)(1).then((function() {
                  u && document.body.removeChild(u),
                  null == r || r()
                }
              )).catch((function() {
                  u && document.body.removeChild(u),
                  null == r || r()
                }
              ))
            } catch (n) {}
          },
          cancelHandler: function() {
            var e, t;
            k.Z.sendLog("loginInfoPopupResult", {
              popup_type: c,
              status: "cancel",
              params_for_special: "uc_login",
              device_id: null === (e = y.Es()) || void 0 === e ? void 0 : e.user_unique_id
            }),
              k.Z.sendLog("loginInfoPopupClose", {
                popup_type: c,
                method: "click",
                params_for_special: "uc_login",
                device_id: null === (t = y.Es()) || void 0 === t ? void 0 : t.user_unique_id
              });
            try {
              2 !== w.$o(_.LocalStorageKeys.IsAllowTrust) ? (0,
                E.dg)(2).then((function() {
                  u && document.body.removeChild(u),
                  null == i || i()
                }
              )).catch((function() {
                  u && document.body.removeChild(u),
                  null == i || i()
                }
              )) : (u && document.body.removeChild(u),
              null == i || i())
            } catch (n) {}
          },
          defaultHandler: function() {
            var e;
            k.Z.sendLog("loginInfoPopupClose", {
              popup_type: c,
              method: "auto",
              params_for_special: "uc_login",
              device_id: null === (e = y.Es()) || void 0 === e ? void 0 : e.user_unique_id
            });
            try {
              u && document.body.removeChild(u),
              null == i || i()
            } catch (t) {}
          },
          countdown: l
        }), u)
    }
      , N = function() {
      var e = (0,
        r.Z)(a().mark((function e(t) {
          var n, r, i, l, s, c, d, v, f, p, g;
          return a().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    if (1 !== (x && u()(x.getItem({
                      sKey: "LOGIN_STATUS"
                    }), 10) || 0)) {
                      e.next = 3;
                      break
                    }
                    return e.abrupt("return");
                  case 3:
                    return e.next = 5,
                      m().all([h.h.getVar({
                        name: "is_allow_trust",
                        defaultValue: 0
                      }), h.h.getVar({
                        name: "trust_dialog_freq",
                        defaultValue: 0
                      })]);
                  case 5:
                    if (r = e.sent,
                      i = (0,
                        o.Z)(r, 2),
                      l = i[0],
                      s = i[1],
                      l) {
                      e.next = 11;
                      break
                    }
                    return e.abrupt("return");
                  case 11:
                    return x.setItem("LOGIN_STATUS", 1, 1 / 0, "/", "douyin.com", ""),
                    (null == (c = w.$o(_.LocalStorageKeys.UserInfo)) ? void 0 : c.uid) !== (null == t || null === (n = t.info) || void 0 === n ? void 0 : n.secUid) && (w.qQ(_.LocalStorageKeys.UserInfo, {
                      uid: null == t || null === (d = t.info) || void 0 === d ? void 0 : d.secUid,
                      nickname: null == t || null === (v = t.info) || void 0 === v ? void 0 : v.nickname,
                      avatarUrl: null == t || null === (f = t.info) || void 0 === f ? void 0 : f.avatarUrl
                    }),
                      w.bv(_.LocalStorageKeys.HasLoginShow),
                      w.bv(_.LocalStorageKeys.HasLogoutShow),
                      w.bv(_.LocalStorageKeys.IsAllowTrust)),
                      p = w.$o(_.LocalStorageKeys.HasLoginShow),
                      g = 0,
                      e.prev = 16,
                      e.next = 19,
                      (0,
                        E.q3)();
                  case 19:
                    g = e.sent,
                      e.next = 25;
                    break;
                  case 22:
                    e.prev = 22,
                      e.t0 = e.catch(16);
                  case 25:
                    if (1 === g || (0 !== s || 1 === p) && 1 !== s) {
                      e.next = 29;
                      break
                    }
                    return w.qQ(_.LocalStorageKeys.HasLoginShow, 1),
                      C({
                        showWay: "login"
                      }),
                      e.abrupt("return");
                  case 29:
                  case "end":
                    return e.stop()
                }
            }
          ), e, null, [[16, 22]])
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }()
  }
  ,
  36408: (e,t,n)=>{
    n.d(t, {
      Z: ()=>w
    });
    var r, o = n(65146), i = n(32781), a = n(44503), l = n(79705), s = n.n(l), c = n(90414), u = n(92557), d = n(25083), m = n(76659), v = n(51652), f = n(83218), h = n(52255);
    function p() {
      return p = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        p.apply(this, arguments)
    }
    const g = function(e) {
      return a.createElement("svg", p({
        width: 15,
        height: 16,
        viewBox: "0 0 15 16",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = a.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M7.5 15.473a7.5 7.5 0 100-15 7.5 7.5 0 000 15zm.034-12c-.956 0-1.842.367-2.45 1.076-.076.089-.162.22-.243.36-.209.357-.056.805.308.999l.027.014c.396.211.842-.003 1.114-.36.3-.393.715-.588 1.244-.588.787 0 1.338.327 1.338.992 0 .536-.427.94-.91 1.371l-.03.028c-.517.469-1.05.953-1.277 1.857-.01.04-.02.088-.028.14-.077.464.31.86.779.86.423 0 .753-.33.858-.74a.984.984 0 01.027-.092c.185-.512.535-.848.885-1.152.676-.6 1.324-1.227 1.324-2.272 0-1.619-1.366-2.493-2.966-2.493zm-.034 7.5a1.125 1.125 0 100 2.25 1.125 1.125 0 000-2.25z",
        fill: "#2F3035",
        fillOpacity: .4
      })))
    };
    var y = n(95992);
    const w = function(e) {
      var t = e.classname
        , n = void 0 === t ? "" : t
        , r = e.iconPosition
        , l = void 0 === r ? "" : r
        , p = e.pageIndex
        , w = e.tipInfoPosition
        , _ = void 0 === w ? "" : w
        , E = c.$o(v.LocalStorageKeys.IsAllowTrust)
        , k = (0,
        a.useState)(1 === E)
        , x = (0,
        i.Z)(k, 2)
        , b = x[0]
        , C = x[1];
      (0,
        a.useEffect)((function() {
          u.listen(u.EVENT.updateTrustSwitch, (function(e) {
              C(1 === e)
            }
          ))
        }
      ), []);
      return a.createElement("div", {
        className: s()("trust-login-switch", (0,
          o.Z)({}, n, n))
      }, a.createElement("div", {
        className: s()("trust-login-tips", (0,
          o.Z)({}, l, l))
      }, a.createElement("div", {
        className: "trust-login-tips-icon"
      }, a.createElement(h.Z, {
        src: globalThis.getFilterXss().filterUrl(g, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: 15,
        height: 16,
        viewBox: "0 0 15 16"
      }), a.createElement("div", {
        className: s()("trust-login-tips-info", (0,
          o.Z)({}, "trust-login-tips-info-".concat(_), Boolean(_)))
      }, "\u4fdd\u5b58\u767b\u5f55\u4fe1\u606f\uff0c\u4e0b\u6b21\u767b\u5f55\u514d\u9a8c\u8bc1"))), a.createElement("div", {
        className: "trust-login-switch-title"
      }, "\u4fdd\u5b58\u767b\u5f55\u4fe1\u606f"), a.createElement("div", {
        className: s()("trust-login-switch-button", {
          check: b
        }, {
          uncheck: !b
        }),
        onClick: function() {
          (0,
            f.dg)(b ? 2 : 1).then((function(e) {
              var t, n = 1 === e;
              y.Z.sendLog("clickLoginInfoSwitch", {
                status: b ? "on" : "off",
                enter_from: d.vM(),
                page: p,
                result: n ? "on" : "off",
                params_for_special: "uc_login",
                device_id: null === (t = m.Es()) || void 0 === t ? void 0 : t.user_unique_id
              })
            }
          )).catch((function(e) {
              var t;
              y.Z.sendLog("clickLoginInfoSwitch", {
                status: b ? "on" : "off",
                enter_from: d.vM(),
                result: b ? "on" : "off",
                params_for_special: "uc_login",
                device_id: null === (t = m.Es()) || void 0 === t ? void 0 : t.user_unique_id
              })
            }
          ))
        }
      }))
    }
  }
  ,
  95992: (e,t,n)=>{
    n.d(t, {
      Z: ()=>a
    });
    var r = n(25083)
      , o = n(37485)
      , i = {
      qrLoginGuide: {
        eventName: "qr_login_guide",
        params: {
          enter_from: r.vM(),
          enter_method: "",
          login_suggest_method: "",
          page_type: r.yW()
        }
      },
      clickLoginMethod: {
        eventName: "click_login_method",
        params: {
          enter_from: r.vM(),
          enter_method: "",
          login_method: "",
          login_suggest_method: ""
        }
      },
      clickLoginOutside: {
        eventName: "click_login_outside",
        params: {
          enter_from: r.vM(),
          enter_method: ""
        }
      },
      loginInfoPopupShow: {
        eventName: "login_info_popup_show",
        params: {
          popup_type: "",
          params_for_special: "uc_login",
          device_id: ""
        }
      },
      loginInfoPopupResult: {
        eventName: "login_info_popup_result",
        params: {
          popup_type: "",
          status: "",
          params_for_special: "uc_login",
          device_id: ""
        }
      },
      loginInfoPopupClose: {
        eventName: "login_info_popup_close",
        params: {
          popup_type: "",
          method: "",
          params_for_special: "uc_login",
          device_id: ""
        }
      },
      clickLoginInfoSwitch: {
        eventName: "click_login_info_switch",
        params: {
          status: "",
          enter_from: "",
          result: "",
          params_for_special: "uc_login",
          device_id: "",
          page: ""
        }
      }
    };
    const a = new o.hD(i)
  }
  ,
  83218: (e,t,n)=>{
    n.d(t, {
      OQ: ()=>f,
      q3: ()=>p,
      dg: ()=>g
    });
    var r, o = n(64408), i = n(5594), a = n.n(i), l = n(80051), s = n.n(l), c = n(15574), u = n(4592), d = n(90414), m = n(51652), v = n(92557);
    function f(e) {
      return h.apply(this, arguments)
    }
    function h() {
      return (h = (0,
        o.Z)(a().mark((function e(t) {
          var o, i;
          return a().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return c.Gn(),
                      e.next = 3,
                      n.e(8860).then(n.bind(n, 28860));
                  case 3:
                    return o = e.sent,
                      i = o.WebInterfaceSdk,
                    r || (r = new i({
                      aid: 6383,
                      isOversea: !1,
                      isBoe: u.uZ,
                      region: "cn",
                      appName: "\u6296\u97f3 Web \u7ad9",
                      secondVerifyWebOptions: {
                        useSmsMode: 6
                      }
                    })),
                      e.abrupt("return", new (s())((function(e, n) {
                          r.request(t).then((function(t) {
                              e(t)
                            }
                          )).catch((function(e) {
                              n(e)
                            }
                          ))
                        }
                      )));
                  case 7:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )))).apply(this, arguments)
    }
    var p = function() {
      return new (s())((function(e, t) {
          f({
            url: "/passport/user/web_record_status/get/"
          }).then((function(t) {
              var n = t.user_web_record_status
                , r = Number(n);
              d.qQ(m.LocalStorageKeys.IsAllowTrust, r),
                v.emit(v.EVENT.updateTrustSwitch, r),
                e(r)
            }
          )).catch((function(e) {
              t(e)
            }
          ))
        }
      ))
    }
      , g = function() {
      var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 2;
      return new (s())((function(t, n) {
          f({
            url: "/passport/user/web_record_status/set/",
            data: {
              user_web_record_status: e
            }
          }).then((function(e) {
              var n = e.user_web_record_status
                , r = Number(n);
              d.qQ(m.LocalStorageKeys.IsAllowTrust, r),
                v.emit(v.EVENT.updateTrustSwitch, r),
                t(r)
            }
          )).catch((function(e) {
              n(e)
            }
          ))
        }
      ))
    }
  }
  ,
  97050: (e,t,n)=>{
    n.r(t),
      n.d(t, {
        default: ()=>G,
        loginPanelInfo: ()=>H,
        navShowAccount: ()=>q,
        showAccountPage: ()=>K
      });
    var r = n(32781)
      , o = n(30906)
      , i = n(67161)
      , a = n(64408)
      , l = n(5594)
      , s = n.n(l)
      , c = n(88677)
      , u = n.n(c)
      , d = n(21805)
      , m = n.n(d)
      , v = n(80051)
      , f = n.n(v)
      , h = n(44503)
      , p = n(9)
      , g = n(78867)
      , y = n(72983)
      , w = n(90414)
      , _ = n(88287)
      , E = n(37541)
      , k = n(43478)
      , x = n(52252)
      , b = n(51652)
      , C = n(53540)
      , N = n(88438)
      , T = n.n(N)
      , Z = n(36539)
      , S = n(1021)
      , I = n(76659)
      , L = n(25083)
      , D = n(82016)
      , M = n(47482)
      , B = n(45627)
      , A = n(4592)
      , P = n(4014)
      , O = ["success", "host", "next", "ScanCodeDescription", "enterMethod", "isActive", "teaEvtParams", "isUnion", "mobileLoginOnly", "isHaveAvatar", "loginTabStyle", "checkQrCodeDelayTime", "isAuto", "gearName", "clarity", "currentUserInfo", "isAllowTrust", "isFirstTrust"]
      , V = [{
      key: "LOGIN_SCAN_CODE",
      existOn: ["LOGIN_ACCOUNT_PWD", "LOGIN_MOBILE_CODE", "LOGIN_SCAN_CODE"]
    }, {
      key: "LOGIN_MOBILE_CODE",
      existOn: ["LOGIN_MOBILE_CODE", "LOGIN_ACCOUNT_PWD", "LOGIN_SCAN_CODE"]
    }, {
      key: "LOGIN_ACCOUNT_PWD",
      existOn: ["LOGIN_ACCOUNT_PWD", "LOGIN_MOBILE_CODE", "LOGIN_SCAN_CODE"]
    }]
      , W = [{
      key: "login",
      existOn: ["PASSWORD_RESET"],
      text: "\u8fd4\u56de\u767b\u5f55",
      type: "page",
      clickToPage: "LOGIN_ACCOUNT_PWD"
    }];
    const R = function() {
      var e = (0,
        a.Z)(s().mark((function e(t) {
          var n, r, a, l, c, u, d, m, v, f, h, p, g, y, _, k, N, R, F, U, H, G, j, K, q, Y, X, z, Q, J, $, ee, te, ne, re, oe;
          return s().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return u = t.success,
                      d = t.host,
                      m = t.next,
                      v = t.ScanCodeDescription,
                      f = t.enterMethod,
                      h = t.isActive,
                      p = t.teaEvtParams,
                      g = void 0 === p ? {} : p,
                      y = t.isUnion,
                      _ = void 0 !== y && y,
                      k = t.mobileLoginOnly,
                      N = void 0 !== k && k,
                      R = t.isHaveAvatar,
                      F = void 0 === R ? "0" : R,
                      U = t.loginTabStyle,
                      void 0 === U ? 1 : U,
                      H = t.checkQrCodeDelayTime,
                      G = void 0 === H ? 0 : H,
                      j = t.isAuto,
                      K = void 0 === j ? 1 : j,
                      q = t.gearName,
                      Y = void 0 === q ? "" : q,
                      X = t.clarity,
                      z = void 0 === X ? "" : X,
                      Q = t.currentUserInfo,
                      J = void 0 === Q ? null : Q,
                      $ = t.isAllowTrust,
                      ee = void 0 !== $ && $,
                      te = t.isFirstTrust,
                      ne = void 0 !== te && te,
                      re = (0,
                        i.Z)(t, O),
                      e.next = 3,
                      (0,
                        C.Q4)();
                  case 3:
                    return oe = e.sent,
                      e.abrupt("return", (0,
                        o.Z)((0,
                        o.Z)({}, oe), {}, {
                        checkQrCodeDelayTime: G,
                        device_id: null === (n = I.Es()) || void 0 === n ? void 0 : n.user_unique_id,
                        slardarContext: {
                          enter_method: f,
                          enter_from: L.vM() || "",
                          page_type: L.yW() || ""
                        },
                        currentUserInfo: J,
                        isAllowTrust: ee,
                        isFirstTrust: ne,
                        lastPage: w.$o(b.LocalStorageKeys.LastLoginWay),
                        refreshNumber: 5,
                        teaConfig: {
                          appId: 6383,
                          config: {
                            evtParams: (0,
                              o.Z)((0,
                              o.Z)({
                              page_type: L.yW() || "",
                              enter_method: f || "",
                              enter_from: L.vM() || "",
                              is_guide: "0",
                              url_path: x.p() ? "" : null === (r = window) || void 0 === r || null === (a = r.location) || void 0 === a ? void 0 : a.pathname,
                              video_detail_enter_from: D.z("web_link"),
                              previous_page: M.Rs("previous_page"),
                              is_active: h,
                              is_video_guide: "0",
                              is_topknot: F,
                              is_full_screen: E.r() ? "1" : "0",
                              is_full_webscreen: P.s.getIsPageFullscreen() ? "1" : "0",
                              is_auto: K,
                              gear_name: Y,
                              clarity: z
                            }, g), re),
                            ug_source: M.Rs("ug_source"),
                            sem_keyword: M.Rs("sem_keyword"),
                            browser_is_360: B.a2() ? "1" : "0"
                          }
                        },
                        host: d || (null == Z || null === (l = A.k4) || void 0 === l ? void 0 : l.sso) || "https://sso.douyin.com",
                        next: m || (null == Z || null === (c = A.k4) || void 0 === c ? void 0 : c.next) || "https://www.douyin.com/",
                        loginType: _ ? ["LOGIN_MOBILE_CODE", "LOGIN_ACCOUNT_PWD"] : ["LOGIN_SCAN_CODE", "LOGIN_MOBILE_CODE", "LOGIN_ACCOUNT_PWD"],
                        ScanCodeDescription: v,
                        bindConflictType: "create_account",
                        rememberPwd: !1,
                        textConfig: {
                          mobileCodeLoginText: {
                            title: "\u9a8c\u8bc1\u7801\u767b\u5f55",
                            mobilePlaceholder: "\u624b\u673a\u53f7",
                            codePlaceholder: "\u8bf7\u8f93\u5165\u9a8c\u8bc1\u7801",
                            buttonText: N ? "\u767b\u5f55" : "\u767b\u5f55/\u6ce8\u518c",
                            confirmInfoBeforeText: "\u540c\u610f"
                          },
                          accountPwdLoginText: {
                            title: "\u5bc6\u7801\u767b\u5f55",
                            accountPlaceholder: "\u624b\u673a\u53f7",
                            accountLabel: "\u8bf7\u8f93\u5165\u624b\u673a\u53f7",
                            pwdPlaceholder: "\u8bf7\u8f93\u5165\u5bc6\u7801",
                            confirmInfoBeforeText: "\u540c\u610f"
                          },
                          scanCodeLoginText: {
                            refreshCode: "\u4e8c\u7ef4\u7801\u5df2\u5931\u6548",
                            getCodeFailed: "\u4e8c\u7ef4\u7801\u5df2\u5931\u6548",
                            refreshBtnText: "\u70b9\u51fb\u5237\u65b0",
                            codeFailedBtnText: "\u70b9\u51fb\u5237\u65b0"
                          },
                          passwordResetText: {
                            accountPlaceholder: "\u624b\u673a\u53f7",
                            accountLabel: "\u8bf7\u8f93\u5165\u624b\u673a\u53f7",
                            newPwdPlaceholder: "\u65b0\u5bc6\u7801",
                            confirmPwdPlaceholder: "\u5bc6\u7801\u786e\u8ba4",
                            codePlaceholder: "\u9a8c\u8bc1\u7801"
                          },
                          bindConflictText: {
                            title: "",
                            description: "\u68c0\u6d4b\u5230\u6296\u97f3\u6388\u6743\u7684\u624b\u673a\u53f7\u6ce8\u518c\u7684\u897f\u74dc\u8d26\u53f7\u5df2\u7ed1\u5b9a\u53e6\u4e00\u4e2a\u6296\u97f3\u8d26\u53f7\u201c{aweme_conflict_name}\u201d\uff0c\u5b58\u5728\u7ed1\u5b9a\u51b2\u7a81\uff0c\u8bf7\u5728\u4e0b\u65b9\u9009\u62e9\u89e3\u51b3\u65b9\u5f0f",
                            loginBtnText: "\u6362\u7ed1\u5e76\u767b\u5f55",
                            unbindText: "\u89e3\u9664\u7ed1\u5b9a",
                            backToLogin: "\u8fd4\u56de\u91cd\u65b0\u767b\u5f55"
                          },
                          extraText: {
                            otherLoginText: "\u5176\u4ed6\u65b9\u5f0f\uff1a"
                          }
                        },
                        unionLoginPanel: _,
                        linkAreaPosition: "top",
                        loginTab: V,
                        loginOnly: {
                          mobileCode: N
                        },
                        linkList: W,
                        accountType: ["mobile"],
                        success: function(e) {
                          var t = e.currentPage;
                          w.qQ(b.LocalStorageKeys.LastLoginWay, t),
                            u(e),
                            T()((function() {
                                (0,
                                  S.tokenBeatInit)()
                              }
                            ), 800)
                        },
                        confirm: [{
                          text: "\u7528\u6237\u534f\u8bae",
                          url: "https://www.douyin.com/agreements/?id=6773906068725565448"
                        }, {
                          text: "\u9690\u79c1\u653f\u7b56",
                          url: "https://www.douyin.com/agreements/?id=6773901168964798477"
                        }],
                        unsetCheckbox: {
                          accountPwd: 1,
                          mobileCode: 1,
                          scanCode: 1,
                          trusted: 1,
                          resetPwd: 1
                        },
                        isPwdToMobile: !0,
                        useWrap: _ ? {
                          mobileCode: !0,
                          accountPwd: !0,
                          scanCode: !1
                        } : {},
                        upSmsRegisterCallback: {
                          showCallback: function() {
                            var e = document.getElementsByClassName("screen-mask");
                            if (0 !== e.length) {
                              e[0].style.visibility = "hidden"
                            } else {
                              var t = document.getElementById("login-pannel");
                              t && (t.style.visibility = "hidden")
                            }
                          },
                          closeCallBack: function() {
                            var e = document.getElementsByClassName("screen-mask");
                            if (0 !== e.length) {
                              e[0].style.visibility = "visible"
                            } else {
                              var t = document.getElementById("login-pannel");
                              t && (t.style.visibility = "hidden")
                            }
                          }
                        },
                        LoginSecondSmsCallback: {
                          showCallback: function() {
                            var e = document.getElementsByClassName("screen-mask");
                            if (0 !== e.length) {
                              e[0].style.visibility = "hidden"
                            } else {
                              var t = document.getElementById("login-pannel");
                              t && (t.style.visibility = "hidden")
                            }
                          },
                          closeCallBack: function() {
                            var e = document.getElementsByClassName("screen-mask");
                            if (0 !== e.length) {
                              e[0].style.visibility = "visible"
                            } else {
                              var t = document.getElementById("login-pannel");
                              t && (t.style.visibility = "hidden")
                            }
                          }
                        }
                      }));
                  case 5:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }();
    var F = n(66019)
      , U = ["success", "host", "next", "enterMethod", "headerText", "isPage", "isActive", "onClose", "isCanClose", "teaEvtParams", "disabledABTest", "isGuide", "isAuto", "gearName", "clarity"]
      , H = {
      isShowingAccount: !1,
      isInAccountPage: !1,
      accountPageParams: {
        enterMethod: ""
      }
    };
    function G(e, t) {
      return j.apply(this, arguments)
    }
    function j() {
      return j = (0,
        a.Z)(s().mark((function e(t, n) {
          var o, l, c, u, d, v, x, C, N, T, Z, S, I, L, D, M, B, A, P, O, V, W, G, j, K, q, Y, X, z, Q, J, $, ee, te, ne;
          return s().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return o = t.success,
                      l = void 0 === o ? null : o,
                      c = t.host,
                      u = void 0 === c ? null : c,
                      d = t.next,
                      v = void 0 === d ? null : d,
                      x = t.enterMethod,
                      C = void 0 === x ? "" : x,
                      N = t.headerText,
                      T = void 0 === N ? "" : N,
                      Z = t.isPage,
                      S = void 0 !== Z && Z,
                      I = t.isActive,
                      L = void 0 === I ? "1" : I,
                      D = t.onClose,
                      M = void 0 === D ? null : D,
                      B = t.isCanClose,
                      A = void 0 === B || B,
                      P = t.teaEvtParams,
                      O = void 0 === P ? {} : P,
                      V = t.disabledABTest,
                    void 0 !== V && V,
                      W = t.isGuide,
                      G = void 0 !== W && W,
                      j = t.isAuto,
                      K = void 0 === j ? 1 : j,
                      q = t.gearName,
                      Y = void 0 === q ? "" : q,
                      X = t.clarity,
                      z = void 0 === X ? "" : X,
                      (0,
                        i.Z)(t, U),
                      e.next = 3,
                      (0,
                        F.SJ)();
                  case 3:
                    if (S) {
                      e.next = 7;
                      break
                    }
                    if (!(H.isShowingAccount || null !== (Q = document) && void 0 !== Q && null !== (J = Q.querySelector) && void 0 !== J && J.call(Q, "#login-pannel"))) {
                      e.next = 7;
                      break
                    }
                    return null == M || M(),
                      e.abrupt("return", (function() {
                          return null
                        }
                      ));
                  case 7:
                    return $ = function(e) {
                      e.stopPropagation()
                    }
                      ,
                    A || null === (ee = document) || void 0 === ee || ee.addEventListener("keydown", $, !0),
                      te = "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/login-resetpwd-bg.png",
                      H.isShowingAccount = !0,
                      H.isInAccountPage = !1,
                      ne = function() {
                        var e = (0,
                          a.Z)(s().mark((function e(t) {
                            var r, o, i, a, c, d, f, y, x, N, Z, I, D, B, P, V, W, U, G, j, q, X, Q, J, ee, ne, re, oe, ie, ae, le, se, ce, ue, de, me;
                            return s().wrap((function(e) {
                                for (; ; )
                                  switch (e.prev = e.next) {
                                    case 0:
                                      return c = t.avatarLoginGuide,
                                        d = void 0 === c ? 0 : c,
                                        f = t.checkQrCodeDelayTime,
                                        y = void 0 === f ? 0 : f,
                                        x = t.loginBgImg,
                                        N = void 0 === x ? te : x,
                                        Z = t.isFirstTrust,
                                        I = void 0 === Z ? 0 : Z,
                                        D = t.isAllowTrust,
                                        B = void 0 === D ? 0 : D,
                                        P = t.scanLoginText,
                                        V = void 0 === P ? 0 : P,
                                        W = t.coldStartPanelTitle,
                                        U = void 0 === W ? "" : W,
                                        G = t.subTitle,
                                        j = void 0 === G ? [] : G,
                                        q = m()(r = ["cold_start", "cold_start_full"]).call(r, C) && 1 === d && !(F.u % 3 == 0 && F.Vg),
                                        X = m()(o = ["cold_start", "cold_start_full"]).call(o, C) && 2 === d && !F.Vg && F.u < 5,
                                        Q = !(m()(i = ["cold_start", "cold_start_full"]).call(i, C) || 1 !== d || F.FT % 3 == 0 && F.q5),
                                        J = !m()(a = ["cold_start", "cold_start_full"]).call(a, C) && 2 === d && !F.q5 && F.FT < 5,
                                        ee = String(Number(q || X || Q || J)),
                                        ne = T || (m()(re = ["cold_start_full", "cold_start", "auto", "navigation_bar"]).call(re, C) ? U : ""),
                                        oe = function() {
                                          return h.createElement("div", {
                                            className: "web-login-scan-desc-text"
                                          }, h.createElement("div", null, "\u6253\u5f00\u6296\u97f3APP"), h.createElement("div", {
                                            className: "web-login-scan-desc-text-sub"
                                          }, "\u70b9\u51fb\u9996\u9875\u5de6\u4e0a\u89d2", h.createElement("div", {
                                            className: "web-login-scan-desc-icon"
                                          }), "\u626b\u4e00\u626b"))
                                        }
                                        ,
                                        ie = function() {
                                          return h.createElement("div", {
                                            className: "web-login-scan-desc-text"
                                          }, h.createElement("div", null, "\u6253\u5f00\u6296\u97f3APP"), h.createElement("div", {
                                            className: "web-login-scan-desc-text-sub"
                                          }, h.createElement("span", {
                                            style: {
                                              paddingRight: "20px"
                                            }
                                          }, "1. \u70b9\u51fb\u9996\u9875\u53f3\u4e0a\u89d2", h.createElement("span", {
                                            className: "web-login-scan-desc-icon-search"
                                          })), h.createElement("span", null, "2. \u70b9\u51fb", h.createElement("span", {
                                            className: "web-login-scan-desc-icon-scan"
                                          }), "\u626b\u63cf\u4e8c\u7ef4\u7801")))
                                        }
                                        ,
                                        ae = function() {
                                          return h.createElement("div", {
                                            className: "web-login-scan-desc-text"
                                          }, h.createElement("div", null, "\u6253\u5f00", h.createElement("span", {
                                            className: "web-login-scan-desc-text-sub"
                                          }, "\u300c\u6296\u97f3APP\u300d"), "\u626b\u63cf\u4e8c\u7ef4\u7801\u767b\u5f55"))
                                        }
                                        ,
                                        le = function() {
                                          switch (V) {
                                            case g.ScanLoginTextType.GuideSearch:
                                              return ie;
                                            case g.ScanLoginTextType.OpenApp:
                                              return ae;
                                            default:
                                              return oe
                                          }
                                        }(),
                                        !1,
                                        e.next = 15,
                                        R({
                                          success: l,
                                          host: u,
                                          next: v,
                                          ScanCodeDescription: le,
                                          enterMethod: C,
                                          isUnion: false,
                                          isActive: L,
                                          teaEvtParams: O,
                                          isHaveAvatar: ee,
                                          checkQrCodeDelayTime: y,
                                          isAuto: K,
                                          gearName: Y,
                                          clarity: z,
                                          currentUserInfo: w.$o(b.LocalStorageKeys.UserInfo),
                                          isAllowTrust: Boolean(B) && 1 === w.$o(b.LocalStorageKeys.IsAllowTrust),
                                          isFirstTrust: Boolean(I),
                                          mobileLoginOnly: _.X()
                                        });
                                    case 15:
                                      return se = e.sent,
                                        ce = document.createElement("div"),
                                        ue = document.body,
                                        n ? (ue = n,
                                          n.appendChild(ce)) : (de = document.getElementsByClassName("xgplayer-fullscreen-parent")[0],
                                          E.r() && de ? (ue = de,
                                            de.appendChild(ce)) : document.body.appendChild(ce)),
                                        me = function() {
                                          var e;
                                          (document.body.style.overflow = "",
                                            p.unmountComponentAtNode(ce),
                                          ue.contains(ce) && ue.removeChild(ce),
                                          null == M || M(),
                                            A) || (null === (e = document) || void 0 === e || e.removeEventListener("keydown", $))
                                        }
                                        ,
                                        document.body.style.overflow = "hidden",
                                        k.IX(),
                                        p.render(h.createElement(F.ZP, {
                                          config: se,
                                          destroy: function() {
                                            H.isShowingAccount = !1,
                                              me()
                                          },
                                          text: ne,
                                          isPage: S,
                                          onClose: M,
                                          enterMethod: C,
                                          isCanClose: A,
                                          avatarAbtest: d,
                                          loginBgImg: N,
                                          scanLoginText: V,
                                          subTitle: j
                                        }), ce),
                                        e.abrupt("return", me);
                                    case 24:
                                    case "end":
                                      return e.stop()
                                  }
                              }
                            ), e)
                          }
                        )));
                        return function(t) {
                          return e.apply(this, arguments)
                        }
                      }(),
                      f().all([y.h.getVar({
                        name: "avatar_login_guide",
                        defaultValue: 0
                      }), y.h.getVar({
                        name: "check_qr_code_delay_time",
                        defaultValue: g.CheckQrCodeDelayTimeABVal.Normal
                      }), y.h.getVar({
                        name: "login_bg_img",
                        defaultValue: te
                      }), y.h.getVar({
                        name: "is_first_trust",
                        defaultValue: 0
                      }), y.h.getVar({
                        name: "is_allow_trust",
                        defaultValue: 0
                      }), y.h.getVar({
                        name: "scan_login_text_type",
                        defaultValue: g.ScanLoginTextType.Default
                      }), y.h.getVar({
                        name: "cold_start_panel_title",
                        defaultValue: g.ColdStartPanelTitle.Default
                      }), y.h.getVar({
                        name: "cold_start_panel_subtitle",
                        defaultValue: []
                      })]).then((function(e) {
                          var t = (0,
                            r.Z)(e, 8)
                            , n = t[0]
                            , o = void 0 === n ? 0 : n
                            , i = t[1]
                            , a = void 0 === i ? 0 : i
                            , l = t[2]
                            , s = void 0 === l ? te : l
                            , c = t[3]
                            , u = void 0 === c ? 0 : c
                            , d = t[4]
                            , m = void 0 === d ? 0 : d
                            , v = t[5]
                            , f = void 0 === v ? 0 : v
                            , h = t[6]
                            , p = void 0 === h ? "" : h
                            , g = t[7];
                          return ne({
                            avatarLoginGuide: o,
                            checkQrCodeDelayTime: G ? a : 0,
                            loginBgImg: s,
                            isFirstTrust: u,
                            isAllowTrust: m,
                            scanLoginText: f,
                            coldStartPanelTitle: p,
                            subTitle: void 0 === g ? [] : g
                          })
                        }
                      )).catch((function() {
                          return ne({
                            avatarLoginGuide: 0,
                            checkQrCodeDelayTime: 0,
                            loginBgImg: te,
                            isFirstTrust: 0,
                            isAllowTrust: 0,
                            scanLoginText: 0,
                            coldStartPanelTitle: "",
                            subTitle: []
                          })
                        }
                      )),
                      e.abrupt("return", (function() {
                          return null
                        }
                      ));
                  case 15:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      ))),
        j.apply(this, arguments)
    }
    function K(e) {
      G((0,
        o.Z)({
        isPage: !0,
        next: (0,
          C.pL)()
      }, e)),
        H.accountPageParams = e,
        H.isInAccountPage = !0
    }
    function q(e) {
      H.isShowingAccount = !1;
      var t = H.isInAccountPage ? u()(K).call(K, null, H.accountPageParams) : function() {
          return null
        }
      ;
      G((0,
        o.Z)((0,
        o.Z)({}, e), {}, {
        next: (null == e ? void 0 : e.next) || (0,
          C.pL)(),
        onClose: t
      }))
    }
    x.p() || (window.showAccount = G)
  }
  ,
  22459: (e,t,n)=>{
    n.d(t, {
      q: ()=>d
    });
    var r = n(65146)
      , o = n(32781)
      , i = n(88438)
      , a = n.n(i)
      , l = n(44503)
      , s = n(79705)
      , c = n.n(s);
    const u = {
      avatarIcon: "BXCYEFpt",
      avatar: "F55pZYYH",
      image: "PbpHcHqa",
      live: "hidFvG2l",
      extraExtraExtraSmall: "LI_QQRBx",
      extraExtraSmall: "dq39KdYi",
      extraSmall: "zzYG7dwz",
      small: "MtWaibfJ",
      default: "QsTz7P83",
      showOverflow: "qTgJQqwp",
      self: "XMvzRCvu",
      pendant: "ScZNxJWS"
    };
    function d(e) {
      var t, n = e.type, i = void 0 === n ? "default" : n, s = e.src, d = e.alt, m = void 0 === d ? "" : d, v = e.isSpider, f = void 0 !== v && v, h = e.isSelf, p = void 0 !== h && h, g = e.showImageInSSR, y = void 0 !== g && g, w = e.className, _ = e.defaultClassName, E = e.imgClassName, k = e.maskConf, x = e.onMouseEnter, b = e.onMouseLeave, C = (0,
        l.useState)(0), N = (0,
        o.Z)(C, 2), T = N[0], Z = N[1], S = s && (1 === T || f || y), I = k || {}, L = I.showMask, D = I.MaskItem, M = I.className, B = function() {
        return Z(1)
      };
      return (0,
        l.useEffect)((function() {
          var e = !1
            , t = new Image;
          t.onload = function() {
            e || (e = !0,
              B(),
              t = null)
          }
            ,
            t.onerror = function() {
              e || (e = !0,
                Z(-1),
                t = null)
            }
          ;
          var n = a()((function() {
              e = !0,
                B()
            }
          ), 3e3);
          return t.src = globalThis.getFilterXss().filterUrl(s, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
            function() {
              t && (t.onload = null,
                t.onerror = null),
                clearTimeout(n)
            }
        }
      ), [s]),
        l.createElement("div", {
          className: c()(u.avatar, u[i], "avatar-component-avatar-container", (t = {},
            (0,
              r.Z)(t, w, w),
            (0,
              r.Z)(t, u.self, p),
            t)),
          onMouseEnter: x,
          onMouseLeave: b,
          "data-e2e": "live-avatar"
        }, L ? l.createElement(D, {
          className: M
        }) : null, S ? l.createElement("img", {
          src: globalThis.getFilterXss().filterUrl(s, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          alt: m,
          className: c()(u.image, E),
          onError: function() {
            return Z(-1)
          },
          onLoad: B
        }) : l.createElement("div", {
          className: c()(u[i], u.avatarIcon, (0,
            r.Z)({}, w, _))
        }))
    }
  }
  ,
  81767: (e,t,n)=>{
    n.d(t, {
      n: ()=>h
    });
    var r = n(65146)
      , o = n(44503)
      , i = n(79705)
      , a = n.n(i)
      , l = n(36862)
      , s = n(8704)
      , c = n(50325)
      , u = n(21411)
      , d = n(19104);
    const m = {
      avatarContainer: "QecmPpxX",
      isFirstLive: "JgxT_z8s",
      avatarBorder: "X0v0tibw",
      avatarBorderAnimation: "huP9OS34",
      "first-live-cover-border-scale-animation": "xyb6OqsT",
      "cover-border-scale-animation": "aKbSlHZH",
      avatar: "RUVTDzAp",
      "cover-animation": "sBNZrvc_",
      liveTag: "LrQqtaiB",
      liveTagText: "w4SksZun",
      small: "TrKWAgc9",
      liveTagInner: "XQ9v_nAP",
      liveTagInnerImg: "LkrPIgdh",
      large: "nGtv725p",
      push: "IpUDli_q"
    };
    const v = new (n(37485).hD)({
      livesdkLiveShow: {
        eventName: "livesdk_live_show",
        params: {
          enter_from_merge: "",
          enter_method: "web_video_head",
          action_type: "",
          request_id: "",
          is_vs: 0,
          vs_episode_id: "",
          vs_ep_group_id: "",
          vs_season_id: "",
          vs_episode_stage: "",
          anchor_id: "",
          room_id: "",
          video_id: ""
        }
      },
      livesdkRecLivePlay: {
        eventName: "livesdk_rec_live_play",
        params: {
          anchor_id: "",
          room_id: "",
          enter_from_merge: "",
          enter_method: "web_video_head",
          game_name: "",
          live_type: "",
          is_aweme_tied: 0,
          game_live_source: "",
          url: "",
          url_path: "",
          action_type: "click",
          request_id: "",
          is_vs: 0,
          vs_episode_id: "",
          vs_ep_group_id: "",
          vs_season_id: "",
          vs_episode_stage: ""
        }
      }
    });
    var f = n(14001);
    function h(e) {
      var t, n = e.type, i = void 0 === n ? "normal" : n, h = e.src, p = e.alt, g = void 0 === p ? "" : p, y = e.uid, w = void 0 === y ? "" : y, _ = e.liveRoomUrl, E = e.isNeedSeoOpt, k = void 0 !== E && E, x = e.isNeedSendLog, b = void 0 !== x && x, C = e.liveRoomParam, N = void 0 === C ? {
        logId: ""
      } : C, T = e.isShow, Z = void 0 === T || T, S = e.isFirstLive, I = void 0 !== S && S, L = e.onClick, D = void 0 === L ? function() {}
        : L, M = e.groupId, B = (0,
        o.useMemo)((function() {
          return "String" !== l.tQ(_) ? null : s.D(_.split("?", 2)[1])
        }
      ), [_]), A = (0,
        o.useRef)(!1), P = (0,
        o.useRef)(null), O = (0,
        o.useCallback)((function(e) {
          D(e),
          b && function() {
            var e, t, n, r, o, i, a = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "", l = arguments.length > 1 ? arguments[1] : void 0, s = arguments.length > 2 ? arguments[2] : void 0;
            if (l) {
              var u = null == s ? void 0 : s.episodeExtra;
              v.sendLog("livesdkRecLivePlay", {
                enter_from_merge: l.enter_from_merge,
                enter_method: "web_video_head",
                anchor_id: a,
                room_id: l.room_id,
                live_type: "game",
                game_live_source: "game_web",
                url: location.href,
                url_path: location.pathname,
                request_id: null !== (e = null == s ? void 0 : s.logId) && void 0 !== e ? e : "",
                is_vs: u ? 1 : 0,
                vs_episode_id: u ? null == s || null === (t = s.episodeExtra) || void 0 === t ? void 0 : t.episode_id_str : "",
                vs_ep_group_id: u ? null == s || null === (n = s.episodeExtra) || void 0 === n ? void 0 : n.item_id : "",
                vs_season_id: u ? null == s || null === (r = s.episodeExtra) || void 0 === r ? void 0 : r.season_id_str : "",
                vs_episode_stage: u ? (null == s || null === (o = s.episodeExtra) || void 0 === o || null === (i = o.mod) || void 0 === i ? void 0 : i.episode_stage) === c.W.FirstLive ? "premiere" : "live" : ""
              })
            }
          }(w, B, N)
        }
      ), [b, D, w, B, N]);
      return (0,
        o.useEffect)((function() {
          if (B && null != N && N.logId && !A.current && Z) {
            var e, t, n, r, o, i = null == N ? void 0 : N.episodeExtra;
            v.sendLog("livesdkLiveShow", {
              anchor_id: w,
              room_id: B.room_id,
              action_type: B.action_type,
              enter_from_merge: B.enter_from_merge,
              enter_method: B.enter_method,
              request_id: null == N ? void 0 : N.logId,
              video_id: M,
              is_vs: i ? 1 : 0,
              vs_episode_id: i ? null == N || null === (e = N.episodeExtra) || void 0 === e ? void 0 : e.episode_id_str : "",
              vs_ep_group_id: i ? null == N || null === (t = N.episodeExtra) || void 0 === t ? void 0 : t.item_id : "",
              vs_season_id: i ? null == N || null === (n = N.episodeExtra) || void 0 === n ? void 0 : n.season_id_str : "",
              vs_episode_stage: i ? (null == N || null === (r = N.episodeExtra) || void 0 === r || null === (o = r.mod) || void 0 === o ? void 0 : o.episode_stage) === c.W.FirstLive ? "premiere" : "live" : ""
            }),
              A.current = !0
          }
        }
      ), [N, Z]),
        o.createElement(f.a, {
          href: globalThis.getFilterXss().filterUrl(_, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          isNeedSeoOpt: k,
          target: "_blank",
          refEl: P,
          rel: "noopener noreferrer",
          className: a()(m.Streamline),
          onClick: O
        }, o.createElement("div", {
          className: a()(m.avatarContainer, (t = {},
            (0,
              r.Z)(t, m.isFirstLive, I),
            (0,
              r.Z)(t, m.small, "small" === i),
            (0,
              r.Z)(t, m.large, "large" === i),
            (0,
              r.Z)(t, m.push, "push" === i),
            t))
        }, o.createElement("img", {
          className: m.avatar,
          src: globalThis.getFilterXss().filterUrl(h, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          alt: g
        }), o.createElement("div", {
          className: m.avatarBorder
        }), o.createElement("div", {
          className: a()(m.avatarBorder, m.avatarBorderAnimation)
        }), "small" !== i && "push" !== i ? o.createElement("div", {
          className: m.liveTag
        }, o.createElement("span", {
          className: m.liveTagText,
          "data-e2e": "user-info-living"
        }, I ? "\u9996\u64ad\u4e2d" : "\u76f4\u64ad\u4e2d")) : o.createElement("div", {
          className: m.liveTagInner
        }, o.createElement("img", {
          className: m.liveTagInnerImg,
          src: globalThis.getFilterXss().filterUrl(I ? d : u, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          alt: "LiveIcon"
        }))))
    }
  }
  ,
  42327: (e,t,n)=>{
    n.d(t, {
      zx: ()=>v,
      qE: ()=>u,
      L$: ()=>d
    });
    var r = n(65146)
      , o = n(30906)
      , i = n(67161)
      , a = n(44503)
      , l = n(79705)
      , s = n.n(l);
    const c = {
      button: "B10aL8VQ",
      small: "gPRZQy7u",
      fixed: "ODGbpnws",
      normal: "s6mStVxD",
      large: "oAtLbey6",
      primary: "vMQD6aai",
      border: "vk7WaOg_",
      secondary: "cFQVxkEQ",
      ghost: "uLcV3IR8"
    };
    var u, d, m = ["size", "type", "children", "autoFixed", "className", "width", "style", "theme", "disabled"];
    function v(e) {
      var t = e.size
        , n = void 0 === t ? "normal" : t
        , l = e.type
        , u = void 0 === l ? "primary" : l
        , d = e.children
        , v = e.autoFixed
        , f = void 0 === v || v
        , h = e.className
        , p = e.width
        , g = e.style
        , y = e.theme
        , w = void 0 === y ? "solid" : y
        , _ = e.disabled
        , E = void 0 !== _ && _
        , k = (0,
        i.Z)(e, m);
      return a.createElement("button", (0,
        o.Z)({
        type: "button",
        disabled: E,
        className: s()(c.button, c[n], c[u], c[w], (0,
          r.Z)({}, c.fixed, !f), h),
        style: (0,
          o.Z)({
          width: p && "".concat(p, "px")
        }, g)
      }, k), d)
    }
    !function(e) {
      e.small = "small",
        e.normal = "normal",
        e.large = "large"
    }(u || (u = {})),
      function(e) {
        e.primary = "primary",
          e.secondary = "secondary"
      }(d || (d = {}))
  }
  ,
  32322: (e,t,n)=>{
    n.d(t, {
      k: ()=>l
    });
    var r = n(44503)
      , o = n(83095)
      , i = n(76659)
      , a = n(64644)
      , l = function(e) {
      var t = e.fallback
        , n = e.beforeCapture
        , l = e.onError
        , s = e.componentName
        , c = e.children
        , u = e.Slardar
        , d = i.Le.getConfig(i.gI.AbtestData)
        , m = (0,
        r.useCallback)((function(e, t) {
          var n;
          a.oe.event.error({
            name: a.Mo.ComponentErrorBoundary,
            report: {
              message: e.message,
              stack: null !== (n = e.stack) && void 0 !== n ? n : "",
              componentStack: t.toString(),
              componentName: s
            }
          }),
          null == l || l(e, t)
        }
      ), []);
      return null != d && d.errorBoundaryOpt && u ? r.createElement(o.SV, {
        fallback: t,
        onError: m,
        beforeCapture: n,
        Slardar: u || a.oe.getSlardarInstance()
      }, c) : r.createElement(r.Fragment, null, c)
    }
  }
  ,
  11189: (e,t,n)=>{
    n.d(t, {
      o: ()=>st
    });
    var r = n(30906)
      , o = n(64408)
      , i = n(30673)
      , a = n(32781)
      , l = n(65146)
      , s = n(5594)
      , c = n.n(s)
      , u = n(92012)
      , d = n.n(u)
      , m = n(92637)
      , v = n.n(m)
      , f = n(84891)
      , h = n.n(f)
      , p = n(41265)
      , g = n.n(p)
      , y = n(21805)
      , w = n.n(y)
      , _ = n(59440)
      , E = n.n(_)
      , k = n(81711)
      , x = n.n(k)
      , b = n(88438)
      , C = n.n(b)
      , N = n(79705)
      , T = n.n(N)
      , Z = n(44503)
      , S = n(89176)
      , I = n(78867)
      , L = n(72983)
      , D = n(81300)
      , M = n(25083)
      , B = n(82226)
      , A = n(45627)
      , P = n(52252)
      , O = n(16655)
      , V = n(59505)
      , W = n(14484)
      , R = n(92345)
      , F = n(92289)
      , U = n(11455);
    const H = "n9PPTk22"
      , G = "N_HNXA04"
      , j = "gtbObvwD"
      , K = "HQwsRJFy"
      , q = "RzBzzWsU"
      , Y = "Bo1o4KGi"
      , X = "XFvPYpcw"
      , z = "iViO9oMI"
      , Q = "BmcsyffA"
      , J = "kQ2JnIMK"
      , $ = "S9ST96Zy"
      , ee = "a9jyVZQj"
      , te = "c4FOEjLr"
      , ne = "YrFhKzRI"
      , re = "bFNyxfOF"
      , oe = "pi5uYseT"
      , ie = "JVPLvXh3"
      , ae = "gaIgCiUy";
    var le = n(96608)
      , se = n(94610)
      , ce = n.n(se)
      , ue = [{
      url: "https://www.oceanengine.com/resource/douyin",
      title: "\u5e7f\u544a\u6295\u653e"
    }, {
      url: "https://www.douyin.com/agreements/?id=6773906068725565448",
      title: "\u7528\u6237\u670d\u52a1\u534f\u8bae"
    }, {
      url: "https://www.douyin.com/agreements/?id=6773901168964798477",
      title: "\u9690\u79c1\u653f\u7b56"
    }, {
      url: "https://www.douyin.com/recovery_account/",
      title: "\u8d26\u53f7\u627e\u56de"
    }, {
      url: "https://www.douyin.com/aboutus/#contact",
      title: "\u8054\u7cfb\u6211\u4eec"
    }, {
      url: "https://www.douyin.com/aboutus/#join",
      title: "\u52a0\u5165\u6211\u4eec"
    }, {
      url: "https://www.douyin.com/business_license/",
      title: "\u8425\u4e1a\u6267\u7167"
    }, {
      url: "https://www.douyin.com/friend_links",
      title: "\u53cb\u60c5\u94fe\u63a5"
    }, {
      url: "https://www.douyin.com/htmlmap/hotauthor_0_1",
      title: "\u7ad9\u70b9\u5730\u56fe"
    }, {
      url: "https://www.douyin.com/downloadpage",
      title: "\u4e0b\u8f7d\u6296\u97f3"
    }, {
      url: "https://mix.jinritemai.com/falcon/mix_page/index.html?__live_platform__=webcast&allowMediaAutoPlay=1&enter_from=others&hide_nav_bar=1&hide_system_video_poster=1&id=7117178766052294949&origin_type=others&should_full_screen=1&trans_status_bar=1&ttwebview_extension_mixrender=1&hide_nav_bar=1&should_full_screen=1&trans_status_bar=1&web_bg_color=#ffffffff",
      title: "\u6296\u97f3\u7535\u5546"
    }]
      , de = [[{
      title: "".concat((new Date).getFullYear(), " \xa9 \u6296\u97f3")
    }, {
      url: "https://beian.miit.gov.cn/",
      title: "\u4eacICP\u590716016397\u53f7-3"
    }, {
      icon: "//p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/emblem.png",
      url: "http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11000002002046",
      title: "\u4eac\u516c\u7f51\u5b89\u5907 11000002002046\u53f7"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/jiemuzhizuojingying.jpeg",
      title: "\u5e7f\u64ad\u7535\u89c6\u8282\u76ee\u5236\u4f5c\u7ecf\u8425\u8bb8\u53ef\u8bc1"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/zengzhixuke.jpeg",
      title: "\u4eacB2-20170846"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/wangluowenhuajingying.jpeg",
      title: "\u7f51\u7edc\u6587\u5316\u8bb8\u53ef\u8bc1-\u4eac\u7f51\u6587-\uff082022\uff090938-030\u53f7"
    }], [{
      url: "https://www.piyao.org.cn/yybgt/index.htm",
      title: "\u7f51\u7edc\u8c23\u8a00\u66dd\u5149\u53f0"
    }, {
      url: "https://www.12377.cn/",
      title: "\u7f51\u4e0a\u6709\u5bb3\u4fe1\u606f\u4e3e\u62a5"
    }, {
      title: "\u8fdd\u6cd5\u548c\u4e0d\u826f\u4fe1\u606f\u4e3e\u62a5 400-140-2108"
    }, {
      title: "\u9752\u5c11\u5e74\u5b88\u62a4\u4e13\u7ebf 400-9922-556"
    }, {
      title: "\u7b97\u6cd5\u63a8\u8350\u4e13\u9879\u4e3e\u62a5 sfjubao@bytedance.com"
    }, {
      title: "\u7f51\u7edc\u5185\u5bb9\u4ece\u4e1a\u4eba\u5458\u8fdd\u6cd5\u8fdd\u89c4\u884c\u4e3a\u4e3e\u62a5 feedback@douyin.com"
    }]]
      , me = n(14001);
    const ve = "NRSpjbcb"
      , fe = "wQmC940F"
      , he = "yA0rrc2M"
      , pe = "o1h2uP_i"
      , ge = "YfdKaFoj"
      , ye = "h9hROuDG"
      , we = "eb9O5iw_";
    const _e = new (n(37485).hD)({
      pageClick: {
        eventName: "page_click",
        params: {
          click_position: "site_map"
        }
      }
    });
    var Ee = n(62305)
      , ke = n.n(Ee)
      , xe = n(46989)
      , be = n(90147);
    function Ce(e) {
      var t = e.linkItems
        , n = e.subLinkItems
        , r = e.specTheme
        , o = t || ue
        , i = n || de
        , a = function(e) {
        var t = e.links;
        return Z.createElement("div", {
          className: he
        }, ce()(t).call(t, (function(e, t) {
            var n = e.url;
            return Z.createElement("div", {
              key: "link_".concat(t),
              className: ge
            }, e.url ? Z.createElement(me.a, {
              href: globalThis.getFilterXss().filterUrl(n, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              onClick: function(t) {
                if ("\u7ad9\u70b9\u5730\u56fe" === e.title) {
                  var r, o, i, a, l, s, c, u, d, m = n, v = ke().parse(null !== (r = null === (o = window) || void 0 === o || null === (i = o.location) || void 0 === i ? void 0 : i.search) && void 0 !== r ? r : "");
                  v.from = null === (a = window) || void 0 === a || null === (l = a.location) || void 0 === l ? void 0 : l.pathname,
                  null !== (s = window) && void 0 !== s && null !== (c = s.location) && void 0 !== c && w()(u = c.href).call(u, be.LIVE_DOMAIN) && (v.from = "live"),
                    m += "".concat(decodeURIComponent("?".concat(ke().stringify(v)))),
                  null === (d = window) || void 0 === d || d.open(m, "_blank"),
                    _e.sendLog("pageClick"),
                    t.preventDefault()
                }
              },
              target: "_blank",
              rel: "noopener noreferrer".concat(xe.P(e.title))
            }, e.title) : Z.createElement("span", null, e.title))
          }
        )))
      }
        , s = function(e) {
        var t = e.sublink;
        return Z.createElement("div", {
          className: ye
        }, t.url ? Z.createElement(me.a, {
          href: globalThis.getFilterXss().filterUrl(t.url, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          target: "_blank",
          rel: "noopener noreferrer"
        }, t.icon && Z.createElement("img", {
          className: we,
          src: globalThis.getFilterXss().filterUrl(t.icon, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          alt: "icon"
        }), t.title) : Z.createElement("span", null, t.title))
      }
        , c = function(e) {
        var t = e.sublinksGroup;
        return Z.createElement(Z.Fragment, null, ce()(t).call(t, (function(e, t) {
            return Z.createElement("div", {
              key: "g_".concat(t),
              className: pe
            }, ce()(e).call(e, (function(e, t) {
                return Z.createElement(s, {
                  key: "sublink_".concat(t),
                  sublink: e
                })
              }
            )))
          }
        )))
      };
      return Z.createElement("footer", null, Z.createElement("div", {
        className: T()(fe, (0,
          l.Z)({}, ve, null == r ? void 0 : r.themeFurtherSwitch))
      }, Z.createElement(c, {
        sublinksGroup: i
      }), Z.createElement(a, {
        links: o
      })))
    }
    var Ne = n(3748)
      , Te = n(76659)
      , Ze = n(8841);
    const Se = "HLKZ9U4X"
      , Ie = "r62Yt4yT"
      , Le = "qoKzjoSV"
      , De = "L4Q5Pfp6";
    var Me = function(e) {
      var t, n = e.list, i = e.current, s = e.onChange, u = e.className, d = e.activeClickable, m = e.userInfo, f = e.abTestData, h = e.customProps, p = Z.useRef(null), g = (0,
        Z.useState)(), y = (0,
        a.Z)(g, 2), w = y[0], _ = y[1];
      return (0,
        Z.useEffect)((function() {
          var e = !1;
          return i && (0,
            o.Z)(c().mark((function t() {
              var n, r, o;
              return c().wrap((function(t) {
                  for (; ; )
                    switch (t.prev = t.next) {
                      case 0:
                        return t.next = 2,
                          Ne.U();
                      case 2:
                        n = t.sent,
                        e || (r = Te.Le.getConfig(Te.gI.TabPointCache),
                          o = n,
                          Te.Le.setConfig(Te.gI.TabPointCache, {
                            followCount: "follow" === i ? 0 : (null == o ? void 0 : o.count) || (null == r ? void 0 : r.followCount),
                            followHasLive: "follow" !== i && ((null == o ? void 0 : o.hasLive) || (null == r ? void 0 : r.followHasNotice)),
                            followHasNotice: "follow" !== i && ((null == o ? void 0 : o.hasNotice) || (null == r ? void 0 : r.followHasLive)),
                            friendHasNotice: "friend" !== i && ((null == o ? void 0 : o.friendHasNotice) || (null == r ? void 0 : r.friendHasNotice)),
                            friendNoticeCount: "friend" === i ? 0 : (null == o ? void 0 : o.friendNoticeCount) || (null == r ? void 0 : r.friendNoticeCount)
                          }),
                          o.count = "follow" === i ? 0 : n.count || (null == r ? void 0 : r.followCount),
                          o.hasNotice = "follow" !== i && (n.hasNotice || (null == r ? void 0 : r.followHasNotice)),
                          o.hasLive = "follow" !== i && (n.hasLive || (null == r ? void 0 : r.followHasLive)),
                          o.friendHasNotice = "friend" !== i && (n.friendHasNotice || (null == r ? void 0 : r.friendHasNotice)),
                          o.friendNoticeCount = "friend" === i ? 0 : n.friendNoticeCount || (null == r ? void 0 : r.friendNoticeCount),
                          _(o));
                      case 4:
                      case "end":
                        return t.stop()
                    }
                }
              ), t)
            }
          )))(),
            function() {
              e = !0
            }
        }
      ), [i]),
        Z.createElement("div", {
          className: T()(Se, u, (0,
            l.Z)({}, De, null == h ? void 0 : h.isSearchSideNav)),
          ref: p
        }, ce()(t = v()(n).call(n, (function(e) {
            return !e.hideTab
          }
        ))).call(t, (function(e) {
            return "divider" === e.value ? Z.createElement("div", {
              key: e.value,
              className: Ie
            }) : Z.createElement(Ze.G, (0,
              r.Z)({
              abTestData: f,
              userInfo: m,
              active: e.value === i,
              activeClickable: d,
              className: Le,
              onClick: s,
              customProps: (0,
                r.Z)((0,
                r.Z)({}, h), e.custom),
              isHidden: e.hideTab,
              key: e.value,
              socialInfo: w
            }, e))
          }
        )))
    }
      , Be = n(91707)
      , Ae = n(98343);
    const Pe = "GuSbEOy7"
      , Oe = "PZ9RCv1n"
      , Ve = "H3w1iDzb"
      , We = "zPc4oZVy"
      , Re = "vUCGH4WQ"
      , Fe = "eKaSqTbb"
      , Ue = "ETaKHYhF"
      , He = "vrKoVatG"
      , Ge = "MxoM7PCk"
      , je = "D8gl48qZ"
      , Ke = "SKasw4pP"
      , qe = "GctVLOFA"
      , Ye = "PFKtPjJX";
    var Xe, ze = (0,
      Z.memo)((function(e) {
        var t = e.showType
          , n = e.miniImageDark
          , r = e.miniImageLight
          , o = e.miniImageLightHover
          , i = e.miniImageDarkHover
          , s = e.miniAnimationLight
          , c = e.miniAnimationDark
          , u = e.miniTextLight
          , m = e.miniTextDark
          , v = (0,
          Z.useState)(!1)
          , f = (0,
          a.Z)(v, 2)
          , h = f[0]
          , p = f[1];
        (0,
          Z.useEffect)((function() {
            var e, t, a, l = [{
              name: "--vs-spring-entry-mini-animation-light",
              value: s
            }, {
              name: "--vs-spring-entry-mini-animation-dark",
              value: c
            }, {
              name: "--vs-spring-entry-mini-image-light",
              value: r
            }, {
              name: "--vs-spring-entry-mini-image-dark",
              value: n
            }, {
              name: "--vs-spring-entry-mini-image-light-hover",
              value: o
            }, {
              name: "--vs-spring-entry-mini-image-dark-hover",
              value: i
            }, {
              name: "--vs-spring-entry-mini-text-light",
              value: u
            }, {
              name: "--vs-spring-entry-mini-text-dark",
              value: m
            }], v = ce()(l).call(l, (function(e) {
                var t;
                return d()(t = "".concat(e.name, ": url(")).call(t, e.value, ");")
              }
            )).join("");
            null === (e = document.getElementsByClassName(He)) || void 0 === e || null === (t = e[0]) || void 0 === t || null === (a = t.setAttribute) || void 0 === a || a.call(t, "style", v)
          }
        ), [n, r, o, i, s, c, u, m]);
        var g = t === U.pC.Animation && !h;
        return Z.createElement("div", {
          className: T()(He),
          onMouseEnter: function() {
            p(!0)
          }
        }, Z.createElement("div", {
          className: T()(Ge, Ke, (0,
            l.Z)({}, Ye, g))
        }), Z.createElement("div", {
          className: T()(Ge, je, (0,
            l.Z)({}, Ye, !g))
        }), Z.createElement("div", {
          className: qe
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(r, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(n, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(o, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(i, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(u, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Ye,
          src: globalThis.getFilterXss().filterUrl(m, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }))
      }
    )), Qe = (0,
      Z.memo)((function(e) {
        var t, n = e.showType, o = e.imageDark, i = e.imageLight, s = e.imageDarkHover, c = e.imageLightHover, u = e.animationDark, m = e.animationLight, v = e.animationDarkV2, f = e.animationLightV2, h = e.abtest, p = (0,
          Ae.TH)(), g = (0,
          Z.useState)(!1), y = (0,
          a.Z)(g, 2), _ = y[0], E = y[1];
        (0,
          Z.useEffect)((function() {
            var e, t, n, r = [{
              name: "--vs-spring-entry-animation-light",
              value: null != h && h.vsEntryAnimate ? f : m
            }, {
              name: "--vs-spring-entry-animation-dark",
              value: null != h && h.vsEntryAnimate ? v : u
            }, {
              name: "--vs-spring-entry-image-light",
              value: i
            }, {
              name: "--vs-spring-entry-image-dark",
              value: o
            }, {
              name: "--vs-spring-entry-image-light-hover",
              value: c
            }, {
              name: "--vs-spring-entry-image-dark-hover",
              value: s
            }], a = ce()(r).call(r, (function(e) {
                var t;
                return d()(t = "".concat(e.name, ": url(")).call(t, e.value, ");")
              }
            )).join("");
            null === (e = document.getElementsByClassName(Pe)) || void 0 === e || null === (t = e[0]) || void 0 === t || null === (n = t.setAttribute) || void 0 === n || n.call(t, "style", a)
          }
        ), [m, u, i, o, c, s, v, f, null == h ? void 0 : h.vsEntryAnimate]);
        var k = n === U.pC.Animation && !_;
        return Z.createElement("div", {
          className: T()(Pe, (0,
            l.Z)({}, Fe, null == p || null === (t = p.pathname) || void 0 === t ? void 0 : w()(t).call(t, "/search"))),
          onMouseEnter: function() {
            E(!0)
          }
        }, Z.createElement("div", {
          className: Ue
        }, Z.createElement(ze, (0,
          r.Z)({}, e))), Z.createElement("div", {
          className: T()(Oe, We, (0,
            l.Z)({}, Re, k))
        }), Z.createElement("div", {
          className: T()(Oe, Ve, (0,
            l.Z)({}, Re, !k))
        }), Z.createElement("img", {
          className: Re,
          src: globalThis.getFilterXss().filterUrl(i, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Re,
          src: globalThis.getFilterXss().filterUrl(o, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Re,
          src: globalThis.getFilterXss().filterUrl(c, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }), Z.createElement("img", {
          className: Re,
          src: globalThis.getFilterXss().filterUrl(s, null, {
            logType: "js.href/src",
            reportOnly: !1
          })
        }))
      }
    )), Je = n(16340), $e = n(9070), et = n(73750), tt = R, nt = tt.commonChannelMenu, rt = tt.channelMenu, ot = tt.commonChannelMenuWithSelfLandingFavoriteCollection, it = tt.commonChannelMenuWithSelfLandingLike, at = (Xe = {},
      (0,
        l.Z)(Xe, I.SelfTabABVal.LandingLike, it()),
      (0,
        l.Z)(Xe, I.SelfTabABVal.LandingFavoriteCollection, ot()),
      Xe), lt = (0,
      l.Z)({
      hot: "trend"
    }, "user_self", "personal_tab"), st = function(e) {
      var t, n, s, u, m, f, p, y, _, k = Z.useState(!1), b = (0,
        a.Z)(k, 2), N = b[0], I = b[1], se = Z.useState(!1), ce = (0,
        a.Z)(se, 2), ue = ce[0], de = ce[1], ve = Z.useState(void 0), fe = (0,
        a.Z)(ve, 2), he = fe[0], pe = fe[1], ge = Z.useState(!1), ye = (0,
        a.Z)(ge, 2), we = ye[0], _e = ye[1], Ee = Z.useState((null == e || null === (t = e.customProps) || void 0 === t ? void 0 : t.isClient) || !1), ke = (0,
        a.Z)(Ee, 1)[0], xe = Z.useRef(null), be = Z.useRef(null), Ne = Z.useRef(null), Te = Z.useRef(null), Ze = Z.useRef(null), Se = function() {
        var e = (0,
          Z.useState)(U.pC.Hide)
          , t = (0,
          a.Z)(e, 2)
          , n = t[0]
          , r = t[1]
          , i = (0,
          Z.useState)(U.CN.Origin)
          , l = (0,
          a.Z)(i, 2)
          , s = l[0]
          , u = l[1]
          , d = (0,
          Z.useState)("")
          , m = (0,
          a.Z)(d, 2)
          , v = m[0]
          , f = m[1]
          , h = (0,
          Z.useState)("")
          , p = (0,
          a.Z)(h, 2)
          , g = p[0]
          , y = p[1]
          , w = (0,
          Z.useState)("")
          , _ = (0,
          a.Z)(w, 2)
          , E = _[0]
          , k = _[1]
          , x = (0,
          Z.useState)("")
          , b = (0,
          a.Z)(x, 2)
          , C = b[0]
          , N = b[1]
          , T = (0,
          Z.useState)("")
          , S = (0,
          a.Z)(T, 2)
          , I = S[0]
          , L = S[1]
          , D = (0,
          Z.useState)("")
          , M = (0,
          a.Z)(D, 2)
          , B = M[0]
          , A = M[1]
          , P = (0,
          Z.useState)("")
          , O = (0,
          a.Z)(P, 2)
          , V = O[0]
          , W = O[1]
          , R = (0,
          Z.useState)("")
          , F = (0,
          a.Z)(R, 2)
          , H = F[0]
          , G = F[1]
          , j = (0,
          Z.useState)("")
          , K = (0,
          a.Z)(j, 2)
          , q = K[0]
          , Y = K[1]
          , X = (0,
          Z.useState)("")
          , z = (0,
          a.Z)(X, 2)
          , Q = z[0]
          , J = z[1]
          , $ = (0,
          Z.useState)("")
          , ee = (0,
          a.Z)($, 2)
          , te = ee[0]
          , ne = ee[1]
          , re = (0,
          Z.useState)("")
          , oe = (0,
          a.Z)(re, 2)
          , ie = oe[0]
          , ae = oe[1]
          , le = (0,
          Z.useState)("")
          , se = (0,
          a.Z)(le, 2)
          , ce = se[0]
          , ue = se[1]
          , de = (0,
          Z.useState)("")
          , me = (0,
          a.Z)(de, 2)
          , ve = me[0]
          , fe = me[1]
          , he = (0,
          Z.useState)("")
          , pe = (0,
          a.Z)(he, 2)
          , ge = pe[0]
          , ye = pe[1]
          , we = (0,
          Z.useState)("")
          , _e = (0,
          a.Z)(we, 2)
          , Ee = _e[0]
          , ke = _e[1]
          , xe = (0,
          Ae.TH)();
        return (0,
          Z.useEffect)((function() {
            (0,
              o.Z)(c().mark((function e() {
                var t, n, o, i, a, l, s, d, m, v, h, p, g, w, _, E, x, b, C;
                return c().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          return e.next = 2,
                            $e.U2({
                              key: et.TccKey.VsSpringEntry,
                              defaultValue: {
                                showType: U.pC.Text,
                                location: U.CN.Origin,
                                imageLight: "",
                                imageDark: "",
                                imageLightHover: "",
                                imageDarkHover: "",
                                animationLight: "",
                                animationDark: "",
                                animationLightV2: "",
                                animationDarkV2: "",
                                miniImageLight: "",
                                miniImageDark: "",
                                miniImageLightHover: "",
                                miniImageDarkHover: "",
                                miniAnimationLight: "",
                                miniAnimationDark: "",
                                miniTextLight: "",
                                miniTextDark: ""
                              }
                            });
                        case 2:
                          C = e.sent,
                            r(null !== (t = C.showType) && void 0 !== t ? t : U.pC.Text),
                            u(null !== (n = C.location) && void 0 !== n ? n : U.CN.Origin),
                            f(null !== (o = C.imageLight) && void 0 !== o ? o : ""),
                            y(null !== (i = C.imageDark) && void 0 !== i ? i : ""),
                            k(null !== (a = C.imageLightHover) && void 0 !== a ? a : ""),
                            N(null !== (l = C.imageDarkHover) && void 0 !== l ? l : ""),
                            Y(null !== (s = C.animationLight) && void 0 !== s ? s : ""),
                            J(null !== (d = C.animationDark) && void 0 !== d ? d : ""),
                            ne(null !== (m = C.animationLightV2) && void 0 !== m ? m : ""),
                            ae(null !== (v = C.animationDarkV2) && void 0 !== v ? v : ""),
                            L(null !== (h = C.miniImageLight) && void 0 !== h ? h : ""),
                            A(null !== (p = C.miniImageDark) && void 0 !== p ? p : ""),
                            W(null !== (g = C.miniImageLightHover) && void 0 !== g ? g : ""),
                            G(null !== (w = C.miniImageDarkHover) && void 0 !== w ? w : ""),
                            ue(null !== (_ = C.miniAnimationLight) && void 0 !== _ ? _ : ""),
                            fe(null !== (E = C.miniAnimationDark) && void 0 !== E ? E : ""),
                            ye(null !== (x = C.miniTextLight) && void 0 !== x ? x : ""),
                            ke(null !== (b = C.miniTextDark) && void 0 !== b ? b : "");
                        case 21:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            )))()
          }
        ), []),
          {
            showType: "/vs" === (null == xe ? void 0 : xe.pathname) ? U.pC.Text : n,
            location: s,
            imageLight: v,
            imageDark: g,
            imageLightHover: E,
            imageDarkHover: C,
            animationLight: q,
            animationDark: Q,
            animationLightV2: te,
            animationDarkV2: ie,
            miniImageLight: I,
            miniImageDark: B,
            miniImageLightHover: V,
            miniImageDarkHover: H,
            miniAnimationLight: ce,
            miniAnimationDark: ve,
            miniTextLight: ge,
            miniTextDark: Ee
          }
      }(), Ie = e.abTestData, Le = e.refEl, De = Z.useMemo((function() {
          var e, t, n = d()(e = []).call(e, (0,
            i.Z)(null !== (t = at[null == Ie ? void 0 : Ie.selfTab]) && void 0 !== t ? t : nt()), [{
            value: "divider"
          }], (0,
            i.Z)((null == Ie ? void 0 : Ie.selfTab) > 0 ? (0,
            R.channelMenuWithSelf)() : rt())), r = v()(n).call(n, (function(e) {
              return e.value === R.NavigationMenuItemVal.Vs
            }
          ))[0];
          if (r && Se.location === U.CN.BelowRecommend && Se.showType !== U.pC.Hide && null != Ie && Ie.vsSpring) {
            var o = v()(n).call(n, (function(e) {
                return e.value !== R.NavigationMenuItemVal.Vs
              }
            ))
              , a = h()(o).call(o, (function(e) {
                return e.value === R.NavigationMenuItemVal.Recommend
              }
            ));
            if (-1 !== a)
              return g()(o).call(o, a + 1, 0, r),
                o
          }
          return n
        }
      ), [null == Ie ? void 0 : Ie.selfTab, Se.location, null == Ie ? void 0 : Ie.vsSpring, Se.showType]);
      Z.useEffect((function() {
          (0,
            o.Z)(c().mark((function e() {
              var t;
              return c().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        return e.next = 2,
                          L.h.getVar({
                            name: "showNewTab",
                            defaultValue: 0
                          });
                      case 2:
                        t = e.sent,
                          pe(t);
                      case 4:
                      case "end":
                        return e.stop()
                    }
                }
              ), e)
            }
          )))()
        }
      ), []);
      var Pe = function(e) {
        var t;
        return null !== (t = lt[e]) && void 0 !== t ? t : e
      };
      Z.useEffect((function() {
          var t = {
            only: "stayVideoTab",
            event: function(t, n) {
              n > 0 && le.Z.sendLog("stayVideoTab", {
                tab_name: Pe(e.current),
                duration: n,
                is_visible: Number(t)
              }, !1)
            }
          };
          B.vP(t)
        }
      ), [e.current]);
      var Oe = Z.useCallback((function(e) {
          var t = e.wheelDelta || -e.detail;
          e.currentTarget.scrollTop += 15 * (t < 0 ? 1 : -1),
            e.preventDefault()
        }
      ), [])
        , Ve = (0,
        D.D)((function() {
          var e, t, n, r;
          we && (((null === (e = Te.current) || void 0 === e || null === (t = e.getBoundingClientRect()) || void 0 === t ? void 0 : t.bottom) || 0) - ((null === (n = xe.current) || void 0 === n || null === (r = n.getBoundingClientRect()) || void 0 === r ? void 0 : r.bottom) || 0) >= 140 ? (I(!0),
          A.i7() || Te.current.addEventListener("mousewheel", Oe)) : I(!1))
        }
      ), 50, {
        leading: !0
      })
        , We = (0,
        D.D)((function() {
          var e, t, n, r, o = (null === (e = Te.current) || void 0 === e || null === (t = e.getBoundingClientRect()) || void 0 === t ? void 0 : t.bottom) || 0, i = ((null === (n = Ne.current) || void 0 === n || null === (r = n.getBoundingClientRect()) || void 0 === r ? void 0 : r.bottom) || 0) - o;
          399.9 <= i && i <= 400.1 ? (de(!0),
          A.i7() || Te.current.removeEventListener("mousewheel", Oe)) : de(!1)
        }
      ), 50, {
        leading: !0
      })
        , Re = (0,
        S.Z)((function(t) {
          var n, r, o, i, a;
          (null != e && null !== (n = e.customProps) && void 0 !== n && n.isSearchSideNav ? window.innerWidth <= 1452 : window.innerWidth <= 1240) || (t.preventDefault(),
            !N || ue && t.deltaY < 0 ? null === (r = be.current) || void 0 === r || null === (o = r.scrollBy) || void 0 === o || o.call(r, 0, t.deltaY) : null === (i = Te.current) || void 0 === i || null === (a = i.scrollBy) || void 0 === a || a.call(i, 0, t.deltaY))
        }
      ))
        , Fe = (0,
        D.D)((function() {
          Ve(),
            We()
        }
      ), 50, {
        leading: !0,
        trailing: !0
      })
        , Ue = Z.useMemo((function() {
          if (he) {
            var e = E()(De).call(De, (function(e) {
                return "channel_300203" === e.value
              }
            ))
              , t = E()(De).call(De, (function(e) {
                return "channel_200204" === e.value
              }
            ))
              , n = E()(De).call(De, (function(e) {
                return "channel_200202" === e.value
              }
            ));
            e.hideTab = !0,
              t.hideTab = !1,
              n.hideTab = !1
          }
          return x()(De).call(De, (function(e) {
              if (e.value === R.NavigationMenuItemVal.Vs) {
                var t;
                if (!P.p() && null !== (t = window.TTE_ENV) && void 0 !== t && t.isMas)
                  return void (e.hideTab = !0);
                if ((null == Ie || !Ie.vsSpring) && Se.showType !== U.pC.Hide)
                  return e.hideTab = !1,
                    e.type = "text",
                    void (e.renderLabel = void 0);
                switch (e.hideTab = Se.showType === U.pC.Hide,
                  Se.showType) {
                  case U.pC.Text:
                    e.type = "text",
                      e.renderLabel = void 0;
                    break;
                  case U.pC.Image:
                  case U.pC.Animation:
                    e.type = "image",
                      e.renderLabel = function() {
                        return Z.createElement(Qe, (0,
                          r.Z)((0,
                          r.Z)({}, Se), {}, {
                          abtest: Ie
                        }))
                      }
                }
              }
            }
          )),
            C()((function() {
                Fe()
              }
            )),
            De
        }
      ), [he, Fe, De, Se, null == Ie ? void 0 : Ie.vsSpring])
        , He = Z.useCallback((0,
        o.Z)(c().mark((function e() {
          var t, n;
          return c().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    n = null !== (t = O.FJ().awemePcClient) && void 0 !== t ? t : "",
                      ke && V.y(n, ">=", "1.2.0") ? _e(!1) : _e(!0);
                  case 2:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      ))), [ke]);
      Z.useEffect((function() {
          He()
        }
      ), [He]),
        Z.useEffect((function() {
            var e;
            return null === (e = Te.current) || void 0 === e || e.addEventListener("wheel", Re),
              function() {
                var e;
                null === (e = Te.current) || void 0 === e || e.removeEventListener("wheel", Re)
              }
          }
        ), []),
        Z.useEffect((function() {
            var e, t, n = function(e) {
              "ArrowDown" !== e.key && "ArrowUp" !== e.key || null == e || e.preventDefault()
            };
            return null === (e = Te.current) || void 0 === e || e.setAttribute("tabindex", 0),
            null === (t = Te.current) || void 0 === t || t.addEventListener("keydown", n),
              window.addEventListener("resize", Fe),
              function() {
                var e;
                null === (e = Te.current) || void 0 === e || e.removeEventListener("keydown", n),
                  window.removeEventListener("resize", Fe)
              }
          }
        ), []);
      var Ge = (0,
        Je.Z)()
        , je = Ge.specTheme
        , Ke = Ge.isDark
        , qe = Z.useMemo((function() {
          return null != je && je.themeFurtherSwitch ? {
            backgroundImage: "url(".concat(Ke ? null == je ? void 0 : je.siderDark : null == je ? void 0 : je.siderLight, ")")
          } : {}
        }
      ), [je, Ke]);
      return Z.createElement("div", {
        className: T()(G, null == e ? void 0 : e.className, (0,
          l.Z)({}, ie, null == e || null === (n = e.customProps) || void 0 === n ? void 0 : n.isSearchSideNav)),
        ref: function(e) {
          Le && (Le.current = e)
        }
      }, Z.createElement("div", {
        className: T()(K, (m = {},
          (0,
            l.Z)(m, Y, null == e || null === (s = e.customProps) || void 0 === s ? void 0 : s.isLogoFixed),
          (0,
            l.Z)(m, q, ke),
          (0,
            l.Z)(m, X, null == e || null === (u = e.customProps) || void 0 === u ? void 0 : u.isSearchLogoFixed),
          (0,
            l.Z)(m, j, null == e ? void 0 : e.needGrayscale),
          m))
      }, !(ke && "Mac" === (null == e || null === (f = e.customProps) || void 0 === f || null === (p = f.os) || void 0 === p ? void 0 : p.os)) && Z.createElement("div", {
        ref: Ze,
        className: T()(z)
      }, Z.createElement(me.a, {
        href: globalThis.getFilterXss().filterUrl(W.kj(), null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: Q,
        onClick: function() {
          le.Z.sendLog("clickAwemeLogo", {
            enter_from: M.yW()
          })
        }
      }))), Z.createElement("div", {
        "data-e2e": "douyin-navigation",
        className: T()(J, $, (0,
          l.Z)({}, j, null == e ? void 0 : e.needGrayscale)),
        onScroll: We,
        style: qe,
        ref: Te
      }, Z.createElement("div", {
        className: T()(ee, (y = {},
          (0,
            l.Z)(y, $, ue || !we),
          (0,
            l.Z)(y, te, null == je ? void 0 : je.themeFurtherSwitch),
          y)),
        onScroll: Ve,
        ref: be
      }, Z.createElement("div", {
        className: T()(ne, (_ = {},
          (0,
            l.Z)(_, oe, !we),
          (0,
            l.Z)(_, re, A.vU()),
          _)),
        ref: xe
      }, Z.createElement(Me, (0,
        r.Z)((0,
        r.Z)({}, e), {}, {
        onChange: function(t, n) {
          var r, o, i = M.yW(), a = i.match(F.PH) ? i : "";
          null !== (r = location) && void 0 !== r && null !== (o = r.pathname) && void 0 !== o && w()(o).call(o, "/search") && (a = "search_result"),
            le.Z.sendLog("enterVideoTab", {
              tab_name: Pe(t),
              previous_page: a
            }),
            (0,
              Be.b)(),
          e.onChange && e.onChange(t, n)
        },
        className: e.className,
        list: Ue,
        customProps: null == e ? void 0 : e.customProps
      })))), we && Z.createElement("div", {
        className: T()(H, (0,
          l.Z)({}, ae, null == je ? void 0 : je.themeFurtherSwitch)),
        ref: Ne
      }, Z.createElement(Ce, {
        specTheme: je
      }))))
    }
  }
  ,
  96608: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = new (n(37485).hD)({
      enterVideoTab: {
        eventName: "enter_video_tab",
        params: {
          tab_name: "",
          previous_page: ""
        }
      },
      stayVideoTab: {
        eventName: "stay_video_tab",
        params: {
          tab_name: "",
          duration: 0,
          is_visible: 1
        }
      },
      clickMoreTab: {
        eventName: "click_more_tab",
        params: {}
      },
      navigationBarExpand: {
        eventName: "navigation_bar_expand",
        params: {
          enter_from: ""
        }
      },
      navigationBarFold: {
        eventName: "navigation_bar_fold",
        params: {
          enter_from: ""
        }
      },
      clickAwemeLogo: {
        eventName: "click_aweme_logo",
        params: {
          enter_from: ""
        }
      }
    })
  }
  ,
  95881: (e,t,n)=>{
    n.d(t, {
      i: ()=>l
    });
    var r = n(44503);
    const o = "HWiSubLL";
    var i = n(79705)
      , a = n.n(i);
    function l(e) {
      var t = e || {}
        , n = t.style
        , i = t.className
        , l = void 0 === i ? "" : i;
      return r.createElement("div", {
        className: a()(o, l),
        style: n
      })
    }
  }
  ,
  63805: (e,t,n)=>{
    n.d(t, {
      $: ()=>B
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(5594)
      , a = n.n(i)
      , l = n(9120)
      , s = n.n(l)
      , c = n(92012)
      , u = n.n(c)
      , d = n(80051)
      , m = n.n(d)
      , v = n(94610)
      , f = n.n(v)
      , h = n(44503)
      , p = n(79705)
      , g = n.n(p)
      , y = n(46989)
      , w = n(41150)
      , _ = [{
      url: "https://www.oceanengine.com/resource/douyin?source=douyin-pc",
      title: "\u5e7f\u544a\u6295\u653e"
    }, {
      url: "https://www.douyin.com/agreements/?id=6773906068725565448",
      title: "\u7528\u6237\u670d\u52a1\u534f\u8bae"
    }, {
      url: "https://www.douyin.com/agreements/?id=6773901168964798477",
      title: "\u9690\u79c1\u653f\u7b56"
    }, {
      url: "https://www.douyin.com/recovery_account/",
      title: "\u8d26\u53f7\u627e\u56de"
    }, {
      url: "https://www.douyin.com/aboutus/#contact",
      title: "\u8054\u7cfb\u6211\u4eec"
    }, {
      url: "https://www.douyin.com/aboutus/#join",
      title: "\u52a0\u5165\u6211\u4eec"
    }, {
      url: "https://www.douyin.com/business_license/",
      title: "\u8425\u4e1a\u6267\u7167"
    }, {
      url: "https://www.douyin.com/friend_links",
      title: "\u53cb\u60c5\u94fe\u63a5"
    }, {
      url: "https://www.douyin.com/htmlmap/hotauthor_0_1",
      title: "\u7ad9\u70b9\u5730\u56fe"
    }, {
      url: "https://www.douyin.com/downloadpage",
      title: "\u4e0b\u8f7d\u6296\u97f3"
    }, {
      url: "https://mix.jinritemai.com/falcon/mix_page/index.html?__live_platform__=webcast&allowMediaAutoPlay=1&enter_from=others&hide_nav_bar=1&hide_system_video_poster=1&id=7117178766052294949&origin_type=others&should_full_screen=1&trans_status_bar=1&ttwebview_extension_mixrender=1&hide_nav_bar=1&should_full_screen=1&trans_status_bar=1&web_bg_color=#ffffffff",
      title: "\u6296\u97f3\u7535\u5546"
    }]
      , E = [[{
      url: "https://www.piyao.org.cn/yybgt/index.htm",
      title: "\u7f51\u7edc\u8c23\u8a00\u66dd\u5149\u53f0 \uff5c "
    }, {
      url: "https://www.12377.cn/",
      title: "\u7f51\u4e0a\u6709\u5bb3\u4fe1\u606f\u4e3e\u62a5"
    }, {
      title: "\uff5c \u8fdd\u6cd5\u548c\u4e0d\u826f\u4fe1\u606f\u4e3e\u62a5\uff1a400-140-2108 \uff5c \u9752\u5c11\u5e74\u5b88\u62a4\u4e13\u7ebf\uff1a400-9922-556 \uff5c \u7b97\u6cd5\u63a8\u8350\u4e13\u9879\u4e3e\u62a5\uff1asfjubao@bytedance.com \uff5c \u7f51\u7edc\u5185\u5bb9\u4ece\u4e1a\u4eba\u5458\u8fdd\u6cd5\u8fdd\u89c4\u884c\u4e3a\u4e3e\u62a5\uff1afeedback@douyin.com"
    }], [{
      url: "https://beian.miit.gov.cn/",
      title: "\u4eacICP\u590716016397\u53f7-3"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/jiemuzhizuojingying.jpeg",
      title: " \uff5c \u5e7f\u64ad\u7535\u89c6\u8282\u76ee\u5236\u4f5c\u7ecf\u8425\u8bb8\u53ef\u8bc1"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/zengzhixuke.jpeg",
      title: " \uff5c \u4eacB2-20170846"
    }, {
      url: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/wangluowenhuajingying.jpeg",
      title: " \uff5c \u7f51\u7edc\u6587\u5316\u8bb8\u53ef\u8bc1-\u4eac\u7f51\u6587-\uff082022\uff090938-030\u53f7 \uff5c "
    }, {
      icon: "//p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/emblem.png",
      url: "http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11000002002046",
      title: "\u4eac\u516c\u7f51\u5b89\u5907 11000002002046\u53f7"
    }]];
    const k = "VRcJSlv6"
      , x = "uy0xcb2o"
      , b = "Es34a3Bm"
      , C = "JXaUfgsM"
      , N = "cHlCoDpR"
      , T = "OqamRr48"
      , Z = "WltbFpmM"
      , S = "SBRU08_v"
      , I = "FipJiH3x"
      , L = "RWEDYsSQ";
    var D, M = n(26637);
    function B(e) {
      var t = e.theme
        , n = e.linkItems
        , i = e.subLinkItems
        , l = e.innerLink
        , c = void 0 === l ? [] : l
        , d = e.showInnerLink
        , v = void 0 === d || d
        , p = e.className
        , B = (0,
        h.useState)((function() {
          return null == c ? void 0 : s()(c).call(c, (function(e, t) {
              return u()(e).call(e, null == t ? void 0 : t.links)
            }
          ), [])
        }
      ))
        , A = (0,
        o.Z)(B, 2)
        , P = A[0]
        , O = A[1]
        , V = ((0,
        M.o)().isHorizontalLayout,
      n || _)
        , W = i || E;
      return (0,
        h.useEffect)((function() {
          var e = null == c ? void 0 : s()(c).call(c, (function(e, t) {
              return u()(e).call(e, null == t ? void 0 : t.links)
            }
          ), [])
            , t = !1;
          return null != e && e.length || !v || (0,
            r.Z)(a().mark((function e() {
              var n, r, i, l, c, d, v, h, p, g;
              return a().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        return e.next = 2,
                          m().all([(0,
                            w.Ws)(), (0,
                            w.F8)()]);
                      case 2:
                        i = e.sent,
                          l = (0,
                            o.Z)(i, 2),
                          c = l[0],
                          d = l[1],
                          v = 0 === (null == c ? void 0 : c.statusCode) ? null == c ? void 0 : c.data : [],
                          h = 0 === (null == d ? void 0 : d.statusCode) ? [{
                            links: null == d || null === (n = d.data) || void 0 === n || null === (r = f()(n)) || void 0 === r ? void 0 : r.call(n, (function(e) {
                                return {
                                  url: null == e ? void 0 : e.url,
                                  anchor: null == e ? void 0 : e.keyword
                                }
                              }
                            ))
                          }] : [],
                        t || (g = s()(p = u()(v).call(v, h)).call(p, (function(e, t) {
                            return u()(e).call(e, null == t ? void 0 : t.links)
                          }
                        ), []),
                          O(g));
                      case 9:
                      case "end":
                        return e.stop()
                    }
                }
              ), e)
            }
          )))(),
            function() {
              t = !0
            }
        }
      ), []),
        h.createElement("footer", {
          className: g()(D[t], p)
        }, h.createElement("div", {
          className: k
        }, h.createElement("div", {
          className: x
        }, Boolean(V.length) && f()(V).call(V, (function(e, t) {
            return h.createElement("div", {
              className: b,
              key: t
            }, h.createElement("a", {
              href: globalThis.getFilterXss().filterUrl(e.url, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              target: "_blank",
              rel: "noopener noreferrer".concat(y.P(e.title))
            }, e.title))
          }
        ))), Boolean(W.length) && f()(W).call(W, (function(e, t) {
            return h.createElement("div", {
              key: "group_".concat(t),
              className: C
            }, Boolean(e.length) && f()(e).call(e, (function(e, t) {
                return h.createElement("div", {
                  className: N,
                  key: t
                }, e.icon && h.createElement("img", {
                  className: T,
                  src: globalThis.getFilterXss().filterUrl(e.icon, null, {
                    logType: "js.href/src",
                    reportOnly: !1
                  }),
                  alt: "icon"
                }), e.url ? h.createElement("a", {
                  href: globalThis.getFilterXss().filterUrl(e.url, null, {
                    logType: "js.href/src",
                    reportOnly: !1
                  }),
                  target: "_blank",
                  rel: "noopener noreferrer nofollow"
                }, e.title) : h.createElement("span", null, e.title))
              }
            )))
          }
        )), Boolean(P.length) && v && h.createElement("div", {
          className: Z
        }, h.createElement("span", {
          className: S
        }), h.createElement("span", {
          className: I
        }, "\u70ed\u95e8\uff1a"), f()(P).call(P, (function(e) {
            return h.createElement("span", {
              className: L,
              key: e.url
            }, h.createElement("a", {
              href: globalThis.getFilterXss().filterUrl(e.url, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              target: "_blank",
              rel: "noopener noreferrer"
            }, e.anchor))
          }
        )))))
    }
    !function(e) {
      e.light = "isLight",
        e.dark = "isDark"
    }(D || (D = {}))
  }
  ,
  47285: (e,t,n)=>{
    n.d(t, {
      z: ()=>D,
      g: ()=>L
    });
    var r, o = n(44503), i = n(78867), a = n(66231);
    function l() {
      return l = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        l.apply(this, arguments)
    }
    const s = function(e) {
      return o.createElement("svg", l({
        width: 12,
        height: 12,
        viewBox: "0 0 12 12",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = o.createElement("path", {
        d: "M5.255.695c.258-.66 1.232-.66 1.49 0L7.91 3.68l3.327.14c.735.03 1.036.918.46 1.356L9.092 7.16l.89 3.072c.197.679-.592 1.227-1.205.839L6 9.31l-2.777 1.76c-.613.388-1.402-.16-1.205-.839l.89-3.072L.3 5.176C-.274 4.738.027 3.85.761 3.82l3.328-.14L5.255.695z",
        fill: "#000"
      })))
    };
    var c;
    function u() {
      return u = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        u.apply(this, arguments)
    }
    const d = function(e) {
      return o.createElement("svg", u({
        width: 16,
        height: 15,
        viewBox: "0 0 16 15",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), c || (c = o.createElement("path", {
        d: "M7.103.557a1 1 0 011.794 0l1.05 2.129a3 3 0 002.259 1.64l2.348.342a1 1 0 01.555 1.706l-1.7 1.656a3 3 0 00-.863 2.655l.402 2.34a1 1 0 01-1.451 1.054l-2.101-1.105a3 3 0 00-2.792 0l-2.1 1.105a1 1 0 01-1.452-1.055l.402-2.338A3 3 0 002.59 8.03L.89 6.374a1 1 0 01.555-1.706l2.348-.341a3 3 0 002.259-1.641L7.103.557z",
        fill: "#FFC122"
      })))
    };
    var m;
    function v() {
      return v = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        v.apply(this, arguments)
    }
    const f = function(e) {
      return o.createElement("svg", v({
        width: 7,
        height: 8,
        viewBox: "0 0 7 8",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), m || (m = o.createElement("path", {
        clipRule: "evenodd",
        d: "M3.893 4.5v2.893h-1V4.5H0v-1h2.893V.607h1V3.5h2.892v1H3.893z"
      })))
    }
      , h = "WvriN2FJ"
      , p = "tojlKG5g"
      , g = "_MH4WNqd"
      , y = "_GBtL6gp"
      , w = "m0IxXQmQ"
      , _ = "jFKE9ldv"
      , E = "LWqS0cLw"
      , k = "q_a7MQn1"
      , x = "gLBz9LCQ"
      , b = "Dr88hd68"
      , C = "Px9YAX9F"
      , N = "YOxtKc6u";
    var T = n(52255)
      , Z = n(51382)
      , S = n(12164)
      , I = a.Q() ? "command" : "ctrl"
      , L = (0,
      o.memo)((function(e) {
        var t = e.collectionGuideType
          , n = (void 0 === t ? i.CollectionGuide.StressShortcut : t) === i.CollectionGuide.StressCollect;
        return o.createElement("div", {
          className: p
        }, o.createElement("div", {
          className: g
        }, o.createElement("div", {
          className: E
        }, o.createElement("span", {
          className: k
        }, "\u6536\u85cf\u7f51\u9875\u770b\u6296\u97f3\u89c6\u9891\u66f4\u65b9\u4fbf "), o.createElement("span", {
          className: x
        }, "\u201c", I, "+D\u201d\u6216 \u70b9\u51fb\u6d4f\u89c8\u5668\u201c\u6536\u85cf\u6309\u94ae\ufe0f\u201d ")), o.createElement("div", {
          className: y
        }, n ? o.createElement("div", {
          className: b
        }, o.createElement("span", {
          className: C
        }, "www.douyin.com"), o.createElement(T.Z, {
          src: globalThis.getFilterXss().filterUrl(d, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 16,
          height: 15,
          viewBox: "0 0 16 15"
        })) : o.createElement("div", {
          className: w
        }, o.createElement("div", {
          className: _
        }, I), o.createElement(T.Z, {
          className: N,
          src: globalThis.getFilterXss().filterUrl(f, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 7,
          height: 8,
          viewBox: "0 0 7 8"
        }), o.createElement("div", {
          className: _
        }, "D")))))
      }
    ))
      , D = (0,
      o.memo)((function(e) {
        var t = e.collectionGuideType
          , n = void 0 === t ? i.CollectionGuide.StressShortcut : t
          , r = e.isLogin
          , a = e.uid
          , l = e.activityName
          , c = e.transparent
          , u = (0,
          S.s)(a, r)
          , d = u.onClick
          , m = u.badgeVisible
          , v = u.collectionPanelVisible
          , f = u.onCollectionGuideEnter
          , p = u.onCollectionGuideLeave;
        return o.createElement(Z.Y, {
          type: "circleButtonWithText",
          badge: "round",
          text: "\u6536\u85cf\u7f51\u9875",
          icon: s,
          iconHeight: 12,
          iconWidth: 12,
          viewBox: "0 0 12 12",
          onMouseEnter: f,
          onMouseLeave: p,
          onClick: d,
          showBadge: m,
          activityName: l,
          transparent: c
        }, v && o.createElement("div", {
          className: h
        }, o.createElement(L, {
          collectionGuideType: n
        })))
      }
    ))
  }
  ,
  80714: (e,t,n)=>{
    n.d(t, {
      p: ()=>l
    });
    var r = n(44503)
      , o = n(95127)
      , i = n(92557)
      , a = n(9988)
      , l = function(e) {
      var t = e.children
        , n = e.headerPopupName
        , l = (0,
        a.U)({
        enterDelay: 100,
        leaveDelay: 200,
        onMouseEnter: function() {
          o.YY.replaceCurrentTask({
            id: o.BE.HoverTaskId,
            priority: o.T0.HoverPriority,
            isBlock: !0
          }),
          n && i.emit(i.EVENT.showHeaderPopUp, {
            type: n,
            isShow: !0
          })
        },
        onMouseLeave: function() {
          o.YY.finishTask(o.BE.HoverTaskId)
        }
      })
        , s = l.onMouseEnter
        , c = l.onMouseLeave;
      return r.createElement("div", {
        onMouseEnter: s,
        onMouseLeave: c
      }, t)
    }
  }
  ,
  51382: (e,t,n)=>{
    n.d(t, {
      Y: ()=>k
    });
    var r = n(30906)
      , o = n(65146)
      , i = n(92012)
      , a = n.n(i)
      , l = n(94610)
      , s = n.n(l)
      , c = n(44503)
      , u = n(79705)
      , d = n.n(u)
      , m = n(53850)
      , v = n(13079)
      , f = n(92557);
    const h = {
      circleButtonWrapper: "gVAgxPt4",
      circleButtonWithText: "q7itrkcz",
      textBadge: "eWId3EeD",
      roundBadge: "CPQ46DEr",
      circleButtonWithTextRoundBadge: "ATU7pfeV",
      circleButton: "XyCeQKrx",
      circleButtonAvatar: "HfOiEY9W",
      activity: "BYWQkd_k",
      iconContainer: "ErRR3mNa",
      vsTransMode: "tBOngNBR",
      transparent: "KakDUzX5",
      iconSvg: "lG5TmBA_",
      text: "ck1_UmL3",
      imageBadge: "Zqqn054W",
      circleButtonNoTextImageBadge: "KdFLVILi",
      circleButtonWithTextImageBadge: "PRw67Cxk",
      themeSwitch: "Os_brk6Y",
      dropdownContainer: "hipNfQvh",
      active: "OLBujdZM",
      shadowChange: "UyPtgm0l",
      overflowChange: "vaPb40TJ",
      dropDownListInCenterChange: "iL8wmqWL",
      textLinkALink: "F_Jaoez_",
      conversationDtailAnimationKeyframes: "dVesF2gU",
      dropDownListInNoCenterChange: "wZr_ore7",
      showDeleteAllMessageModal: "Pjo5kCGk",
      dropDownListInNoCenterLeftTopChange: "d9lHvYy5",
      dropDownListOutChange: "ipS33FS1"
    };
    var p = n(69234)
      , g = n(52255)
      , y = n(26395)
      , w = n(16340)
      , _ = n(14001);
    function E(e) {
      var t, n, r, i, l, s, u, m = e.className, p = e.avatarUrl, E = e.text, k = e.avatarHeight, x = e.avatarWidth, b = e.badge, C = e.badgeText, N = e.onMouseEnter, T = e.onMouseLeave, Z = e.onMouseOver, S = e.onMouseOut, I = e.onClick, L = e.viewBox, D = e.activityName, M = e.badgeIconSvg, B = e.badgeIconHeight, A = e.badgeIconWidth, P = e.badgeIconViewbox, O = e.headerPopupName, V = e.circleButtonContainerClassName, W = e.children, R = e.svgContainerClassName, F = e.showBadge, U = void 0 !== F && F, H = e.url, G = e.downloadAttr, j = e.target, K = e.transparent, q = e.icon, Y = e.iconHeight, X = e.iconWidth;
      q = null !== (t = q) && void 0 !== t ? t : p,
        X = null !== (n = X) && void 0 !== n ? n : x,
        Y = null !== (r = Y) && void 0 !== r ? r : k;
      var z = (0,
        y.P)({
        delayShow: 100
      })
        , Q = (z.type,
        z.changeType);
      (0,
        c.useEffect)((function() {
          var e = f.listen(f.EVENT.showHeaderPopUp, (function(e) {
              O === e.type && !1 === e.isShow && Q()
            }
          ));
          return function() {
            return e()
          }
        }
      ), [O]);
      var J = (0,
        c.useMemo)((function() {
          var e;
          return c.createElement(g.Z, {
            src: globalThis.getFilterXss().filterUrl(q, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            width: X,
            height: Y,
            viewBox: L || a()(e = "0 0 ".concat(X, " ")).call(e, Y),
            className: h.iconSvg
          })
        }
      ), [q, X, Y, L])
        , $ = (0,
        w.Z)().specTheme;
      return c.createElement("div", {
        className: d()(h.circleButtonWrapper, V),
        onMouseEnter: function(e) {
          null == N || N(e)
        },
        onMouseLeave: function(e) {
          null == T || T(e)
        },
        onMouseOver: function(e) {
          null == Z || Z(e)
        },
        onMouseOut: function(e) {
          null == S || S(e)
        }
      }, H && c.createElement(_.a, {
        href: globalThis.getFilterXss().filterUrl(H, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        download: G,
        target: j,
        onClick: I,
        className: d()(h.circleButton, h.circleButtonWithText, (i = {
          isDark: Boolean(D) || K
        },
          (0,
            o.Z)(i, h.activity, Boolean(D) || K),
          (0,
            o.Z)(i, null == h ? void 0 : h[D], D),
          (0,
            o.Z)(i, h.transparent, K),
          i), m)
      }, c.createElement("div", {
        className: h.iconContainer
      }, J), c.createElement("p", {
        className: h.text
      }, E)), !H && c.createElement("div", {
        onClick: I,
        className: d()(h.circleButton, h.circleButtonWithText, (l = {
          isDark: Boolean(D) || K
        },
          (0,
            o.Z)(l, h.activity, Boolean(D) || K),
          (0,
            o.Z)(l, null == h ? void 0 : h[D], D),
          (0,
            o.Z)(l, h.transparent, K),
          l), m),
        "data-e2e": "something-button"
      }, c.createElement("div", {
        className: h.iconContainer
      }, J), c.createElement("p", {
        className: h.text
      }, E)), U && ("text" === b || "round" === b) && c.createElement(v.C, {
        className: d()((s = {},
          (0,
            o.Z)(s, h.textBadge, "text" === b),
          (0,
            o.Z)(s, h.roundBadge, "round" === b),
          (0,
            o.Z)(s, h.circleButtonWithTextRoundBadge, "round" === b),
          s)),
        type: b,
        text: "text" === b ? C || E : ""
      }), U && "image" === b && c.createElement("div", {
        className: d()(h.imageBadge, R, h.circleButtonWithTextImageBadge, (0,
          o.Z)({}, h.themeSwitch, null == $ ? void 0 : $.themeSwitch))
      }, c.createElement(g.Z, {
        src: globalThis.getFilterXss().filterUrl(M, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: A,
        height: B,
        viewBox: P || a()(u = "0 0 ".concat(A, " ")).call(u, B)
      })), W)
    }
    var k = (0,
      c.memo)((function e(t) {
        var n = t.type
          , i = t.className
          , a = t.trigger
          , l = t.items
          , u = t.onMouseEnter
          , v = t.onMouseLeave
          , g = t.onMouseOver
          , w = t.onMouseOut
          , _ = t.children
          , k = t.itemsContainerClassName
          , x = t.headerPopupName
          , b = (0,
          y.P)({
          delayDisappear: 200,
          delayShow: 100
        })
          , C = b.type
          , N = b.changeType
          , T = (0,
          c.useCallback)((function(e) {
            "hover" === a && N("active"),
            null == u || u(e)
          }
        ), [a, u, N])
          , Z = (0,
          c.useCallback)((function(e) {
            "hover" === a && N(),
            null == v || v(e)
          }
        ), [a, v, N])
          , S = (0,
          c.useCallback)((function(e) {
            return null == g ? void 0 : g(e)
          }
        ), [g])
          , I = (0,
          c.useCallback)((function(e) {
            return null == w ? void 0 : w(e)
          }
        ), [w])
          , L = (0,
          c.useMemo)((function() {
            var t;
            return "hover" === a && l && l.length ? c.createElement("div", {
              className: d()(h.dropdownContainer, (t = {},
                (0,
                  o.Z)(t, h.active, Boolean(C)),
                (0,
                  o.Z)(t, k, Boolean(C && void 0 !== k)),
                t))
            }, c.createElement("ul", {
              "data-e2e": "cooperate-list"
            }, s()(l).call(l, (function(t) {
                return c.createElement("li", {
                  key: t.key || t.text
                }, c.createElement(e, (0,
                  r.Z)({}, t)))
              }
            )))) : []
          }
        ), [l, a, C, k]);
        (0,
          c.useEffect)((function() {
            return x && f.listen(f.EVENT.showHeaderPopUp, (function(e) {
                "active" === C && e.type !== x && e.isShow && N("", !0)
              }
            ))
          }
        ), [N, C, x]);
        var D = (0,
          m.Z)(C);
        return (0,
          c.useEffect)((function() {
            D !== C && x && f.emit(f.EVENT.showHeaderPopUp, {
              type: x,
              isShow: Boolean(C)
            })
          }
        ), [C, x, D]),
          c.createElement(c.Fragment, null, "textLink" !== n && c.createElement(E, (0,
            r.Z)({}, (0,
            r.Z)((0,
            r.Z)({}, t), {}, {
            className: i,
            onMouseEnter: T,
            onMouseLeave: Z,
            onMouseOver: S,
            onMouseOut: I
          })), L, _), "textLink" === n && c.createElement("div", null, c.createElement(p.h, (0,
            r.Z)({}, (0,
            r.Z)((0,
            r.Z)({}, t), {}, {
            className: i,
            onMouseEnter: T,
            onMouseLeave: Z,
            onMouseOver: S,
            onMouseOut: I,
            aLinkStyle: h.textLinkALink
          })), L, _)))
      }
    ))
  }
  ,
  66470: (e,t,n)=>{
    n.d(t, {
      H: ()=>O
    });
    var r = n(30673)
      , o = n(32781)
      , i = n(92012)
      , a = n.n(i)
      , l = n(88438)
      , s = n.n(l)
      , c = n(92637)
      , u = n.n(c)
      , d = n(67827)
      , m = n.n(d)
      , v = n(21805)
      , f = n.n(v)
      , h = n(94610)
      , p = n.n(h)
      , g = n(44503)
      , y = n(89176)
      , w = n(25083)
      , _ = n(92557)
      , E = n(64644)
      , k = n(61936);
    const x = "EAnZYE_A"
      , b = "wl54lwxY"
      , C = "vT3pEATX"
      , N = "lhN14CeY"
      , T = "KFtP7bgM"
      , Z = "FUBL0LO9"
      , S = "Qqv8ONZm"
      , I = "XVAncFKz";
    var L;
    function D() {
      return D = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        D.apply(this, arguments)
    }
    const M = function(e) {
      return g.createElement("svg", D({
        width: 20,
        height: 20,
        viewBox: "0 0 20 20",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), L || (L = g.createElement("path", {
        d: "M13.667 13.667a.757.757 0 01-1.07 0l-2.32-2.32-2.318 2.32a.757.757 0 01-1.07-1.07l2.318-2.32-2.319-2.319a.757.757 0 111.07-1.07l2.32 2.319 2.319-2.32a.757.757 0 111.07 1.071l-2.319 2.32 2.32 2.318a.757.757 0 010 1.07z"
      })))
    };
    var B = n(81767)
      , A = n(52255)
      , P = (0,
      g.memo)((function(e) {
        var t = e.liveInfo
          , n = e.onClose
          , r = t || {}
          , o = r.id
          , i = r.imageUrl
          , l = r.title
          , c = r.text
          , u = r.webRid
          , d = r.roomId
          , m = r.anchorId
          , v = (0,
          g.useRef)()
          , f = w.yW()
          , h = (0,
          y.Z)((function() {
            v.current = s()((function() {
                n(o)
              }
            ), 1e4)
          }
        ));
        return (0,
          g.useEffect)((function() {
            k.i.sendLog("appointmentPushShow", {
              enter_from: f,
              room_id: d,
              anchor_id: m
            })
          }
        ), []),
          (0,
            g.useEffect)((function() {
              return h(),
                function() {
                  clearTimeout(v.current)
                }
            }
          ), []),
          g.createElement("div", {
            className: x,
            onMouseEnter: function() {
              clearTimeout(v.current)
            },
            onMouseLeave: function() {
              v.current = s()((function() {
                  n(o)
                }
              ), 1e4)
            }
          }, g.createElement("div", {
            className: b,
            onClick: function() {
              var e;
              k.i.sendLog("appointmentPushClick", {
                enter_from: f,
                room_id: d,
                anchor_id: m
              }),
                window.open(a()(e = "https://live.douyin.com/".concat(u, "?enter_from_merge=")).call(e, f, "&enter_method=inner_push"), "_blank")
            }
          }, g.createElement("div", {
            className: C
          }, g.createElement(B.n, {
            type: "push",
            src: globalThis.getFilterXss().filterUrl(i, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            liveRoomUrl: "",
            onClick: function(e) {
              return e.preventDefault()
            }
          })), g.createElement("div", {
            className: N
          }, g.createElement("div", {
            className: T
          }, l), c && g.createElement("div", {
            className: Z
          }, c)), g.createElement("div", {
            className: S
          }, g.createElement("span", null, "\u53bb\u770b\u770b"))), g.createElement(A.Z, {
            onClick: function() {
              n(o)
            },
            className: I,
            src: globalThis.getFilterXss().filterUrl(M, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            width: 20,
            height: 20,
            viewBox: "0 0 20 20"
          }))
      }
    ))
      , O = function() {
      var e = (0,
        g.useState)([])
        , t = (0,
        o.Z)(e, 2)
        , n = t[0]
        , i = t[1]
        , l = function(e) {
        i((function(t) {
            return null == t ? void 0 : u()(t).call(t, (function(t) {
                return (null == t ? void 0 : t.id) !== e
              }
            ))
          }
        ))
      };
      return (0,
        g.useEffect)((function() {
          var e = _.listen(_.EVENT.webLivePushMessage, (function(e) {
              var t;
              null != e && e.imageUrl && null != e && e.text && null != e && e.title && null != e && e.webRid ? f()(t = location.href).call(t, "live.douyin.com/".concat(null == e ? void 0 : e.webRid)) || i((function(t) {
                  var n;
                  return a()(n = [e]).call(n, (0,
                    r.Z)(t))
                }
              )) : E.oe.event.error({
                name: E.Mo.LivePushMessageError,
                report: {
                  message: m()(e)
                }
              })
            }
          ));
          return function() {
            e()
          }
        }
      ), []),
        g.createElement("div", null, p()(n).call(n, (function(e) {
            return g.createElement(P, {
              key: null == e ? void 0 : e.id,
              liveInfo: e,
              onClose: l
            })
          }
        )))
    }
  }
  ,
  69234: (e,t,n)=>{
    n.d(t, {
      h: ()=>w,
      j: ()=>T
    });
    var r = n(65146)
      , o = n(32781)
      , i = n(92012)
      , a = n.n(i)
      , l = n(44503)
      , s = n(79705)
      , c = n.n(s)
      , u = n(36539)
      , d = n(4592)
      , m = n(46989)
      , v = n(83346)
      , f = n(13079)
      , h = n(90147);
    const p = {
      hoverBold: "bhpixfNG",
      aLinkWrapper: "OMlv_Xup",
      badge: "QIJri12p",
      activity: "qm891520",
      vsTransMode: "oTbgb08Q",
      childrenContainer: "nkKKNGny"
    };
    var g = n(14001)
      , y = "\u5f00\u64ad\u5b9e\u65f6\u6570\u636e";
    function w(e) {
      var t, i = e.className, s = e.onClick, v = e.isLogin, h = e.url, w = e.text, _ = e.clickToLogin, E = e.loginSuccess, k = e.onMouseEnter, x = e.onMouseLeave, b = e.onMouseOver, C = e.onMouseOut, N = e.loginHeaderText, T = e.jumpAfterLogin, Z = e.loginEventParams, S = e.badge, I = e.activityName, L = e.aLinkStyle, D = e.children, M = e.childrenContainerClassName, B = e.downloadAttr, A = e.target, P = (e.key,
        (0,
          l.useState)(!0)), O = (0,
        o.Z)(P, 2), V = O[0], W = O[1], R = function(e) {
        var t, r, o = null == s ? void 0 : s(e);
        _ && !1 === v && (n.e(1674).then(n.bind(n, 61674)).then((function(e) {
            var t, n, r;
            (0,
              e.navShowAccount)({
              success: function() {
                T && window.open(h, "_blank"),
                null == E || E()
              },
              enterMethod: "navigation_bar",
              next: a()(t = "".concat(null == u ? void 0 : d.tJ)).call(t, null === (n = window) || void 0 === n || null === (r = n.location) || void 0 === r ? void 0 : r.host),
              headerText: N,
              teaEvtParams: Z
            })
          }
        )),
        null == e || null === (r = e.preventDefault) || void 0 === r || r.call(e));
        return !h && (null == e || null === (t = e.preventDefault) || void 0 === t || t.call(e)),
          o
      }, F = ["noopener", m.P(w)];
      return w !== y && F.push("noreferrer"),
        l.createElement("div", {
          onMouseEnter: function(e) {
            null == k || k(e)
          },
          onMouseLeave: function(e) {
            null == x || x(e)
          },
          onMouseOver: function(e) {
            W(!1),
            null == b || b(e)
          },
          onMouseOut: function(e) {
            null == C || C(e)
          },
          className: c()(p.aLinkWrapper, p.hoverBold, i, (t = {
            isDark: Boolean(I)
          },
            (0,
              r.Z)(t, p.activity, Boolean(I)),
            (0,
              r.Z)(t, null == p ? void 0 : p[I], I),
            t))
        }, h ? l.createElement(g.a, {
          target: A || "_blank",
          rel: F.join(" "),
          href: globalThis.getFilterXss().filterUrl(h, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          onClick: R,
          className: L,
          download: B,
          "data-e2e": "alink-item"
        }, w) : l.createElement("span", {
          className: L,
          onClick: R
        }, w), V && ("round" === S || "text" === S) && l.createElement(f.C, {
          className: p.badge,
          type: S
        }), l.createElement("div", {
          className: c()(p.childrenContainer, M)
        }, D))
    }
    var _ = {
      key: "doubi_recharge",
      text: "\u6296\u5e01\u5145\u503c",
      url: "//".concat(h.HOME_DOMAIN, "/falcon/webcast_openpc/pages/douyin_recharge/index.html")
    }
      , E = {
      key: "streaming_tool",
      text: "\u76f4\u64ad\u4f34\u4fa3",
      url: "//".concat(h.HOME_DOMAIN, "/falcon/webcast_openpc/pages/streamingtool_download/index.html"),
      clickToLogin: !0,
      jumpAfterLogin: !0,
      loginHeaderText: "\u767b\u5f55\u540e\u5373\u53ef\u67e5\u770b\u201c\u76f4\u64ad\u4f34\u4fa3\u201d"
    }
      , k = {
      key: "creator",
      text: "\u521b\u4f5c\u8005\u670d\u52a1",
      url: "//".concat(h.CREATOR_DOMAIN)
    }
      , x = {
      key: "rule",
      text: "\u89c4\u5219\u4e2d\u5fc3",
      url: "//".concat(h.HOME_DOMAIN, "/rule")
    }
      , b = {
      key: "aboutDouyin",
      text: "\u5173\u4e8e\u6296\u97f3",
      url: "//".concat(h.HOME_DOMAIN, "/home")
    }
      , C = {
      key: "platform",
      text: "\u6296\u97f3\u5f00\u653e\u5e73\u53f0",
      url: "//".concat(h.OPRNPLATFORM_DOMAIN)
    }
      , N = {
      key: "certification",
      text: "\u8ba4\u8bc1\u4e0e\u5408\u4f5c",
      url: "//".concat(h.HOME_DOMAIN, "/certification/#certification")
    }
      , T = {
      recharge: _,
      homepage: {
        key: "personal_panel",
        text: "\u4e2a\u4eba\u4e3b\u9875",
        clickToLogin: !0,
        loginHeaderText: "\u767b\u5f55\u540e\u5373\u53ef\u67e5\u770b\u201c\u4e2a\u4eba\u4e3b\u9875\u201d"
      },
      liveMate: E,
      logout: {
        key: "logout",
        text: "\u9000\u51fa\u767b\u5f55"
      },
      creator: k,
      rule: x,
      aboutDouyin: b,
      marketing: {
        key: "marketing",
        text: "\u5e7f\u544a\u6295\u653e",
        url: "//".concat(h.OCEAN_ENGINE_DOMAIN, "/resource/douyin?source=douyin-pc")
      },
      ecommerce: {
        text: "\u6296\u97f3\u7535\u5546",
        url: "//".concat(h.DOUYIN_EC_DOMAIN, "/"),
        key: "ecommerce"
      },
      certification: N,
      platform: C,
      publish: {
        key: "publish",
        text: "\u53d1\u5e03\u89c6\u9891",
        url: "//".concat(h.CREATOR_DOMAIN, "/creator-micro/content/upload")
      },
      videoManage: {
        key: "videoManage",
        text: "\u89c6\u9891\u7ba1\u7406",
        url: "//".concat(h.CREATOR_DOMAIN, "/creator-micro/content/manage")
      },
      postStatistics: {
        key: "postStatistics",
        text: "\u4f5c\u54c1\u6570\u636e",
        url: "//".concat(h.CREATOR_DOMAIN, "/creator-micro/data/stats/overview")
      },
      creatorSchool: {
        key: "creatorSchool",
        text: "\u521b\u4f5c\u8005\u5b66\u4e60\u4e2d\u5fc3",
        url: "//".concat(h.CREATOR_DOMAIN, "/creator-school")
      },
      backToHome: {
        key: "backToHome",
        text: "\u8fd4\u56de\u63a8\u8350\u9875",
        url: "//".concat(h.HOME_DOMAIN)
      },
      cooperation: {
        key: "cooperation",
        text: "\u5408\u4f5c"
      },
      downloadClient: {
        key: "downloadClient",
        text: "\u4e0b\u8f7d\u5ba2\u6237\u7aef"
      },
      collectionGuide: {
        key: "collectionDouyin",
        text: "\u6536\u85cf\u7f51\u9875"
      },
      liveData: {
        key: "livedata",
        text: y,
        url: v.LIVE_DATA_LINK
      }
    }
  }
  ,
  16141: (e,t,n)=>{
    n.d(t, {
      DK: ()=>k,
      RG: ()=>C,
      zV: ()=>b
    });
    n(64408),
      n(32781);
    var r = n(30906)
      , o = n(65146)
      , i = (n(5594),
      n(94610),
      n(99860),
      n(34246),
      n(92012))
      , a = n.n(i)
      , l = n(44503)
      , s = n(79705)
      , c = n.n(s)
      , u = n(36539)
      , d = n(4592)
      , m = n(90147)
      , v = n(83655);
    const f = {
      publishIcon: "yx_3kuUB",
      hoverPolyfill: "Z2qXwbQN",
      hoverBold: "qQBjri23",
      publishCt: "ZoRNpuEX",
      iconColor: "bn9MsPmQ",
      buttonColorHidden: "rFVcVXD5",
      publishBtn: "Ao06yJny",
      buttonBounding: "T2fywHvz",
      publishHoverIn: "ChaTApKg",
      leftIconColor: "j5B116pW",
      rightIconColor: "O4ebQloG",
      publishBtnAlink: "V4Wv98va",
      isActivity: "F9DDpGIQ",
      vsTransMode: "JAjTGRiQ",
      loginCt: "qdblhsHs",
      loginBtn: "yH8KQLcx",
      loginButtonText: "aPikQDkS",
      xuguaBut: "yqS0qXRr",
      loginCircleCt: "Qf6c6FMM",
      circleLoginBtn: "R0xtz8q0",
      aboutHome: "_bwc5czk",
      dropdownContainer: "l75jtQfL",
      active: "X8WlMCp6",
      shadowChange: "LBELGnvg",
      dropDownListInCenterChange: "J0GVK9U5",
      download: "JlZDnd5d",
      show: "tK8Uzu5i",
      hidden: "PFd5tknY",
      downloadContainer: "ubaV_lvE",
      downloadContainerInMiniScreen: "kERMGlY4",
      downloadContainerInMiniScreenWithBackToHome: "xFylSVFu",
      downloadDetailPanel: "WiTMRtpK",
      detailHeader: "GoDLrbQo",
      closeIcon: "ZKY59YoH",
      logoContainer: "y43wTsil",
      logo: "R9aO6IDA",
      mainTip: "m3iPWuqB",
      subTip: "OV9Jhr45",
      guideToDesktop: "tcUe19EM",
      add2desktopBtn: "ecWJlhgf",
      overflowChange: "vIeTT6Ke",
      conversationDtailAnimationKeyframes: "ArLkuirc",
      dropDownListInNoCenterChange: "KP7XYNKF",
      showDeleteAllMessageModal: "lpFUVjev",
      dropDownListInNoCenterLeftTopChange: "mqhxAnuH",
      dropDownListOutChange: "hnH0ekUH"
    };
    var h = n(42327)
      , p = n(52255)
      , g = n(66301)
      , y = n(35625)
      , w = n(81971)
      , _ = function(e) {
      var t = e.width
        , n = void 0 === t ? 38 : t
        , o = e.height
        , i = void 0 === o ? 38 : o
        , a = e.className
        , s = e.viewBox
        , c = void 0 === s ? "0 0 38 38" : s;
      return l.createElement(w.A, (0,
        r.Z)((0,
        r.Z)({}, e), {}, {
        width: n,
        height: i,
        src: globalThis.getFilterXss().filterUrl(y.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        id: "svg_icon_circle_close",
        defaultWidth: 38,
        defaultHeight: 38,
        viewBox: c,
        className: a
      }))
    }
      , E = m;
    E.HOME_DOMAIN,
      E.CREATOR_DOMAIN,
      E.OPRNPLATFORM_DOMAIN;
    function k(e) {
      var t = e.className
        , n = e.success
        , o = e.onMouseEnter
        , i = e.onMouseLeave
        , a = e.displayAvatar
        , s = void 0 === a || a
        , c = e.avatarUrl
        , u = void 0 === c ? v.Z : c
        , d = e.headerText
        , m = (0,
        g.UC)(n, d);
      return l.createElement("div", {
        className: t,
        id: f.loginCircleCt
      }, s ? l.createElement("div", (0,
        r.Z)({
        className: f.circleLoginBtn
      }, {
        onClick: m,
        onMouseEnter: o,
        onMouseLeave: i
      }), l.createElement(p.Z, {
        src: globalThis.getFilterXss().filterUrl(u, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: 32,
        height: 32,
        viewBox: "0 0 32 32"
      })) : l.createElement("div", (0,
        r.Z)({
        className: f.circleLoginBtn
      }, {
        onClick: m,
        onMouseEnter: o,
        onMouseLeave: i
      }), " ", "\u767b\u5f55", " "))
    }
    function x(e) {
      var t, n = e.className, r = e.isActivity, i = e.theme, a = e.success, s = e.customProps, u = e.onMouseEnter, d = e.onMouseLeave, m = e.headerText;
      return l.createElement("div", {
        className: c()(n, null == f ? void 0 : f[null == s ? void 0 : s.activityName], (t = {},
          (0,
            o.Z)(t, f.isActivity, r),
          (0,
            o.Z)(t, "isDark", "dark" === i),
          (0,
            o.Z)(t, "theme", "light" === i),
          t)),
        id: f.loginCt,
        onMouseEnter: u,
        onMouseLeave: d
      }, l.createElement(h.zx, {
        className: f.loginBtn,
        theme: "border",
        onClick: (0,
          g.UC)(a, m)
      }, l.createElement(_, {
        height: 18,
        width: 18,
        viewBox: "0 0 18 18"
      }), l.createElement("p", {
        className: f.loginButtonText
      }, "\u767b\u5f55")))
    }
    function b(e) {
      var t = e.isToggleLoginBtn
        , n = void 0 === t || t
        , o = e.success
        , i = e.className
        , a = e.customProps
        , s = e.displayAvatar
        , c = e.onMouseEnter
        , u = e.onMouseLeave;
      return n ? l.createElement(x, (0,
        r.Z)({}, {
        success: o,
        className: i,
        customProps: a,
        isActivity: null == a ? void 0 : a.isActivity,
        theme: null == a ? void 0 : a.theme,
        onMouseEnter: c,
        onMouseLeave: u
      })) : l.createElement(k, (0,
        r.Z)({}, {
        success: o,
        className: i,
        onMouseEnter: c,
        onMouseLeave: u,
        displayAvatar: s
      }))
    }
    function C(e) {
      var t, r = e.success, i = e.isLogin, s = e.children, m = e.className, v = e.customProps, p = e.xiguaBut, g = e.disabledABTest;
      return l.createElement(l.Fragment, null, i ? s : l.createElement("li", {
        className: c()(m, null == f ? void 0 : f[null == v ? void 0 : v.activityName], (t = {},
          (0,
            o.Z)(t, f.isActivity, null == v ? void 0 : v.isActivity),
          (0,
            o.Z)(t, "isDark", "dark" === (null == v ? void 0 : v.theme)),
          (0,
            o.Z)(t, "isLight", "light" === (null == v ? void 0 : v.theme)),
          t)),
        id: f.loginCt
      }, l.createElement(h.zx, {
        className: c()(f.loginBtn, (0,
          o.Z)({}, f.xuguaBut, p)),
        theme: "border",
        onClick: function(e) {
          e.preventDefault(),
            n.e(4606).then(n.bind(n, 24606)).then((function(e) {
                var t, n, o;
                (0,
                  e.navShowAccount)({
                  success: r,
                  enterMethod: "navigation_bar",
                  next: a()(t = "".concat(null == u ? void 0 : d.tJ)).call(t, null === (n = window) || void 0 === n || null === (o = n.location) || void 0 === o ? void 0 : o.host),
                  disabledABTest: g
                })
              }
            ))
        }
      }, "\u767b\u5f55")))
    }
  }
  ,
  57023: (e,t,n)=>{
    n.d(t, {
      E6: ()=>ce
    });
    var r = n(30906)
      , o = n(32781)
      , i = n(44503)
      , a = n(37541)
      , l = n(65146)
      , s = n(79705)
      , c = n.n(s)
      , u = n(25361)
      , d = n(36794);
    const m = "fDnxVO4K"
      , v = "NHdGr1he"
      , f = "axcaw7Or"
      , h = "OB566taK"
      , p = "BUuB45Oo"
      , g = "NVZEtZMn"
      , y = "gXinDMC0"
      , w = "Bb0OfhbR"
      , _ = "Zmyd68GR"
      , E = "nhILhCdm";
    function k(e) {
      var t = e.downloadAttr
        , n = e.downloadHref
        , r = e.children
        , o = e.withClose
        , a = e.onClose
        , s = e.buttonText
        , k = e.withEffect
        , x = e.onDownload
        , b = e.downloadPWA
        , C = e.shouldDownloadPWA;
      return i.createElement("div", {
        className: m
      }, i.createElement("div", {
        className: v
      }, i.createElement(d.Z, {
        src: globalThis.getFilterXss().filterUrl(u.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: c()(h, (0,
          l.Z)({}, p, !o)),
        onClick: a,
        width: 10,
        height: 10,
        viewBox: "0 0 13 13"
      }), i.createElement("div", {
        className: f,
        "data-e2e": "download-container"
      }, r), i.createElement("div", {
        className: g
      }, C && i.createElement("span", {
        className: c()(w, y),
        onClick: function(e) {
          null == b || b(),
          null == x || x(e)
        }
      }, s), !C && i.createElement("a", {
        className: c()(w, y),
        onClick: x,
        download: t,
        href: globalThis.getFilterXss().filterUrl(n, null, {
          logType: "js.href/src",
          reportOnly: !1
        })
      }, s), k && i.createElement("div", {
        className: _
      }), k && i.createElement("div", {
        className: E
      }))))
    }
    const x = "OJheq9Ab"
      , b = "Z19CJIKl";
    var C, N, T;
    function Z() {
      return Z = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        Z.apply(this, arguments)
    }
    const S = function(e) {
      return i.createElement("svg", Z({
        width: 18,
        height: 18,
        viewBox: "0 0 18 18",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), C || (C = i.createElement("path", {
        opacity: .1,
        d: "M0 9a9 9 0 1118 0A9 9 0 010 9z",
        fill: "#FE2C55"
      })), N || (N = i.createElement("path", {
        d: "M3 11.071v.78c0 .22.18.399.4.399h1.189a.4.4 0 00.4-.4V9.831H6.438v2.02c0 .22.179.399.4.399h1.188a.4.4 0 00.4-.4V6.93v-.78a.4.4 0 00-.4-.399H6.838a.4.4 0 00-.4.4v1.904H4.989V6.929v-.78a.4.4 0 00-.4-.399H3.4a.4.4 0 00-.4.4v4.921zM9.735 9.988v1.863c0 .22.179.399.4.399h2.28c1.165 0 2.045-.468 2.386-1.51.152-.469.199-.851.199-1.74s-.047-1.271-.199-1.74c-.34-1.042-1.222-1.51-2.386-1.51h-2.28a.4.4 0 00-.4.4v3.838zm1.988.484V7.528H12.007c.512 0 .777.115.9.497.066.2.085.373.085.975s-.019.774-.085.975c-.123.382-.388.497-.9.497H11.723z",
        fill: "#FE2C55"
      })), T || (T = i.createElement("defs", null, i.createElement("linearGradient", {
        id: "hd_svg__paint0_linear_31317_137960",
        x1: 3,
        y1: 5.75,
        x2: 8.511,
        y2: 15.806,
        gradientUnits: "userSpaceOnUse"
      }, i.createElement("stop", {
        stopColor: "#FF1764"
      }), i.createElement("stop", {
        offset: 1,
        stopColor: "#ED3495"
      })), i.createElement("linearGradient", {
        id: "hd_svg__paint1_linear_31317_137960",
        x1: 3,
        y1: 5.75,
        x2: 8.511,
        y2: 15.806,
        gradientUnits: "userSpaceOnUse"
      }, i.createElement("stop", {
        stopColor: "#FF1764"
      }), i.createElement("stop", {
        offset: 1,
        stopColor: "#ED3495"
      })))))
    };
    var I, L, D;
    function M() {
      return M = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        M.apply(this, arguments)
    }
    const B = function(e) {
      return i.createElement("svg", M({
        width: 18,
        height: 18,
        viewBox: "0 0 18 18",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), I || (I = i.createElement("path", {
        opacity: .1,
        d: "M0 9a9 9 0 1118 0A9 9 0 010 9z",
        fill: "#FE2C55"
      })), L || (L = i.createElement("path", {
        d: "M13.25 11.083c-.016.04-.22.726-.72 1.426-.44.61-.888 1.22-1.598 1.23-.7.01-.924-.4-1.723-.4s-1.05.39-1.713.41c-.684.025-1.211-.665-1.65-1.27-.892-1.23-1.582-3.507-.657-5.027a2.582 2.582 0 012.161-1.26c.668-.01 1.31.434 1.718.434.418 0 1.19-.54 2.005-.46.34.015 1.295.135 1.905.99-.046.03-1.138.65-1.127 1.906.01 1.516 1.383 2.016 1.399 2.021zm-2.715-5.727c.365-.43.61-1.02.543-1.606-.522.02-1.164.335-1.54.76-.334.37-.632.97-.548 1.551.58.03 1.18-.295 1.545-.705z",
        fill: "#FE2C55"
      })), D || (D = i.createElement("defs", null, i.createElement("linearGradient", {
        id: "apple_svg__paint0_linear_31317_137969",
        x1: 4.75,
        y1: 3.75,
        x2: 14.658,
        y2: 12.074,
        gradientUnits: "userSpaceOnUse"
      }, i.createElement("stop", {
        stopColor: "#FF1764"
      }), i.createElement("stop", {
        offset: 1,
        stopColor: "#ED3495"
      })))))
    };
    var A, P, O;
    function V() {
      return V = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        V.apply(this, arguments)
    }
    const W = function(e) {
      return i.createElement("svg", V({
        width: 18,
        height: 18,
        viewBox: "0 0 18 18",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), A || (A = i.createElement("path", {
        opacity: .3,
        d: "M0 9a9 9 0 1118 0A9 9 0 010 9z",
        fill: "#FE2C55"
      })), P || (P = i.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M4.5 8.487C4.5 6.144 6.515 4.25 9 4.25s4.5 1.894 4.5 4.237c0 2.342-2.015 4.236-4.5 4.236 0 0-1.09.064-1.534.166-.291.064-.786.23-1.09.333a.35.35 0 01-.469-.243c-.045-.188-.028-.63-.015-.971.01-.241.017-.432 0-.448C5.04 10.784 4.5 9.693 4.5 8.487zm3.586 2.17a1.976 1.976 0 01-.349-.126.429.429 0 11.383-.767c.024.012.089.037.191.065.446.122.995.122 1.625-.088a.429.429 0 01.27.813c-.798.266-1.518.266-2.12.102z",
        fill: "url(#message_svg__paint0_linear_4551_137166)"
      })), O || (O = i.createElement("defs", null, i.createElement("linearGradient", {
        id: "message_svg__paint0_linear_4551_137166",
        x1: 4.5,
        y1: 4.25,
        x2: 13.549,
        y2: 13.197,
        gradientUnits: "userSpaceOnUse"
      }, i.createElement("stop", {
        stopColor: "#FF1764"
      }), i.createElement("stop", {
        offset: 1,
        stopColor: "#ED3495"
      })))))
    };
    var R, F, U;
    function H() {
      return H = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        H.apply(this, arguments)
    }
    const G = function(e) {
      return i.createElement("svg", H({
        width: 18,
        height: 18,
        viewBox: "0 0 18 18",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), R || (R = i.createElement("path", {
        opacity: .1,
        d: "M0 9a9 9 0 1118 0A9 9 0 010 9z",
        fill: "#FE2C55"
      })), F || (F = i.createElement("path", {
        d: "M12.744 7.615H9.81V4.657a.4.4 0 00-.715-.248L4.909 9.737a.4.4 0 00.314.648h2.935v2.958a.4.4 0 00.714.248l4.187-5.328a.4.4 0 00-.315-.648z",
        fill: "#FE2C55"
      })), U || (U = i.createElement("defs", null, i.createElement("linearGradient", {
        id: "thunder_svg__paint0_linear_31317_137964",
        x1: 4.4,
        y1: 3.5,
        x2: 15.26,
        y2: 12.444,
        gradientUnits: "userSpaceOnUse"
      }, i.createElement("stop", {
        stopColor: "#FF1764"
      }), i.createElement("stop", {
        offset: 1,
        stopColor: "#ED3495"
      })))))
    };
    function j(e) {
      var t = e.svg
        , n = e.text
        , r = e.svgWidth
        , o = e.svgHeight
        , a = e.svgViewBox;
      return i.createElement("div", {
        className: x
      }, i.createElement(d.Z, {
        src: globalThis.getFilterXss().filterUrl(t, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: r,
        height: o,
        viewBox: a
      }), i.createElement("span", {
        className: b
      }, n))
    }
    function K() {
      return i.createElement(j, {
        svgWidth: 18,
        svgHeight: 18,
        svgViewBox: "0 0 18 18",
        text: "\u9ad8\u6e05\u6d41\u7545\u64ad\u653e",
        svg: S
      })
    }
    function q() {
      return i.createElement(j, {
        svgWidth: 18,
        svgHeight: 18,
        svgViewBox: "0 0 18 18",
        text: "\u4e3aMac\u8bbe\u5907\u5b9a\u5236",
        svg: B
      })
    }
    function Y() {
      return i.createElement(j, {
        svgWidth: 18,
        svgHeight: 18,
        svgViewBox: "0 0 18 18",
        text: "\u597d\u53cb\u6d88\u606f\u901a\u77e5",
        svg: W
      })
    }
    function X() {
      return i.createElement(j, {
        svgWidth: 18,
        svgHeight: 18,
        svgViewBox: "0 0 18 18",
        text: "\u684c\u9762\u4fbf\u6377\u8bbf\u95ee",
        svg: G
      })
    }
    const z = "GUjjfnC_"
      , Q = "qScktcui"
      , J = "I6OwFsJu"
      , $ = "jcjnHarg"
      , ee = "InqOpTNF";
    function te(e) {
      var t = e.text
        , n = e.textClassName;
      return i.createElement("div", {
        className: J
      }, i.createElement("div", {
        className: $
      }), i.createElement("div", {
        className: c()(ee, n)
      }, t))
    }
    var ne, re = n(74394), oe = n(14737), ie = n(84696), ae = n(1392);
    function le(e) {
      var t = e.isShow
        , n = e.onDownload
        , r = (0,
        ie.o)()
        , o = r.downloadAttr
        , l = r.downloadHref
        , s = (0,
        i.useCallback)((function() {
          ae.Z.sendLog("addToDesktopClick", {
            enter_from: "personal_homepage",
            type: "live_detail_button",
            platform: "client",
            is_full_screen: a.r() ? "1" : "0"
          }),
          null == n || n()
        }
      ), [n]);
      return (0,
        i.useEffect)((function() {
          t && ae.Z.sendLog("addToDesktopShow", {
            enter_from: "live_detail",
            is_full_screen: a.r() ? "1" : "0",
            platform: "client",
            type: "live_detail_button"
          })
        }
      ), [t]),
        i.createElement("div", null, t && i.createElement(k, {
          buttonText: "\u4e0b\u8f7d\u7535\u8111\u5ba2\u6237\u7aef",
          downloadAttr: o,
          downloadHref: l,
          onDownload: s,
          withClose: !1
        }, i.createElement("div", {
          className: z
        }, i.createElement(K, null), i.createElement(X, null))))
    }
    function se(e) {
      var t = e.onDownload
        , n = e.onClose
        , r = e.downloadPWA
        , l = e.shouldShowGuideType
        , s = e.clientDownloadAttr
        , c = e.clientDownloadHref
        , u = e.withClose
        , d = e.withEffect
        , m = e.showType
        , v = (0,
        i.useState)(null)
        , f = (0,
        o.Z)(v, 2)
        , h = f[0]
        , p = f[1]
        , g = (0,
        i.useCallback)((function() {
          ae.Z.sendLog("addToDesktopClick", {
            enter_from: (0,
              ae.v)(),
            is_full_screen: a.r() ? "1" : "0",
            type: m === oe.KK.Hover ? "hover" : "guide",
            platform: l === oe.xj.PWA ? "pwa" : "client"
          }),
          null == t || t()
        }
      ), [t, l, m]);
      return (0,
        i.useEffect)((function() {
          ae.Z.sendLog("addToDesktopShow", {
            enter_from: (0,
              ae.v)(),
            is_full_screen: a.r() ? "1" : "0",
            platform: l === oe.xj.PWA ? "pwa" : "client",
            type: m === oe.KK.Hover ? "hover" : "guide"
          })
        }
      ), [m, l]),
        (0,
          i.useEffect)((function() {
            p((0,
              re.P0)())
          }
        ), []),
        i.createElement("div", {
          className: Q
        }, l !== oe.xj.None && i.createElement(k, {
          buttonText: l === oe.xj.Client ? "\u4e0b\u8f7d\u7535\u8111\u5ba2\u6237\u7aef" : "\u6dfb\u52a0\u5230\u684c\u9762",
          downloadAttr: s,
          downloadHref: c,
          shouldDownloadPWA: l === oe.xj.PWA,
          downloadPWA: r,
          withClose: u,
          onDownload: g,
          onClose: n,
          withEffect: d
        }, i.createElement("div", {
          className: z
        }, l === oe.xj.Client && h === re.CT.Mac && i.createElement(i.Fragment, null, i.createElement(K, null), i.createElement(X, null), i.createElement(q, null)), l === oe.xj.Client && h === re.CT.Win7Up && i.createElement(i.Fragment, null, i.createElement(K, null), i.createElement(Y, null), i.createElement(X, null)), l === oe.xj.PWA && i.createElement(te, {
          text: "\u684c\u9762\u4fbf\u6377\u8bbf\u95ee"
        }))))
    }
    function ce(e) {
      return e.forLive ? i.createElement(le, (0,
        r.Z)({}, e)) : i.createElement(se, (0,
        r.Z)({}, e))
    }
    !function(e) {
      e[e.NormalDownloadGuide = 0] = "NormalDownloadGuide",
        e[e.HoverDownloadGuide = 1] = "HoverDownloadGuide",
        e[e.MiniScreenNormalDownloadGuide = 2] = "MiniScreenNormalDownloadGuide",
        e[e.MiniScreenHoverDownloadGuide = 3] = "MiniScreenHoverDownloadGuide"
    }(ne || (ne = {}))
  }
  ,
  5200: (e,t,n)=>{
    n.d(t, {
      Z: ()=>H
    });
    var r = n(30906), o = n(65146), i = n(32781), a = n(79705), l = n.n(a), s = n(44503), c = n(24260), u = n(21857), d = n.n(u), m = n(52172), v = n(80212), f = n(92557), h = n(25083), p = n(52252), g = n(85938), y = n(76659), w = n(78867), _ = n(14484), E = n(67255), k = n(44420), x = n(50790), b = n(25725), C = n(14001), N = n(83484), T = n(52491), Z = n(28796), S = n(2143), I = n(98853), L = n(27117), D = n(67594), M = n(16340), B = n(98767), A = n(34276), P = n(89543), O = n(95680), V = n(69343), W = n(66470), R = n(91881), F = (0,
      c.default)({
      resolved: {},
      chunkName: function() {
        return "ModalVideo"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(3973), n.e(9684), n.e(434), n.e(6515), n.e(2520), n.e(1115), n.e(1779), n.e(7774), n.e(2045), n.e(8930)]).then(n.bind(n, 15101))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 15101
      }
    }, {
      ssr: !1
    }), U;
    function H(e) {
      var t, n, a, c, u, H = e.userInfo, G = e.onChangeLoginStatus, j = e.abTestData, K = e.customProps, q = e.className, Y = e.needGrayscale, X = void 0 !== Y && Y, z = e.loginPopupStatus, Q = void 0 === z ? D.T.Off : z;
      (0,
        B.i)();
      var J = K.pathname
        , $ = K.isClient
        , ee = K.os
        , te = K.redirectFrom
        , ne = K.isVsTab
        , re = K.isVsTabTrans
        , oe = K.isActivity
        , ie = K.activityName
        , ae = K.disableSpecTheme
        , le = (0,
        T.T)({
        userInfo: H,
        redirectFrom: te
      }).handleHiddenLog
        , se = (0,
        s.useState)(!1)
        , ce = (0,
        i.Z)(se, 2)
        , ue = ce[0]
        , de = ce[1]
        , me = (0,
        s.useState)(!1)
        , ve = (0,
        i.Z)(me, 2)
        , fe = ve[0]
        , he = ve[1]
        , pe = (0,
        s.useState)(null)
        , ge = (0,
        i.Z)(pe, 2)
        , ye = ge[0]
        , we = ge[1]
        , _e = (0,
        s.useState)(!1)
        , Ee = (0,
        i.Z)(_e, 2)
        , ke = Ee[0]
        , xe = Ee[1]
        , be = (0,
        s.useState)(null)
        , Ce = (0,
        i.Z)(be, 2)
        , Ne = Ce[0]
        , Te = Ce[1]
        , Ze = (0,
        s.useRef)()
        , Se = oe
        , Ie = ie
        , Le = ae || Se
        , De = m.a.wrapClientOsInfo($, ee).isMac
        , Me = (0,
        P.c)()
        , Be = (0,
        s.useState)(!1)
        , Ae = (0,
        i.Z)(Be, 2)
        , Pe = Ae[0]
        , Oe = Ae[1]
        , Ve = (0,
        s.useMemo)((function() {
          return ne && re
        }
      ), [ne, re])
        , We = (0,
        L.L)()
        , Re = We.setModalCardInfo
        , Fe = We.restoreModalCardInfo
        , Ue = (0,
        R.j)().transparent;
      (0,
        s.useEffect)((function() {
          v.f() && de(!0)
        }
      ), []),
        (0,
          D.S)({
          isLogin: null == H ? void 0 : H.isLogin,
          noDisturbVal: null == j ? void 0 : j.noDisturbV2,
          loginPopupStatus: Q
        }),
        (0,
          s.useEffect)((function() {
            var e = f.listen(f.EVENT.openImAwemeModal, (function(e) {
                we(e),
                  Re(),
                  he(!0),
                  f.emit(f.EVENT.videoPause),
                  f.emit(f.EVENT.livePause)
              }
            ))
              , t = f.listen(f.EVENT.openNoticeAwemeModal, (function(e) {
                Te(e),
                  xe(!0),
                  f.emit(f.EVENT.videoPause),
                  f.emit(f.EVENT.livePause)
              }
            ));
            return function() {
              e(),
                t()
            }
          }
        ), []);
      var He = (0,
        s.useCallback)((function(e) {
          De && "doubleClick" === e.target.getAttribute("data-click") && d().app.maximize()
        }
      ), [De]);
      (0,
        s.useEffect)((function() {
          var e = f.listen(f.EVENT.changeNavBarBlur, (function(e) {
              Oe(e)
            }
          ));
          return function() {
            return e()
          }
        }
      ), []);
      var Ge = (0,
        M.Z)()
        , je = Ge.specTheme
        , Ke = Ge.isDark
        , qe = (0,
        s.useMemo)((function() {
          if (Le)
            return {};
          var e = h.yW();
          return "vs" === e || "vschannel" === e || "download" === e ? {} : null != je && je.themeSwitch ? {
            backgroundImage: "url(".concat(Ke ? null == je ? void 0 : je.headerDark : null == je ? void 0 : je.headerLight, ")")
          } : {}
        }
      ), [je, Ke, Le])
        , Ye = !p.p() && !Le && (null == je ? void 0 : je.themeSwitch);
      (0,
        s.useEffect)((function() {
          var e = g.Bj(h.yW());
          e && (Ze.current = e)
        }
      ), []);
      var Xe = null === (t = y.Es()) || void 0 === t ? void 0 : t.user_unique_id;
      (0,
        V.E)({
        isLogin: null == H ? void 0 : H.isLogin,
        webId: Xe,
        open: null == j ? void 0 : j.vsLivePush
      });
      var ze = (0,
        s.useMemo)((function() {
          return (null == j ? void 0 : j.searchBarStyleOpt) === w.SearchBarStyleOpt.Center
        }
      ), [null == j ? void 0 : j.searchBarStyleOpt])
        , Qe = (0,
        s.useMemo)((function() {
          return (null == j ? void 0 : j.searchBarStyleOpt) === w.SearchBarStyleOpt.Aggressive || (null == j ? void 0 : j.searchBarStyleOpt) === w.SearchBarStyleOpt.Mild
        }
      ), [null == j ? void 0 : j.searchBarStyleOpt]);
      return s.createElement("div", {
        onDoubleClick: He,
        className: l()(U[Ze.current], x.Z.container, (n = {},
          (0,
            o.Z)(n, x.Z.activity, Se || Ue),
          (0,
            o.Z)(n, x.Z.transparent, Ue),
          (0,
            o.Z)(n, q, q),
          (0,
            o.Z)(n, x.Z.isVsHeader, ne),
          (0,
            o.Z)(n, x.Z.isNormalHeader, ne && !Ve),
          (0,
            o.Z)(n, x.Z.transmode, Ve),
          (0,
            o.Z)(n, x.Z.blur, (Se || Ue) && Pe),
          (0,
            o.Z)(n, x.Z.searchBarCenterLayout, ze),
          n))
      }, s.createElement("div", {
        className: l()(x.Z.fixed, (0,
          o.Z)({}, x.Z.grayscale, X)),
        id: "douyin-header",
        "data-click": "doubleClick"
      }, s.createElement("header", {
        className: l()(x.Z.header, (a = {},
          (0,
            o.Z)(a, x.Z.electron, $),
          (0,
            o.Z)(a, x.Z.electronDrag, $ && !Me),
          (0,
            o.Z)(a, x.Z.electronMacInner, De),
          a))
      }, $ && s.createElement(s.Fragment, null, s.createElement("div", {
        className: x.Z.headerNoDragArea
      }), s.createElement(N.ReturnButton, {
        transparent: Ue
      })), !$ && s.createElement("div", {
        className: l()(x.Z.logoCt, {
          isDark: Se || Ve || Ue
        }),
        onClick: function() {
          b.Z.sendLog("clickAwemeLogo", {
            enter_from: h.yW()
          })
        }
      }, s.createElement(C.a, {
        href: globalThis.getFilterXss().filterUrl(_.kj("enter_recommend_method=feed_click"), null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: x.Z.logo
      })), s.createElement("div", {
        className: x.Z.rightContent,
        "data-click": "doubleClick",
        style: qe
      }, s.createElement("div", {
        className: x.Z.searchCt
      }, s.createElement("div", {
        className: l()(x.Z.searchBar, (0,
          o.Z)({}, x.Z.newSearchBar, Qe))
      }, s.createElement("div", {
        className: x.Z.searchBlank
      }), s.createElement(A.SearchBar, {
        customProps: {
          isActivity: Se || Ve,
          activityName: Ie || (Ve ? "vsTransMode" : ""),
          transparent: Ue,
          isSearchPage: Boolean(null == J ? void 0 : J.match(/^\/search/)),
          pathname: J,
          themeSwitch: Ye
        },
        userInfo: H,
        abTestData: j,
        onSearchClick: function(e) {
          return le(e)
        },
        onHistoryClick: function(e) {
          var t = e.currentTarget.dataset.text;
          return le(t)
        },
        onInputKeyDown: function(e, t) {
          if ("Enter" === E.C(e))
            return le(t)
        }
      }))), s.createElement("div", {
        className: l()(x.Z.menuCt, {
          isDark: Se
        })
      }, s.createElement("div", {
        className: x.Z.floatRight
      }, s.createElement(O.R.Provider, {
        value: {
          isActivity: Se || Ve || (null == K ? void 0 : K.isActivity),
          activityName: Ie || (Ve ? "vsTransMode" : "") || (null == K ? void 0 : K.activityName),
          isVsTransmode: Ve
        }
      }, s.createElement(Z.Z, {
        customProps: (0,
          r.Z)((0,
          r.Z)({}, K), {}, {
          isActivity: Se || Ve,
          activityName: Ie || (Ve ? "vsTransMode" : "")
        }),
        success: G,
        userInfo: H,
        abTestData: j,
        transparent: Ue
      })))))), ue && s.createElement("div", {
        className: x.Z.pwaDivider
      }), fe && s.createElement(F, {
        className: x.Z.imModalVideo,
        awemeIds: null == ye ? void 0 : ye.videoMsgList,
        clientId: null == ye ? void 0 : ye.msgClientId,
        fetchAwemeIds: null == ye ? void 0 : ye.getMoreVideo,
        logParams: null == ye ? void 0 : ye.logParams,
        insertCommentId: null == ye ? void 0 : ye.commentId,
        defaultCommentShow: null == ye ? void 0 : ye.commentId,
        disableAutoPlay: !0,
        abtestData: j,
        anyHooks: I.Z,
        useOldModal: !0,
        moreBoxShowList: {
          notInterestingIcon: !1,
          unfollow: !1,
          report: !0
        },
        close: function() {
          Fe(),
            he(!1)
        },
        userContext: {
          userInfo: H,
          dispatch: function() {}
        },
        modalEnterFrom: "im",
        shortCutFilteredList: [null === (c = k.getShortcut().dislike) || void 0 === c ? void 0 : c.key]
      }), ke && s.createElement(F, {
        className: x.Z.imModalVideo,
        awemeId: null == Ne ? void 0 : Ne.awemeId,
        insertCommentId: null == Ne ? void 0 : Ne.cid,
        logParams: null == Ne ? void 0 : Ne.logParams,
        defaultCommentShow: null == Ne ? void 0 : Ne.cid,
        disableSwitch: !0,
        disableAutoPlay: !0,
        abtestData: j,
        anyHooks: S.Z,
        useOldModal: !0,
        moreBoxShowList: {
          notInterestingIcon: !1,
          unfollow: !1,
          report: !0
        },
        close: function() {
          xe(!1)
        },
        userContext: {
          userInfo: H,
          dispatch: function() {}
        },
        danmakuInfo: null == Ne ? void 0 : Ne.danmakuInfo,
        modalEnterFrom: "im",
        shortCutFilteredList: [null === (u = k.getShortcut().dislike) || void 0 === u ? void 0 : u.key]
      }), s.createElement("div", {
        className: x.Z.pushMessageEntry
      }, s.createElement(W.H, null))))
    }
    !function(e) {
      e.light = "isLight",
        e.dark = "isDark"
    }(U || (U = {}))
  }
  ,
  25725: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = new (n(37485).hD)({
      clickAwemeLogo: {
        eventName: "click_aweme_logo",
        params: {
          enter_from: ""
        }
      }
    })
  }
  ,
  95680: (e,t,n)=>{
    n.d(t, {
      R: ()=>W,
      Z: ()=>R
    });
    var r = n(30906)
      , o = n(65146)
      , i = n(32781)
      , a = n(44503)
      , l = n(79705)
      , s = n.n(l)
      , c = n(24260)
      , u = n(21857)
      , d = n.n(u)
      , m = n(52172)
      , v = n(80212)
      , f = n(92557)
      , h = n(25083)
      , p = n(76659)
      , g = n(78867)
      , y = n(14484)
      , w = n(67255)
      , _ = n(96411)
      , E = n(44420)
      , k = n(74474)
      , x = n(52491)
      , b = n(28796)
      , C = n(96608)
      , N = n(2143)
      , T = n(98853)
      , Z = n(16340)
      , S = n(14001)
      , I = n(27117)
      , L = n(98767)
      , D = n(67594)
      , M = n(34276)
      , B = n(91881)
      , A = n(89543)
      , P = n(69343)
      , O = n(66470)
      , V = (0,
      c.default)({
      resolved: {},
      chunkName: function() {
        return "ModalVideo"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(3973), n.e(9684), n.e(434), n.e(6515), n.e(2520), n.e(1115), n.e(1779), n.e(7774), n.e(2045), n.e(8930)]).then(n.bind(n, 15101))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 15101
      }
    }, {
      ssr: !1
    })
      , W = a.createContext({
      activityName: "",
      isActivity: !1,
      isVsTransmode: !1
    });
    function R(e) {
      var t, n, l, c, u, R, F, U, H, G, j = e.userInfo, K = e.onChangeLoginStatus, q = e.abTestData, Y = void 0 === q ? {} : q, X = e.customProps, z = e.className, Q = e.needGrayscale, J = e.loginPopupStatus, $ = void 0 === J ? D.T.Off : J;
      (0,
        L.i)();
      var ee = (0,
        x.T)({
        userInfo: j,
        redirectFrom: null == X ? void 0 : X.redirectFrom
      }).handleHiddenLog
        , te = a.useState(!1)
        , ne = (0,
        i.Z)(te, 2)
        , re = ne[0]
        , oe = ne[1]
        , ie = a.useState(!1)
        , ae = (0,
        i.Z)(ie, 2)
        , le = ae[0]
        , se = ae[1]
        , ce = a.useState(!1)
        , ue = (0,
        i.Z)(ce, 2)
        , de = ue[0]
        , me = ue[1]
        , ve = a.useState(null)
        , fe = (0,
        i.Z)(ve, 2)
        , he = fe[0]
        , pe = fe[1]
        , ge = a.useState(!1)
        , ye = (0,
        i.Z)(ge, 2)
        , we = ye[0]
        , _e = ye[1]
        , Ee = a.useState(null)
        , ke = (0,
        i.Z)(Ee, 2)
        , xe = ke[0]
        , be = ke[1]
        , Ce = (0,
        B.j)().transparent
        , Ne = X.isClient
        , Te = X.os
        , Ze = (0,
        a.useMemo)((function() {
          return m.a.wrapClientOsInfo(Ne, Te)
        }
      ), [Ne, Te]).isMac
        , Se = (0,
        A.c)()
        , Ie = a.useMemo((function() {
          return (null == X ? void 0 : X.isVsTab) && (null == X ? void 0 : X.isVsTabTrans)
        }
      ), [X])
        , Le = (0,
        I.L)()
        , De = Le.setModalCardInfo
        , Me = Le.restoreModalCardInfo;
      (0,
        D.S)({
        isLogin: null == j ? void 0 : j.isLogin,
        noDisturbVal: null == Y ? void 0 : Y.noDisturbV2,
        loginPopupStatus: $
      }),
        a.useEffect((function() {
            v.f() && oe(!0)
          }
        ), []),
        a.useEffect((function() {
            var e = f.listen(f.EVENT.headerGradient, (function(e) {
                return se(e)
              }
            ))
              , t = f.listen(f.EVENT.openImAwemeModal, (function(e) {
                pe(e),
                  De(),
                  me(!0),
                  f.emit(f.EVENT.videoPause),
                  f.emit(f.EVENT.livePause)
              }
            ))
              , n = f.listen(f.EVENT.openNoticeAwemeModal, (function(e) {
                be(e),
                  _e(!0),
                  f.emit(f.EVENT.videoPause),
                  f.emit(f.EVENT.livePause)
              }
            ));
            return function() {
              t(),
                n(),
                e()
            }
          }
        ), []);
      var Be = a.useCallback((function(e) {
          Ze && "doubleClick" === e.target.getAttribute("data-click") && d().app.maximize()
        }
      ), [Ze])
        , Ae = (0,
        Z.Z)()
        , Pe = Ae.specTheme
        , Oe = Ae.isDark
        , Ve = a.useMemo((function() {
          return null != Pe && Pe.themeSwitch ? {
            backgroundImage: "url(".concat(Oe ? null == Pe ? void 0 : Pe.headerDark : null == Pe ? void 0 : Pe.headerLight, ")")
          } : {}
        }
      ), [Pe, Oe])
        , We = null === (t = p.Es()) || void 0 === t ? void 0 : t.user_unique_id;
      (0,
        P.E)({
        isLogin: null == j ? void 0 : j.isLogin,
        webId: We,
        open: null == Y ? void 0 : Y.vsLivePush
      });
      var Re = (0,
        a.useMemo)((function() {
          return (null == Y ? void 0 : Y.searchBarStyleOpt) === g.SearchBarStyleOpt.Center
        }
      ), [null == Y ? void 0 : Y.searchBarStyleOpt])
        , Fe = (0,
        a.useMemo)((function() {
          return (null == Y ? void 0 : Y.searchBarStyleOpt) === g.SearchBarStyleOpt.Aggressive || (null == Y ? void 0 : Y.searchBarStyleOpt) === g.SearchBarStyleOpt.Mild
        }
      ), [null == Y ? void 0 : Y.searchBarStyleOpt]);
      return a.createElement("div", {
        onDoubleClick: Be,
        className: s()(k.Z.container, k.Z.containerNew, (n = {},
          (0,
            o.Z)(n, k.Z.activity, (null == X ? void 0 : X.isActivity) || Ce),
          (0,
            o.Z)(n, k.Z.transparent, Ce),
          (0,
            o.Z)(n, k.Z.changeColor, le),
          (0,
            o.Z)(n, z, z),
          (0,
            o.Z)(n, k.Z.isFixed, null == X ? void 0 : X.isFixed),
          (0,
            o.Z)(n, k.Z.isVsHeader, X.isVsTab),
          (0,
            o.Z)(n, k.Z.isNormalHeader, X.isVsTab && !Ie),
          (0,
            o.Z)(n, k.Z.transmode, Ie),
          (0,
            o.Z)(n, k.Z.isVideoOrVsHeader, null == X ? void 0 : X.isVsOrVideo),
          (0,
            o.Z)(n, k.Z.isSearchHeader, null == X ? void 0 : X.isSearchResult),
          (0,
            o.Z)(n, k.Z.grayscale, Q),
          (0,
            o.Z)(n, k.Z.searchBarCenterLayout, Re),
          n)),
        id: "douyin-header",
        "data-click": "doubleClick"
      }, a.createElement("div", {
        className: s()(k.Z.fixed, (0,
          o.Z)({}, k.Z.searchLightActivity, null == X ? void 0 : X.searchLightActivity)),
        style: Ve,
        "data-click": "doubleClick"
      }, a.createElement("header", {
        className: s()(k.Z.header)
      }, a.createElement("div", {
        className: s()(k.Z.rightContent, (l = {},
          (0,
            o.Z)(l, k.Z.clientRightContent, Ne),
          (0,
            o.Z)(l, k.Z.electronDrag, Ne && !Se),
          l)),
        "data-click": "doubleClick"
      }, Ze && a.createElement("div", {
        className: k.Z.basicHeight
      }, a.createElement("div", {
        className: s()(k.Z.logoCt)
      }, a.createElement(S.a, {
        href: globalThis.getFilterXss().filterUrl(y.kj(), null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        className: s()(k.Z.logo, (0,
          o.Z)({}, k.Z.transparentLogo, Ce)),
        onClick: function() {
          C.Z.sendLog("clickAwemeLogo", {
            enter_from: h.yW()
          })
        }
      }))), a.createElement("div", {
        className: s()(k.Z.rightContentInner, k.Z.rightContentInnerNew),
        "data-click": "doubleClick"
      }, a.createElement("div", {
        className: s()(k.Z.searchCt)
      }, a.createElement("div", {
        className: s()(k.Z.searchBar, (0,
          o.Z)({}, k.Z.newSearchBar, Fe))
      }, a.createElement("div", {
        className: k.Z.searchBlank
      }), a.createElement("div", null, a.createElement(M.SearchBar, {
        customProps: {
          isActivity: Ie || (null == X ? void 0 : X.isActivity),
          activityName: (Ie ? "vsTransMode" : "") || (null == X ? void 0 : X.activityName),
          isSearchPage: Boolean(null == X || null === (c = X.pathname) || void 0 === c ? void 0 : c.match(/^\/search/)),
          pathname: null == X ? void 0 : X.pathname,
          themeSwitch: null == Pe ? void 0 : Pe.themeSwitch,
          transparent: Ce
        },
        userInfo: j,
        abTestData: Y,
        onSearchClick: function(e) {
          return ee(e)
        },
        onHistoryClick: function(e) {
          var t = e.currentTarget.dataset.text;
          return ee(t)
        },
        onInputKeyDown: function(e, t) {
          if ("Enter" === w.C(e))
            return ee(t)
        }
      })))), a.createElement("div", {
        className: s()(k.Z.menuCt)
      }, a.createElement("div", {
        className: k.Z.floatRight
      }, a.createElement(W.Provider, {
        value: {
          isActivity: Ie || (null == X ? void 0 : X.isActivity),
          activityName: (Ie ? "vsTransMode" : "") || (null == X ? void 0 : X.activityName),
          isVsTransmode: Ie
        }
      }, a.createElement(b.Z, {
        customProps: (0,
          r.Z)((0,
          r.Z)({}, X), {}, {
          isActivity: Ie || (null == X ? void 0 : X.isActivity),
          activityName: (Ie ? "vsTransMode" : "") || (null == X ? void 0 : X.activityName),
          landingPage: X.landingPage
        }),
        transparent: Ce,
        success: K,
        userInfo: j,
        abTestData: Y
      }))))))), re && a.createElement("div", {
        className: k.Z.pwaDivider
      }), de && a.createElement(V, {
        className: k.Z.imModalVideo,
        awemeIds: null == he ? void 0 : he.videoMsgList,
        clientId: null == he ? void 0 : he.msgClientId,
        fetchAwemeIds: null == he ? void 0 : he.getMoreVideo,
        logParams: null == he ? void 0 : he.logParams,
        insertCommentId: null == he ? void 0 : he.commentId,
        defaultCommentShow: null == he ? void 0 : he.commentId,
        disableAutoPlay: !0,
        abtestData: Y,
        anyHooks: T.Z,
        useOldModal: !0,
        moreBoxShowList: {
          notInterestingIcon: !1,
          unfollow: !1,
          report: !0
        },
        close: function() {
          Me(),
            me(!1)
        },
        userContext: {
          userInfo: j,
          dispatch: function() {}
        },
        shortCutFilteredList: [null == _ || null === (u = E) || void 0 === u || null === (R = u.getShortcut()) || void 0 === R || null === (F = R.dislike) || void 0 === F ? void 0 : F.key],
        modalEnterFrom: "im"
      }), we && a.createElement(V, {
        className: k.Z.imModalVideo,
        awemeId: null == xe ? void 0 : xe.awemeId,
        insertCommentId: null == xe ? void 0 : xe.cid,
        logParams: null == xe ? void 0 : xe.logParams,
        defaultCommentShow: null == xe ? void 0 : xe.cid,
        disableSwitch: !0,
        disableAutoPlay: !0,
        abtestData: Y,
        anyHooks: N.Z,
        useOldModal: !0,
        moreBoxShowList: {
          notInterestingIcon: !1,
          unfollow: !1,
          report: !0
        },
        close: function() {
          _e(!1)
        },
        userContext: {
          userInfo: j,
          dispatch: function() {}
        },
        danmakuInfo: null == xe ? void 0 : xe.danmakuInfo,
        modalEnterFrom: "im",
        shortCutFilteredList: [null == _ || null === (U = E) || void 0 === U || null === (H = U.getShortcut()) || void 0 === H || null === (G = H.dislike) || void 0 === G ? void 0 : G.key]
      })), a.createElement("div", {
        className: k.Z.pushMessageEntry
      }, a.createElement(O.H, null)))
    }
  }
  ,
  58801: (e,t,n)=>{
    n.d(t, {
      a: ()=>_
    });
    var r = n(30906)
      , o = n(65146)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a)
      , s = n(78867)
      , c = n(92557)
      , u = n(14484)
      , d = n(25083)
      , m = n(2758)
      , v = n(22459)
      , f = n(14001)
      , h = n(26395)
      , p = n(26637)
      , g = n(1392)
      , y = n(30410)
      , w = n(80714);
    function _(e) {
      var t, n = (0,
        h.P)({
        delayDisappear: 100,
        delayShow: 100
      }), a = n.type, _ = n.changeType, E = e.secUid, k = e.avatarUrl, x = e.awemeCount, b = e.favoritingCount, C = e.awemeCollectCount, N = e.className, T = e.isClient, Z = e.abtest, S = (0,
        p.o)(null !== (t = null == Z ? void 0 : Z.hasHorizontalHeader) && void 0 !== t ? t : s.HasHorizontalHeader.Default, T).isHorizontalLayout;
      return (0,
        i.useEffect)((function() {
          var e = c.listen(c.EVENT.showHeaderPopUp, (function(e) {
              var t = e || {}
                , n = t.type
                , r = t.isShow;
              "im" === n && r && _()
            }
          ));
          return function() {
            return e()
          }
        }
      ), []),
        (0,
          i.useEffect)((function() {
            "active" === a && c.emit(c.EVENT.showHeaderPopUp, {
              type: "userDetail",
              isShow: !0
            })
          }
        ), [a]),
        i.createElement(w.p, {
          headerPopupName: "userDetail"
        }, i.createElement("div", {
          className: l()(m.Z.avataUserCt, m.Z.avataUserMini, N, (0,
            o.Z)({}, m.Z.clientAvatarLi, T)),
          onMouseEnter: function() {
            _("active")
          },
          onMouseLeave: function() {
            _()
          }
        }, i.createElement(f.a, {
          target: (null == Z ? void 0 : Z.selfTab) > 0 && S ? "_self" : "_blank",
          rel: "noopener noreferrer",
          href: globalThis.getFilterXss().filterUrl(u.HC((null == Z ? void 0 : Z.selfTab) > 0 && S ? "self" : E, "enter_method=top_bar"), null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          className: l()(m.Z.avatar, m.Z.hoverEnlarge)
        }, i.createElement(v.q, {
          type: "extraExtraSmall",
          className: l()((0,
            o.Z)({}, m.Z.clientAvatr, T)),
          src: globalThis.getFilterXss().filterUrl(k, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          isSelf: !0
        })), i.createElement("div", {
          className: l()(m.Z.dropdownContainer, m.Z.userPanelCollect, (0,
            o.Z)({}, m.Z.active, Boolean(a))),
          onMouseEnter: function() {
            _("active"),
              g.Z.sendLog("personalPanelShow", {
                enter_from: d.vM()
              })
          },
          onMouseLeave: function() {
            _()
          }
        }, i.createElement("ul", null, i.createElement(y.Y, (0,
          r.Z)({}, {
          awemeCount: x,
          favoritingCount: b,
          awemeCollectCount: C,
          secUid: E,
          isLogin: !0,
          isActive: "active" === a,
          hide: function() {
            return _()
          },
          abtest: Z,
          isClient: T
        }))))))
    }
  }
  ,
  36788: (e,t,n)=>{
    n.d(t, {
      T: ()=>y
    });
    var r = n(30906)
      , o = n(65146)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a)
      , s = n(92557)
      , c = n(25083)
      , u = n(2758)
      , d = n(26395)
      , m = n(1392)
      , v = n(30410)
      , f = n(55861)
      , h = n(16141)
      , p = n(80714)
      , g = n(32781);
    function y(e) {
      var t = e.success
        , n = e.isToggleLoginBtn
        , a = e.displayAvatar
        , y = void 0 !== a && a
        , w = e.className
        , _ = e.isClient
        , E = e.abtest
        , k = (0,
        d.P)({
        delayDisappear: 100,
        delayShow: 100
      })
        , x = k.type
        , b = k.changeType;
      (0,
        i.useEffect)((function() {
          var e = s.listen(s.EVENT.showHeaderPopUp, (function(e) {
              var t = e || {}
                , n = t.type
                , r = t.isShow;
              "im" === n && r && b()
            }
          ));
          return function() {
            return e()
          }
        }
      ), []),
        (0,
          i.useEffect)((function() {
            "active" === x && (s.emit(s.EVENT.showHeaderPopUp, {
              type: "userDetail",
              isShow: !0
            }),
            null !== f.n && void 0 !== f.n && f.n.loginGuideShowed && f.n.destroy())
          }
        ), [x]);
      var C, N, T, Z = (C = (0,
        i.useState)(!0),
        N = (0,
          g.Z)(C, 2),
        T = N[0],
        N[1],
        T);
      return i.createElement(p.p, {
        headerPopupName: "userDetail"
      }, i.createElement("div", {
        className: l()(u.Z.avataUserCt, u.Z.avataUserMini, w, (0,
          o.Z)({}, u.Z.clientAvataUserCt, _)),
        onMouseEnter: function() {
          b("active")
        },
        onMouseLeave: function() {
          b()
        }
      }, _ ? i.createElement(h.DK, {
        success: t
      }) : i.createElement(h.zV, {
        className: l()((0,
          o.Z)({}, u.Z.springBtnGg, Z && n)),
        isToggleLoginBtn: n,
        displayAvatar: y,
        success: t
      }), i.createElement("div", {
        className: l()(u.Z.dropdownContainer, u.Z.userPanelCollect, (0,
          o.Z)({}, u.Z.active, Boolean(x))),
        onMouseEnter: function() {
          b("active"),
            m.Z.sendLog("personalPanelShow", {
              enter_from: c.vM()
            })
        },
        onMouseLeave: function() {
          b()
        }
      }, i.createElement("ul", null, i.createElement(v.Y, (0,
        r.Z)((0,
        r.Z)({}, {
        secUid: "0",
        isLogin: !1,
        hide: function() {
          return b()
        },
        abtest: E,
        isClient: _
      }), {}, {
        success: t
      }))))))
    }
  }
  ,
  54187: (e,t,n)=>{
    n.d(t, {
      E: ()=>v
    });
    var r = n(65146)
      , o = n(92012)
      , i = n.n(o)
      , a = n(44503)
      , l = n(79705)
      , s = n.n(l)
      , c = n(13079);
    const u = {
      circleButtonWrapper: "l9GtwryL",
      circleButtonWithText: "DK01dqWY",
      textBadge: "B7vr6DkN",
      roundBadge: "XOC_hz4n",
      circleButtonWithTextRoundBadge: "heFN6NVX",
      circleButton: "c5nOy36o",
      circleButtonAvatar: "b0rgKMiD",
      activity: "uHPHXz6B",
      iconContainer: "fFCNku1f",
      vsTransMode: "cSV8EtxW",
      transparent: "MEnqRhJg",
      iconSvg: "F6D9A5IA",
      text: "qwqADnG4",
      imageBadge: "kRW3VB5O",
      circleButtonNoTextImageBadge: "VViuly9K",
      circleButtonWithTextImageBadge: "laUikbz3",
      themeSwitch: "RLtbi3OO",
      dropdownContainer: "nLFiDJQ5",
      active: "UajfwWKs",
      shadowChange: "WNcpRJxY",
      overflowChange: "ebrgo2O0",
      dropDownListInCenterChange: "rBPW0eFj",
      textLinkALink: "taokk4gb",
      conversationDtailAnimationKeyframes: "Qx81pgdz",
      dropDownListInNoCenterChange: "mARZZth7",
      showDeleteAllMessageModal: "UvLDKCT4",
      dropDownListInNoCenterLeftTopChange: "EgDS3Y2Z",
      dropDownListOutChange: "xMmPHqjv"
    };
    var d = n(52255)
      , m = n(16340)
      , v = (0,
      a.memo)((function(e) {
        var t, n, o, l, v = e.activityName, f = e.className, h = e.text, p = e.icon, g = e.iconHeight, y = e.iconViewBox, w = e.showBadge, _ = e.badge, E = e.badgeText, k = e.badgeIconHeight, x = e.badgeIconSvg, b = e.badgeIconViewBox, C = e.badgeIconWidth, N = e.iconWidth, T = e.onClick, Z = e.transparent, S = (0,
          m.Z)().specTheme;
        return a.createElement("div", {
          className: s()(u.circleButtonWrapper, f)
        }, a.createElement("div", {
          onClick: T,
          className: s()(u.circleButton, u.circleButtonWithText, (t = {
            isDark: Boolean(v) || Z
          },
            (0,
              r.Z)(t, u.activity, Boolean(v) || Z),
            (0,
              r.Z)(t, null == u ? void 0 : u[v], v),
            (0,
              r.Z)(t, u.transparent, Z),
            t), f),
          "data-e2e": "something-button"
        }, a.createElement("div", {
          className: u.iconContainer
        }, a.createElement(d.Z, {
          src: globalThis.getFilterXss().filterUrl(p, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: N,
          height: g,
          viewBox: y || i()(n = "0 0 ".concat(N, " ")).call(n, g),
          className: u.iconSvg
        })), a.createElement("p", {
          className: u.text
        }, h)), w && ("text" === _ || "round" === _) && a.createElement(c.C, {
          className: s()((o = {},
            (0,
              r.Z)(o, u.textBadge, "text" === _),
            (0,
              r.Z)(o, u.roundBadge, "round" === _),
            (0,
              r.Z)(o, u.circleButtonWithTextRoundBadge, "round" === _),
            o)),
          type: _,
          text: "text" === _ ? E || h : ""
        }), w && "image" === _ && a.createElement("div", {
          className: s()(u.imageBadge, u.circleButtonWithTextImageBadge, (0,
            r.Z)({}, u.themeSwitch, null == S ? void 0 : S.themeSwitch))
        }, a.createElement(d.Z, {
          src: globalThis.getFilterXss().filterUrl(x, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: C,
          height: k,
          viewBox: b || i()(l = "0 0 ".concat(C, " ")).call(l, k)
        })))
      }
    ))
  }
  ,
  28796: (e,t,n)=>{
    n.d(t, {
      Z: ()=>J
    });
    var r = n(65146)
      , o = n(30906)
      , i = n(32781)
      , a = n(92637)
      , l = n.n(a)
      , s = n(44503)
      , c = n(79705)
      , u = n.n(c)
      , d = n(24260)
      , m = n(52172)
      , v = n(14484)
      , f = n(25083)
      , h = n(37541)
      , p = n(92557)
      , g = n(78867)
      , y = n(10387)
      , w = n(20445)
      , _ = n(41967)
      , E = n(1946)
      , k = n(35709)
      , x = n(85922)
      , b = n(90147)
      , C = n(2758)
      , N = n(54187)
      , T = n(58801)
      , Z = n(36788)
      , S = n(1392)
      , I = n(69234)
      , L = n(51382)
      , D = n(58704)
      , M = n(73969)
      , B = n(57023)
      , A = n(14737)
      , P = n(47285)
      , O = n(12164)
      , V = n(85284)
      , W = n(88848)
      , R = n(17705)
      , F = n(92253)
      , U = n(59750)
      , H = n(91548)
      , G = n(80714)
      , j = n(26867)
      , K = (0,
      d.default)({
      resolved: {},
      chunkName: function() {
        return "NoticeEntry"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(5234), n.e(5590)]).then(n.bind(n, 75234))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 75234
      }
    }, {
      ssr: !1
    })
      , q = (0,
      d.default)({
      resolved: {},
      chunkName: function() {
        return "ImEntry"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(4490), n.e(9707), n.e(5019), n.e(6780)]).then(n.bind(n, 34490))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 34490
      }
    }, {
      ssr: !1
    })
      , Y = (0,
      d.default)({
      resolved: {},
      chunkName: function() {
        return "electronInject"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(2520), n.e(8617)]).then(n.bind(n, 83484))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 83484
      }
    }, {
      resolveComponent: function(e) {
        return e.ReturnToMainWindow
      }
    })
      , X = (0,
      d.default)({
      resolved: {},
      chunkName: function() {
        return "electronInject"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(2520), n.e(8617)]).then(n.bind(n, 24819))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 24819
      }
    }, {
      resolveComponent: function(e) {
        return e.WindowToolBar
      }
    })
      , z = (0,
      d.default)({
      resolved: {},
      chunkName: function() {
        return "electronInject"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(2520), n.e(8617)]).then(n.bind(n, 19204))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 19204
      }
    }, {
      resolveComponent: function(e) {
        return e.NewWallpaper
      }
    });
    function Q(e) {
      var t, n = e.isLogin, a = e.abTestData, c = e.info, d = e.customProps, Q = e.uid, J = e.secUid, $ = e.avatarUrl, ee = e.awemeCount, te = e.favoritingCount, ne = e.awemeCollectCount, re = e.success, oe = e.transparent, ie = a.collectionGuide, ae = (0,
        D.r)(), le = ae.shouldShowBackToHome, se = ae.inVideoDetailPage, ce = ae.inNoteDetailPage, ue = (0,
        s.useState)(!1), de = (0,
        i.Z)(ue, 2), me = de[0], ve = de[1], fe = d.isClient, he = d.landingPage, pe = d.os, ge = d.activityName, ye = m.a.useIsMainWindowDetect(), we = (0,
        j.Z)({
        isClient: fe,
        abTestData: a,
        osInfo: pe
      }).newWallpaperShow, _e = (0,
        A.GZ)({
        isLogin: n
      }), Ee = _e.onDownloadGuideEnter, ke = _e.onDownloadGuideLeave, xe = _e.show, be = _e.downloadPWA, Ce = _e.withClose, Ne = _e.withEffect, Te = _e.shouldShowGuideType, Ze = _e.clientDownloadHref, Se = _e.clientDownloadAttr, Ie = _e.showDownloadGuide, Le = _e.hideDownloadGuide, De = _e.onDownloadGuideEntryEnter, Me = _e.onDownloadGuideEntryLeave, Be = _e.onDownloadGuideVisibleChange, Ae = _e.showType, Pe = _e.showClientBadge, Oe = Boolean(me || !(null != a && a.click2Download)), Ve = Oe ? v.rV() : Ze, We = !Oe && Se, Re = Oe ? "_blank" : "_self";
      (0,
        s.useEffect)((function() {
          return ve(/live/.test(location.host))
        }
      ), []),
        (0,
          U.c)(fe, Q, J, n);
      var Fe = (0,
        H.u)(n)
        , Ue = Fe.postDropdownItems
        , He = Fe.cooperationDropdownItems;
      (0,
        s.useEffect)((function() {
          return Pe && S.Z.sendLog("addToDesktopBadgeShow", {
            enter_from: f.vM()
          })
        }
      ), [Pe]);
      var Ge = (0,
        M._)().inMiniScreen
        , je = (0,
        s.useCallback)((function() {
          S.Z.sendLog("feedClick", {
            enter_from: se || ce ? "video_detail" : "personal_homepage"
          }),
            window.location.href = globalThis.getFilterXss().filterUrl("https://".concat(b.HOME_DOMAIN), null, {
              logType: "js.window.location",
              reportOnly: !1
            })
        }
      ), [se, ce])
        , Ke = (0,
        O.j)(ie, n)
        , qe = (0,
        O.s)(Q, n, !0)
        , Ye = qe.onCollectionGuideEnter
        , Xe = qe.onCollectionGuideLeave
        , ze = qe.collectionPanelVisible
        , Qe = (0,
        s.useMemo)((function() {
          var e;
          return l()(e = [le ? (0,
            o.Z)((0,
            o.Z)({}, I.j.backToHome), {}, {
            type: "textLink",
            onClick: je
          }) : void 0, Ke ? (0,
            o.Z)((0,
            o.Z)({}, I.j.collectionGuide), {}, {
            type: "textLink",
            onMouseEnter: Ye,
            onMouseLeave: Xe,
            children: [s.createElement("div", {
              className: C.Z.hoverToShowMiniDownloadGuideContainer,
              key: "downloadMenuInMiniscreen"
            }, s.createElement("div", {
              className: C.Z.hoverToShowMiniDownloadGuide,
              key: "downloadMenuInMiniscreen"
            }, ze && s.createElement(P.g, {
              collectionGuideType: ie
            })))]
          }) : void 0, (0,
            o.Z)((0,
            o.Z)({}, I.j.cooperation), {}, {
            type: "textLink",
            items: He,
            trigger: "hover",
            itemsContainerClassName: C.Z.miniScreenCooperationDropdownContainer,
            onMouseEnter: function() {
              S.Z.sendLog("cooperatePanelShow", {
                enter_from: f.mo()
              })
            }
          }), (0,
            o.Z)((0,
            o.Z)((0,
            o.Z)({}, I.j.downloadClient), {}, {
            type: "textLink",
            onMouseEnter: De,
            onMouseLeave: Me
          }, me || null == a || !a.click2Download ? {
            onClick: function() {
              return window.open((0,
                v.rV)())
            }
          } : {
            url: Ze,
            downloadAttr: Se,
            target: "_self",
            onClick: function() {
              return S.Z.sendLog("addToDesktopClick", {
                enter_from: (0,
                  S.v)(),
                is_full_screen: h.r() ? "1" : "0",
                type: "icon",
                platform: Te === A.xj.PWA ? "pwa" : "client"
              })
            }
          }), {}, {
            children: [s.createElement("div", {
              className: C.Z.hoverToShowMiniDownloadGuideContainer,
              key: "downloadMenuInMiniscreen"
            }, s.createElement("div", {
              className: C.Z.hoverToShowMiniDownloadGuide,
              key: "downloadMenuInMiniscreen"
            }, xe && s.createElement(B.E6, (0,
              o.Z)({
              isLogin: n
            }, {
              downloadPWA: be,
              withClose: Ce,
              withEffect: Ne,
              clientDownloadAttr: Se,
              showType: Ae,
              shouldShowGuideType: Te,
              clientDownloadHref: Ze,
              showDownloadGuide: Ie,
              onClose: Le
            }))))]
          })]).call(e, (function(e) {
              return e
            }
          ))
        }
      ), [He, le, je, n, be, Ce, Ne, Te, Ze, Ie, Le, xe, De, Me, Ae, Se, ze, Ye, Xe, Ke, ie, me, null == a ? void 0 : a.click2Download]);
      (0,
        s.useEffect)((function() {
          return p.listen(p.EVENT.showHeaderPopUp, (function(e) {
              return "post" === (null == e ? void 0 : e.type) && !0 === (null == e ? void 0 : e.isShow) && S.Z.sendLog("publishPanelShow", {
                enter_from: f.vM()
              })
            }
          ))
        }
      ), []);
      var Je = (0,
        s.useCallback)((function() {
          var e, t, n = null === (e = l()(Ue).call(Ue, (function(e) {
              return "publish" === e.key
            }
          ))) || void 0 === e ? void 0 : e[0];
          null == n || null === (t = n.onClick) || void 0 === t || t.call(n),
          (null == n ? void 0 : n.url) && window.open(n.url, "_blank")
        }
      ), [Ue])
        , $e = (0,
        W.u)({
        initImSDK: !1,
        initNoticeSDK: !1
      })
        , et = $e.initImSDK
        , tt = $e.initNoticeSDK
        , nt = $e.setInitImSDK
        , rt = $e.setNoticeSDK;
      return s.createElement("div", {
        className: u()(C.Z.newHeaderContainer, C.Z.buttonWithTextContainer, (0,
          r.Z)({}, C.Z.clientHeaderContainer, fe))
      }, fe && !ye && s.createElement(R.r, null, s.createElement(Y, {
        transparent: oe
      })), !fe && Ge && s.createElement("div", {
        className: C.Z.menuItem
      }, s.createElement(G.p, {
        headerPopupName: "more"
      }, s.createElement(L.Y, {
        text: "\u66f4\u591a",
        type: "circleButtonWithText",
        avatarUrl: k.Z,
        activityName: ge,
        avatarHeight: 12.44,
        avatarWidth: 12.44,
        viewBox: "0.5 0.5 13 13",
        trigger: "hover",
        items: Qe,
        itemsContainerClassName: u()(C.Z.miniScreenCooperationDropdownContainerFirstLevel, (0,
          r.Z)({}, C.Z.inPageWithBackToHome, le)),
        headerPopupName: "more",
        transparent: oe
      }))), !fe && !Ge && s.createElement(s.Fragment, null, s.createElement(F.J, {
        position: "bottom",
        visible: xe,
        onVisibleChange: Be,
        mouseEnterDelay: 100,
        mouseLeaveDelay: 200,
        content: s.createElement("div", {
          onMouseEnter: Ee,
          onMouseLeave: ke
        }, s.createElement(B.E6, (0,
          o.Z)({
          isLogin: n
        }, {
          downloadPWA: be,
          withClose: Ce,
          withEffect: Ne,
          showType: Ae,
          shouldShowGuideType: Te,
          clientDownloadHref: Ze,
          clientDownloadAttr: Se,
          showDownloadGuide: Ie,
          onClose: Le
        })))
      }, s.createElement("div", {
        className: C.Z.menuItem
      }, s.createElement(G.p, {
        headerPopupName: "client"
      }, s.createElement("a", {
        href: globalThis.getFilterXss().filterUrl(Ve, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        download: We,
        target: Re,
        onClick: function() {
          S.Z.sendLog("addToDesktopClick", {
            enter_from: (0,
              S.v)(),
            is_full_screen: h.r() ? "1" : "0",
            type: "icon",
            platform: Te === A.xj.PWA ? "pwa" : "client"
          })
        }
      }, s.createElement(N.E, {
        activityName: null == d ? void 0 : d.activityName,
        text: "\u5ba2\u6237\u7aef",
        icon: _.Z,
        iconWidth: 15,
        iconHeight: 12.16,
        iconViewBox: "0 -0.5 18.83 12.91",
        showBadge: Pe,
        badge: "image",
        badgeIconSvg: x.Z,
        badgeIconHeight: 15,
        badgeIconWidth: 28,
        badgeIconViewBox: "0 0 28 15",
        transparent: oe
      }))))), le && s.createElement("div", {
        className: u()(C.Z.menuItem, C.Z.goToRecommendTipWrapper)
      }, s.createElement("div", {
        className: C.Z.goToRecommendTip
      }, s.createElement("div", {
        className: C.Z.delta
      }), "\u70b9\u51fb\u8fd9\u91cc\u524d\u5f80\u63a8\u8350\u9875\uff0c\u89c6\u9891\u66f4\u597d\u770b"), s.createElement(L.Y, {
        text: "\u63a8\u8350",
        type: "circleButtonWithText",
        avatarUrl: y.Z,
        avatarHeight: 10.9,
        avatarWidth: 12,
        viewBox: "0 0 14 12.9",
        activityName: null == d ? void 0 : d.activityName,
        onClick: je,
        transparent: oe
      })), Ke && s.createElement("div", {
        className: C.Z.menuItem
      }, s.createElement(G.p, {
        headerPopupName: "collection"
      }, s.createElement(P.z, {
        activityName: null == d ? void 0 : d.activityName,
        isLogin: n,
        uid: Q,
        collectionGuideType: ie,
        transparent: oe
      }))), s.createElement("div", {
        className: C.Z.menuItem
      }, s.createElement(G.p, {
        headerPopupName: "cooperation"
      }, s.createElement(L.Y, {
        text: "\u5408\u4f5c",
        type: "circleButtonWithText",
        avatarUrl: w.Z,
        activityName: null == d ? void 0 : d.activityName,
        avatarHeight: 10.9,
        avatarWidth: 12,
        trigger: "hover",
        items: He,
        itemsContainerClassName: C.Z.dropdownContainer,
        onMouseEnter: function() {
          S.Z.sendLog("cooperatePanelShow", {
            enter_from: f.mo()
          })
        },
        headerPopupName: "cooperation",
        transparent: oe
      })))), we && s.createElement(z, {
        abTestData: a,
        transparent: oe,
        isClient: fe,
        activityName: null == d ? void 0 : d.activityName
      }), tt && s.createElement("ul", {
        className: C.Z.menuItem,
        onMouseEnter: function() {
          rt(!0)
        }
      }, s.createElement(G.p, null, (null == a ? void 0 : a.imAsyncLoadLoginOnly) !== g.ImAsyncLoadLoginOnly.On || n ? s.createElement(K, {
        customProps: {
          isActivity: null == d ? void 0 : d.isActivity,
          activityName: null == d ? void 0 : d.activityName
        },
        className: C.Z.menuItemContent,
        isLogin: n,
        abTestData: a,
        uInfo: c,
        initNoticeSDK: tt,
        transparent: oe
      }) : s.createElement(V.M, {
        customProps: {
          isActivity: null == d ? void 0 : d.isActivity,
          activityName: null == d ? void 0 : d.activityName
        },
        transparent: oe
      }))), et && s.createElement("ul", {
        className: C.Z.menuItem,
        onMouseEnter: function() {
          nt(!0)
        }
      }, s.createElement(G.p, null, (null == a ? void 0 : a.imAsyncLoadLoginOnly) !== g.ImAsyncLoadLoginOnly.On || n ? s.createElement(q, {
        isLogin: n,
        abTestData: a,
        uInfo: c,
        className: C.Z.menuItemContent,
        customProps: {
          isActivity: null == d ? void 0 : d.isActivity,
          activityName: null == d ? void 0 : d.activityName
        },
        initImSDK: et,
        transparent: oe
      }) : s.createElement(V.R, {
        customProps: {
          isActivity: null == d ? void 0 : d.isActivity,
          activityName: null == d ? void 0 : d.activityName
        },
        transparent: oe
      }))), s.createElement("div", {
        className: C.Z.menuItem
      }, s.createElement(G.p, {
        headerPopupName: "post"
      }, s.createElement(L.Y, {
        text: "\u6295\u7a3f",
        type: "circleButtonWithText",
        avatarUrl: E.Z,
        activityName: null == d ? void 0 : d.activityName,
        avatarHeight: 10,
        avatarWidth: 13,
        viewBox: "0 0 12.65 10",
        trigger: "hover",
        items: Ue,
        itemsContainerClassName: C.Z.dropdownContainer,
        headerPopupName: "post",
        onClick: Je,
        transparent: oe
      }))), s.createElement("div", {
        className: u()(C.Z.verticalDivider, (t = {},
          (0,
            r.Z)(t, null === C.Z || void 0 === C.Z ? void 0 : C.Z[null == d ? void 0 : d.activityName], null == d ? void 0 : d.activityName),
          (0,
            r.Z)(t, C.Z.transparent, oe),
          (0,
            r.Z)(t, C.Z.hidden, fe),
          t))
      }), n && s.createElement(T.a, (0,
        o.Z)({}, {
        uid: Q,
        secUid: J,
        avatarUrl: $,
        awemeCount: ee,
        favoritingCount: te,
        awemeCollectCount: ne,
        className: C.Z.isLogin,
        isClient: fe,
        abtest: a
      })), !n && void 0 !== n && Ge && s.createElement(Z.T, (0,
        o.Z)({}, {
        isToggleLoginBtn: !1,
        success: re,
        displayAvatar: !1,
        abtest: a,
        className: u()(C.Z.avataUserMini, C.Z.isLogout, C.Z.miniScreen),
        isClient: fe
      })), !n && void 0 !== n && !Ge && s.createElement(Z.T, (0,
        o.Z)((0,
        o.Z)({}, {
        isToggleLoginBtn: !0,
        success: re,
        isClient: fe,
        abtest: a
      }), {}, {
        className: C.Z.isLogout
      })), Ae === A.KK.Auto && s.createElement("div", {
        className: C.Z.miniScreen
      }, Ge && xe && s.createElement("div", {
        className: C.Z.fixedToHeaderBelow
      }, s.createElement("div", {
        className: C.Z.miniScreenDownloadGuideContainer
      }, s.createElement(B.E6, (0,
        o.Z)({
        isLogin: n,
        isShow: xe
      }, {
        showType: Ae,
        downloadPWA: be,
        withClose: Ce,
        withEffect: Ne,
        shouldShowGuideType: Te,
        clientDownloadAttr: Se,
        clientDownloadHref: Ze,
        showDownloadGuide: Ie,
        onClose: Le
      }))))), fe && s.createElement(X, (0,
        o.Z)({}, {
        osInfo: pe,
        abTestData: a,
        isLogin: n,
        landingPage: he
      })))
    }
    function J(e) {
      var t, n, i = e.success, a = e.userInfo, c = e.showYear100, d = e.abTestData, m = e.customProps, v = e.transparent, f = a || {}, h = f.isLogin, p = f.info, g = p || {}, y = g.avatarUrl, w = g.secUid, _ = g.awemeCount, E = void 0 === _ ? 0 : _, k = g.favoritingCount, x = void 0 === k ? 0 : k, b = g.userCollectCount, N = void 0 === b ? {} : b, T = g.uid, Z = void 0 === T ? "" : T, S = null == N || null === (t = N.collectCountList) || void 0 === t ? void 0 : l()(t).call(t, (function(e) {
          return 2 === e.itemType
        }
      ))[0], I = null !== (n = null == S ? void 0 : S.collectCount) && void 0 !== n ? n : 0;
      return s.createElement("div", {
        className: u()((0,
          r.Z)({}, C.Z.year100, c))
      }, s.createElement(Q, (0,
        o.Z)({}, {
        isLogin: h,
        abTestData: d,
        info: p,
        customProps: m,
        uid: Z,
        secUid: w,
        avatarUrl: y,
        awemeCount: E,
        favoritingCount: x,
        awemeCollectCount: I,
        success: i,
        transparent: v
      })))
    }
  }
  ,
  30410: (e,t,n)=>{
    n.d(t, {
      Y: ()=>he
    });
    var r = n(65146)
      , o = n(64408)
      , i = n(30906)
      , a = n(32781)
      , l = n(92637)
      , s = n.n(l)
      , c = n(94610)
      , u = n.n(c)
      , d = n(5594)
      , m = n.n(d)
      , v = n(44503)
      , f = n(79705)
      , h = n.n(f)
      , p = n(78867)
      , g = n(72983)
      , y = n(52252)
      , w = n(53607)
      , _ = n(14484)
      , E = n(25083)
      , k = n(85938)
      , x = n(43478)
      , b = n(90414)
      , C = n(68094)
      , N = n(51652)
      , T = n(90147)
      , Z = n(70038)
      , S = n(72389)
      , I = n(78595)
      , L = n(89784)
      , D = n(88287);
    const M = "QYL6YoEb"
      , B = "xOYQgf3L"
      , A = "de0WAGYo"
      , P = "kDmWiWzh"
      , O = "pMBwmxGS"
      , V = "HAR_KXpk"
      , W = "KTBfvwdu"
      , R = "wiqwDybA"
      , F = "OBTB5uUk"
      , U = "rkXLBN0o"
      , H = "M47JrU_f"
      , G = "n9pk1U7S"
      , j = "dRK46_Ne"
      , K = "rXIy1Pzb"
      , q = "ZjthpVf3"
      , Y = "lI8OjXhd";
    var X = n(66301)
      , z = n(95881)
      , Q = n(14001)
      , J = n(1392)
      , $ = n(52255)
      , ee = n(69234)
      , te = n(21857)
      , ne = n.n(te)
      , re = n(61936)
      , oe = n(92557)
      , ie = n(3345)
      , ae = n(16655);
    const le = "Ox4lnVeA"
      , se = "AalWIHiD";
    var ce = n(92024)
      , ue = function() {
      var e = N
        , t = e.CookieKeys
        , n = e.ThemeValues
        , r = oe.EVENT
        , o = w.Q.getItem({
        sKey: t.Theme
      })
        , i = k.Dr(o) === n.Dark
        , l = (0,
        v.useState)(i)
        , s = (0,
        a.Z)(l, 2)
        , c = s[0]
        , u = s[1];
      return (0,
        v.useEffect)((function() {
          (0,
            ce.Ly)(c),
            oe.emit(r.changeTheme, {
              theme: c ? n.Dark : n.Light
            })
        }
      ), [c]),
        v.createElement("div", {
          className: le,
          onClick: function() {
            (0,
              ce.c4)(!c),
              (0,
                ce.Ly)(!c),
            "undefined" != typeof localStorage && localStorage.setItem("ELECTRON_THEME_KEY", c ? "" : "DARK"),
            (0,
              ae.DT)() && ne().app.themeChange({
              isDark: !c
            }),
              re.i.sendLog("changeThemeSetting", {
                theme: c ? n.Light : n.Dark,
                enter_from: E.yW()
              }),
              u((function(e) {
                  return !e
                }
              ))
          }
        }, v.createElement($.Z, {
          src: globalThis.getFilterXss().filterUrl(ie.Z, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 24.7,
          height: 20.3,
          viewBox: "0 0 22 19"
        }), v.createElement("span", {
          className: se
        }, "\u6362\u80a4"))
    }
      , de = n(53494)
      , me = n(36408)
      , ve = n(26637)
      , fe = y.p() ? null : w.Q;
    function he(e) {
      var t, n, l = e.awemeCount, c = e.favoritingCount, d = e.awemeCollectCount, f = e.secUid, y = e.isLogin, w = e.success, te = e.hide, ne = e.isActive, re = e.abtest, oe = e.isClient, ie = (0,
        v.useState)(!1), ae = (0,
        a.Z)(ie, 2), le = ae[0], se = ae[1], ce = (0,
        ve.o)(null !== (t = null == re ? void 0 : re.hasHorizontalHeader) && void 0 !== t ? t : p.HasHorizontalHeader.Default, oe).isHorizontalLayout, he = [{
        key: "post",
        iconSvg: Z.Z,
        title: "\u6211\u7684\u4f5c\u54c1",
        count: l,
        clickPosition: "post",
        clickToLogin: (0,
          X.UC)((null == re ? void 0 : re.selfTab) > 0 && ce ? (0,
          X.qR)(w, "post", ce) : (0,
          X.Tf)(w, "post"), "\u767b\u5f55\u5373\u53ef\u67e5\u770b\u201c\u6211\u7684\u4f5c\u54c1\u201d", {
          enter_method: "panel_post"
        })
      }, {
        key: "like",
        iconSvg: S.Z,
        title: "\u6211\u7684\u559c\u6b22",
        count: c,
        clickPosition: "like",
        clickToLogin: (0,
          X.UC)((null == re ? void 0 : re.selfTab) > 0 && ce ? (0,
          X.qR)(w, "like", ce) : (0,
          X.Tf)(w, "like"), "\u767b\u5f55\u5373\u53ef\u67e5\u770b\u201c\u6211\u7684\u559c\u6b22\u201d", {
          enter_method: "panel_like"
        })
      }, {
        key: "favorite_collection",
        iconSvg: I.Z,
        title: "\u6211\u7684\u6536\u85cf",
        count: d,
        clickPosition: "favorite_collection",
        clickToLogin: (0,
          X.UC)((null == re ? void 0 : re.selfTab) > 0 && ce ? (0,
          X.qR)(w, "favorite_collection", ce) : (0,
          X.Tf)(w, "favorite_collection"), "\u767b\u5f55\u5373\u53ef\u67e5\u770b\u201c\u6211\u7684\u6536\u85cf\u201d", {
          enter_method: "panel_favotite"
        })
      }, {
        key: "record",
        iconSvg: L.Z,
        title: "\u89c2\u770b\u5386\u53f2",
        count: 0,
        clickPosition: "record",
        clickToLogin: (0,
          X.UC)((null == re ? void 0 : re.selfTab) > 0 && ce ? (0,
          X.qR)(w, "record", ce) : (0,
          X.Tf)(w, "record"), "\u767b\u5f55\u5373\u53ef\u67e5\u770b\u201c\u89c2\u770b\u5386\u53f2\u201d", {
          enter_method: "panel_record"
        })
      }], pe = [(0,
        i.Z)((0,
        i.Z)({}, ee.j.homepage), {}, {
        url: y ? _.HC((null == re ? void 0 : re.selfTab) > 0 && ce ? "self" : f, "enter_method=personal_panel") : "",
        isLogin: y,
        onClick: function() {
          J.Z.sendLog("personalPanelClick", {
            enter_from: E.vM(),
            click_position: "personal_homepage"
          }),
          null == te || te()
        },
        target: null != re && re.selfTab && ce ? "_self" : "_blank",
        jumpAfterLogin: !1,
        loginSuccess: (null == re ? void 0 : re.selfTab) > 0 && ce ? (0,
          X.qR)(w, "record", ce) : (0,
          X.Tf)(w, "record")
      }), (0,
        i.Z)((0,
        i.Z)({}, ee.j.recharge), {}, {
        onClick: te
      }), (0,
        i.Z)((0,
        i.Z)({}, ee.j.liveMate), {}, {
        isLogin: y,
        loginSuccess: w,
        onClick: te
      })], ge = k.Bj(E.yW()), ye = function(e) {
        fe.setItem("LOGIN_STATUS", 0, 1 / 0, "/", "douyin.com", ""),
          e.preventDefault(),
          x.JB(),
          x.kS(location.href),
          J.Z.sendLog("clickLogOut", {
            enter_from: E.vM()
          }),
        null == te || te()
      }, we = function() {
        var e = (0,
          o.Z)(m().mark((function e(t) {
            var n, r;
            return m().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      if (n = b.$o(N.LocalStorageKeys.HasLogoutShow),
                      1 !== b.$o(N.LocalStorageKeys.IsAllowTrust)) {
                        e.next = 7;
                        break
                      }
                      ye(t),
                        e.next = 18;
                      break;
                    case 7:
                      return e.next = 9,
                        g.h.getVar({
                          name: "trust_dialog_freq",
                          defaultValue: 0
                        });
                    case 9:
                      if (r = e.sent,
                      !le || (0 !== r || 1 === n) && 1 !== r) {
                        e.next = 17;
                        break
                      }
                      return b.qQ(N.LocalStorageKeys.HasLogoutShow, 1),
                        (0,
                          de.w)({
                          confirmHandler: function() {
                            ye(t)
                          },
                          cancelHandler: function() {
                            ye(t)
                          },
                          showWay: "logout"
                        }),
                        e.abrupt("return");
                    case 17:
                      ye(t);
                    case 18:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }();
      return y && pe.push((0,
        i.Z)((0,
        i.Z)({}, ee.j.logout), {}, {
        isLogin: y,
        onClick: function(e) {
          we(e)
        }
      })),
      (0,
        D.X)() && (pe = s()(pe).call(pe, (function(e) {
          return "doubi_recharge" !== e.key
        }
      ))),
        (0,
          v.useEffect)((function() {
            document.domain !== T.LIVE_DOMAIN && g.h.getVar({
              name: "is_allow_trust",
              defaultValue: 0
            }).then((function(e) {
                se(Boolean(e))
              }
            ))
          }
        ), []),
        v.createElement("div", {
          className: h()(M)
        }, !y && v.createElement("p", {
          className: B
        }, "\u767b\u5f55\u540e\u5373\u53ef\u89c2\u770b\u559c\u6b22\u3001\u6536\u85cf\u7684\u89c6\u9891"), y && le && v.createElement("div", {
          className: h()(A)
        }, v.createElement("div", {
          className: h()(P)
        }, (null === (n = b.$o(N.LocalStorageKeys.UserInfo)) || void 0 === n ? void 0 : n.nickname) || "\u672a\u77e5"), ne ? v.createElement(me.Z, {
          pageIndex: "personal_panel"
        }) : null), v.createElement("ul", {
          className: O
        }, u()(he).call(he, (function(e, t) {
            return v.createElement("ul", {
              key: e.key,
              className: V
            }, y ? v.createElement(Q.a, {
              rel: "noopener noreferrer",
              href: globalThis.getFilterXss().filterUrl(_.HC((null == re ? void 0 : re.selfTab) > 0 && ce ? "self" : f, "showTab=".concat(e.key, "&enter_method=personal_panel")), null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              target: (null == re ? void 0 : re.selfTab) > 0 && ce ? "_self" : "_blank",
              onClick: function() {
                J.Z.sendLog("personalPanelClick", {
                  enter_from: E.vM(),
                  click_position: e.clickPosition || e.key
                }),
                null == te || te()
              }
            }, v.createElement("li", {
              className: W,
              "data-e2e": "usermsg-item"
            }, v.createElement($.Z, {
              width: 32,
              height: 32,
              src: globalThis.getFilterXss().filterUrl(e.iconSvg, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              viewBox: "0 0 32 32",
              className: Y
            }), v.createElement("p", {
              className: F
            }, "record" === e.key ? v.createElement("span", null, "30") : C.qe(e.count), "record" === e.key ? v.createElement("span", {
              className: U
            }, "\u5929\u5185") : void 0), v.createElement("p", {
              className: R
            }, e.title))) : v.createElement("div", {
              onClick: function(t) {
                J.Z.sendLog("personalPanelClick", {
                  enter_from: E.vM(),
                  click_position: e.clickPosition || e.key
                }),
                  e.clickToLogin(t),
                null == te || te()
              }
            }, v.createElement("li", {
              className: h()(W, H)
            }, v.createElement($.Z, {
              width: 32,
              height: 32,
              src: globalThis.getFilterXss().filterUrl(e.iconSvg, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              viewBox: "0 0 32 32",
              className: Y
            }), v.createElement("p", {
              className: R
            }, e.title))), t !== he.length - 1 && v.createElement("div", {
              className: G
            }))
          }
        ))), v.createElement(z.i, null), v.createElement("ul", {
          className: h()(j, (0,
            r.Z)({}, q, !y))
        }, u()(pe).call(pe, (function(e) {
            return v.createElement("li", {
              key: e.key
            }, v.createElement(ee.h, (0,
              i.Z)({}, e)))
          }
        )), !ge && v.createElement("div", {
          className: K
        }, v.createElement(ue, null))))
    }
  }
  ,
  17705: (e,t,n)=>{
    n.d(t, {
      r: ()=>l
    });
    var r = n(32781)
      , o = n(44503)
      , i = n(21857)
      , a = n.n(i)
      , l = function(e) {
      var t = e.children
        , n = o.useState(!1)
        , i = (0,
        r.Z)(n, 2)
        , l = i[0]
        , s = i[1];
      return o.useEffect((function() {
          s(!0),
            a().app.handlePageReady()
        }
      ), []),
        l ? t : null
    }
  }
  ,
  83484: (e,t,n)=>{
    n.r(t),
      n.d(t, {
        ReturnButton: ()=>C,
        ReturnToMainWindow: ()=>N
      });
    var r = n(65146)
      , o = n(32781)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a)
      , s = n(21857)
      , c = n.n(s)
      , u = n(16655)
      , d = n(59505)
      , m = n(25083)
      , v = n(10014);
    const f = "A2WRPAeV"
      , h = "IPKap7uO"
      , p = "FQO_2z92"
      , g = "LZZr1cWF"
      , y = "Whkn0rwo"
      , w = "lwgi4rmB";
    var _;
    function E() {
      return E = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        E.apply(this, arguments)
    }
    const k = function(e) {
      return i.createElement("svg", E({
        width: 20,
        height: 20,
        viewBox: "0 0 20 20",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), _ || (_ = i.createElement("path", {
        d: "M7 3l-6 7 6 7",
        stroke: "#2F3035",
        strokeWidth: 2,
        strokeLinecap: "round",
        strokeLinejoin: "round"
      })))
    };
    var x = n(52255)
      , b = n(1392);
    function C(e) {
      var t = e.transparent
        , n = (0,
        i.useState)(!0)
        , a = (0,
        o.Z)(n, 2)
        , s = a[0]
        , g = a[1]
        , y = (0,
        i.useRef)("");
      (0,
        i.useEffect)((function() {
          var e, t, n, r, o;
          y.current = null !== (e = u.FJ().awemePcClient) && void 0 !== e ? e : "";
          var i = "ACTIVITY_WINDOW" === (null !== (t = null === (n = window.TTE_ENV) || void 0 === n || null === (r = n.initPageStore) || void 0 === r || null === (o = r.window) || void 0 === o ? void 0 : o.name) && void 0 !== t ? t : "");
          g(d.y(y.current, ">", "1.0.6")),
          i && g(!1)
        }
      ), []);
      return s ? i.createElement("div", {
        className: l()(f, (0,
          r.Z)({}, p, t)),
        onClick: function() {
          if (b.Z.sendLog("clickReturnPage", {
            enter_from: m.vM()
          }),
            d.y(y.current, ">=", "1.2.0"))
            c().app.navigationGoBack();
          else if (s) {
            var e;
            null === (e = c().app.canGoBack()) || void 0 === e || e.then((function(e) {
                e.data ? c().app.goBack() : v.F.info("\u5df2\u9000\u5230\u6700\u540e\u5566~")
              }
            )).catch((function(e) {
                v.F.info("\u5df2\u9000\u5230\u6700\u540e\u5566~")
              }
            ))
          }
        }
      }, i.createElement(x.Z, {
        width: 20,
        height: 20,
        viewBox: "-5 0 20 20",
        className: l()(h),
        src: globalThis.getFilterXss().filterUrl(k, null, {
          logType: "js.href/src",
          reportOnly: !1
        })
      })) : null
    }
    function N(e) {
      var t = e.transparent;
      return i.createElement("div", {
        onClick: function() {
          b.Z.sendLog("clickMainPage", {
            enter_from: m.vM()
          }),
            c().app.mainWindowMoveTop()
        },
        className: l()(g, (0,
          r.Z)({}, p, t))
      }, i.createElement("div", {
        className: l()(y)
      }), i.createElement("div", {
        className: l()(w)
      }, "\u4e3b\u9875"))
    }
  }
  ,
  66301: (e,t,n)=>{
    n.d(t, {
      Tf: ()=>f,
      qR: ()=>h,
      UC: ()=>p
    });
    var r = n(64408)
      , o = n(92012)
      , i = n.n(o)
      , a = n(5594)
      , l = n.n(a)
      , s = n(44503)
      , c = n(53246)
      , u = n(14484)
      , d = n(36862)
      , m = n(36539)
      , v = n(4592);
    function f(e, t, n) {
      return (0,
        r.Z)(l().mark((function n() {
          var r, o, i = arguments;
          return l().wrap((function(n) {
              for (; ; )
                switch (n.prev = n.next) {
                  case 0:
                    return n.prev = 0,
                      n.next = 3,
                      c.b();
                  case 3:
                    o = n.sent,
                      window.open(u.HC(null == o || null === (r = o.user) || void 0 === r ? void 0 : r.secUid, "showTab=".concat(t, "&enter_method=personal_panel")), "_blank"),
                      n.next = 9;
                    break;
                  case 7:
                    n.prev = 7,
                      n.t0 = n.catch(0);
                  case 9:
                    "Function" === d.tQ(e) && e.apply(void 0, i);
                  case 10:
                  case "end":
                    return n.stop()
                }
            }
          ), n, null, [[0, 7]])
        }
      )))
    }
    function h(e, t, n) {
      return function() {
        try {
          window.open(u.HC("self", "showTab=".concat(t, "&enter_method=personal_panel")), n ? "_self" : "_blank")
        } catch (r) {}
        !n && "Function" === d.tQ(e) && e.apply(void 0, arguments)
      }
    }
    function p(e, t, r) {
      return (0,
        s.useCallback)((function(o) {
          o.preventDefault(),
            n.e(1674).then(n.bind(n, 61674)).then((function(n) {
                var o, a, l;
                (0,
                  n.navShowAccount)({
                  success: e,
                  enterMethod: "navigation_bar",
                  next: i()(o = "".concat(null == m ? void 0 : v.tJ)).call(o, null === (a = window) || void 0 === a || null === (l = a.location) || void 0 === l ? void 0 : l.host),
                  headerText: t,
                  teaEvtParams: r
                })
              }
            ))
        }
      ), [e, t])
    }
  }
  ,
  59750: (e,t,n)=>{
    n.d(t, {
      c: ()=>a
    });
    var r = n(44503)
      , o = n(21857)
      , i = n.n(o);
    function a(e, t, n, o) {
      (0,
        r.useEffect)((function() {
          e && void 0 !== o && i().app.syncLoginState({
            isLogin: o,
            uid: t,
            secUid: n
          })
        }
      ), [o, t, n, e])
    }
  }
  ,
  26867: (e,t,n)=>{
    n.d(t, {
      Z: ()=>i
    });
    var r = n(32781)
      , o = n(44503);
    function i(e) {
      var t = e.isClient
        , n = e.abTestData
        , i = e.osInfo
        , a = (0,
        o.useState)(!1)
        , l = (0,
        r.Z)(a, 2)
        , s = l[0]
        , c = l[1];
      return (0,
        o.useEffect)((function() {
          t && null != n && n.secondWallpaper && ("Windows" === i.os && "Win10" === i.version && c(!0),
          "Mac" === i.os && c(!0))
        }
      ), [i, n, t]),
        {
          newWallpaperShow: s
        }
    }
  }
  ,
  12164: (e,t,n)=>{
    n.d(t, {
      j: ()=>U,
      s: ()=>F
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(30906)
      , a = n(5594)
      , l = n.n(a)
      , s = n(21805)
      , c = n.n(s)
      , u = n(88438)
      , d = n.n(u)
      , m = n(89176)
      , v = n(7809)
      , f = n.n(v)
      , h = n(44503)
      , p = n(61936)
      , g = n(78867)
      , y = n(90414)
      , w = n(52252)
      , _ = n(25083)
      , E = n(92557)
      , k = n(67255)
      , x = n(16655)
      , b = n(27687)
      , C = n(51652)
      , N = n(9988)
      , T = n(74394)
      , Z = n(95127)
      , S = function() {
      Z.YY.replaceCurrentTask({
        id: Z.BE.HoverTaskId,
        priority: Z.T0.HoverPriority,
        isBlock: !0
      })
    }
      , I = function() {
      Z.YY.finishTask(Z.BE.HoverTaskId)
    }
      , L = {
      showGuide: !1,
      showUids: [],
      userData: {},
      autoShowCount: 0,
      autoShowDate: ""
    }
      , D = 6e5
      , M = 12e5
      , B = function(e) {
      return function() {
        try {
          return e.apply(void 0, arguments)
        } catch (t) {}
      }
    }
      , A = function() {
      return (0,
        i.Z)((0,
        i.Z)({}, L), y.$o(C.LocalStorageKeys.CollectionGuide))
    };
    function P() {
      return f()().format("YYYY-MM-DD")
    }
    var O = B((function() {
        var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : ""
          , t = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
        if (w.p())
          return !1;
        var n = A()
          , r = n.showGuide
          , o = void 0 !== r && r
          , i = n.showUids
          , a = void 0 === i ? [] : i;
        return !(!t && o) && (!t || !c()(a).call(a, e))
      }
    ))
      , V = B((function(e, t) {
        var n = A();
        e ? n.showUids.push(t) : n.showGuide = !0,
          y.qQ(C.LocalStorageKeys.CollectionGuide, n)
      }
    ))
      , W = B((function() {
        var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : ""
          , t = arguments.length > 1 && void 0 !== arguments[1] && arguments[1];
        if (w.p())
          return !1;
        var n = A()
          , r = n.userData
          , o = void 0 === r ? {} : r
          , i = n.autoShowCount
          , a = n.autoShowDate
          , l = i
          , s = a;
        if (t && e) {
          var c = o[e] || {};
          l = c.autoShowCount || 0,
            s = c.autoShowDate || ""
        }
        return !(l >= 5) && (!s || !f()().isSame(s, "day"))
      }
    ))
      , R = B((function() {
        var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : ""
          , t = arguments.length > 1 && void 0 !== arguments[1] && arguments[1]
          , n = A();
        if (t && e) {
          var r = n.userData[e] || {}
            , o = r.autoShowCount
            , i = void 0 === o ? 0 : o;
          return r.autoShowCount = i + 1,
            r.autoShowDate = P(),
            n.userData[e] = r,
            void y.qQ(C.LocalStorageKeys.CollectionGuide, n)
        }
        var a = n.autoShowCount
          , l = void 0 === a ? 0 : a;
        n.autoShowCount = l + 1,
          n.autoShowDate = P(),
          y.qQ(C.LocalStorageKeys.CollectionGuide, n)
      }
    ))
      , F = function(e, t) {
      var n = arguments.length > 2 && void 0 !== arguments[2] && arguments[2]
        , i = (0,
        h.useState)(!1)
        , a = (0,
        o.Z)(i, 2)
        , s = a[0]
        , c = a[1]
        , u = (0,
        h.useState)(!1)
        , v = (0,
        o.Z)(u, 2)
        , f = v[0]
        , g = v[1]
        , y = (0,
        h.useRef)()
        , w = (0,
        N.U)({
        enterDelay: 200,
        leaveDelay: 200,
        onMouseEnter: function() {
          p.i.sendLog("pageCollectionDetailShow", {
            enter_from: _.yW(),
            enter_method: "hover",
            if_red_dot: f ? 1 : 0
          }),
            clearTimeout(y.current),
            c(!0),
          n || (S(),
            E.emit(E.EVENT.showHeaderPopUp, {
              type: "collection",
              isShow: !0
            }))
        },
        onMouseLeave: function() {
          f && void 0 !== t && (g(!1),
            V(t, e)),
            c(!1),
            clearTimeout(y.current),
          n || I()
        }
      })
        , x = w.onMouseEnter
        , b = w.onMouseLeave
        , C = function() {
        s || (R(e, t),
          c(!0),
          y.current = d()((function() {
              c(!1)
            }
          ), 1e4))
      }
        , Z = (0,
        h.useRef)()
        , L = (0,
        m.Z)((0,
        r.Z)(l().mark((function n() {
          var r, o;
          return l().wrap((function(n) {
              for (; ; )
                switch (n.prev = n.next) {
                  case 0:
                    if (W(e, t)) {
                      n.next = 2;
                      break
                    }
                    return n.abrupt("return");
                  case 2:
                    return n.next = 4,
                      (0,
                        T.Tw)();
                  case 4:
                    r = n.sent,
                      o = M,
                    r && (o = D),
                      Z.current = d()((function() {
                          C()
                        }
                      ), o);
                  case 8:
                  case "end":
                    return n.stop()
                }
            }
          ), n)
        }
      ))));
      (0,
        h.useEffect)((function() {
          if (void 0 !== t && !n)
            return L(),
              function() {
                clearTimeout(y.current),
                  clearTimeout(Z.current)
              }
        }
      ), [t, n]),
        (0,
          h.useEffect)((function() {
            var e = E.listen(E.EVENT.showHeaderPopUp, (function(e) {
                "collection" !== e.type && e.isShow && c(!1)
              }
            ));
            return function() {
              e()
            }
          }
        ), []);
      var B = function() {
        p.i.sendLog("pageCollectionDetailShow", {
          enter_from: _.yW(),
          enter_method: "click",
          if_red_dot: f ? 1 : 0
        }),
          S(),
          c(!0)
      };
      return (0,
        h.useEffect)((function() {
          void 0 === t || n || g(O(e, t))
        }
      ), [t, e, n]),
        (0,
          h.useEffect)((function() {
            var e = function(e) {
              k.S(e) && (c(!1),
              n || I())
            };
            return window.addEventListener("keydown", e),
              function() {
                window.removeEventListener("keydown", e)
              }
          }
        ), [n]),
        {
          onCollectionGuideEnter: x,
          onCollectionGuideLeave: b,
          collectionPanelVisible: s,
          badgeVisible: f,
          onClick: B
        }
    }
      , U = function(e, t) {
      var n = (0,
        h.useState)(!1)
        , r = (0,
        o.Z)(n, 2)
        , i = r[0]
        , a = r[1];
      return (0,
        h.useEffect)((function() {
          e === g.CollectionGuide.Off || x.DT() || b.Y().then((function(e) {
              a(!e)
            }
          )).catch((function() {
              a(!0)
            }
          ))
        }
      ), [e, t]),
        i
    }
  }
  ,
  67594: (e,t,n)=>{
    n.d(t, {
      T: ()=>r,
      S: ()=>m
    });
    var r, o = n(21805), i = n.n(o), a = n(44503), l = n(95127), s = n(16655), c = n(78867), u = n(48499);
    function d(e) {
      e.shouldShowLoginPopup && l.YY.configTask(l.BE.LoginGuideTaskId, l.T0.LoginGuidePriority),
        s.DT() ? l.YY.configTask(l.BE.MiniScreenOrWallPaperTaskId, l.T0.MiniScreenWallPaperPriority) : l.YY.configTask(l.BE.DownloadGuideTaskId, l.T0.ClientDownloadPriority),
        l.YY.configTaskComplete()
    }
    !function(e) {
      e[e.Unknown = 0] = "Unknown",
        e[e.On = 1] = "On",
        e[e.Off = 2] = "Off"
    }(r || (r = {}));
    var m = function(e) {
      var t = e.isLogin
        , n = e.loginPopupStatus
        , o = void 0 === n ? r.Off : n
        , s = e.noDisturbVal
        , m = void 0 === s ? c.NoDisturbABVal.Normal : s
        , v = (0,
        a.useRef)(!1);
      (0,
        a.useEffect)((function() {
          var e;
          void 0 !== t && (i()(e = [c.NoDisturbABVal.A1, c.NoDisturbABVal.All]).call(e, m) ? l.YY.setMode(u.f.SingleMode) : l.YY.setMode(u.f.ParallelMode),
          v.current || (t ? (v.current = !0,
            d({
              shouldShowLoginPopup: !1
            })) : o !== r.Unknown && d({
            shouldShowLoginPopup: o === r.On
          })))
        }
      ), [t, o, m])
    }
  }
  ,
  14737: (e,t,n)=>{
    n.d(t, {
      KK: ()=>P,
      xj: ()=>A,
      GZ: ()=>q
    });
    var r, o = n(64408), i = n(32781), a = n(5594), l = n.n(a), s = n(92012), c = n.n(s), u = n(88438), d = n.n(u), m = n(44503), v = n(7809), f = n.n(v), h = n(89176), p = n(95127), g = n(48387), y = n(53607), w = n(16655), _ = n(80212), E = n(89942), k = n(92557), x = n(51652), b = n(27687), C = n(21805), N = n.n(C), T = n(94610), Z = n.n(T), S = n(52252), I = n(90147), L = n(1392);
    function D() {
      var e;
      return N()(e = [I.HOME_DOMAIN, I.LIVE_DOMAIN]).call(e, document.domain) ? document.domain === I.HOME_DOMAIN ? x.CookieKeys.HomeCanAddDY2desktop : x.CookieKeys.LiveCanAddDY2desktop : ""
    }
    function M(e) {
      if (!S.p()) {
        var t = D();
        t && y.Q.setItem(t, e ? "1" : "0", x.COOKIE_DEFAULT_EXPIRE_DURATION, "/", x.COOKIE_DOMAIN, "")
      }
    }
    function B() {
      var e, t;
      return N()(e = Z()(t = [x.CookieKeys.HomeCanAddDY2desktop, x.CookieKeys.LiveCanAddDY2desktop]).call(t, (function(e) {
          return function(e) {
            if (S.p())
              return r.CanNotDownload;
            var t = e || D();
            if (!t)
              return r.Unknown;
            var n = document.domain === y.Q.getItem({
              sKey: t
            });
            return "0" === n ? r.CanNotDownload : "1" === n ? r.CanDownload : r.Unknown
          }(e)
        }
      ))).call(e, r.CanNotDownload)
    }
    !function(e) {
      e[e.CanNotDownload = 0] = "CanNotDownload",
        e[e.CanDownload = 1] = "CanDownload",
        e[e.Unknown = 2] = "Unknown"
    }(r || (r = {}));
    var A, P, O = n(84696), V = n(74394), W = n(9988), R = x, F = R.COOKIE_DEFAULT_EXPIRE_DURATION, U = R.CookieKeys, H = R.COOKIE_DOMAIN;
    function G() {
      var e = (y.Q.getItem({
        sKey: U.DownloadGuide
      }) || "").split("/");
      return {
        count: Number(e[0] || "0"),
        lastTime: e[1] || ""
      }
    }
    function j() {
      var e, t = G();
      y.Q.setItem(U.DownloadGuide, c()(e = "".concat(t.count + 1, "/")).call(e, f()().format("YYYYMMDD")), F, "/", H)
    }
    !function(e) {
      e[e.None = 0] = "None",
        e[e.PWA = 1] = "PWA",
        e[e.Client = 2] = "Client"
    }(A || (A = {})),
      function(e) {
        e[e.Hover = 0] = "Hover",
          e[e.Auto = 1] = "Auto"
      }(P || (P = {}));
    var K = Math.pow(2, 31) - 1
      , q = function(e) {
      var t = e.isLogin
        , n = (0,
        O.o)()
        , r = n.downloadAttr
        , a = n.downloadHref
        , s = function() {
        var e = (0,
          m.useRef)()
          , t = (0,
          m.useState)(!1)
          , n = (0,
          i.Z)(t, 2)
          , r = n[0]
          , o = n[1];
        return (0,
          m.useEffect)((function() {
            M(!1);
            var t = function(t) {
              null == t || t.preventDefault(),
                e.current = t,
                M(!0),
                o(!0)
            }
              , n = function() {
              M(!1),
                o(!1)
            };
            return window.addEventListener("beforeinstallprompt", t),
              window.addEventListener("appinstalled", n),
              function() {
                window.removeEventListener("beforeinstallprompt", t),
                  window.removeEventListener("appinstalled", n)
              }
          }
        ), []),
          {
            PWAInstallable: r,
            installPWA: (0,
              m.useCallback)((function() {
                e.current && (e.current.prompt(),
                  e.current.userChoice.then((function(t) {
                      "accepted" === t.outcome && (M(!1),
                        o(!1)),
                        L.Z.sendLog("installNativePanelClick", {
                          action: "accepted" === t.outcome ? "install" : "cancel"
                        }),
                        e.current = null
                    }
                  )))
              }
            ), [])
          }
      }()
        , c = s.PWAInstallable
        , u = s.installPWA
        , v = (0,
        m.useState)(A.None)
        , y = (0,
        i.Z)(v, 2)
        , x = y[0]
        , C = y[1]
        , N = (0,
        m.useState)(K)
        , T = (0,
        i.Z)(N, 2)
        , Z = T[0]
        , S = T[1]
        , I = (0,
        m.useState)(!1)
        , D = (0,
        i.Z)(I, 2)
        , R = D[0]
        , F = D[1]
        , U = (0,
        m.useState)(!1)
        , H = (0,
        i.Z)(U, 2)
        , q = H[0]
        , Y = H[1]
        , X = (0,
        m.useState)(!1)
        , z = (0,
        i.Z)(X, 2)
        , Q = z[0]
        , J = z[1]
        , $ = (0,
        m.useState)(P.Hover)
        , ee = (0,
        i.Z)($, 2)
        , te = ee[0]
        , ne = ee[1]
        , re = (0,
        m.useRef)(!1)
        , oe = (0,
        h.Z)((function() {
          return u()
        }
      ))
        , ie = (0,
        m.useCallback)(function() {
        var e = (0,
          o.Z)(l().mark((function e(n) {
            var r, i, a;
            return l().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return i = function() {
                        return (i = (0,
                          o.Z)(l().mark((function e() {
                            return l().wrap((function(e) {
                                for (; ; )
                                  switch (e.prev = e.next) {
                                    case 0:
                                      if (!1 !== (0,
                                        V.D5)()) {
                                        e.next = 2;
                                        break
                                      }
                                      return e.abrupt("return", !1);
                                    case 2:
                                      if (!w.DT()) {
                                        e.next = 4;
                                        break
                                      }
                                      return e.abrupt("return", !1);
                                    case 4:
                                      if (!n) {
                                        e.next = 6;
                                        break
                                      }
                                      return e.abrupt("return", !0);
                                    case 6:
                                      if (e.t0 = t,
                                        !e.t0) {
                                        e.next = 11;
                                        break
                                      }
                                      return e.next = 10,
                                        (0,
                                          b.Y)();
                                    case 10:
                                      e.t0 = e.sent;
                                    case 11:
                                      if (!e.t0) {
                                        e.next = 13;
                                        break
                                      }
                                      return e.abrupt("return", !1);
                                    case 13:
                                      return e.abrupt("return", !0);
                                    case 14:
                                    case "end":
                                      return e.stop()
                                  }
                              }
                            ), e)
                          }
                        )))).apply(this, arguments)
                      }
                        ,
                        r = function() {
                          return i.apply(this, arguments)
                        }
                        ,
                        a = function() {
                          return !(0,
                            V.D5)() && (!_.f() && (!!_.y() && (!B() && c)))
                        }
                        ,
                        e.next = 5,
                        r();
                    case 5:
                      if (!e.sent) {
                        e.next = 7;
                        break
                      }
                      return e.abrupt("return", A.Client);
                    case 7:
                      return e.abrupt("return", a() ? A.PWA : A.None);
                    case 8:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), [c, t])
        , ae = (0,
        m.useRef)(5e3);
      (0,
        m.useEffect)((function() {
          var e = function() {
            var e = (0,
              o.Z)(l().mark((function e() {
                var t;
                return l().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          return e.next = 2,
                            g.pL();
                        case 2:
                          return t = e.sent,
                            e.abrupt("return", !t || E.KC(1e3 * t));
                        case 4:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            )));
            return function() {
              return e.apply(this, arguments)
            }
          }();
          (0,
            o.Z)(l().mark((function n() {
              return l().wrap((function(n) {
                  for (; ; )
                    switch (n.prev = n.next) {
                      case 0:
                        if (void 0 === t) {
                          n.next = 8;
                          break
                        }
                        return n.next = 3,
                          e();
                      case 3:
                        if (!n.sent) {
                          n.next = 7;
                          break
                        }
                        return S(6e4),
                          n.abrupt("return");
                      case 7:
                        S(3e4);
                      case 8:
                      case "end":
                        return n.stop()
                    }
                }
              ), n)
            }
          )))()
        }
      ), [t]);
      var le = (0,
        m.useRef)()
        , se = (0,
        m.useRef)(!1)
        , ce = (0,
        h.Z)((function() {
          J(!0),
            re.current = !0
        }
      ))
        , ue = (0,
        h.Z)((function() {
          clearTimeout(le.current),
            J(!1),
            re.current = !1,
            p.YY.finishTask(p.BE.DownloadGuideTaskId),
            se.current = !1,
            F(!1),
            Y(!1)
        }
      ))
        , de = (0,
        h.Z)((function() {
          ce(),
            F(!0),
            Y(!0)
        }
      ))
        , me = (0,
        h.Z)((0,
        o.Z)(l().mark((function e() {
          var t;
          return l().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      ie(!1);
                  case 2:
                    if (t = e.sent,
                    t !== A.None && (n = 3,
                      r = !1,
                      o = void 0,
                      !((o = G()).count >= n || r && o.lastTime === f()().format("YYYYMMDD"))) && !re.current) {
                      e.next = 7;
                      break
                    }
                    return p.YY.cancelTask(p.BE.DownloadGuideTaskId),
                      e.abrupt("return");
                  case 7:
                    C(t),
                      ne(P.Auto),
                      de(),
                      j(),
                      le.current = d()((function() {
                          ue()
                        }
                      ), ae.current);
                  case 12:
                  case "end":
                    return e.stop()
                }
              var n, r, o
            }
          ), e)
        }
      ))));
      (0,
        m.useEffect)((function() {
          Z !== K && p.YY.insertTask(p.BE.DownloadGuideTaskId, (function() {
              me()
            }
          ), {
            onFinish: function() {
              ue()
            },
            delay: Z,
            priority: p.T0.ClientDownloadPriority
          })
        }
      ), [Z]);
      var ve = (0,
        h.Z)((function() {
          te === P.Auto && (se.current = !0),
            clearTimeout(le.current)
        }
      ))
        , fe = (0,
        h.Z)((function() {
          se.current && (clearTimeout(le.current),
            le.current = d()((function() {
                ue()
              }
            ), ae.current))
        }
      ));
      (0,
        m.useEffect)((function() {
          return k.listen(k.EVENT.showHeaderPopUp, (function(e) {
              return "client" !== e.type && e.isShow && Q && ue()
            }
          ))
        }
      ), [Q, ue]);
      var he = function() {
        var e = (0,
          o.Z)(l().mark((function e() {
            var t;
            return l().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      if (clearTimeout(le.current),
                        p.YY.replaceCurrentTask({
                          id: p.BE.DownloadGuideTaskId,
                          priority: p.T0.HoverPriority,
                          isBlock: !0
                        }),
                        re.current) {
                        e.next = 9;
                        break
                      }
                      return e.next = 5,
                        ie(!0);
                    case 5:
                      t = e.sent,
                        C(t),
                        ce(),
                        ne(P.Hover);
                    case 9:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function() {
          return e.apply(this, arguments)
        }
      }()
        , pe = function() {
        se.current || (be(!1),
          ue())
      }
        , ge = (0,
        h.Z)(function() {
        var e = (0,
          o.Z)(l().mark((function e(t) {
            return l().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      if (!t) {
                        e.next = 3;
                        break
                      }
                      return he(),
                        e.abrupt("return");
                    case 3:
                      pe();
                    case 4:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }())
        , ye = (0,
        W.U)({
        enterDelay: 100,
        leaveDelay: 200,
        onMouseEnter: function() {
          he()
        },
        onMouseLeave: function() {
          pe()
        }
      })
        , we = ye.onMouseEnter
        , _e = ye.onMouseLeave
        , Ee = (0,
        m.useState)(!1)
        , ke = (0,
        i.Z)(Ee, 2)
        , xe = ke[0]
        , be = ke[1];
      return (0,
        m.useEffect)((function() {
          (0,
            V.D5)() && "boolean" == typeof t && (t ? (0,
            b.Y)().then((function(e) {
              return be(!e)
            }
          )) : be(!0))
        }
      ), [t]),
        {
          shouldShowGuideType: x,
          clientDownloadHref: a,
          clientDownloadAttr: r,
          downloadPWA: oe,
          show: Q,
          hideDownloadGuide: ue,
          showDownloadGuideWithCloseAndEffect: de,
          withClose: R,
          withEffect: q,
          showDownloadGuide: ce,
          onDownloadGuideEnter: ve,
          onDownloadGuideLeave: fe,
          onDownloadGuideEntryEnter: we,
          onDownloadGuideEntryLeave: _e,
          onDownloadGuideVisibleChange: ge,
          showType: te,
          showClientBadge: xe
        }
    }
  }
  ,
  84696: (e,t,n)=>{
    n.d(t, {
      o: ()=>_
    });
    var r = n(32781)
      , o = n(34246)
      , i = n.n(o)
      , a = n(92012)
      , l = n.n(a)
      , s = n(44503)
      , c = n(76659)
      , u = n(69283)
      , d = n(12167)
      , m = n(64408)
      , v = n(5594)
      , f = n.n(v)
      , h = n(9070)
      , p = n(73750)
      , g = {
      apk: "https://lf3-cdn-tos.bytegoofy.com/obj/douyin-pc-client/7044145585217083655/releases/7617694/1.0.3/win32-ia32/douyin-v1.0.3-win32-ia32.exe",
      apkExp1: "https://lf3-cdn-tos.bytegoofy.com/obj/douyin-pc-client/7044145585217083655/releases/8094749/1.0.4/win32-ia32/douyin-v1.0.4-win32-ia32-douyinDownload1.exe",
      apkExp2: "https://lf3-cdn-tos.bytegoofy.com/obj/douyin-pc-client/7044145585217083655/releases/8094749/1.0.4/win32-ia32/douyin-v1.0.4-win32-ia32-douyinDownload2.exe",
      limit: "Windows 7\u53ca\u4ee5\u4e0a",
      time: "2022-2-20",
      version: "1.0.4",
      video: "https://p3-pc-weboff.byteimg.com/tos-cn-i-9r5gewecjs/video.mp4",
      macApk: "https://lf3-cdn-tos.bytegoofy.com/obj/douyin-pc-client/7044145585217083655/releases/8094749/1.0.4/win32-ia32/douyin-v1.0.4-win32-ia32-douyinDownload1.exe",
      macLimit: "macOS\u7cfb\u7edf",
      macTime: "2022-5-27",
      macVersion: "1.0.6"
    };
    function y() {
      return (y = (0,
        m.Z)(f().mark((function e() {
          var t;
          return f().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      h.U2({
                        key: p.TccKey.DownloadPCInfo,
                        defaultValue: g
                      });
                  case 2:
                    return t = e.sent,
                      e.abrupt("return", {
                        winUrl: t.apkExp1 || t.apk,
                        macUrl: t.macApk
                      });
                  case 4:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )))).apply(this, arguments)
    }
    var w = n(74394);
    function _() {
      var e = s.useState("")
        , t = (0,
        r.Z)(e, 2)
        , n = t[0]
        , o = t[1]
        , a = (0,
        s.useState)("")
        , m = (0,
        r.Z)(a, 2)
        , v = m[0]
        , f = m[1]
        , h = (0,
        s.useState)("")
        , p = (0,
        r.Z)(h, 2)
        , g = p[0]
        , _ = p[1]
        , E = (0,
        s.useState)("")
        , k = (0,
        r.Z)(E, 2)
        , x = k[0]
        , b = k[1];
      return s.useEffect((function() {
          (function() {
              return y.apply(this, arguments)
            }
          )().then((function(e) {
              o((0,
                w.G1)() ? e.macUrl : e.winUrl)
            }
          ))
        }
      ), []),
        (0,
          s.useEffect)((function() {
            var e, t = (null === (e = c.Es()) || void 0 === e ? void 0 : e.user_unique_id) || "", n = u.N(t, 62);
            f(n)
          }
        ), []),
        (0,
          s.useEffect)((function() {
            var e = (0,
              w.P0)() === w.CT.Mac ? ".dmg" : ".exe"
              , t = "douyin".concat(e);
            if (n) {
              var r, o = n;
              t = o.substring(i()(o).call(o, "/") + 1),
                t = "".concat(l()(r = "".concat(t.split(e)[0], "-wid-")).call(r, v), e)
            }
            b(t)
          }
        ), [v, n]),
        (0,
          s.useEffect)((function() {
            var e, t = d.w(n);
            null != t && t.pathname ? _(l()(e = "https://".concat(location.host, "/download/pc")).call(e, t.pathname)) : _(n)
          }
        ), [n]),
        {
          downloadHref: g,
          downloadAttr: x,
          downloadUrl: n
        }
    }
  }
  ,
  91548: (e,t,n)=>{
    n.d(t, {
      u: ()=>c
    });
    var r = n(30906)
      , o = n(44503)
      , i = n(25083)
      , a = n(90147)
      , l = n(1392)
      , s = n(69234);
    function c(e) {
      var t = function(e) {
        return l.Z.sendLog("pageClick", {
          enter_from: i.vM(),
          click_position: e
        })
      };
      return {
        postDropdownItems: (0,
          o.useMemo)((function() {
            return [(0,
              r.Z)((0,
              r.Z)({}, s.j.publish), {}, {
              type: "textLink",
              url: e ? s.j.publish.url : "//".concat(a.CREATOR_DOMAIN, "/"),
              onClick: function() {
                return t("publish")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.videoManage), {}, {
              type: "textLink",
              onClick: function() {
                return t("manage")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.postStatistics), {}, {
              type: "textLink",
              onClick: function() {
                return t("data")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.liveData), {}, {
              type: "textLink"
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.creatorSchool), {}, {
              type: "textLink",
              onClick: function() {
                return t("creator_learning")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.creator), {}, {
              type: "textLink",
              text: "\u521b\u4f5c\u8005\u670d\u52a1\u5e73\u53f0",
              onClick: function() {
                return t("creator_platform")
              },
              url: e ? s.j.creator.url : "//".concat(a.CREATOR_DOMAIN, "/")
            })]
          }
        ), [e]),
        cooperationDropdownItems: (0,
          o.useMemo)((function() {
            return [(0,
              r.Z)((0,
              r.Z)({}, s.j.platform), {}, {
              type: "textLink",
              onClick: function() {
                return t("open_platform")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.certification), {}, {
              type: "textLink",
              onClick: function() {
                return t("certification")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.marketing), {}, {
              type: "textLink",
              onClick: function() {
                return t("ad_serving")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.ecommerce), {}, {
              type: "textLink",
              onClick: function() {
                return t("ecommerce")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.rule), {}, {
              type: "textLink",
              text: "\u89c4\u5219\u4e2d\u5fc3",
              onClick: function() {
                return t("security_report")
              }
            }), (0,
              r.Z)((0,
              r.Z)({}, s.j.aboutDouyin), {}, {
              type: "textLink",
              onClick: function() {
                return t("about_douyin")
              }
            })]
          }
        ), [])
      }
    }
  }
  ,
  98767: (e,t,n)=>{
    n.d(t, {
      i: ()=>c
    });
    var r = n(64408)
      , o = n(5594)
      , i = n.n(o)
      , a = n(44503)
      , l = n(9070)
      , s = n(73750)
      , c = function() {
      var e = (0,
        a.useCallback)((0,
        r.Z)(i().mark((function e() {
          var t;
          return i().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      l.U2({
                        key: s.TccKey.SpecUserFollowerUidList,
                        defaultValue: []
                      });
                  case 2:
                    t = e.sent,
                      window.spec_user_follower_uid_list = t;
                  case 4:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      ))), []);
      return (0,
        a.useEffect)((function() {
          e()
        }
      ), []),
        null
    }
  }
  ,
  52491: (e,t,n)=>{
    n.d(t, {
      T: ()=>O
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(5594)
      , a = n.n(i)
      , l = n(10081)
      , s = n.n(l)
      , c = n(57617)
      , u = n.n(c)
      , d = n(70995)
      , m = n.n(d)
      , v = n(21805)
      , f = n.n(v)
      , h = n(58256)
      , p = n(44503)
      , g = n(37610)
      , y = n(7809)
      , w = n.n(y)
      , _ = n(92289)
      , E = n(80477)
      , k = n(47482)
      , x = n(76659)
      , b = n(15499)
      , C = n(16655)
      , N = n(25083)
      , T = n(85938)
      , Z = n(53607)
      , S = n(8685)
      , I = n(82226)
      , L = n(51652)
      , D = n(7778)
      , M = n(80212)
      , B = n(34301)
      , A = n(1392)
      , P = n(91707)
      , O = function(e) {
      var t = e.userInfo
        , n = e.redirectFrom
        , i = (0,
        B.x)()
        , l = (0,
        o.Z)(i, 2)
        , c = (l[0],
        l[1])
        , d = (0,
        p.useRef)(t)
        , v = (0,
        g.k6)()
        , y = _.lp
        , O = _.sN
        , V = (0,
        p.useRef)("")
        , W = (0,
        p.useRef)(!1);
      (0,
        E.s)();
      var R = (0,
        p.useCallback)((function() {
          var e = h.parseUrl(location.href)
            , t = e.url
            , n = e.query || {}
            , r = k.Rs("sourceid") || (null == n ? void 0 : n.sourceid);
          if (r && !W.current) {
            var o, i = null === (o = x.Es()) || void 0 === o ? void 0 : o.user_unique_id;
            if (k.U$(["sourceid"]),
            null != n && n.sourceid) {
              var a, l;
              delete n.sourceid;
              var s = (0,
                h.stringify)(n);
              null === (a = window) || void 0 === a || null === (l = a.history) || void 0 === l || l.replaceState({}, "", s ? [t, s].join("?") : t)
            }
            W.current = !0,
              A.Z.sendLog("from360", {
                qhclickid: r || "",
                uuid: i
              }),
              b.N({
                qhclickid: r,
                trans_id: (0,
                  D.H)(i)
              })
          }
        }
      ), [])
        , F = (0,
        p.useCallback)((0,
        r.Z)(a().mark((function e() {
          var r, o, i, l, c, d, v, f, h, p, g, w, _, E, b, D, B, W, F, U, H, G, j;
          return a().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    for (A.Z.sendLog("pageViewMonitorTest", {
                      url: location.href
                    }, !1),
                         (-1 !== (null === (r = location) || void 0 === r || null === (o = r.host) || void 0 === o ? void 0 : s()(o).call(o, "live")) || new RegExp(O).test(null === (i = location) || void 0 === i ? void 0 : i.pathname) && !C._Q()) && R(),
                           d = (t || {}).info,
                           v = null === (l = x.Es()) || void 0 === l ? void 0 : l.user_unique_id,
                           f = k.Rs("previous_page") || "",
                           p = 0,
                           g = u()(y); p < g.length; p++)
                      E = g[p],
                      null !== (w = location) && void 0 !== w && null !== (_ = w.pathname) && void 0 !== _ && _.match(new RegExp(E)) && "search_result" !== (h = -1 === (null === (b = location) || void 0 === b || null === (D = b.host) || void 0 === D ? void 0 : s()(D).call(D, "live")) ? y[E] : "/" === (null === (B = location) || void 0 === B ? void 0 : B.pathname) ? "live" : y[E]) && N.TU(h);
                    "live_detail" === N.yW() && (h = "live_detail"),
                      W = {
                        app_code_link: "app_code",
                        web_code_link: "web_code"
                      },
                      F = m()(c = location.pathname).call(c, "/note") ? 68 : 0,
                      A.Z.sendLog("pageViewMonitor", {
                        enter_from: h || "",
                        url: location.href,
                        uid: null == d ? void 0 : d.uid,
                        uuid: v
                      }),
                      h && (null != d && d.uid || v) ? (U = "/hot" === location.pathname ? "trend" : "",
                        H = k.Rs("enter_method"),
                        A.Z.sendLog("pageView", {
                          enter_from: h,
                          url: location.href,
                          url_path: location.pathname,
                          link_from: (0,
                            M.f)() ? "pwa" : W[f] || "",
                          enter_method: H,
                          tab_name: U,
                          aweme_type: F,
                          theme: T.Dr(Z.Q.getItem({
                            sKey: L.CookieKeys.Theme
                          })),
                          enter_by_tab: (0,
                            P.S)(),
                          browser_height: window.innerHeight,
                          browser_width: window.innerWidth,
                          browser_ratio: window.innerHeight / window.innerWidth,
                          redirect_from: n,
                          from_push: Z.Q.getItem({
                            sKey: L.CookieKeys.FromClientPush
                          }) ? 1 : 0,
                          seo_vids: S.t("seo_vids") || ""
                        }),
                        G = location.href,
                        j = location.pathname,
                        V.current = j,
                        I.vP({
                          key: j,
                          event: function(e, t) {
                            t > 0 && N.yW() && A.Z.sendLog("pageStayTime", {
                              enter_from: N.yW(),
                              enter_method: H,
                              url: G,
                              url_path: j,
                              duration: t,
                              is_visible: Number(e),
                              link_from: (0,
                                M.f)() ? "pwa" : W[f] || "",
                              tab_name: U,
                              aweme_type: F
                            }, !1)
                          }
                        })) : A.Z.sendLog("pageViewError", {
                        enter_from: h || "",
                        url: location.href,
                        uid: null == d ? void 0 : d.uid,
                        uuid: v
                      });
                  case 11:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      ))), [t, R, n]);
      return (0,
        p.useEffect)((function() {
          F(),
            v.listen((function() {
                if (x.Le.setConfig(x.gI.MarkFirstEnter, null),
                  V.current) {
                  try {
                    I.wq()
                  } catch (e) {}
                  I.xC(V.current)
                }
                F()
              }
            ))
        }
      ), []),
        (0,
          p.useEffect)((function() {
            var e, n = d.current;
            d.current = t;
            var r = null == t ? void 0 : t.info;
            (null == n || null === (e = n.info) || void 0 === e ? void 0 : e.uid) !== (null == r ? void 0 : r.uid) && void 0 !== (null == n ? void 0 : n.isLogin) && F()
          }
        ), [t]),
        (0,
          p.useEffect)((function() {
            var e = w()().format("YYYY-MM-DD");
            return I.vP({
              key: "PAGE_VIEW_EVENTS_TRACKING_UPDATE_ACROSS_DAY",
              event: function() {
                var t = "visible" === document.visibilityState
                  , n = w()().format("YYYY-MM-DD");
                t ? n !== e && (F(),
                  e = n) : e = n
              }
            }),
              function() {
                return I.xC("PAGE_VIEW_EVENTS_TRACKING_UPDATE_ACROSS_DAY")
              }
          }
        ), []),
        {
          handleHiddenLog: (0,
            p.useCallback)((function(e) {
              var t;
              if (!f()(t = [B.O.LogTrace, B.O.UserInfo]).call(t, e))
                return !0;
              c({
                key: e
              })
            }
          ), [c])
        }
    }
  }
  ,
  98853: (e,t,n)=>{
    n.d(t, {
      Z: ()=>L
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(5594)
      , a = n.n(i)
      , l = n(70995)
      , s = n.n(l)
      , c = n(84891)
      , u = n.n(c)
      , d = n(94610)
      , m = n.n(d)
      , v = n(80051)
      , f = n.n(v)
      , h = n(92637)
      , p = n.n(h)
      , g = n(88438)
      , y = n.n(g)
      , w = n(92012)
      , _ = n.n(w)
      , E = n(44503)
      , k = n(14819)
      , x = n.n(k)
      , b = n(5794)
      , C = n.n(b)
      , N = n(86632)
      , T = n(92557)
      , Z = n(10790)
      , S = function(e, t) {
      for (var n = 0, r = 0; r < e.length && n < t.length; r++) {
        var o;
        s()(o = e[r].awemeId).call(o, t[n].awemeId) && (t[n].msgClientId = e[r].msgClientId,
          n++)
      }
      return t
    }
      , I = function(e, t, n) {
      var r = u()(t).call(t, (function(e) {
          return (null == e ? void 0 : e.msgClientId) === n
        }
      ));
      if (-1 !== r)
        return {
          status: !0,
          rank: r
        };
      for (var o = u()(e).call(e, (function(e) {
          return (null == e ? void 0 : e.msgClientId) === n
        }
      )), i = 0, a = 0; a <= o && i < t.length; a++) {
        var l;
        s()(l = e[a].awemeId).call(l, t[i].awemeId) && i++
      }
      return {
        status: !1,
        rank: i < t.length ? i : i - 1
      }
    };
    const L = function(e) {
      var t = e.awemeIds
        , n = e.clientId
        , i = e.fetchAwemeIds
        , l = e.currentNumber
        , s = e.setCurrentNumber
        , c = e.awemeInfoList
        , d = e.setAwemeInfoList
        , v = e.refPrevVideoCallBack
        , h = e.refNextVideoCallBack
        , g = e.setIsFirst
        , w = (e.setIsLast,
        e.close)
        , k = (0,
        E.useRef)(!0)
        , b = (0,
        E.useRef)(!1)
        , L = (0,
        E.useRef)(!0)
        , D = (0,
        E.useRef)(l)
        , M = (0,
        E.useState)(t)
        , B = (0,
        o.Z)(M, 2)
        , A = B[0]
        , P = B[1]
        , O = (0,
        E.useCallback)(function() {
        var e = (0,
          r.Z)(a().mark((function e(t) {
            var r, o, i, l, c, u, v, h;
            return a().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return b.current = !0,
                        o = m()(t).call(t, (function(e) {
                            return e.awemeId
                          }
                        )),
                        i = x()(o, 50),
                        e.next = 5,
                        f().all(m()(i).call(i, (function(e) {
                            return N.c7(e)
                          }
                        )));
                    case 5:
                      if (l = e.sent,
                        c = p()(l).call(l, (function(e) {
                            return 0 === (null == e ? void 0 : e.statusCode)
                          }
                        )),
                        !(0 === (u = {
                          statusCode: c.length > 0 ? 0 : 1,
                          detail: C()(m()(c).call(c, (function(e) {
                              var t;
                              return (null === (t = e.detail) || void 0 === t ? void 0 : t.length) > 0 ? e.detail : []
                            }
                          )))
                        }).statusCode && (null === (r = u.detail) || void 0 === r ? void 0 : r.length) > 0)) {
                        e.next = 26;
                        break
                      }
                      if (v = S(t, u.detail),
                        !k.current) {
                        e.next = 22;
                        break
                      }
                      if (k.current = !1,
                      -1 !== (h = I(t, v, n)).rank) {
                        e.next = 17;
                        break
                      }
                      return Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86"),
                        y()((function() {
                            null == w || w()
                          }
                        ), 3e3),
                        e.abrupt("return");
                    case 17:
                      h.status || Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86"),
                        d(u.detail),
                        s(h.rank),
                        e.next = 24;
                      break;
                    case 22:
                      d((function(e) {
                          var t;
                          return _()(t = u.detail).call(t, e)
                        }
                      )),
                        s(u.detail.length - 1);
                    case 24:
                      e.next = 28;
                      break;
                    case 26:
                      Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86"),
                        y()((function() {
                            null == w || w()
                          }
                        ), 3e3);
                    case 28:
                      b.current = !1;
                    case 29:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), []);
      (0,
        E.useEffect)((function() {
          O(t)
        }
      ), []),
        (0,
          E.useEffect)((function() {
            h.current = (0,
              r.Z)(a().mark((function e() {
                var t, n;
                return a().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          t = A[A.length - 1],
                            n = c[c.length - 1],
                          t.msgClientId !== n.msgClientId && Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86");
                        case 3:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            ))),
              v.current = (0,
                r.Z)(a().mark((function e() {
                  var t, n;
                  return a().wrap((function(e) {
                      for (; ; )
                        switch (e.prev = e.next) {
                          case 0:
                            if (A[0].msgClientId !== c[0].msgClientId && Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86"),
                              L.current) {
                              e.next = 3;
                              break
                            }
                            return e.abrupt("return");
                          case 3:
                            if (b.current) {
                              e.next = 12;
                              break
                            }
                            return b.current = !0,
                              e.next = 7,
                              i();
                          case 7:
                            n = e.sent,
                              L.current = n.hasMore,
                              g(!n.hasMore),
                              P((function(e) {
                                  var t;
                                  return _()(t = n.videoMsgList).call(t, e)
                                }
                              )),
                              (null == n || null === (t = n.videoMsgList) || void 0 === t ? void 0 : t.length) > 0 ? O(n.videoMsgList) : b.current = !1;
                          case 12:
                          case "end":
                            return e.stop()
                        }
                    }
                  ), e)
                }
              )))
          }
        ), [A, c]),
        (0,
          E.useEffect)((function() {
            if (-1 !== D.current) {
              var e = c[D.current].msgClientId
                , t = u()(A).call(A, (function(t) {
                  return t.msgClientId === e
                }
              ));
              D.current + 1 === l && A[t + 1].msgClientId !== c[l].msgClientId && Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86"),
              D.current - 1 === l && A[t - 1].msgClientId !== c[l].msgClientId && Z.F.info("\u89c6\u9891\u6d88\u5931\u4e86")
            }
            D.current = l
          }
        ), [l, c, A]),
        (0,
          E.useEffect)((function() {
            g(!L.current && 0 === l)
          }
        ), [l, c]),
        (0,
          E.useEffect)((function() {
            var e = T.listen(T.EVENT.imAwemeRecall, (function(e) {
                e.msgClientId === c[l].msgClientId ? (null == w || w(),
                  Z.F.info("\u6d88\u606f\u5df2\u88ab\u64a4\u56de")) : (u()(c).call(c, (function(t) {
                    return t.msgClientId === e.msgClientId
                  }
                )) < l && s((function(e) {
                    return e - 1
                  }
                )),
                  P((function(t) {
                      return p()(t).call(t, (function(t) {
                          return t.msgClientId !== e.msgClientId
                        }
                      ))
                    }
                  )),
                  d((function(t) {
                      return p()(t).call(t, (function(t) {
                          return t.msgClientId !== e.msgClientId
                        }
                      ))
                    }
                  )))
              }
            ));
            return function() {
              return e()
            }
          }
        ), [l, c, A])
    }
  }
  ,
  73969: (e,t,n)=>{
    n.d(t, {
      _: ()=>l
    });
    var r = n(30906)
      , o = n(32781)
      , i = n(44503)
      , a = n(52252);
    function l() {
      var e, t, n, l, s, c, u = (0,
        i.useState)(!1), d = (0,
        o.Z)(u, 2), m = d[0], v = d[1], f = (e = function() {
        return a.p() ? {
          innerHeight: 0,
          innerWidth: 0,
          inSSR: !0
        } : {
          innerHeight: window.innerHeight,
          innerWidth: window.innerWidth
        }
      }
        ,
        t = i.useState(e()),
        n = (0,
          o.Z)(t, 2),
        l = n[0],
        s = n[1],
        c = function() {
          s(e())
        }
        ,
        i.useEffect((function() {
            return window.addEventListener("resize", c),
              function() {
                return window.removeEventListener("resize", c)
              }
          }
        ), []),
        l), h = f.inSSR, p = f.innerWidth;
      return (0,
        i.useEffect)((function() {
          return v(!h && p <= 1032)
        }
      ), [p, h]),
        (0,
          r.Z)({
          inMiniScreen: m
        }, f)
    }
  }
  ,
  2143: (e,t,n)=>{
    n.d(t, {
      Z: ()=>v
    });
    var r = n(30906)
      , o = n(64408)
      , i = n(32781)
      , a = n(5594)
      , l = n.n(a)
      , s = n(88438)
      , c = n.n(s)
      , u = n(10790)
      , d = n(86632)
      , m = n(44503);
    const v = function(e) {
      var t = e.awemeId
        , n = (e.currentNumber,
        e.setCurrentNumber)
        , a = (e.awemeInfoList,
        e.setAwemeInfoList)
        , s = (0,
        m.useState)(null)
        , v = (0,
        i.Z)(s, 2)
        , f = v[0]
        , h = v[1]
        , p = (0,
        m.useCallback)((0,
        o.Z)(l().mark((function n() {
          var o, i;
          return l().wrap((function(n) {
              for (; ; )
                switch (n.prev = n.next) {
                  case 0:
                    return n.next = 2,
                      d.m_({
                        awemeId: t
                      });
                  case 2:
                    0 === (null == (o = n.sent) ? void 0 : o.statusCode) ? (i = (0,
                      r.Z)((0,
                      r.Z)({}, null == o ? void 0 : o.detail), {}, {
                      logPb: null == o ? void 0 : o.logPb
                    }),
                      h(i)) : (u.F.info("\u89c6\u9891\u6d88\u5931\u4e86\uff0c\u8bf7\u7ee7\u7eed\u6d4f\u89c8\u5176\u4ed6\u4f5c\u54c1"),
                      c()((function() {
                          var t;
                          null === (t = e.close) || void 0 === t || t.call(e)
                        }
                      ), 5e3));
                  case 4:
                  case "end":
                    return n.stop()
                }
            }
          ), n)
        }
      ))), [t]);
      (0,
        m.useEffect)((function() {
          p()
        }
      ), [t, p]),
        (0,
          m.useEffect)((function() {
            f && (a([f]),
              n(0))
          }
        ), [f, a, n])
    }
  }
  ,
  69343: (e,t,n)=>{
    n.d(t, {
      E: ()=>p
    });
    var r = n(64408)
      , o = n(5594)
      , i = n.n(o)
      , a = n(44503)
      , l = n(65981)
      , s = n.n(l)
      , c = n(76208)
      , u = n(82201)
      , d = n(58256)
      , m = n(5158)
      , v = n(64644)
      , f = n(92557)
      , h = function(e) {
      var t, n, r, o = "", i = "", a = "";
      if (null != e && e.open_url) {
        var l = d.parseUrl(null == e ? void 0 : e.open_url).query;
        o = null == l ? void 0 : l.web_rid,
          i = null == l ? void 0 : l.room_id,
          a = null == l ? void 0 : l.user_id
      }
      return {
        id: null == e || null === (t = e.id) || void 0 === t ? void 0 : t.toString(),
        text: null == e ? void 0 : e.text,
        title: null == e ? void 0 : e.title,
        imageUrl: null == e ? void 0 : e.image_url,
        webRid: o,
        roomId: i,
        anchorId: a,
        type: null == e || null === (n = e.ttpush_event_extra) || void 0 === n ? void 0 : n.push_type,
        eventType: null == e || null === (r = e.ttpush_event_extra) || void 0 === r ? void 0 : r.event_type
      }
    }
      , p = function(e) {
      var t = e.webId
        , n = e.isLogin
        , o = e.open
        , l = (0,
        a.useRef)()
        , d = function() {
        var e = (0,
          r.Z)(i().mark((function e() {
            var n;
            return i().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return e.next = 2,
                        m.k();
                    case 2:
                      n = new c.FWS({
                        fpID: "32",
                        aID: "6383",
                        enableTransformTextPayload: !0,
                        accessKey: u("".concat(32, "a1ede44a8715fd38c64d52cbd6dc7f5b", t, "f8a69f1719916z")),
                        deviceID: t,
                        url: "ws://frontier-pc.douyin.com",
                        payloadEncoding: {
                          encoding: "",
                          force: !0
                        },
                        payloadType: {
                          type: "application/json",
                          force: !0
                        }
                      }),
                        l.current = n,
                        n.onopen = function(e) {}
                        ,
                        n.onmessage = function(e) {
                          var t, n, r = {};
                          try {
                            var o, i = s().parse(null == e || null === (o = e.message) || void 0 === o ? void 0 : o.textPayload);
                            r = h(i)
                          } catch (l) {
                            var a;
                            v.oe.event.error({
                              name: v.Mo.FrontierMessageError,
                              report: {
                                message: null == e || null === (a = e.message) || void 0 === a ? void 0 : a.textPayload
                              }
                            })
                          }
                          "live" === (null === (t = r) || void 0 === t ? void 0 : t.type) && "live_start_appointed" === (null === (n = r) || void 0 === n ? void 0 : n.eventType) && f.emit(f.EVENT.webLivePushMessage, r)
                        }
                      ;
                    case 6:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function() {
          return e.apply(this, arguments)
        }
      }();
      (0,
        a.useEffect)((function() {
          return t && n && o && d(),
            function() {
              var e;
              null == l || null === (e = l.current) || void 0 === e || e.close()
            }
        }
      ), [t, n, o])
    }
  }
  ,
  89543: (e,t,n)=>{
    n.d(t, {
      c: ()=>a
    });
    var r = n(32781)
      , o = n(44503)
      , i = n(92557);
    function a() {
      var e = o.useState(!1)
        , t = (0,
        r.Z)(e, 2)
        , n = t[0]
        , a = t[1];
      return (0,
        o.useEffect)((function() {
          var e = i.listen(i.EVENT.searchBarFocus, (function() {
              a(!0)
            }
          ))
            , t = i.listen(i.EVENT.searchBarBlur, (function() {
              a(!1)
            }
          ));
          return function() {
            e(),
              t()
          }
        }
      ), []),
        n
    }
  }
  ,
  58704: (e,t,n)=>{
    n.d(t, {
      r: ()=>c
    });
    var r = n(32781)
      , o = n(70995)
      , i = n.n(o)
      , a = n(44503)
      , l = n(37610)
      , s = n(90147);
    function c() {
      var e = (0,
        a.useState)(!1)
        , t = (0,
        r.Z)(e, 2)
        , n = t[0]
        , o = t[1]
        , c = (0,
        a.useState)(!1)
        , u = (0,
        r.Z)(c, 2)
        , d = u[0]
        , m = u[1]
        , v = (0,
        a.useState)(!1)
        , f = (0,
        r.Z)(v, 2)
        , h = f[0]
        , p = f[1]
        , g = (0,
        a.useState)(!1)
        , y = (0,
        r.Z)(g, 2)
        , w = y[0]
        , _ = y[1]
        , E = (0,
        l.k6)();
      return (0,
        a.useEffect)((function() {
          var e;
          return o(i()(e = window.location.href).call(e, "https://".concat(s.HOME_DOMAIN, "/video")))
        }
      ), []),
        (0,
          a.useEffect)((function() {
            var e;
            return m(i()(e = window.location.href).call(e, "https://".concat(s.HOME_DOMAIN, "/user")))
          }
        ), []),
        (0,
          a.useEffect)((function() {
            var e;
            return p(i()(e = window.location.href).call(e, "https://".concat(s.HOME_DOMAIN, "/note")))
          }
        ), []),
        (0,
          a.useEffect)((function() {
            return _(n || d || h)
          }
        ), [n, d, h]),
        (0,
          a.useEffect)((function() {
            var e = E.listen((function(e) {
                var t = e.pathname
                  , n = i()(t).call(t, "/user/")
                  , r = i()(t).call(t, "/video/")
                  , o = i()(t).call(t, "/note/");
                n || r || o || !w || _(!1)
              }
            ));
            return function() {
              return e()
            }
          }
        ), [E, w]),
        {
          shouldShowBackToHome: w,
          inVideoDetailPage: n,
          inUserPage: d,
          inNoteDetailPage: h
        }
    }
  }
  ,
  16340: (e,t,n)=>{
    n.d(t, {
      Z: ()=>f
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(5594)
      , a = n.n(i)
      , l = n(44503)
      , s = n(53607)
      , c = n(9070)
      , u = n(73750)
      , d = n(16655)
      , m = n(92557)
      , v = n(51652);
    function f() {
      var e = l.useState(null)
        , t = (0,
        o.Z)(e, 2)
        , n = t[0]
        , i = t[1]
        , f = (0,
        l.useState)(!0)
        , h = (0,
        o.Z)(f, 2)
        , p = h[0]
        , g = h[1];
      return (0,
        l.useEffect)((function() {
          var e = function() {
            var e = s.Q.getItem({
              sKey: v.CookieKeys.Theme
            }) !== v.ThemeValues.Light;
            g(e)
          };
          if (e(),
            (0,
              r.Z)(a().mark((function e() {
                var t;
                return a().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          return e.next = 2,
                            c.U2({
                              key: u.TccKey.SpecTheme,
                              defaultValue: u.TCC_DEFAULT_VALUE_MAP.get(u.TccKey.SpecTheme)
                            });
                        case 2:
                          t = e.sent,
                            i(t);
                        case 4:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            )))(),
            d.DT())
            return document.addEventListener("visibilitychange", e),
              function() {
                document.removeEventListener("visibilitychange", e)
              }
        }
      ), []),
        (0,
          l.useEffect)((function() {
            var e = m.listen(m.EVENT.changeTheme, (function(e) {
                var t = e.theme;
                return g(t === v.ThemeValues.Dark)
              }
            ));
            return function() {
              e()
            }
          }
        ), []),
        {
          specTheme: n,
          isDark: p
        }
    }
  }
  ,
  91881: (e,t,n)=>{
    n.d(t, {
      j: ()=>a
    });
    var r = n(32781)
      , o = n(44503)
      , i = n(37610);
    function a() {
      var e, t = (0,
        o.useState)(!0), n = (0,
        r.Z)(t, 2), a = n[0], l = n[1], s = (0,
        o.useRef)(0), c = (0,
        o.useRef)(!1), u = (0,
        i.k6)(), d = null == u || null === (e = u.location) || void 0 === e ? void 0 : e.pathname;
      return (0,
        o.useEffect)((function() {
          var e = function() {
            s.current = window.scrollY,
            c.current || window.requestAnimationFrame((function() {
                l(0 === s.current),
                  c.current = !1
              }
            )),
              c.current = !0
          };
          return window.addEventListener("scroll", e),
            function() {
              return window.removeEventListener("scroll", e)
            }
        }
      ), []),
        {
          transparent: a && new RegExp("^/user/*?").test(d)
        }
    }
  }
  ,
  73796: (e,t,n)=>{
    n.d(t, {
      h4: ()=>s
    });
    var r = n(30906)
      , o = n(44503)
      , i = n(26637)
      , a = n(5200)
      , l = n(95680)
      , s = function(e) {
      var t, n;
      return (0,
        i.o)(null === (t = e.abTestData) || void 0 === t ? void 0 : t.hasHorizontalHeader, null === (n = e.customProps) || void 0 === n ? void 0 : n.isClient).isHorizontalLayout ? o.createElement(l.Z, (0,
        r.Z)({}, e)) : o.createElement(a.Z, (0,
        r.Z)({}, e))
    }
  }
  ,
  1392: (e,t,n)=>{
    n.d(t, {
      v: ()=>a,
      Z: ()=>s
    });
    var r = n(52252)
      , o = n(25083)
      , i = n(37485)
      , a = function() {
      return r.p() ? "" : o.vM()
    }
      , l = {
      pageClick: {
        eventName: "page_click",
        params: {
          click_position: "",
          enter_from: ""
        }
      },
      pageView: {
        eventName: "page_view",
        params: {
          url: "",
          url_path: "",
          enter_from: "",
          link_from: "",
          tab_name: "",
          enter_method: "",
          aweme_type: 0,
          theme: "light",
          is_topknot: 0,
          abtest: "",
          ischange: "",
          old_ttwid: "",
          enter_by_tab: 0,
          browser_height: 0,
          browser_width: 0,
          browser_ratio: 0,
          redirect_from: "",
          from_push: 0,
          seo_vids: ""
        }
      },
      pageViewError: {
        eventName: "page_view_error",
        params: {
          url: "",
          enter_from: "",
          uid: "",
          uuid: ""
        }
      },
      pageViewMonitor: {
        eventName: "page_view_monitor",
        params: {
          url: "",
          enter_from: "",
          uid: "",
          uuid: ""
        }
      },
      pageViewMonitorTest: {
        eventName: "page_view_monitor_test",
        params: {
          url: ""
        }
      },
      pageStayTime: {
        eventName: "page_stay_time",
        params: {
          url: "",
          url_path: "",
          enter_from: "",
          enter_method: "",
          duration: 0,
          is_visible: 1,
          link_from: "",
          tab_name: "",
          aweme_type: 0
        }
      },
      topknotWearShow: {
        eventName: "topknot_waer_show",
        params: {}
      },
      webPushVerify: {
        eventName: "web_push_verify",
        params: {
          browser: "",
          can_use_notification_api: "0",
          can_use_push_api: "0",
          can_use_sw_api: "0",
          can_use_all_api: "0",
          user_agant: ""
        }
      },
      addToDesktopShow: {
        eventName: "add_to_desktop_show",
        params: {
          enter_from: "",
          type: "hover",
          is_full_screen: "0",
          platform: ""
        }
      },
      addToDesktopClick: {
        eventName: "add_to_desktop_click",
        params: {
          enter_from: "",
          type: "hover",
          is_full_screen: "0",
          platform: ""
        }
      },
      addToDesktopGuideClose: {
        eventName: "add_to_desktop_guide_close",
        params: {
          enter_from: "",
          is_full_screen: "0"
        }
      },
      installNativePanelShow: {
        eventName: "install_native_panel_show",
        params: {}
      },
      installNativePanelClick: {
        eventName: "install_native_panel_click",
        params: {
          action: "cancel"
        }
      },
      personalPanelShow: {
        eventName: "personal_panel_show",
        params: {
          enter_from: ""
        }
      },
      personalPanelClick: {
        eventName: "personal_panel_click",
        params: {
          enter_from: "",
          click_position: "post"
        }
      },
      clickLogOut: {
        eventName: "click_log_out",
        params: {
          enter_from: ""
        }
      },
      newImShow: {
        eventName: "new_im_show",
        params: {
          is_new: "",
          enter_from: o.yW()
        }
      },
      clickPreviousPage: {
        eventName: "click_previous_page",
        params: {
          enter_from: ""
        }
      },
      clickMainPage: {
        eventName: "click_main_page",
        params: {
          enter_from: ""
        }
      },
      clientSettingHover: {
        eventName: "client_setting_hover",
        params: {
          badge: 1
        }
      },
      clientSettingClick: {
        eventName: "client_setting_click",
        params: {
          position: "",
          badge: 1
        }
      },
      from360: {
        eventName: "from_360",
        params: {
          qhclickid: "",
          uuid: ""
        }
      },
      cooperatePanelShow: {
        eventName: "cooperate_panel_show",
        params: {
          enter_from: ""
        }
      },
      publishPanelShow: {
        eventName: "publish_panel_show",
        params: {
          enter_from: ""
        }
      },
      downloadPanelShow: {
        eventName: "download_panel_show",
        params: {
          enter_from: ""
        }
      },
      downloadPanelClick: {
        eventName: "download_panel_click",
        params: {
          enter_from: ""
        }
      },
      feedClick: {
        eventName: "feed_click",
        params: {
          enter_from: ""
        }
      },
      clickReturnPage: {
        eventName: "click_return_page",
        params: {
          enter_from: ""
        }
      },
      addToDesktopBadgeShow: {
        eventName: "add_to_desktop_badge_show",
        params: {
          enter_from: ""
        }
      },
      clientSettingBadgeShow: {
        eventName: "client_setting_badge_show",
        params: {}
      },
      addToDesktopClose: {
        eventName: "add_to_desktop_close",
        params: {
          enter_from: ""
        }
      }
    };
    const s = new i.hD(l)
  }
  ,
  91707: (e,t,n)=>{
    n.d(t, {
      b: ()=>o,
      S: ()=>i
    });
    var r = 0;
    function o() {
      r = 1
    }
    function i() {
      return r
    }
  }
  ,
  74394: (e,t,n)=>{
    n.d(t, {
      G1: ()=>m,
      Jo: ()=>v,
      CT: ()=>r,
      P0: ()=>f,
      D5: ()=>h,
      Tw: ()=>p
    });
    var r, o = n(64408), i = n(5594), a = n.n(i), l = n(21805), s = n.n(l), c = n(66231), u = n(48387), d = n(89942);
    function m(e) {
      return "Mac" === (e || c.f()).os
    }
    function v(e) {
      var t, n = e || c.f();
      return "Windows" === n.os && s()(t = ["Win7", "Win8", "Win8.1", "Win10"]).call(t, n.version)
    }
    function f() {
      var e = c.f();
      return m(e) ? r.Mac : function(e) {
        return "Linux" === (e || c.f()).os
      }(e) ? r.Linux : v(e) ? r.Win7Up : function(e) {
        var t, n = e || c.f();
        return "Windows" === n.os && s()(t = ["Win2000", "WinXp", "Win2003", "WinVista"]).call(t, n.version)
      }(e) ? r.Win7Down : r.Unknown
    }
    function h() {
      var e = f();
      return e === r.Win7Up || e === r.Mac
    }
    !function(e) {
      e.Mac = "Mac",
        e.Win7Up = "Win7Up",
        e.Linux = "Linux",
        e.Win7Down = "Win7Down",
        e.Unknown = "Unknown"
    }(r || (r = {}));
    var p = function() {
      var e = (0,
        o.Z)(a().mark((function e() {
          var t;
          return a().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      u.pL();
                  case 2:
                    return t = e.sent,
                      e.abrupt("return", !t || d.KC(1e3 * t));
                  case 4:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
  }
  ,
  95294: (e,t,n)=>{
    n.d(t, {
      Z: ()=>b
    });
    var r = n(65146)
      , o = n(99860)
      , i = n.n(o)
      , a = n(44503)
      , l = n(79705)
      , s = n.n(l)
      , c = n(92762)
      , u = n(34080);
    const d = "MoQWZoTN"
      , m = "UqusYa12"
      , v = "kVDE1onh"
      , f = "AJbcSJri"
      , h = "LQOiJJXR"
      , p = "T3FP2rdt"
      , g = "CyFHfLRN"
      , y = "I6O_p7Gl"
      , w = "Rlk_prZy"
      , _ = "e0OEnO1u"
      , E = "_XYQB999";
    var k = n(14001)
      , x = n(52255);
    const b = function(e) {
      var t, n, o = e.value, l = e.spa, b = e.href, C = e.label, N = e.target, T = e.handleTabClick, Z = e.className, S = e.showYellowPoint, I = void 0 !== S && S, L = e.showDotRedPoint, D = void 0 !== L && L, M = e.showLiveRedPoint, B = void 0 !== M && M, A = e.showNumberYellowPoint, P = void 0 !== A && A, O = e.showLiveRedCnPoint, V = void 0 !== O && O, W = e.numberYellowPointCount, R = void 0 === W ? 0 : W, F = e.numberYellowClassName, U = e.showNumberRedPoint, H = e.numberRedPointCount, G = e.renderLabel, j = new (i())([]);
      return a.createElement("div", {
        className: s()(d, Z)
      }, a.createElement(k.a, {
        className: _,
        spa: l,
        href: globalThis.getFilterXss().filterUrl(b, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        target: N,
        onClick: T,
        title: C
      }, a.createElement("div", {
        className: s()(f, j.get(o))
      }, I && a.createElement("div", {
        className: m
      }), D && a.createElement("div", {
        className: v
      }), B && a.createElement("div", {
        className: h
      }, a.createElement(x.Z, {
        src: globalThis.getFilterXss().filterUrl(c.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        viewBox: "0 0 19 7",
        height: 7,
        width: 19
      })), P && a.createElement("div", {
        className: s()(F, (t = {},
          (0,
            r.Z)(t, y, R < 10),
          (0,
            r.Z)(t, g, R >= 10),
          t))
      }, R > 99 ? "99+" : R), U && a.createElement("div", {
        className: s()(F, (n = {},
          (0,
            r.Z)(n, w, H < 10),
          (0,
            r.Z)(n, E, H >= 10),
          n))
      }, H > 99 ? "99+" : H), V && a.createElement("div", {
        className: p
      }, a.createElement(x.Z, {
        src: globalThis.getFilterXss().filterUrl(u.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        viewBox: "0 0 44 20",
        height: 20,
        width: 44
      })), null == G ? void 0 : G())))
    }
  }
  ,
  8841: (e,t,n)=>{
    n.d(t, {
      G: ()=>D
    });
    var r = n(65146)
      , o = n(64408)
      , i = n(30906)
      , a = n(32781)
      , l = n(5594)
      , s = n.n(l)
      , c = n(81711)
      , u = n.n(c)
      , d = n(59440)
      , m = n.n(d)
      , v = n(88438)
      , f = n.n(v)
      , h = n(21805)
      , p = n.n(h)
      , g = n(79705)
      , y = n.n(g)
      , w = n(44503)
      , _ = n(24260)
      , E = n(93662)
      , k = n.n(E)
      , x = n(92345)
      , b = n(92762)
      , C = n(55717)
      , N = n(75570)
      , T = n(95294)
      , Z = n(14001)
      , S = n(52255)
      , I = n(16340)
      , L = (0,
      _.default)({
      resolved: {},
      chunkName: function() {
        return "Lottie"
      },
      isReady: function(e) {
        var t = this.resolve(e);
        return !0 === this.resolved[t] && !!n.m[t]
      },
      importAsync: function() {
        return Promise.all([n.e(1115), n.e(8670)]).then(n.bind(n, 86256))
      },
      requireAsync: function(e) {
        var t = this
          , n = this.resolve(e);
        return this.resolved[n] = !1,
          this.importAsync(e).then((function(e) {
              return t.resolved[n] = !0,
                e
            }
          ))
      },
      requireSync: function e(t) {
        var r = this.resolve(t);
        return n(r)
      },
      resolve: function e() {
        return 86256
      }
    }, {
      ssr: !1
    })
      , D = function(e) {
      var t, n, l, c = e.label, d = e.value, v = e.type, h = e.onClick, g = e.active, _ = e.className, E = e.renderLabel, D = e.href, M = e.target, B = e.spa, A = e.activeClickable, P = e.iconBackgroundPosition, O = e.iconAnimation, V = e.points, W = e.pointClick, R = e.pointShow, F = e.userInfo, U = void 0 === F ? {} : F, H = (e.tccKeyWord,
        e.socialInfo), G = void 0 === H ? {} : H, j = e.customProps, K = w.useState(k()(O) ? null : O), q = (0,
        a.Z)(K, 2), Y = q[0], X = q[1], z = w.useState(!1), Q = (0,
        a.Z)(z, 2), J = Q[0], $ = Q[1], ee = w.useState(!1), te = (0,
        a.Z)(ee, 2), ne = te[0], re = te[1], oe = w.useState(!1), ie = (0,
        a.Z)(oe, 2), ae = ie[0], le = ie[1], se = w.useState(!1), ce = (0,
        a.Z)(se, 2), ue = ce[0], de = ce[1], me = w.useState(!1), ve = (0,
        a.Z)(me, 2), fe = ve[0], he = ve[1], pe = w.useState(!1), ge = (0,
        a.Z)(pe, 2), ye = ge[0], we = ge[1], _e = w.useState(!1), Ee = (0,
        a.Z)(_e, 2), ke = Ee[0], xe = Ee[1], be = w.useState(!1), Ce = (0,
        a.Z)(be, 2), Ne = Ce[0], Te = Ce[1], Ze = w.useState(0), Se = (0,
        a.Z)(Ze, 2), Ie = Se[0], Le = Se[1], De = w.useState(!1), Me = (0,
        a.Z)(De, 2), Be = Me[0], Ae = Me[1], Pe = w.useState(0), Oe = (0,
        a.Z)(Pe, 2), Ve = Oe[0], We = Oe[1], Re = w.useRef(), Fe = w.useRef(), Ue = ["friend", "home", "recommend", "follow", "live", "hot", "channel_300201", "channel_200204", "channel_300203", "channel_300205", "channel_300204", "channel_300207", "channel_300208", "channel_300209", "channel_300202"], He = ["channel_300206"], Ge = w.useCallback((function(e) {
          if (h) {
            var t = [{
              isShow: ue,
              type: x.TabPointType.YellowDot
            }, {
              isShow: Ne,
              type: x.TabPointType.YellowNumber
            }, {
              isShow: ae,
              type: x.TabPointType.RedDot
            }, {
              isShow: fe,
              type: x.TabPointType.RedNew
            }, {
              isShow: ye,
              type: x.TabPointType.RedLive
            }, {
              isShow: ke,
              type: x.TabPointType.RedLiveCn
            }, {
              isShow: Be,
              type: x.TabPointType.RedNumber
            }];
            u()(t).call(t, (function(e) {
                var t = e.isShow
                  , n = e.type;
                t && (null == W || W((0,
                  i.Z)((0,
                  i.Z)({}, U.info), {}, {
                  pointType: n,
                  isLogin: U.isLogin,
                  redPointCount: Ve
                })))
              }
            )),
              de(!1),
              le(!1),
              he(!1),
              Te(!1),
              we(!1),
              xe(!1),
              Ae(!1),
              A ? h(d, e) : g || h(d, e)
          }
        }
      ), [d, h, g, U, ue, Ne, ae, fe, ye, ke, A, W, Be, Ve]);
      w.useEffect((function() {
          var e = !1;
          return "function" == typeof V && (g ? (de(!1),
            le(!1),
            he(!1),
            Te(!1),
            we(!1),
            xe(!1),
            Ae(!1)) : (0,
            o.Z)(s().mark((function t() {
              var n, r, o, a, l, c, u;
              return s().wrap((function(t) {
                  for (; ; )
                    switch (t.prev = t.next) {
                      case 0:
                        return t.next = 2,
                          V((0,
                            i.Z)((0,
                            i.Z)({}, null == U ? void 0 : U.info), {}, {
                            isLogin: null == U ? void 0 : U.isLogin,
                            socialInfo: G
                          }));
                      case 2:
                        if (t.t0 = t.sent,
                          t.t0) {
                          t.next = 5;
                          break
                        }
                        t.t0 = [];
                      case 5:
                        n = t.t0,
                        e || (r = m()(n).call(n, (function(e) {
                            return e.type === x.TabPointType.YellowDot
                          }
                        )),
                          de(!g && Boolean(null == r ? void 0 : r.hasNotice)),
                          o = m()(n).call(n, (function(e) {
                              return e.type === x.TabPointType.YellowNumber
                            }
                          )),
                          Te(!g && Boolean((null == o ? void 0 : o.hasNotice) && (null == o ? void 0 : o.count) > 0)),
                          Le((null == o ? void 0 : o.count) || 0),
                          a = m()(n).call(n, (function(e) {
                              return e.type === x.TabPointType.RedNumber
                            }
                          )),
                          Ae(!g && Boolean((null == a ? void 0 : a.hasNotice) && (null == a ? void 0 : a.count) > 0)),
                          We((null == a ? void 0 : a.count) || 0),
                          l = m()(n).call(n, (function(e) {
                              return e.type === x.TabPointType.RedDot
                            }
                          )),
                          le(!g && Boolean(null == l ? void 0 : l.hasNotice)),
                          c = m()(n).call(n, (function(e) {
                              return e.type === x.TabPointType.RedNew
                            }
                          )),
                          he(!g && Boolean(null == c ? void 0 : c.hasNotice)),
                          u = m()(n).call(n, (function(e) {
                              return e.type === x.TabPointType.RedLive
                            }
                          )),
                          we(!g && Boolean(null == u ? void 0 : u.hasNotice)));
                      case 7:
                      case "end":
                        return t.stop()
                    }
                }
              ), t)
            }
          )))()),
            function() {
              e = !0
            }
        }
      ), [U, g, G]),
        w.useEffect((function() {
            var e = [{
              isShow: ue,
              type: x.TabPointType.YellowDot
            }, {
              isShow: Ne,
              type: x.TabPointType.YellowNumber
            }, {
              isShow: ae,
              type: x.TabPointType.RedDot
            }, {
              isShow: ye,
              type: x.TabPointType.RedLive
            }, {
              isShow: ke,
              type: x.TabPointType.RedLiveCn
            }, {
              isShow: Be,
              type: x.TabPointType.RedNumber
            }];
            u()(e).call(e, (function(e) {
                e.isShow && (null == R || R((0,
                  i.Z)((0,
                  i.Z)({}, U.info), {}, {
                  pointType: e.type,
                  isLogin: U.isLogin,
                  redPointCount: Ve
                })))
              }
            ))
          }
        ), [U, ue, Ne, ae, fe, ye, ke, Be, Ve, R]);
      var je = w.useCallback((function() {
          var e, t, n = null === (e = Re.current) || void 0 === e || null === (t = e.getLottieInstance) || void 0 === t ? void 0 : t.call(e);
          return {
            playLottie: function() {
              var e, t;
              null == n || null === (e = n.setDirection) || void 0 === e || e.call(n, 1),
              null == n || null === (t = n.play) || void 0 === t || t.call(n)
            },
            resetLottie: function() {
              var e;
              null == n || null === (e = n.goToAndStop) || void 0 === e || e.call(n, 0)
            },
            reversePlayLottie: function() {
              var e, t;
              null == n || null === (e = n.setDirection) || void 0 === e || e.call(n, -1),
              null == n || null === (t = n.play) || void 0 === t || t.call(n)
            },
            endOfLottie: function() {
              var e;
              null == n || null === (e = n.goToAndStop) || void 0 === e || e.call(n, null == n ? void 0 : n.getDuration(!0), !0)
            }
          }
        }
      ), []);
      w.useEffect((function() {
          Fe.current && clearTimeout(Fe.current),
            g ? je().endOfLottie() : je().resetLottie()
        }
      ), [g]);
      var Ke = (0,
        I.Z)().specTheme;
      return w.createElement(w.Fragment, null, "text" === v && w.createElement("div", {
        className: y()(C.Z.tab, (t = {},
          (0,
            r.Z)(t, C.Z.active, g),
          (0,
            r.Z)(t, C.Z.activeClickable, A && g),
          (0,
            r.Z)(t, C.Z.searchTabWrap, null == j ? void 0 : j.isSearchSideNav),
          t), _)
      }, w.createElement(Z.a, {
        className: C.Z.itemLink,
        spa: B,
        href: globalThis.getFilterXss().filterUrl(D, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        target: M,
        onClick: Ge,
        onMouseEnter: function() {
          k()(O) ? O().then((function(e) {
              !Y && X(e),
                re(!0),
              g || (Fe.current = f()((function() {
                  je().playLottie()
                }
              ), 300))
            }
          )) : (re(!0),
          g || (Fe.current = f()((function() {
              je().playLottie()
            }
          ), 300)))
        },
        onMouseLeave: function() {
          g || (clearTimeout(Fe.current),
            je().reversePlayLottie())
        }
      }, ue && w.createElement("div", {
        className: C.Z.yellowPoint
      }), ae && w.createElement("div", {
        className: C.Z.redPoint
      }), ye && w.createElement("div", {
        className: y()(C.Z.liveRedPoint, (0,
          r.Z)({}, C.Z.borderNone, null == Ke ? void 0 : Ke.themeFurtherSwitch))
      }, w.createElement(S.Z, {
        src: globalThis.getFilterXss().filterUrl(b.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        viewBox: "0 0 19 7",
        height: 7,
        width: 19
      })), Ne && w.createElement("div", {
        className: y()((n = {},
          (0,
            r.Z)(n, C.Z.numberYellowPointPosText2, p()(Ue).call(Ue, d)),
          (0,
            r.Z)(n, C.Z.numberYellowPointPosText3, p()(He).call(He, d)),
          (0,
            r.Z)(n, C.Z.digitsNumberYellowPoint, Ie < 10),
          (0,
            r.Z)(n, C.Z.numberYellowPoint, Ie >= 10),
          (0,
            r.Z)(n, C.Z.moreCount, Ie > 99),
          (0,
            r.Z)(n, C.Z.borderNone, null == Ke ? void 0 : Ke.themeFurtherSwitch),
          n))
      }, Ie > 99 ? w.createElement(S.Z, {
        src: globalThis.getFilterXss().filterUrl(N.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        viewBox: "0 0 22 9",
        height: 9,
        width: 22
      }) : Ie), Be && w.createElement("div", {
        className: y()((l = {},
          (0,
            r.Z)(l, C.Z.numberYellowPointPosText2, p()(Ue).call(Ue, d)),
          (0,
            r.Z)(l, C.Z.numberYellowPointPosText3, p()(He).call(He, d)),
          (0,
            r.Z)(l, C.Z.digitsNumberRedPoint, Ve < 10),
          (0,
            r.Z)(l, C.Z.numberRedPoint, Ve >= 10),
          (0,
            r.Z)(l, C.Z.moreCount, Ve > 99),
          (0,
            r.Z)(l, C.Z.borderNone, null == Ke ? void 0 : Ke.themeFurtherSwitch),
          l))
      }, Ve > 99 ? w.createElement(S.Z, {
        src: globalThis.getFilterXss().filterUrl(N.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        viewBox: "0 0 22 9",
        height: 9,
        width: 22
      }) : Ve), w.createElement("div", {
        className: y()(C.Z.icon, C.Z.iconDark, (0,
          r.Z)({}, C.Z.hidden, J)),
        style: {
          backgroundPosition: "".concat(g ? P.darkActive : P.dark),
          backgroundSize: "".concat(x.ICON_BACKGROUND_SIZE, "px auto")
        }
      }), w.createElement("div", {
        className: y()(C.Z.icon, C.Z.iconLight, (0,
          r.Z)({}, C.Z.hidden, J)),
        style: {
          backgroundPosition: "".concat(g ? P.lightActive : P.light),
          backgroundSize: "".concat(x.ICON_BACKGROUND_SIZE, "px auto")
        }
      }), ne && w.createElement(L, {
        data: Y,
        hidden: !1,
        loop: !1,
        autoplay: !1,
        ref: Re,
        className: y()(C.Z.icon, (0,
          r.Z)({}, C.Z.hidden, !J)),
        onInit: function() {
          $(!0),
            g ? je().endOfLottie() : je().resetLottie()
        }
      }), w.createElement("div", {
        className: C.Z.textWrap
      }, w.createElement("span", {
        className: C.Z.text
      }, E ? E() : c)))), "image" === v && w.createElement(T.Z, {
        spa: B,
        href: globalThis.getFilterXss().filterUrl(D, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        label: c,
        target: M,
        value: d,
        handleTabClick: Ge,
        showLiveRedPoint: ye,
        showYellowPoint: ue,
        showDotRedPoint: ae,
        showNumberYellowPoint: Ne,
        showLiveRedCnPoint: ke,
        showNumberRedPoint: Be,
        active: g,
        activeClickable: A,
        renderLabel: E
      }))
    }
  }
  ,
  81971: (e,t,n)=>{
    n.d(t, {
      A: ()=>m
    });
    var r = n(30906)
      , o = n(84891)
      , i = n.n(o)
      , a = n(41265)
      , l = n.n(a)
      , s = n(51272)
      , c = n(44503)
      , u = n(52255)
      , d = (n(32781),
      (0,
        c.createContext)(null))
      , m = function(e) {
      var t, n, o, a, m, v, f = e.src, h = e.width, p = e.height, g = e.id, y = e.viewBox, w = e.defaultHeight, _ = e.defaultWidth, E = e.className, k = e.onClick, x = e.isSpider, b = void 0 !== x && x, C = (0,
        c.useContext)(d), N = (0,
        c.useRef)(s.o()), T = (0,
        c.useRef)();
      if (C && T.current !== g) {
        var Z;
        T.current = g;
        var S = C.usedIconMap[g] || [];
        S.push({
          id: N.current,
          width: Number(h),
          height: Number(p)
        }),
          C.usedIconMap[g] = S,
        null === (Z = C.setUsedIconMap) || void 0 === Z || Z.call(C, (0,
          r.Z)({}, C.usedIconMap))
      }
      (0,
        c.useEffect)((function() {
          if (C)
            return function() {
              var e, t = C.usedIconMap[g] || [], n = i()(t).call(t, (function(e) {
                  return e.id === N.current
                }
              ));
              n > -1 && (l()(t).call(t, n, 1),
                C.usedIconMap[g] = t,
              null === (e = C.setUsedIconMap) || void 0 === e || e.call(C, (0,
                r.Z)({}, C.usedIconMap)))
            }
        }
      ), [g]);
      var I = (0,
        c.useMemo)((function() {
          if (C) {
            var e, t, n = C.usedIconMap[g] || [];
            return (null === (e = n[0]) || void 0 === e ? void 0 : e.id) && (null === (t = n[0]) || void 0 === t ? void 0 : t.id) !== N.current
          }
          return !1
        }
      ), [g, null == C ? void 0 : C.usedIconMap]);
      return b ? null : I ? c.createElement("svg", {
        onClick: k,
        width: Number(h) / (null == C || null === (t = C.usedIconMap) || void 0 === t || null === (n = t[g]) || void 0 === n || null === (o = n[0]) || void 0 === o ? void 0 : o.width) * Number(_) || _,
        height: Number(p) / (null == C || null === (a = C.usedIconMap) || void 0 === a || null === (m = a[g]) || void 0 === m || null === (v = m[0]) || void 0 === v ? void 0 : v.height) * Number(w) || w,
        viewBox: y,
        className: E
      }, c.createElement("use", {
        xlinkHref: "#".concat(g)
      })) : c.createElement(u.Z, {
        onClick: k,
        src: globalThis.getFilterXss().filterUrl(f, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: Number(h),
        height: Number(p),
        viewBox: y,
        id: g,
        className: E
      })
    }
  }
  ,
  55861: (e,t,n)=>{
    n.d(t, {
      n: ()=>H
    });
    var r = n(32781)
      , o = n(19049)
      , i = n(95508)
      , a = n(65146)
      , l = n(64408)
      , s = n(14212)
      , c = n.n(s)
      , u = n(88438)
      , d = n.n(u)
      , m = n(80051)
      , v = n.n(m)
      , f = n(5594)
      , h = n.n(f)
      , p = n(44503)
      , g = n(9)
      , y = n(72983)
      , w = n(95127)
      , _ = n(25083)
      , E = n(53607)
      , k = n(53246)
      , x = n(52252)
      , b = n(51652)
      , C = n(62184)
      , N = n(30906)
      , T = n(79705)
      , Z = n.n(T)
      , S = n(70676)
      , I = n.n(S)
      , L = n(1021)
      , D = n(47482)
      , M = n(45627)
      , B = n(97050)
      , A = n(53540);
    const P = JSON.parse('{"v":"5.6.10","fr":60,"ip":0,"op":300,"w":540,"h":114,"nm":"\u767b\u5f55","ddd":0,"assets":[{"id":"comp_0","layers":[{"ddd":0,"ind":1,"ty":4,"nm":"\u201ctext\u201d\u8f6e\u5ed3","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[108,40,0],"ix":2},"a":{"a":0,"k":[0,0,0],"ix":1},"s":{"a":0,"k":[300,300,100],"ix":6}},"ao":0,"shapes":[{"ty":"gr","it":[{"ind":0,"ty":"sh","ix":1,"ks":{"a":0,"k":{"i":[[0,0],[0.415,0.005],[0.392,0.014],[0.341,0.023],[0.252,0.019],[0,0],[-0.28,0.019],[-0.443,0.014],[-0.658,0.005],[-1.008,0],[-0.663,-0.005],[-0.439,-0.014],[-0.285,-0.019],[-0.252,-0.028],[0,0],[0.271,-0.014],[0.359,-0.009],[0.462,-0.005],[0.616,0],[-0.187,0.443],[-0.154,0.364],[-0.126,0.303],[-0.121,0.289],[-0.098,0.135],[-0.047,0.028],[0.014,0.079],[0.149,0.019],[0.159,0.065],[0.233,0.149],[0.14,-0.513],[0.21,-0.583],[0.257,-0.607],[0.271,-0.569]],"o":[[-0.401,0],[-0.415,-0.005],[-0.392,-0.014],[-0.341,-0.023],[0,0],[0.252,-0.028],[0.28,-0.019],[0.443,-0.014],[0.658,-0.005],[1.008,0],[0.663,0.005],[0.439,0.014],[0.285,0.019],[0,0],[-0.224,0.019],[-0.271,0.014],[-0.359,0.009],[-0.462,0.005],[0.243,-0.579],[0.187,-0.443],[0.154,-0.364],[0.126,-0.303],[0.168,-0.401],[0.098,-0.135],[0.159,-0.093],[-0.014,-0.079],[-0.168,-0.019],[-0.159,-0.065],[-0.047,0.383],[-0.14,0.513],[-0.21,0.583],[-0.257,0.607],[0,0]],"v":[[-22.064,-0.472],[-23.289,-0.479],[-24.5,-0.507],[-25.599,-0.563],[-26.488,-0.626],[-26.488,0.41],[-25.69,0.34],[-24.605,0.291],[-22.953,0.263],[-20.454,0.256],[-17.948,0.263],[-16.296,0.291],[-15.211,0.34],[-14.406,0.41],[-14.406,-0.598],[-15.148,-0.549],[-16.093,-0.514],[-17.325,-0.493],[-18.942,-0.486],[-18.298,-2.019],[-17.787,-3.23],[-17.367,-4.231],[-16.996,-5.12],[-16.597,-5.925],[-16.38,-6.17],[-16.163,-6.429],[-16.408,-6.576],[-16.898,-6.702],[-17.486,-7.024],[-17.766,-5.68],[-18.291,-4.035],[-18.991,-2.25],[-19.782,-0.486]],"c":true},"ix":2},"nm":"\u7acb","mn":"ADBE Vector Shape - Group","hd":false},{"ind":1,"ty":"sh","ix":2,"ks":{"a":0,"k":{"i":[[0.079,0.219],[0.084,0.21],[0.098,0.224],[0.131,0.299],[0,0],[-0.177,-0.355],[-0.14,-0.411],[0.504,0.005],[0.369,0.014],[0.261,0.019],[0.215,0.019],[0,0],[-0.266,0.019],[-0.387,0.014],[-0.532,0.005],[-0.747,0],[-0.56,-0.005],[-0.415,-0.014],[-0.294,-0.019],[-0.224,-0.028],[0,0],[0.271,-0.019],[0.373,-0.009],[0.49,-0.009],[0.644,0]],"o":[[-0.079,-0.219],[-0.084,-0.21],[-0.098,-0.224],[0,0],[0.271,0.457],[0.177,0.355],[-0.7,0],[-0.504,-0.005],[-0.369,-0.014],[-0.261,-0.019],[0,0],[0.224,-0.028],[0.266,-0.019],[0.387,-0.014],[0.532,-0.005],[0.747,0],[0.56,0.005],[0.415,0.014],[0.294,0.019],[0,0],[-0.205,0.019],[-0.271,0.019],[-0.373,0.009],[-0.49,0.009],[-0.103,-0.28]],"v":[[-20.237,-9.369],[-20.482,-10.013],[-20.755,-10.664],[-21.098,-11.448],[-21.938,-10.986],[-21.266,-9.768],[-20.79,-8.62],[-22.596,-8.627],[-23.905,-8.655],[-24.85,-8.704],[-25.564,-8.76],[-25.564,-7.766],[-24.829,-7.836],[-23.849,-7.885],[-22.47,-7.913],[-20.552,-7.92],[-18.592,-7.913],[-17.129,-7.885],[-16.065,-7.836],[-15.288,-7.766],[-15.288,-8.76],[-16.002,-8.704],[-16.968,-8.662],[-18.263,-8.634],[-19.964,-8.62]],"c":true},"ix":2},"nm":"\u7acb","mn":"ADBE Vector Shape - Group","hd":false},{"ind":2,"ty":"sh","ix":3,"ks":{"a":0,"k":{"i":[[0,0],[0.387,0.84],[0.42,0.84],[0,0],[-0.21,-0.429],[-0.163,-0.387],[-0.135,-0.369],[-0.131,-0.392]],"o":[[-0.327,-0.793],[-0.387,-0.84],[0,0],[0.261,0.513],[0.21,0.429],[0.163,0.387],[0.135,0.369],[0,0]],"v":[[-21.238,-1.522],[-22.309,-3.972],[-23.52,-6.492],[-24.22,-6.086],[-23.513,-4.672],[-22.953,-3.447],[-22.505,-2.313],[-22.106,-1.172]],"c":true},"ix":2},"nm":"\u7acb","mn":"ADBE Vector Shape - Group","hd":false},{"ty":"mm","mm":1,"nm":"\u5408\u5e76\u8def\u5f84 1","mn":"ADBE Vector Filter - Merge","hd":false},{"ty":"fl","c":{"a":0,"k":[1,1,1,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[100,100],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u7acb","np":6,"cix":2,"bm":0,"ix":1,"mn":"ADBE Vector Group","hd":false},{"ty":"gr","it":[{"ind":0,"ty":"sh","ix":1,"ks":{"a":0,"k":{"i":[[0,0],[0,0],[0,0],[0,0]],"o":[[0,0],[0,0],[0,0],[0,0]],"v":[[-7.168,-5.288],[-10.794,-5.288],[-10.794,-7.178],[-7.168,-7.178]],"c":true},"ix":2},"nm":"\u5373","mn":"ADBE Vector Shape - Group","hd":false},{"ind":1,"ty":"sh","ix":2,"ks":{"a":0,"k":{"i":[[0,0],[0,0],[0,0],[0,0]],"o":[[0,0],[0,0],[0,0],[0,0]],"v":[[-7.168,-7.878],[-10.794,-7.878],[-10.794,-9.796],[-7.168,-9.796]],"c":true},"ix":2},"nm":"\u5373","mn":"ADBE Vector Shape - Group","hd":false},{"ind":2,"ty":"sh","ix":3,"ks":{"a":0,"k":{"i":[[0.471,-0.196],[0.728,-0.243],[0,0],[0,0],[-0.397,-0.014],[-0.243,-0.028],[0,0.709],[0,0],[-0.005,0.154],[-0.005,0.154],[-0.009,0.145],[-0.009,0.112],[0.513,-0.033],[0.644,0],[0.425,0.033],[0.243,0.047],[-0.009,-0.145],[-0.009,-0.154],[-0.005,-0.159],[0,-0.121],[0,0],[0.023,-0.177],[0.051,-0.135],[0.079,-0.107],[0.103,-0.103],[-0.098,-0.145],[-0.065,-0.159],[-0.266,0.135],[-0.373,0.159],[0,0],[-0.149,-0.233],[-0.131,-0.243],[0,0],[0.397,0.495],[0.429,0.457],[0,0],[-0.355,-0.457]],"o":[[-0.471,0.196],[0,0],[0,0],[0.42,0],[0.397,0.014],[-0.056,-0.504],[0,0],[0,-0.121],[0.005,-0.154],[0.005,-0.154],[0.009,-0.145],[-0.252,0.047],[-0.513,0.033],[-0.644,0],[-0.425,-0.033],[0.009,0.103],[0.009,0.145],[0.009,0.154],[0.005,0.159],[0,0],[0,0.243],[-0.023,0.177],[-0.051,0.135],[-0.079,0.107],[0.112,0.131],[0.098,0.145],[0.243,-0.159],[0.266,-0.135],[0,0],[0.159,0.215],[0.149,0.233],[0,0],[-0.429,-0.635],[-0.397,-0.495],[0,0],[0.28,0.233],[-0.327,0.168]],"v":[[-8.995,-1.396],[-10.794,-0.738],[-10.794,-4.574],[-8.428,-4.574],[-7.203,-4.553],[-6.244,-4.49],[-6.328,-6.31],[-6.328,-8.97],[-6.321,-9.383],[-6.307,-9.845],[-6.286,-10.293],[-6.258,-10.678],[-7.406,-10.559],[-9.142,-10.51],[-10.745,-10.559],[-11.746,-10.678],[-11.718,-10.307],[-11.69,-9.859],[-11.669,-9.39],[-11.662,-8.97],[-11.662,-1.928],[-11.697,-1.298],[-11.809,-0.829],[-12.005,-0.465],[-12.278,-0.15],[-11.963,0.263],[-11.718,0.718],[-10.955,0.277],[-9.996,-0.164],[-7.308,-1.298],[-6.846,-0.626],[-6.426,0.088],[-5.628,-0.444],[-6.867,-2.138],[-8.106,-3.566],[-8.75,-2.978],[-7.798,-1.942]],"c":true},"ix":2},"nm":"\u5373","mn":"ADBE Vector Shape - Group","hd":false},{"ind":3,"ty":"sh","ix":4,"ks":{"a":0,"k":{"i":[[0.401,-0.019],[0.467,0],[0.378,0.019],[0.271,0.037],[-0.019,-0.364],[0,-0.327],[0,0],[0.019,-0.49],[0.037,-0.551],[0,0],[0,0],[0,0],[0,0],[0.033,-0.117],[0.126,-0.07],[0.252,-0.023],[0.448,0.028],[-0.07,-0.168],[0.019,-0.215],[-0.299,0.084],[-0.168,0.14],[-0.061,0.201],[0,0.299],[0,0],[-0.023,0.28],[-0.047,0.224]],"o":[[-0.401,0.019],[-0.495,0],[-0.378,-0.019],[0.019,0.224],[0.019,0.364],[0,0],[0,0.588],[-0.019,0.49],[0,0],[0,0],[0,0],[0,0],[0,0.159],[-0.033,0.117],[-0.126,0.07],[-0.252,0.023],[0.168,0.177],[0.07,0.168],[0.485,-0.056],[0.299,-0.084],[0.168,-0.14],[0.061,-0.201],[0,0],[0,-0.495],[0.023,-0.28],[-0.271,0.037]],"v":[[-1.624,-10.314],[-2.926,-10.286],[-4.235,-10.314],[-5.208,-10.398],[-5.152,-9.516],[-5.124,-8.48],[-5.124,-1.634],[-5.152,-0.017],[-5.236,1.544],[-4.312,1.544],[-4.312,-9.572],[-1.596,-9.572],[-1.596,-2.334],[-1.645,-1.921],[-1.883,-1.641],[-2.45,-1.501],[-3.5,-1.508],[-3.143,-0.99],[-3.066,-0.416],[-1.89,-0.626],[-1.19,-0.962],[-0.847,-1.473],[-0.756,-2.222],[-0.756,-8.48],[-0.721,-9.642],[-0.616,-10.398]],"c":true},"ix":2},"nm":"\u5373","mn":"ADBE Vector Shape - Group","hd":false},{"ty":"mm","mm":1,"nm":"\u5408\u5e76\u8def\u5f84 1","mn":"ADBE Vector Filter - Merge","hd":false},{"ty":"fl","c":{"a":0,"k":[1,1,1,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[100,100],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u5373","np":7,"cix":2,"bm":0,"ix":2,"mn":"ADBE Vector Group","hd":false},{"ty":"gr","it":[{"ind":0,"ty":"sh","ix":1,"ks":{"a":0,"k":{"i":[[0,0],[0,0],[0,0],[0,0]],"o":[[0,0],[0,0],[0,0],[0,0]],"v":[[10.584,-2.6],[4.536,-2.6],[4.536,-4.168],[10.584,-4.168]],"c":true},"ix":2},"nm":"\u767b","mn":"ADBE Vector Shape - Group","hd":false},{"ind":1,"ty":"sh","ix":2,"ks":{"a":0,"k":{"i":[[0.005,0.215],[0,0.308],[0,0.121],[-0.005,0.117],[-0.005,0.131],[-0.009,0.168],[0.266,-0.009],[0.313,-0.005],[0.373,-0.005],[0.476,0],[0.378,0.005],[0.308,0.005],[0.266,0.009],[0.252,0.019],[0,-0.616],[0.014,-0.215],[0.028,-0.224],[-0.261,0.009],[-0.313,0.009],[-0.373,0],[-0.476,0],[-0.378,-0.005],[-0.317,-0.005],[-0.261,-0.005],[-0.252,-0.009]],"o":[[-0.005,-0.215],[0,-0.159],[0,-0.121],[0.005,-0.117],[0.005,-0.131],[-0.252,0.019],[-0.266,0.009],[-0.313,0.005],[-0.373,0.005],[-0.476,0],[-0.378,-0.005],[-0.308,-0.005],[-0.266,-0.009],[0.056,0.448],[0,0.308],[-0.014,0.215],[0.252,-0.009],[0.261,-0.009],[0.313,-0.009],[0.373,0],[0.476,0],[0.378,0.005],[0.317,0.005],[0.261,0.005],[-0.019,-0.215]],"v":[[11.473,-2.53],[11.466,-3.314],[11.466,-3.734],[11.473,-4.091],[11.487,-4.462],[11.508,-4.91],[10.731,-4.868],[9.863,-4.847],[8.834,-4.833],[7.56,-4.826],[6.279,-4.833],[5.25,-4.847],[4.389,-4.868],[3.612,-4.91],[3.696,-3.314],[3.675,-2.53],[3.612,-1.872],[4.382,-1.9],[5.243,-1.928],[6.272,-1.942],[7.546,-1.942],[8.827,-1.935],[9.87,-1.921],[10.738,-1.907],[11.508,-1.886]],"c":true},"ix":2},"nm":"\u767b","mn":"ADBE Vector Shape - Group","hd":false},{"ind":2,"ty":"sh","ix":3,"ks":{"a":0,"k":{"i":[[0.723,0.019],[0.485,0.047],[0,0],[-0.733,0.019],[-0.849,0],[0,0],[-0.723,-0.019],[-0.513,-0.047],[0,0],[0.313,-0.014],[0.369,-0.014],[0.397,-0.005],[0.383,0],[-0.14,0.154],[-0.098,0.093],[-0.07,0.042],[-0.047,0.019],[0.009,0.075],[0.131,0.028],[0.159,0.061],[0.131,0.093],[0.187,-0.303],[0.252,-0.299],[0,0],[0.191,0.317],[0.215,0.271],[0,0],[-0.177,-0.229],[-0.149,-0.271]],"o":[[-0.723,-0.019],[0,0],[0.504,-0.047],[0.733,-0.019],[0,0],[0.859,0],[0.723,0.019],[0,0],[-0.215,0.019],[-0.313,0.014],[-0.369,0.014],[-0.397,0.005],[0.177,-0.233],[0.14,-0.154],[0.098,-0.093],[0.07,-0.042],[0.121,-0.037],[-0.009,-0.075],[-0.131,-0.028],[-0.159,-0.061],[-0.177,0.383],[-0.187,0.303],[0,0],[-0.196,-0.364],[-0.191,-0.317],[0,0],[0.233,0.233],[0.177,0.229],[-0.784,0]],"v":[[3.437,0.2],[1.624,0.102],[1.624,1.04],[3.479,0.942],[5.852,0.914],[9.24,0.914],[11.613,0.942],[13.468,1.04],[13.468,0.102],[12.677,0.151],[11.655,0.193],[10.507,0.221],[9.338,0.228],[9.814,-0.353],[10.171,-0.724],[10.423,-0.927],[10.598,-1.018],[10.766,-1.186],[10.556,-1.34],[10.122,-1.473],[9.688,-1.704],[9.142,-0.675],[8.484,0.228],[6.566,0.228],[5.985,-0.794],[5.376,-1.676],[4.592,-1.214],[5.208,-0.521],[5.698,0.228]],"c":true},"ix":2},"nm":"\u767b","mn":"ADBE Vector Shape - Group","hd":false},{"ind":3,"ty":"sh","ix":4,"ks":{"a":0,"k":{"i":[[0,0],[-0.201,0.014],[-0.266,0.009],[-0.35,0.005],[-0.457,0],[-0.322,-0.005],[-0.247,-0.009],[-0.196,-0.014],[-0.196,-0.019],[0,0],[-0.467,-0.224],[-0.551,-0.187],[-0.075,0.154],[-0.131,0.159],[0.859,0.635],[-0.28,0.154],[-0.182,0.089],[-0.107,0.033],[-0.075,0],[-0.009,0.056],[0.112,0.056],[0.126,0.103],[0.112,0.131],[0.149,-0.131],[0.173,-0.126],[0.21,-0.135],[0.271,-0.149],[0.271,0.429],[-0.257,0.149],[-0.168,0.084],[-0.098,0.023],[-0.056,0],[-0.019,0.051],[0.112,0.065],[0.126,0.121],[0.093,0.14],[0.294,-0.243],[0.504,-0.327],[0.075,0.21],[0.075,0.224],[0,0],[-0.392,-0.597],[-0.56,-0.467],[0.168,-0.009],[0.219,-0.005],[0.271,0],[0.364,0],[0.443,0.009],[0.327,0.019],[-0.42,0.583],[-0.364,0.728],[0.149,-0.019],[0.196,-0.009],[0.266,-0.005],[0.364,0],[0.56,0.084],[0,0],[-0.327,0.028],[-0.485,0],[0,0],[0.579,-0.551],[0.275,0.219],[0.308,0.187],[0,0],[-0.28,-0.196],[-0.215,-0.215],[0.504,-0.271],[0.579,-0.215],[-0.149,-0.308],[-0.425,0.266],[-0.355,0.271]],"o":[[0.168,-0.019],[0.201,-0.014],[0.266,-0.009],[0.35,-0.005],[0.448,0],[0.322,0.005],[0.247,0.009],[0.196,0.014],[0,0],[0.392,0.28],[0.467,0.224],[0.047,-0.187],[0.075,-0.154],[-1.307,-0.261],[0.411,-0.252],[0.28,-0.154],[0.182,-0.089],[0.107,-0.033],[0.103,-0.009],[0.009,-0.056],[-0.112,-0.056],[-0.126,-0.103],[-0.149,0.159],[-0.149,0.131],[-0.173,0.126],[-0.21,0.135],[-0.355,-0.327],[0.392,-0.252],[0.257,-0.149],[0.168,-0.084],[0.098,-0.023],[0.103,0.009],[0.019,-0.051],[-0.131,-0.075],[-0.126,-0.121],[-0.159,0.196],[-0.294,0.243],[-0.103,-0.196],[-0.075,-0.21],[0,0],[0.271,0.765],[0.392,0.597],[-0.159,0.009],[-0.168,0.009],[-0.219,0.005],[-0.271,0],[-0.7,0],[-0.443,-0.009],[0.588,-0.513],[0.42,-0.583],[-0.14,0.019],[-0.149,0.019],[-0.196,0.009],[-0.266,0.005],[-1.353,0],[0,0],[0.187,-0.037],[0.327,-0.028],[0,0],[-0.429,0.756],[-0.261,-0.252],[-0.275,-0.219],[0,0],[0.317,0.177],[0.28,0.196],[-0.439,0.345],[-0.504,0.271],[0.308,0.215],[0.504,-0.271],[0.425,-0.266],[0,0]],"v":[[4.2,-6.002],[4.753,-6.051],[5.453,-6.086],[6.377,-6.107],[7.588,-6.114],[8.743,-6.107],[9.597,-6.086],[10.262,-6.051],[10.85,-6.002],[10.85,-6.45],[12.138,-5.694],[13.664,-5.078],[13.846,-5.589],[14.154,-6.058],[10.906,-7.402],[11.942,-8.011],[12.635,-8.375],[13.069,-8.557],[13.342,-8.606],[13.51,-8.704],[13.356,-8.872],[12.999,-9.11],[12.642,-9.46],[12.194,-9.026],[11.711,-8.641],[11.137,-8.249],[10.416,-7.822],[9.478,-8.956],[10.451,-9.558],[11.088,-9.908],[11.487,-10.069],[11.718,-10.104],[11.9,-10.167],[11.76,-10.342],[11.375,-10.636],[11.046,-11.028],[10.367,-10.37],[9.17,-9.516],[8.904,-10.125],[8.68,-10.776],[7.924,-10.468],[8.918,-8.424],[10.346,-6.828],[9.856,-6.8],[9.275,-6.779],[8.54,-6.772],[7.588,-6.772],[5.873,-6.786],[4.718,-6.828],[6.23,-8.473],[7.406,-10.44],[6.972,-10.384],[6.454,-10.342],[5.761,-10.321],[4.816,-10.314],[1.946,-10.44],[1.946,-9.53],[2.716,-9.628],[3.934,-9.67],[6.062,-9.67],[4.55,-7.71],[3.745,-8.417],[2.87,-9.026],[2.352,-8.396],[3.248,-7.836],[3.99,-7.22],[2.576,-6.296],[0.952,-5.568],[1.638,-4.784],[3.031,-5.589],[4.2,-6.394]],"c":true},"ix":2},"nm":"\u767b","mn":"ADBE Vector Shape - Group","hd":false},{"ty":"mm","mm":1,"nm":"\u5408\u5e76\u8def\u5f84 1","mn":"ADBE Vector Filter - Merge","hd":false},{"ty":"fl","c":{"a":0,"k":[1,1,1,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[100,100],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u767b","np":7,"cix":2,"bm":0,"ix":3,"mn":"ADBE Vector Group","hd":false},{"ty":"gr","it":[{"ind":0,"ty":"sh","ix":1,"ks":{"a":0,"k":{"i":[[0,0],[-0.756,-0.616],[0,0],[0.219,0.14],[0.21,0.121],[0.215,0.107],[0.233,0.112]],"o":[[0.896,0.429],[0,0],[-0.252,-0.168],[-0.219,-0.14],[-0.21,-0.121],[-0.215,-0.107],[0,0]],"v":[[16.268,-4.322],[18.746,-2.754],[19.278,-3.454],[18.571,-3.916],[17.927,-4.308],[17.29,-4.651],[16.618,-4.98]],"c":true},"ix":2},"nm":"\u5f55","mn":"ADBE Vector Shape - Group","hd":false},{"ind":1,"ty":"sh","ix":2,"ks":{"a":0,"k":{"i":[[0.831,-0.462],[0.849,-0.289],[-0.079,-0.126],[-0.103,-0.215],[-0.481,0.308],[-0.49,0.308],[-0.406,0.252],[-0.168,0.093],[0.042,0.107],[0.047,0.177]],"o":[[-0.831,0.462],[0.149,0.159],[0.079,0.126],[0.317,-0.205],[0.481,-0.308],[0.49,-0.308],[0.406,-0.252],[-0.093,-0.131],[-0.042,-0.107],[-0.915,0.719]],"v":[[17.598,-1.557],[15.078,-0.43],[15.421,-0.003],[15.694,0.508],[16.891,-0.262],[18.347,-1.186],[19.691,-2.026],[20.552,-2.544],[20.349,-2.901],[20.216,-3.328]],"c":true},"ix":2},"nm":"\u5f55","mn":"ADBE Vector Shape - Group","hd":false},{"ind":2,"ty":"sh","ix":3,"ks":{"a":0,"k":{"i":[[0,0],[0.803,0.005],[0.56,0.009],[0.364,0.014],[0.252,0.019],[0,0],[-0.364,0.014],[-0.565,0.009],[-0.803,0.005],[-1.12,0],[0,0],[0,0],[0.336,0.009],[0.331,0.009],[0.294,0.014],[0.187,0.019],[0,0],[-0.299,0.019],[-0.457,0.009],[-0.639,0.005],[-0.868,0],[0,0],[0.042,-0.173],[0.14,-0.089],[0.275,-0.019],[0.476,0.037],[-0.07,-0.168],[-0.028,-0.187],[-0.331,0.07],[-0.163,0.135],[-0.042,0.219],[0,0.345],[0,0],[-0.355,-0.317],[-0.425,-0.299],[-0.527,-0.299],[-0.672,-0.336],[-0.103,0.14],[-0.159,0.149],[0.798,0.411],[0.709,0.569],[-0.159,0.098],[-0.135,0.089],[-0.131,0.084],[-0.159,0.112],[-0.117,0.056],[-0.103,-0.019],[-0.028,0.084],[0.121,0.075],[0.103,0.112],[0.14,0.205],[0.42,-0.355],[0.784,-0.513],[0.28,0.327],[0,0],[-0.653,-0.005],[-0.448,-0.009],[-0.266,-0.019],[-0.149,-0.019],[0,0],[0.373,-0.019],[0.467,0],[0,0],[-0.019,0.247],[-0.047,0.28],[0.714,-0.023],[1.017,0],[0.714,0.019],[0.42,0.047],[0,0],[-0.35,0.014],[-0.593,0.014],[-0.887,0.009],[-1.288,0]],"o":[[-1.12,0],[-0.803,-0.005],[-0.56,-0.009],[-0.364,-0.014],[0,0],[0.243,-0.019],[0.364,-0.014],[0.565,-0.009],[0.803,-0.005],[0,0],[0,0],[-0.271,0],[-0.336,-0.009],[-0.331,-0.009],[-0.294,-0.014],[0,0],[0.196,-0.019],[0.299,-0.019],[0.457,-0.009],[0.639,-0.005],[0,0],[0,0.28],[-0.042,0.173],[-0.14,0.089],[-0.275,0.019],[0.159,0.168],[0.07,0.168],[0.569,-0.056],[0.331,-0.07],[0.163,-0.135],[0.042,-0.219],[0,0],[0.317,0.373],[0.355,0.317],[0.425,0.299],[0.527,0.299],[0.103,-0.196],[0.103,-0.14],[-0.812,-0.243],[-0.798,-0.411],[0.215,-0.14],[0.159,-0.098],[0.135,-0.089],[0.131,-0.084],[0.243,-0.168],[0.117,-0.056],[0.187,0.019],[0.028,-0.084],[-0.112,-0.075],[-0.103,-0.112],[-0.187,0.271],[-0.42,0.355],[-0.327,-0.28],[0,0],[0.924,0],[0.653,0.005],[0.448,0.009],[0.266,0.019],[0,0],[-0.233,0.037],[-0.373,0.019],[0,0],[0,-0.327],[0.019,-0.247],[-0.401,0.037],[-0.714,0.023],[-1.12,0],[-0.714,-0.019],[0,0],[0.205,-0.019],[0.35,-0.014],[0.593,-0.014],[0.887,-0.009],[0,0]],"v":[[24.598,-8.298],[21.714,-8.305],[19.67,-8.326],[18.284,-8.361],[17.36,-8.41],[17.36,-7.514],[18.27,-7.563],[19.663,-7.598],[21.714,-7.619],[24.598,-7.626],[24.598,-6.254],[18.844,-6.254],[17.934,-6.268],[16.933,-6.296],[15.995,-6.331],[15.274,-6.38],[15.274,-5.47],[16.016,-5.526],[17.15,-5.568],[18.795,-5.589],[21.056,-5.596],[21.056,-0.64],[20.993,0.039],[20.72,0.431],[20.097,0.592],[18.97,0.564],[19.313,1.068],[19.46,1.6],[20.811,1.411],[21.553,1.103],[21.861,0.571],[21.924,-0.276],[21.924,-2.992],[22.932,-1.956],[24.101,-1.032],[25.529,-0.136],[27.328,0.816],[27.636,0.312],[28.028,-0.122],[25.613,-1.102],[23.352,-2.572],[23.912,-2.929],[24.353,-3.209],[24.752,-3.468],[25.186,-3.762],[25.725,-4.098],[26.054,-4.154],[26.376,-4.252],[26.236,-4.49],[25.914,-4.77],[25.55,-5.246],[24.64,-4.308],[22.834,-3.006],[21.924,-3.916],[21.924,-5.596],[24.29,-5.589],[25.942,-5.568],[27.013,-5.526],[27.636,-5.47],[27.636,-6.38],[26.726,-6.296],[25.466,-6.268],[25.466,-8.802],[25.494,-9.663],[25.592,-10.454],[23.919,-10.363],[21.322,-10.328],[18.571,-10.356],[16.87,-10.454],[16.87,-9.544],[17.703,-9.593],[19.117,-9.635],[21.336,-9.67],[24.598,-9.684]],"c":true},"ix":2},"nm":"\u5f55","mn":"ADBE Vector Shape - Group","hd":false},{"ty":"mm","mm":1,"nm":"\u5408\u5e76\u8def\u5f84 1","mn":"ADBE Vector Filter - Merge","hd":false},{"ty":"fl","c":{"a":0,"k":[1,1,1,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[100,100],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u5f55","np":6,"cix":2,"bm":0,"ix":4,"mn":"ADBE Vector Group","hd":false}],"ip":0,"op":300,"st":0,"bm":0},{"ddd":0,"ind":2,"ty":4,"nm":"text","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[108,33,0],"ix":2},"a":{"a":0,"k":[0,0,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"shapes":[{"ty":"gr","it":[{"ty":"rc","d":1,"s":{"a":0,"k":[72,22],"ix":2},"p":{"a":0,"k":[0,0],"ix":3},"r":{"a":0,"k":0,"ix":4},"nm":"\u77e9\u5f62\u8def\u5f84 1","mn":"ADBE Vector Shape - Rect","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[300,300],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"text","np":1,"cix":2,"bm":0,"ix":1,"mn":"ADBE Vector Group","hd":false}],"ip":0,"op":300,"st":0,"bm":0}]}],"layers":[{"ddd":0,"ind":1,"ty":0,"nm":"text","refId":"comp_0","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[270,65,0],"ix":2},"a":{"a":0,"k":[108,33,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"w":216,"h":66,"ip":0,"op":300,"st":0,"bm":0},{"ddd":0,"ind":2,"ty":4,"nm":"dl","td":1,"sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[270,57,0],"ix":2},"a":{"a":0,"k":[0,0,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"shapes":[{"ty":"gr","it":[{"ty":"rc","d":1,"s":{"a":0,"k":[180,38],"ix":2},"p":{"a":0,"k":[0,0],"ix":3},"r":{"a":0,"k":4,"ix":4},"nm":"\u77e9\u5f62\u8def\u5f84 1","mn":"ADBE Vector Shape - Rect","hd":false},{"ty":"fl","c":{"a":0,"k":[0.996078431606,0.172549024224,0.333333343267,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[300,300],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u767b\u5f55","np":2,"cix":2,"bm":0,"ix":1,"mn":"ADBE Vector Group","hd":false}],"ip":0,"op":300,"st":0,"bm":0},{"ddd":0,"ind":3,"ty":4,"nm":"white glow","tt":1,"sr":1,"ks":{"o":{"a":1,"k":[{"i":{"x":[0.568],"y":[0.928]},"o":{"x":[0.215],"y":[0]},"t":0,"s":[0]},{"i":{"x":[0.843],"y":[1]},"o":{"x":[0.316],"y":[15.891]},"t":12.578,"s":[60]},{"i":{"x":[0.2],"y":[1]},"o":{"x":[0.001],"y":[0]},"t":75.473,"s":[60]},{"t":188.6796875,"s":[0]}],"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.2,"y":1},"o":{"x":0.003,"y":0},"t":0,"s":[-73,-9,0],"to":[-7.414,5.349,0],"ti":[-51.44,-43.573,0]},{"i":{"x":0.44,"y":0.469},"o":{"x":0.001,"y":0},"t":7.24,"s":[-36,144,0],"to":[79.725,67.532,0],"ti":[-77.47,8.761,0]},{"i":{"x":0.2,"y":1},"o":{"x":0.313,"y":0.322},"t":21,"s":[240.708,208.447,0],"to":[21.772,-2.462,0],"ti":[-96.884,20.58,0]},{"i":{"x":0.666,"y":0.717},"o":{"x":0.001,"y":0},"t":33.393,"s":[482,191,0],"to":[96.174,-20.429,0],"ti":[-80.544,28.727,0]},{"i":{"x":0.715,"y":0.862},"o":{"x":0.366,"y":0.376},"t":43,"s":[631.804,145.95,0],"to":[106.937,-38.141,0],"ti":[30.43,41.241,0]},{"i":{"x":0.2,"y":1},"o":{"x":0.224,"y":0.215},"t":59.748,"s":[632.556,-39.368,0],"to":[-31.044,-42.073,0],"ti":[52.587,1.14,0]},{"i":{"x":0.546,"y":1},"o":{"x":0.001,"y":0},"t":117.334,"s":[247,-75,0],"to":[-83.825,-1.817,0],"ti":[31.679,-4.216,0]},{"i":{"x":0.2,"y":1},"o":{"x":0.167,"y":0},"t":188.68,"s":[46,-80,0],"to":[-60.847,8.097,0],"ti":[-0.167,-0.167,0]},{"t":250,"s":[-74,-8,0]}],"ix":2},"a":{"a":0,"k":[-107,-39,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ef":[{"ty":29,"nm":"\u9ad8\u65af\u6a21\u7cca","np":5,"mn":"ADBE Gaussian Blur 2","ix":1,"en":1,"ef":[{"ty":0,"nm":"\u6a21\u7cca\u5ea6","mn":"ADBE Gaussian Blur 2-0001","ix":1,"v":{"a":0,"k":150,"ix":1}},{"ty":7,"nm":"\u6a21\u7cca\u65b9\u5411","mn":"ADBE Gaussian Blur 2-0002","ix":2,"v":{"a":0,"k":1,"ix":2}},{"ty":7,"nm":"\u91cd\u590d\u8fb9\u7f18\u50cf\u7d20","mn":"ADBE Gaussian Blur 2-0003","ix":3,"v":{"a":0,"k":0,"ix":3}}]},{"ty":5,"nm":"\u6e4d\u6d41\u7f6e\u6362","np":16,"mn":"ADBE Turbulent Displace","ix":2,"en":1,"ef":[{"ty":7,"nm":"\u7f6e\u6362","mn":"ADBE Turbulent Displace-0001","ix":1,"v":{"a":0,"k":1,"ix":1}},{"ty":0,"nm":"\u6570\u91cf","mn":"ADBE Turbulent Displace-0002","ix":2,"v":{"a":0,"k":50,"ix":2}},{"ty":0,"nm":"\u5927\u5c0f","mn":"ADBE Turbulent Displace-0003","ix":3,"v":{"a":0,"k":50,"ix":3}},{"ty":3,"nm":"\u504f\u79fb\uff08\u6e4d\u6d41\uff09","mn":"ADBE Turbulent Displace-0004","ix":4,"v":{"a":0,"k":[270,57],"ix":4}},{"ty":0,"nm":"\u590d\u6742\u5ea6","mn":"ADBE Turbulent Displace-0005","ix":5,"v":{"a":0,"k":1,"ix":5}},{"ty":0,"nm":"\u6f14\u5316","mn":"ADBE Turbulent Displace-0006","ix":6,"v":{"a":0,"k":0,"ix":6,"x":"var $bm_rt;\\n$bm_rt = $bm_mul(time, 100);"}},{"ty":6,"nm":"\u6f14\u5316\u9009\u9879","mn":"ADBE Turbulent Displace-0007","ix":7,"v":0},{"ty":7,"nm":"\u5faa\u73af\u6f14\u5316","mn":"ADBE Turbulent Displace-0008","ix":8,"v":{"a":0,"k":0,"ix":8}},{"ty":0,"nm":"\u5faa\u73af\uff08\u65cb\u8f6c\u6b21\u6570\uff09","mn":"ADBE Turbulent Displace-0009","ix":9,"v":{"a":0,"k":1,"ix":9}},{"ty":0,"nm":"\u968f\u673a\u690d\u5165","mn":"ADBE Turbulent Displace-0010","ix":10,"v":{"a":0,"k":0,"ix":10}},{"ty":6,"nm":"\u968f\u673a\u690d\u5165","mn":"ADBE Turbulent Displace-0011","ix":11,"v":0},{"ty":7,"nm":"\u56fa\u5b9a","mn":"ADBE Turbulent Displace-0012","ix":12,"v":{"a":0,"k":3,"ix":12}},{"ty":7,"nm":"\u8c03\u6574\u56fe\u5c42\u5927\u5c0f","mn":"ADBE Turbulent Displace-0013","ix":13,"v":{"a":0,"k":0,"ix":13}},{"ty":7,"nm":"\u6d88\u9664\u952f\u9f7f\uff08\u6700\u4f73\u54c1\u8d28\uff09","mn":"ADBE Turbulent Displace-0014","ix":14,"v":{"a":0,"k":1,"ix":14}}]}],"shapes":[{"ty":"gr","it":[{"d":1,"ty":"el","s":{"a":0,"k":[300,200],"ix":2},"p":{"a":0,"k":[0,0],"ix":3},"nm":"Ellipse Path 1","mn":"ADBE Vector Shape - Ellipse","hd":false},{"ty":"fl","c":{"a":0,"k":[1,1,1,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"Fill 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[-109.427,-39.759],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[100,100],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"Ellipse 1","np":3,"cix":2,"bm":0,"ix":1,"mn":"ADBE Vector Group","hd":false}],"ip":0,"op":602.4,"st":0,"bm":0},{"ddd":0,"ind":4,"ty":4,"nm":"dl","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[270,57,0],"ix":2},"a":{"a":0,"k":[0,0,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"shapes":[{"ty":"gr","it":[{"ty":"rc","d":1,"s":{"a":0,"k":[180,38],"ix":2},"p":{"a":0,"k":[0,0],"ix":3},"r":{"a":0,"k":4,"ix":4},"nm":"\u77e9\u5f62\u8def\u5f84 1","mn":"ADBE Vector Shape - Rect","hd":false},{"ty":"fl","c":{"a":0,"k":[0.996078431606,0.172549024224,0.333333343267,1],"ix":4},"o":{"a":0,"k":100,"ix":5},"r":1,"bm":0,"nm":"\u586b\u5145 1","mn":"ADBE Vector Graphic - Fill","hd":false},{"ty":"tr","p":{"a":0,"k":[0,0],"ix":2},"a":{"a":0,"k":[0,0],"ix":1},"s":{"a":0,"k":[300,300],"ix":3},"r":{"a":0,"k":0,"ix":6},"o":{"a":0,"k":100,"ix":7},"sk":{"a":0,"k":0,"ix":4},"sa":{"a":0,"k":0,"ix":5},"nm":"\u53d8\u6362"}],"nm":"\u767b\u5f55","np":2,"cix":2,"bm":0,"ix":1,"mn":"ADBE Vector Group","hd":false}],"ip":0,"op":300,"st":0,"bm":0}],"markers":[]}');
    const O = function(e) {
      var t = e.config
        , o = e.destroy
        , i = e.isVideoGuide
        , a = e.isShowAvatarGuide
        , s = e.isNewBtn
        , c = void 0 !== s && s
        , u = (0,
        p.useRef)(null)
        , d = (0,
        p.useRef)(null)
        , m = (0,
        p.useState)(!1)
        , v = (0,
        r.Z)(m, 2)
        , f = (v[0],
        v[1],
        function() {
          var e = (0,
            l.Z)(h().mark((function e() {
              return h().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        return e.next = 2,
                          o();
                      case 2:
                        (0,
                          B.default)({
                          headerText: a ? "\u767b\u5f55\u540e\u83b7\u5f97\u4e13\u5c5e\u5934\u50cf\u6302\u4ef6" : "",
                          success: function() {
                            window.location.reload()
                          },
                          enterMethod: "cold_start",
                          isActive: "0",
                          next: (0,
                            A.pL)(),
                          teaEvtParams: {
                            is_video_guide: i || "0"
                          }
                        });
                      case 3:
                      case "end":
                        return e.stop()
                    }
                }
              ), e)
            }
          )));
          return function() {
            return e.apply(this, arguments)
          }
        }())
        , g = p.useCallback(function() {
        var e = (0,
          l.Z)(h().mark((function e(n) {
            var r, i;
            return h().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      if (n) {
                        e.next = 2;
                        break
                      }
                      return e.abrupt("return");
                    case 2:
                      return e.next = 4,
                        (0,
                          A.j1)();
                    case 4:
                      if (r = e.sent,
                        !B.loginPanelInfo.isShowingAccount) {
                        e.next = 9;
                        break
                      }
                      return e.next = 8,
                        o();
                    case 8:
                      return e.abrupt("return");
                    case 9:
                      i = new r((0,
                        N.Z)((0,
                        N.Z)({}, t), {}, {
                        success: function(e) {
                          null != e && e.redirect_url ? I().get(null == e ? void 0 : e.redirect_url).then((function() {
                              (0,
                                L.tokenBeatInit)(),
                                window.location.reload()
                            }
                          )).catch((function() {
                              o()
                            }
                          )) : o()
                        }
                      })),
                        u.current = i.init(n),
                        i.setTeaConfig({
                          ug_source: D.Rs("ug_source"),
                          sem_keyword: D.Rs("sem_keyword"),
                          browser_is_360: M.a2() ? "1" : "0"
                        });
                    case 12:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), []);
      return (0,
        p.useEffect)((function() {
          return function() {
            var e;
            null == u || null === (e = u.current) || void 0 === e || e.call(u)
          }
        }
      ), []),
        (0,
          p.useEffect)((function() {
            d && n.e(1115).then(n.t.bind(n, 81115, 23)).then((function(e) {
                null == e || e.loadAnimation({
                  container: d.current,
                  renderer: "svg",
                  loop: !0,
                  animationData: P
                })
              }
            ))
          }
        )),
        p.createElement("div", {
          id: "login-guide",
          className: Z()("login-guide", {
            guideAvatar: a
          }, {
            oldBtn: !c
          }),
          onClick: o
        }, p.createElement("i", {
          className: "login-guide__close"
        }), p.createElement("div", {
          ref: g,
          onClick: function(e) {
            e.stopPropagation()
          }
        }), c ? p.createElement("div", {
          className: "login-guide__btn",
          onClick: f
        }, p.createElement("div", {
          className: "login-guide__btn__animation"
        }, p.createElement("div", {
          className: "login-guide__btn__animation__target"
        }), p.createElement("div", {
          className: "login-guide__btn__animation__cursor"
        })), "\u7acb\u5373\u767b\u5f55") : p.createElement("div", {
          className: "login-guide-btn-el",
          ref: d,
          onClick: f
        }))
    };
    const V = new (n(37485).hD)({
      loginScanQrcodeStay: {
        eventName: "login_scan_qrcode_stay",
        params: {
          duration: 0,
          enter_from: "",
          enter_method: "cold_start",
          isActive: ""
        }
      }
    });
    var W = "0"
      , R = !1
      , F = function() {
      var e = (0,
        l.Z)(h().mark((function e() {
          var t;
          return h().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      n.e(4711).then(n.bind(n, 54711)).then((function(e) {
                          return e.default
                        }
                      ));
                  case 2:
                    if (t = e.sent,
                      !R) {
                      e.next = 5;
                      break
                    }
                    return e.abrupt("return");
                  case 5:
                    t.use(),
                      R = !0;
                  case 7:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , U = function() {
      function e() {
        var t = this;
        (0,
          o.Z)(this, e),
          (0,
            a.Z)(this, "loginGuideShowed", void 0),
          (0,
            a.Z)(this, "TODAY", void 0),
          (0,
            a.Z)(this, "AB_LOGIN_GUIDE_STORAGE_KEY", "AB_LOGIN_GUIDE_TIMESTAMP"),
          (0,
            a.Z)(this, "AVATAR_LOGIN_GUIDE_COUNT", "AVATAR_LOGIN_GUIDE_COUNT"),
          (0,
            a.Z)(this, "duration", void 0),
          (0,
            a.Z)(this, "refreshNumber", void 0),
          (0,
            a.Z)(this, "closeTimer", void 0),
          (0,
            a.Z)(this, "mountEle", void 0),
          (0,
            a.Z)(this, "showTime", void 0),
          (0,
            a.Z)(this, "isScan", void 0),
          (0,
            a.Z)(this, "nowRefreshNum", void 0),
          (0,
            a.Z)(this, "getQrcode", void 0),
          (0,
            a.Z)(this, "avatarCount", void 0),
          (0,
            a.Z)(this, "ScanCodeDescription", (function(e) {
              var n = e.getQRCode
                , r = e.autoRefreshNum;
              return t.getQrcode = n,
                t.nowRefreshNum = r,
                p.createElement("div", {
                  className: "login-guide__desc"
                }, p.createElement("div", null, "\u767b\u5f55\u540e\uff0c\u6296\u97f3\u66f4\u61c2\u4f60"), p.createElement("div", null, "\u8fd8\u53ef\u4ee5\u70b9\u8d5e\u559c\u6b22\u7684\u89c6\u9891\u54e6"))
            }
          )),
          (0,
            a.Z)(this, "dynamicDesc", (function(e) {
              return function(n) {
                var r = n.getQRCode
                  , o = n.autoRefreshNum;
                return t.getQrcode = r,
                  t.nowRefreshNum = o,
                  p.createElement("div", {
                    className: "login-guide__desc"
                  }, p.createElement("div", null, e[0]), p.createElement("div", null, e[1]))
              }
            }
          )),
          (0,
            a.Z)(this, "operationCallback", (function(e, n) {
              if ("LOGIN_SCAN_CODE" === e)
                if ("scannedQrCode" === n) {
                  if (t.isScan = !0,
                    t.showTime) {
                    var r = (new Date).getTime() - t.showTime;
                    V.sendLog("loginScanQrcodeStay", {
                      duration: Math.round(r / 1e3),
                      enter_from: _.vM() || "",
                      enter_method: "cold_start",
                      isActive: "0"
                    })
                  }
                  t.showTime = 0
                } else
                  t.isScan = !1
            }
          )),
          (0,
            a.Z)(this, "setCurrentTime", (function() {
              var e = E.Q;
              e && e.setItem(t.AB_LOGIN_GUIDE_STORAGE_KEY, t.TODAY.toString(), b.COOKIE_DEFAULT_EXPIRE_DURATION, "/", "douyin.com", "")
            }
          )),
          (0,
            a.Z)(this, "setAvatarCurrentTime", (function() {
              t.setCurrentTime();
              var e = E.Q
                , n = t.avatarCount + 1;
              e.setItem(t.AVATAR_LOGIN_GUIDE_COUNT, n.toString(), 2592e3, "/", "douyin.com", "")
            }
          )),
          (0,
            a.Z)(this, "isToday", (function(e, t) {
              return !!e && new Date(e).toDateString() === new Date(t).toDateString()
            }
          )),
          (0,
            a.Z)(this, "getCookiesTime", (function() {
              var e = E.Q
                , n = e && e.getItem({
                sKey: t.AB_LOGIN_GUIDE_STORAGE_KEY
              });
              return n ? c()(n, 10) : 0
            }
          )),
          (0,
            a.Z)(this, "handler", (function() {
              t.isScan ? t.closeTimer = d()(t.handler, 1e3) : t.destroy()
            }
          ));
        var n = E.Q;
        this.loginGuideShowed = !1,
          this.TODAY = (new Date).getTime(),
          this.duration = 5,
          this.refreshNumber = 2,
          this.closeTimer = null,
          this.nowRefreshNum = 0,
          this.getQrcode = null,
          this.avatarCount = n && c()(n.getItem({
            sKey: this.AVATAR_LOGIN_GUIDE_COUNT
          }), 10) || 0
      }
      var t, n;
      return (0,
        i.Z)(e, [{
        key: "extraGetQr",
        value: function() {
          W = "1",
          this.nowRefreshNum >= this.refreshNumber && (this.getQrcode(),
          this.nowRefreshNum >= this.duration && (clearTimeout(this.closeTimer),
            this.closeTimer = d()(this.handler, 6e4)))
        }
      }, {
        key: "show",
        value: (n = (0,
            l.Z)(h().mark((function e() {
              var t, n, o, i, a, l, s, c, u, m, f, w, E = this, x = arguments;
              return h().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        return t = x.length > 0 && void 0 !== x[0] ? x[0] : "0",
                          e.next = 3,
                          F();
                      case 3:
                        return W = t,
                          e.next = 6,
                          k.b();
                      case 6:
                        return n = e.sent,
                          o = n.isLogin,
                          e.next = 10,
                          v().all([y.h.getVar({
                            name: "avatar_login_guide",
                            defaultValue: 0
                          }), y.h.getVar({
                            name: "download_guide_stage2",
                            defaultValue: 0
                          }), y.h.getVar({
                            name: "cold_start_login_guide_panel",
                            defaultValue: []
                          })]);
                      case 10:
                        if (i = e.sent,
                          a = (0,
                            r.Z)(i, 3),
                          l = a[0],
                          s = a[1],
                          c = a[2],
                          u = 1 === l && !(this.avatarCount % 3 == 0 && this.hasShowedToday()) || 2 === l && this.avatarCount < 5,
                        !this.loginGuideShowed && !o && "follow" !== _.yW()) {
                          e.next = 18;
                          break
                        }
                        return e.abrupt("return");
                      case 18:
                        return m = c.length > 0 ? c : ["\u767b\u5f55\u540e\uff0c\u6296\u97f3\u66f4\u61c2\u4f60", "\u8fd8\u53ef\u4ee5\u70b9\u8d5e\u559c\u6b22\u7684\u89c6\u9891\u54e6"],
                          f = u ? ["\u767b\u5f55\u6296\u97f3", "\u83b7\u5f97\u4e13\u5c5e\u5934\u50cf\u6302\u4ef6"] : m,
                          e.next = 23,
                          (0,
                            A.gE)({
                            ScanCodeDescription: this.dynamicDesc(f),
                            refreshNumber: this.refreshNumber,
                            operationCallback: function(e, t) {
                              E.operationCallback(e, t)
                            },
                            enterMethod: "cold_start",
                            videoGuideFunc: function() {
                              return W
                            },
                            teaEvtParams: {
                              is_topknot: u ? "1" : "0"
                            },
                            scanCodeNeedLogo: !0
                          });
                      case 23:
                        w = e.sent,
                          this.showTime = (new Date).getTime(),
                          this.loginGuideShowed = !0,
                          this.mountEle = document.createElement("div"),
                          this.mountEle.classList.add("login-guide-container"),
                          document.body.appendChild(this.mountEle),
                          g.render(p.createElement(O, {
                            config: w,
                            destroy: function() {
                              E.destroy()
                            },
                            isVideoGuide: W,
                            isShowAvatarGuide: u,
                            isNewBtn: 2 === s || 3 === s
                          }), this.mountEle, u ? this.setAvatarCurrentTime : this.setCurrentTime),
                        this.duration > 0 && (this.closeTimer = d()(this.handler, 60 * this.duration * 1e3));
                      case 31:
                      case "end":
                        return e.stop()
                    }
                }
              ), e, this)
            }
          ))),
            function() {
              return n.apply(this, arguments)
            }
        )
      }, {
        key: "showPerDay",
        value: (t = (0,
            l.Z)(h().mark((function e(t) {
              var n, r = this;
              return h().wrap((function(e) {
                  for (; ; )
                    switch (e.prev = e.next) {
                      case 0:
                        if (void 0 !== t) {
                          e.next = 5;
                          break
                        }
                        return e.next = 3,
                          k.b();
                      case 3:
                        n = e.sent,
                          t = null == n ? void 0 : n.isLogin;
                      case 5:
                        if (!t) {
                          e.next = 7;
                          break
                        }
                        return e.abrupt("return");
                      case 7:
                        return e.next = 9,
                          (0,
                            C.iM)();
                      case 9:
                        if (!e.sent) {
                          e.next = 12;
                          break
                        }
                        return e.abrupt("return");
                      case 12:
                        return w.YY.insertTask(w.BE.LoginGuideTaskId, (function() {
                            r.show()
                          }
                        ), {
                          delay: 0,
                          priority: w.T0.LoginGuidePriority,
                          onFinish: function() {
                            r.handler()
                          }
                        }),
                          e.abrupt("return");
                      case 14:
                      case "end":
                        return e.stop()
                    }
                }
              ), e)
            }
          ))),
            function(e) {
              return t.apply(this, arguments)
            }
        )
      }, {
        key: "destroy",
        value: function() {
          clearTimeout(this.closeTimer),
            g.unmountComponentAtNode(this.mountEle),
          document.body.contains(this.mountEle) && document.body.removeChild(this.mountEle),
            this.loginGuideShowed = !1,
            w.YY.finishTask(w.BE.LoginGuideTaskId)
        }
      }, {
        key: "hasShowedToday",
        value: function() {
          var e = this.getCookiesTime();
          return e && this.isToday(e, this.TODAY) || !1
        }
      }]),
        e
    }()
      , H = x.p() ? null : new U
  }
  ,
  92253: (e,t,n)=>{
    n.d(t, {
      J: ()=>f
    });
    var r = n(65146)
      , o = n(32781)
      , i = n(21805)
      , a = n.n(i)
      , l = n(44503)
      , s = n(79705)
      , c = n.n(s)
      , u = n(19538);
    const d = {
      popover: "QUUswvJ3",
      content: "zWjTVNan",
      left: "sSoR5D5a",
      right: "KOMwqSsA",
      top: "F42n42IL",
      bottom: "DWl8khup"
    };
    var m = n(9988)
      , v = {
      left: "right",
      right: "left",
      top: "bottom",
      bottom: "top"
    }
      , f = (0,
      l.memo)((function(e) {
        var t = e.position
          , n = void 0 === t ? "bottom" : t
          , i = e.defaultVisible
          , s = void 0 !== i && i
          , f = e.visible
          , h = e.onVisibleChange
          , p = e.content
          , g = e.spacing
          , y = void 0 === g ? 10 : g
          , w = e.children
          , _ = e.contentClassName
          , E = e.mouseEnterDelay
          , k = e.mouseLeaveDelay
          , x = e.className
          , b = (0,
          u.C)({
          defaultValue: s,
          value: f
        })
          , C = (0,
          o.Z)(b, 2)
          , N = C[0]
          , T = C[1]
          , Z = (0,
          l.useRef)(null)
          , S = (0,
          m.U)({
          enterDelay: E,
          leaveDelay: k,
          onMouseEnter: function() {
            T(!0),
            N || null == h || h(!0)
          },
          onMouseLeave: function() {
            T(!1),
            N && (null == h || h(!1))
          }
        })
          , I = S.onMouseEnter
          , L = S.onMouseLeave
          , D = (0,
          l.useState)(0)
          , M = (0,
          o.Z)(D, 2)
          , B = M[0]
          , A = M[1];
        return (0,
          l.useEffect)((function() {
            var e, t;
            N && Z.current && (a()(e = ["top", "bottom"]).call(e, n) ? A(Z.current.offsetHeight) : a()(t = ["left", "right"]).call(t, n) && A(Z.current.offsetWidth))
          }
        ), [N, n]),
          l.createElement("div", {
            className: c()(d.popover, x),
            ref: Z,
            onMouseEnter: I,
            onMouseLeave: L
          }, w, N && l.createElement("div", {
            className: c()(d.content, d[n], _),
            style: (0,
              r.Z)({}, v[n], B + y)
          }, p))
      }
    ))
  }
  ,
  55618: (e,t,n)=>{
    n.d(t, {
      T: ()=>u
    });
    var r = n(30906)
      , o = n(67161)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a);
    const s = "mPWahmAI";
    var c = ["children", "className", "style"];
    function u(e) {
      var t = e.children
        , n = e.className
        , a = e.style
        , u = (0,
        o.Z)(e, c)
        , d = u.onMaskClick
        , m = (0,
        i.useRef)(null)
        , v = (0,
        i.useCallback)((function(e) {
          e.target === m.current && (null == d || d())
        }
      ), [d]);
      return (0,
        i.useEffect)((function() {
          if ("" === document.body.className)
            return document.body.style.overflow = "hidden",
              function() {
                document.body.style.overflow = ""
              }
        }
      ), []),
        i.createElement("div", (0,
          r.Z)({
          className: l()(s, n),
          style: a,
          ref: m,
          onClick: v
        }, u), t)
    }
  }
  ,
  34276: (e,t,n)=>{
    n.r(t),
      n.d(t, {
        SearchBar: ()=>Pt,
        default: ()=>Ot
      });
    var r = n(65146)
      , o = n(94610)
      , i = n.n(o)
      , a = n(84578)
      , l = n.n(a)
      , s = n(44503)
      , c = n(79705)
      , u = n.n(c)
      , d = n(78867)
      , m = n(92557)
      , v = n(76653)
      , f = n(25361)
      , h = n(34357)
      , p = n(50062)
      , g = n(42716)
      , y = n(4561)
      , w = n(97568)
      , _ = n(67136)
      , E = n(52296)
      , k = n(64215)
      , x = n(45985)
      , b = n(71181)
      , C = n(92012)
      , N = n.n(C);
    const T = {
      container: "Edp6sg8Y",
      activity: "jHjyLdAn",
      vsTransMode: "K6ytCcCN",
      textContainer: "oZqQkOiC",
      transparent: "uDREsUPh",
      divider: "tOVjdP5_",
      item: "mKaKWenM",
      bottomWordText: "oxvtZXib",
      guessListItemIcon: "jYF8SZRX",
      guessListItemIconHot: "ve5rTciT",
      guessListItemIconLive: "WdHbJvDc"
    };
    var Z = function(e) {
      var t = e.word;
      return s.createElement("div", {
        className: T.bottomWordText
      }, t)
    };
    const S = function(e) {
      var t, n = e.wordList, o = void 0 === n ? [] : n, a = e.onBottomWordClick, l = e.customProps;
      return s.createElement("div", {
        className: u()(T.container, (t = {},
          (0,
            r.Z)(t, T.activity, (null == l ? void 0 : l.isActivity) || (null == l ? void 0 : l.transparent)),
          (0,
            r.Z)(t, null == T ? void 0 : T[null == l ? void 0 : l.activityName], null == l ? void 0 : l.activityName),
          (0,
            r.Z)(t, T.transparent, null == l ? void 0 : l.transparent),
          t))
      }, i()(o).call(o, (function(e, t) {
          var n, o, i = "2" === e.words_type;
          return s.createElement("div", {
            className: T.item,
            key: N()(n = "bottom_".concat(null !== (o = e.id) && void 0 !== o ? o : "", "_")).call(n, t)
          }, 0 !== t && s.createElement("div", {
            className: T.divider
          }), s.createElement("div", {
            className: T.textContainer,
            "data-text": e.word,
            "data-index": t,
            "data-id": e.id,
            onClick: a
          }, s.createElement(Z, {
            word: e.word
          }), i && s.createElement("div", {
            className: u()(T.guessListItemIcon, (0,
              r.Z)({}, T.guessListItemIconHot, i))
          })))
        }
      )))
    }
      , I = {
      container: "ynBZuEjF",
      activity: "qLspBRSK",
      vsTransMode: "p4fRQID2",
      textContainer: "lasTvRnl",
      transparent: "wEFIXLMr",
      active: "cOkC67q3",
      divider: "rsoSxKGW",
      item: "SS3QikUi",
      bottomWordText: "NweHClwp"
    };
    var L = function(e) {
      var t = e.word
        , n = e.index;
      return s.createElement("div", {
        className: I.bottomWordText,
        "data-text": t,
        "data-index": n
      }, t)
    };
    const D = function(e) {
      var t, n = e.wordList, o = void 0 === n ? [] : n, a = e.active, l = void 0 !== a && a, c = e.customProps;
      return s.createElement("div", {
        className: u()(I.container, (t = {},
          (0,
            r.Z)(t, I.activity, (null == c ? void 0 : c.isActivity) || (null == c ? void 0 : c.transparent)),
          (0,
            r.Z)(t, null == I ? void 0 : I[null == c ? void 0 : c.activityName], null == c ? void 0 : c.activityName),
          (0,
            r.Z)(t, I.transparent, null == c ? void 0 : c.transparent),
          t))
      }, i()(o).call(o, (function(e, t) {
          return 0 === t ? s.createElement("div", {
            className: I.item,
            key: e.id
          }, s.createElement("div", {
            className: u()(I.textContainer, (0,
              r.Z)({}, I.active, l))
          }, s.createElement(L, {
            word: e.word,
            index: t
          }))) : s.createElement("div", {
            className: I.item,
            key: e.id
          }, s.createElement("div", {
            className: I.divider
          }), s.createElement("div", {
            className: I.textContainer
          }, s.createElement(L, {
            word: e.word,
            index: t
          })))
        }
      )))
    };
    var M = 10
      , B = 30069
      , A = "\u641c\u7d22\u4f60\u611f\u5174\u8da3\u7684\u5185\u5bb9"
      , P = 999
      , O = ["main_page", "discover", "follow", "friend", "live", "hot", "vs", "recommend", "pandemic"]
      , V = ["vs"]
      , W = [{
      searchText: "\u70b9\u51fb\u641c\u7d22\uff0c\u770b\u592e\u89c6\u6625\u665a",
      searchKeyword: "\u592e\u89c6\u6625\u665a",
      startTime: 16436124e5,
      endTime: 1643652e6
    }, {
      searchText: "\u9650\u65f6\u514d\u8d39\u770b\u6211\u548c\u6211\u7684\u7236\u8f88",
      searchKeyword: "\u6211\u548c\u6211\u7684\u7236\u8f88",
      startTime: 16436772e5,
      endTime: 16441632e5
    }]
      , R = {
      enterSearch: {
        eventName: "enter_search",
        params: {
          enter_from: "",
          enter_from_second: "",
          click_method: ""
        }
      },
      searchAnti: {
        eventName: "search_anti_rpt",
        params: {
          anti_id: "",
          anti_query_input_time: 0,
          anti_search_press_duration: 0,
          anti_search_viewport: ""
        }
      },
      sugShow: {
        eventName: "search_sug",
        params: {
          impr_id: "",
          search_keyword: "",
          search_type: "",
          sug_keyword: "",
          action_type: "show"
        }
      },
      sugClick: {
        eventName: "search_sug",
        params: {
          impr_id: "",
          search_keyword: "",
          search_type: "",
          sug_keyword: "",
          action_type: "click"
        }
      },
      trendingShow: {
        eventName: "trending_show",
        params: {
          log_pb: {},
          impr_id: "",
          search_id: "",
          words_num: 0,
          words_source: "sug",
          raw_query: "",
          rank: -1,
          search_position: ""
        }
      },
      trendingWordsShow: {
        eventName: "trending_words_show",
        params: {
          impr_id: "",
          search_id: "",
          words_source: "sug",
          words_position: 0,
          words_content: "",
          raw_query: "",
          rank: -1,
          search_position: "",
          query_id: "",
          group_id: ""
        }
      },
      trendingWordsClick: {
        eventName: "trending_words_click",
        params: {
          impr_id: "",
          words_source: "sug",
          words_position: 0,
          words_content: "",
          raw_query: "",
          rank: -1,
          search_position: "",
          query_id: "",
          group_id: ""
        }
      },
      historyClick: {
        eventName: "trending_words_click",
        params: {
          enter_from: "",
          words_source: "search_history",
          words_num: "0",
          words_position: 0,
          words_content: ""
        }
      },
      hotWordClick: {
        eventName: "trending_words_click",
        params: {
          impr_id: "",
          enter_from: "",
          words_source: "hot_search_board",
          words_num: "0",
          words_position: 0,
          words_content: "",
          group_id: ""
        }
      },
      historyShow: {
        eventName: "trending_words_show",
        params: {
          enter_from: "",
          words_source: "search_history",
          words_num: "0",
          words_position: 0,
          words_content: ""
        }
      },
      hotWordShow: {
        eventName: "trending_words_show",
        params: {
          impr_id: "",
          enter_from: "",
          words_source: "hot_search_board",
          words_num: "0",
          words_position: 0,
          words_content: "",
          group_id: ""
        }
      },
      guessWordShow: {
        eventName: "trending_words_show",
        params: {
          impr_id: "",
          enter_from: "",
          words_source: "recom_search",
          words_num: "0",
          words_position: 0,
          words_content: "",
          group_id: ""
        }
      },
      guessWordClick: {
        eventName: "trending_words_click",
        params: {
          impr_id: "",
          enter_from: "",
          words_source: "recom_search",
          words_num: "0",
          words_position: 0,
          words_content: "",
          group_id: ""
        }
      },
      clearButtonClick: {
        eventName: "clear_search_keyword",
        params: {
          enter_from: ""
        }
      },
      searchSugLoadPerformance: {
        eventName: "search_sug_load_performance",
        params: {
          impr_id: "",
          search_type: "",
          sug_keyword: "",
          words_num: 0,
          sug_fetch_duration: 0,
          sug_render_duration: 0,
          enter_from: ""
        }
      },
      relatedTrendingShow: {
        eventName: "trending_show",
        params: {
          words_num: "",
          words_source: "related_search",
          raw_query: "",
          rank: 0,
          search_position: "general"
        }
      },
      relatedWordsShow: {
        eventName: "trending_words_show",
        params: {
          words_source: "related_search",
          words_position: 0,
          words_content: "",
          raw_query: "",
          rank: 0,
          search_position: "general",
          query_id: "",
          group_id: "",
          sug_type: ""
        }
      },
      relatedWordsClick: {
        eventName: "trending_words_click",
        params: {
          words_source: "related_search",
          words_position: 0,
          words_content: "",
          raw_query: "",
          rank: 0,
          search_position: "general",
          query_id: "",
          group_id: "",
          sug_type: ""
        }
      },
      recomSearchChangeButtonShow: {
        eventName: "recom_search_change_button_show",
        params: {}
      },
      recomSearchChangeButtonClick: {
        eventName: "recom_search_change_button_click",
        params: {}
      },
      historyFoldButtonShow: {
        eventName: "history_fold_button_show",
        params: {}
      },
      historyFoldButtonClick: {
        eventName: "history_fold_button_click",
        params: {}
      }
    }
      , F = n(67161)
      , U = n(30673)
      , H = n(30906)
      , G = n(64408)
      , j = n(32781)
      , K = n(19478)
      , q = n.n(K)
      , Y = n(88438)
      , X = n.n(Y)
      , z = n(63135)
      , Q = n.n(z)
      , J = n(21805)
      , $ = n.n(J)
      , ee = n(47776)
      , te = n.n(ee)
      , ne = n(71912)
      , re = n.n(ne)
      , oe = n(81711)
      , ie = n.n(oe)
      , ae = n(5594)
      , le = n.n(ae)
      , se = n(9070)
      , ce = n(73750)
      , ue = n(79852)
      , de = n(37485)
      , me = n(55131)
      , ve = n(16501)
      , fe = n(56493)
      , he = n(72983)
      , pe = n(23587)
      , ge = n(25083)
      , ye = n(75403)
      , we = n(52252)
      , _e = n(42103)
      , Ee = n(43564)
      , ke = n(67255)
      , xe = n(76659)
      , be = n(77606)
      , Ce = n(18343)
      , Ne = n(150)
      , Te = n(29529)
      , Ze = n(78170)
      , Se = n.n(Ze)
      , Ie = n(57617)
      , Le = n.n(Ie)
      , De = n(77521)
      , Me = n.n(De)
      , Be = n(92637)
      , Ae = n.n(Be)
      , Pe = n(9120)
      , Oe = n.n(Pe)
      , Ve = n(42155)
      , We = n.n(Ve)
      , Re = n(86860)
      , Fe = n(52558)
      , Ue = n(14484)
      , He = n(67606);
    function Ge(e) {
      e.preventDefault()
    }
    function je(e, t, n, r, o, i, a) {
      var l = (0,
        s.useState)(null)
        , c = (0,
        j.Z)(l, 2)
        , u = c[0]
        , d = c[1]
        , m = (0,
        s.useState)("")
        , v = (0,
        j.Z)(m, 2)
        , f = v[0]
        , h = v[1];
      return (0,
        Fe.Z)("ArrowUp", (function(n) {
          n.stopPropagation(),
          t || d((function(t) {
              return 0 === e ? null : o.enableSearchBarShuffling && "sug" === r && 0 === t ? (a && a(f),
                null) : o.enableSearchBarShuffling && "sug" === r && null === t ? (h(i),
              e - 1) : null === t ? 0 : 0 === t ? e - 1 : Math.max(0, t - 1)
            }
          ))
        }
      ), {
        target: n
      }),
        (0,
          Fe.Z)("ArrowDown", (function(n) {
            n.stopPropagation(),
            t || d((function(t) {
                return 0 === e ? null : (o.enableSearchBarShuffling && "sug" === r && null === t && h(i),
                  o.enableSearchBarShuffling && "sug" === r && t === e - 1 ? (a && a(f),
                    null) : null === t || t === e - 1 ? 0 : Math.min(e - 1, t + 1))
              }
            ))
          }
        ), {
          target: n
        }),
        {
          keyboardNavIndex: u,
          restKeyboardNavIndex: (0,
            s.useCallback)((function() {
              d(null)
            }
          ), [])
        }
    }
    function Ke(e, t, n, r) {
      var o = /firefox/i.test(navigator.userAgent)
        , i = "param-input";
      if (o)
        if (r) {
          var a, l = function() {
            var e;
            ie()(e = Se()(n.getElementsByClassName(i))).call(e, (function(e) {
                e.parentNode.removeChild(e)
              }
            ))
          };
          l(),
            ie()(a = Le()(t)).call(a, (function(e) {
                var r = document.createElement("input");
                r.type = "hidden",
                  r.name = e,
                  r.value = t[e],
                  r.className = i,
                  n.insertBefore(r, n.children[0])
              }
            )),
            n.action = Ue.Sp(encodeURIComponent(e)),
            X()((function() {
                l()
              }
            ), 0)
        } else {
          var s = window.open("about:blank");
          s && (s.location.href = globalThis.getFilterXss().filterUrl(Ue.Sp(encodeURIComponent(e), (0,
            Re.stringify)(t)), null, {
            logType: "js.href/src",
            reportOnly: !1
          }))
        }
      else {
        var c = Ue.Sp(encodeURIComponent(e), (0,
          Re.stringify)(t));
        window.open(c)
      }
    }
    function qe() {
      var e = ""
        , t = ""
        , n = Me()();
      return ie()(W).call(W, (function(r) {
          var o = r.startTime
            , i = r.endTime
            , a = r.searchText
            , l = r.searchKeyword;
          n >= o && n <= i && (e = a,
            t = l)
        }
      )),
        {
          hotSearchText: e,
          hotSearchKeyword: t
        }
    }
    function Ye(e) {
      var t = Ae()(e).call(e, (function(e) {
          return e.scene === He.gQ.FeedBottomRec
        }
      ))
        , n = Oe()(t).call(t, (function(e, t) {
          var n;
          return N()(e).call(e, i()(n = t.words).call(n, (function(e) {
              return e.wordId
            }
          )))
        }
      ), []);
      return Se()(new (We())(n)).join(",")
    }
    var Xe = function() {
      var e, t;
      if (!we.p()) {
        var n = "header-with-bottom"
          , r = document.documentElement;
        null != r && null !== (e = r.hasAttribute) && void 0 !== e && e.call(r, n) || null == r || null === (t = r.setAttribute) || void 0 === t || t.call(r, n, "")
      }
    }
      , ze = function() {
      var e;
      if (!we.p()) {
        var t, n = "header-with-bottom", r = document.documentElement;
        if (null != r && null !== (e = r.hasAttribute) && void 0 !== e && e.call(r, n))
          null == r || null === (t = r.removeAttribute) || void 0 === t || t.call(r, n)
      }
    }
      , Qe = function(e, t, n) {
      var r = {
        dedupedInboxWords: e,
        dedupedUnderboxWords: t
      };
      if (null == e || !e.word || 0 === t.length)
        return r;
      "inbox" === n ? r.dedupedUnderboxWords = Ae()(t).call(t, (function(t) {
          return (null == t ? void 0 : t.word) !== e.word
        }
      )) : Ae()(t).call(t, (function(t) {
          return (null == t ? void 0 : t.word) === e.word
        }
      )).length > 0 && (r.dedupedInboxWords = null);
      return r
    }
      , Je = function(e, t) {
      var n, r = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : 0, o = [];
      o.push.apply(o, (0,
        U.Z)(e));
      var i = l()(t).call(t, r, t.length)
        , a = l()(t).call(t, 0, r);
      return o.push.apply(o, N()(n = (0,
        U.Z)(i)).call(n, (0,
        U.Z)(a))),
        o
    }
      , $e = function(e, t, n) {
      return (e + t) % n
    }
      , et = function(e) {
      return "object" !== (0,
        Te.Z)(e) ? {} : (null != e && e.from_group_id || delete e.from_group_id,
        e)
    }
      , tt = Ne.COMMON_SEARCH_PARAMS
      , nt = "/aweme/v1/web/hot/search/list/"
      , rt = "/aweme/v1/web/search/sug/"
      , ot = function(e) {
      var t, n = {
        logId: null == e ? void 0 : e.log_id,
        data: {
          barWords: {
            words: []
          },
          bottomWords: {
            words: []
          },
          underboxMore: {
            words: []
          }
        }
      }, r = null !== (t = null == e ? void 0 : e.data) && void 0 !== t ? t : [];
      if (te()(r) && r.length > 0 && ie()(r).call(r, (function(e) {
          var t = n.data
            , r = t.barWords
            , o = t.bottomWords
            , i = t.underboxMore;
          null != e && e.type && te()(null == e ? void 0 : e.words) && 0 !== e.words.length && ("inbox" === e.type ? r.words = e.words : "under_inbox" === e.type ? o.words = e.words : "under_inbox_more" === e.type && (i.words = e.words))
        }
      )),
      n.data.barWords.words.length > 0) {
        var o, i, a = n.data.barWords.words[0];
        if (null != a && null !== (o = a.params) && void 0 !== o && null !== (i = o.extra_info) && void 0 !== i && i.tag_icon) {
          var l = JSON.parse(a.params.extra_info.tag_icon);
          l.icon_url && (a.icon_info = l)
        }
      }
      return n
    }
      , it = function() {
      var e = (0,
        G.Z)(le().mark((function e(t) {
          var n;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      (0,
                        Ce.U2)("/aweme/v1/web/api/suggest_words/", (0,
                        H.Z)((0,
                        H.Z)({}, tt), et(t)));
                  case 2:
                    return n = e.sent,
                      e.abrupt("return", n);
                  case 4:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }()
      , at = function() {
      var e = (0,
        G.Z)(le().mark((function e(t) {
          var n, r, o, i, a, l = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return n = l.length > 1 && void 0 !== l[1] ? l[1] : {},
                      r = ge.yW(),
                      o = (n || {}).isModalVideo,
                      i = void 0 !== o && o,
                    "recommend" !== r || i || (t.pd = "pc_recommend"),
                      e.next = 6,
                      it((0,
                        H.Z)({
                        business_id: B,
                        rsp_source: ["inbox"]
                      }, et(t)));
                  case 6:
                    return a = e.sent,
                      e.abrupt("return", ot(a));
                  case 8:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }()
      , lt = function() {
      var e = (0,
        G.Z)(le().mark((function e() {
          var t, n, r = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return t = r.length > 0 && void 0 !== r[0] ? r[0] : {},
                      e.next = 3,
                      it((0,
                        H.Z)({
                        business_id: 30068
                      }, et(t)));
                  case 3:
                    return n = e.sent,
                      e.abrupt("return", ot(n));
                  case 5:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , st = function() {
      var e = (0,
        G.Z)(le().mark((function e() {
          var t, n, r, o, i, a, l = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return t = l.length > 0 && void 0 !== l[0] ? l[0] : {},
                      n = l.length > 1 && void 0 !== l[1] ? l[1] : {},
                      r = et(t),
                      o = (n || {}).shouldUseUnderInbox,
                      i = (void 0 === o || o) && null != r && r.from_group_id ? ["under_inbox", "under_inbox_more"] : ["under_inbox_more"],
                      e.next = 7,
                      it((0,
                        H.Z)({
                        business_id: B,
                        rsp_source: i
                      }, r));
                  case 7:
                    return a = e.sent,
                      e.abrupt("return", ot(a));
                  case 9:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , ct = function() {
      var e = (0,
        G.Z)(le().mark((function e(t) {
          var n, r, o, i, a, l, s, c, u, d, m = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return n = m.length > 1 && void 0 !== m[1] ? m[1] : {},
                      r = ge.yW(),
                      i = (o = n || {}).isModalVideo,
                      a = void 0 !== i && i,
                      l = o.shouldUseUnderInbox,
                      s = void 0 === l || l,
                    "recommend" !== r || a || (t.pd = "pc_recommend"),
                      c = et(t),
                      u = s && null != c && c.from_group_id ? ["inbox", "under_inbox", "under_inbox_more"] : ["inbox", "under_inbox_more"],
                      e.next = 8,
                      it((0,
                        H.Z)({
                        business_id: B,
                        rsp_source: u
                      }, c));
                  case 8:
                    return d = e.sent,
                      e.abrupt("return", ot(d));
                  case 10:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }()
      , ut = function() {
      var e = (0,
        G.Z)(le().mark((function e() {
          var t, n, r = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return t = r.length > 0 && void 0 !== r[0] ? r[0] : {},
                      e.next = 3,
                      (0,
                        Ce.U2)(nt, (0,
                        H.Z)((0,
                        H.Z)({}, tt), {}, {
                        detail_list: 1,
                        source: 6
                      }, et(t)));
                  case 3:
                    return n = e.sent,
                      e.abrupt("return", n);
                  case 5:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , dt = function() {
      var e = (0,
        G.Z)(le().mark((function e() {
          var t, n, r = arguments;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return t = r.length > 0 && void 0 !== r[0] ? r[0] : {},
                      e.next = 3,
                      (0,
                        Ce.U2)(rt, (0,
                        H.Z)((0,
                        H.Z)({}, tt), et(t)));
                  case 3:
                    return n = e.sent,
                      e.abrupt("return", n);
                  case 5:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , mt = function() {
      var e = arguments.length > 2 ? arguments[2] : void 0
        , t = arguments.length > 3 ? arguments[3] : void 0
        , n = arguments.length > 4 ? arguments[4] : void 0
        , r = arguments.length > 5 ? arguments[5] : void 0
        , o = (0,
        s.useState)([])
        , i = (0,
        j.Z)(o, 2)
        , a = i[0]
        , l = i[1]
        , c = (0,
        s.useState)(!1)
        , u = (0,
        j.Z)(c, 2)
        , d = u[0]
        , m = u[1]
        , v = (0,
        s.useRef)([])
        , f = (0,
        s.useMemo)((function() {
          return (0,
            de.y$)(R)
        }
      ), [])
        , h = (0,
        s.useCallback)((function(e) {
          l(e),
            v.current = e
        }
      ), [])
        , p = (0,
        s.useCallback)((function() {
          var o;
          e || (r(""),
            m(!0),
            ie()(o = v.current).call(o, (function(e, r) {
                f("guessWordShow", {
                  enter_from: t(),
                  impr_id: n.current.guessListLogId,
                  words_content: e.word,
                  words_num: String(v.current.length),
                  words_position: Number(r),
                  words_source: "search_bar_inner",
                  group_id: e.id
                })
              }
            )))
        }
      ), [e, t, f, n, r])
        , g = (0,
        s.useCallback)((function() {
          d && (m(!1),
            r(A))
        }
      ), [d, r]);
      return {
        insideWordList: a,
        updateInsideWord: h,
        showInsideWord: p,
        hideInsideWord: g,
        isInsideWordShow: d
      }
    }
      , vt = function() {
      var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
        , t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {}
        , n = arguments.length > 2 ? arguments[2] : void 0
        , r = arguments.length > 3 ? arguments[3] : void 0
        , o = arguments.length > 4 ? arguments[4] : void 0
        , i = arguments.length > 5 ? arguments[5] : void 0
        , a = arguments.length > 6 ? arguments[6] : void 0
        , c = (0,
        s.useState)([])
        , u = (0,
        j.Z)(c, 2)
        , v = u[0]
        , f = u[1]
        , h = (0,
        s.useMemo)((function() {
          return (0,
            de.y$)(R)
        }
      ), [])
        , p = (0,
        s.useRef)("")
        , g = (0,
        s.useRef)([])
        , y = (0,
        s.useRef)(0)
        , w = (0,
        s.useMemo)((function() {
          return ["recommend", "follow", "friend"]
        }
      ), [])
        , _ = (0,
        s.useRef)(null)
        , E = 1e4
        , k = (0,
        s.useCallback)((function() {
          return !((null == e ? void 0 : e.bottomWordOpt) !== d.BottomWordOpt.NoDeDup && (null == e ? void 0 : e.bottomWordOpt) !== d.BottomWordOpt.BarWordPrior && (null == e ? void 0 : e.bottomWordOpt) !== d.BottomWordOpt.BottomWordPrior || $()(w).call(w, ge.yW()))
        }
      ), [null == e ? void 0 : e.bottomWordOpt, w])
        , x = (0,
        s.useCallback)((function(t) {
          var i, a = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0, s = l()(t).call(t, 0), c = o.current;
          if (c) {
            var u = c.clientWidth;
            if (e.bottomWordOpt === d.BottomWordOpt.NoDeDup && null !== (i = n.current.guessText) && void 0 !== i && i.word) {
              var m, v = null === (m = n.current.guessText) || void 0 === m ? void 0 : m.word;
              (s = Ae()(s).call(s, (function(e) {
                  return (null == e ? void 0 : e.word) !== v
                }
              ))).unshift(n.current.guessText)
            }
            var y = Ee.y(s, u, "bottom")
              , w = y.displayableNum
              , _ = Math.min(w, P);
            n.current.underInboxMoreCursor = $e(n.current.underInboxMoreCursor, Math.max(_ - a, 0), 20);
            var E = l()(s).call(s, 0, _);
            return f(E),
              g.current = E,
              ie()(E).call(E, (function(e, t) {
                  h("guessWordShow", {
                    enter_from: r(),
                    impr_id: p.current,
                    words_content: e.word,
                    words_num: String(E.length),
                    words_position: Number(t),
                    words_source: "recom_under_box",
                    group_id: e.id
                  })
                }
              )),
              {
                displayableNum: w
              }
          }
        }
      ), [r, o, h, e.bottomWordOpt, n])
        , b = (0,
        s.useCallback)((0,
        G.Z)(le().mark((function t() {
          var r, o, i, a, l, s, c, u, m, v;
          return le().wrap((function(t) {
              for (; ; )
                switch (t.prev = t.next) {
                  case 0:
                    if (!we.p()) {
                      t.next = 2;
                      break
                    }
                    return t.abrupt("return");
                  case 2:
                    return r = $()(w).call(w, ge.yW()),
                      t.next = 5,
                      st({
                        from_group_id: n.current.curVideoGroupId,
                        penetrate_params: {
                          inbox_exist_word_id: n.current.feedBarIds
                        }
                      }, {
                        shouldUseUnderInbox: r
                      });
                  case 5:
                    o = t.sent,
                      i = o.data,
                      a = i.bottomWords,
                      l = i.underboxMore,
                      s = o.logId,
                      c = Je(r ? a.words : [], l.words, n.current.underInboxMoreCursor),
                      u = c,
                    e.bottomWordOpt === d.BottomWordOpt.BarWordPrior && (m = Qe(n.current.guessText, u, "inbox"),
                      v = m.dedupedUnderboxWords,
                      u = v),
                    te()(u) && u.length > 0 && (x(u, r ? a.words.length : 0),
                      p.current = s);
                  case 11:
                  case "end":
                    return t.stop()
                }
            }
          ), t)
        }
      ))), [n, x, w, e.bottomWordOpt])
        , C = (0,
        s.useCallback)((function(e) {
          var t, n = e.currentTarget.dataset, o = n.text, a = n.index;
          i(o, "recom_under_box", "", !1, !0),
            h("guessWordClick", {
              enter_from: r(),
              impr_id: p.current,
              words_content: o,
              words_num: String(g.current.length),
              words_position: Number(a),
              words_source: "recom_under_box",
              group_id: null === (t = g.current[a]) || void 0 === t ? void 0 : t.id
            })
        }
      ), [i, r, h])
        , N = (0,
        s.useCallback)((function(e) {
          $()(V).call(V, e.tab) || (e.scrollType ? "down" === e.scrollType ? ze() : "up" === e.scrollType && Xe() : "number" == typeof e.scrollTop && (n.current.tab !== e.tab && (n.current.tab = e.tab,
            y.current = 0),
            e.scrollTop - y.current > 20 ? (ze(),
              y.current = e.scrollTop) : y.current - e.scrollTop > 20 && (Xe(),
              y.current = e.scrollTop)))
        }
      ), [n])
        , T = (0,
        s.useCallback)((function(e) {
          _.current && clearTimeout(_.current);
          !function t() {
            _.current = X()((function() {
                b(),
                  t()
              }
            ), e)
          }()
        }
      ), [b])
        , Z = (0,
        s.useCallback)((function() {
          _.current && clearTimeout(_.current)
        }
      ), []);
      return (0,
        s.useEffect)((function() {
          if (a())
            return (e.searchBarBottomWord === d.searchBarBottomWord.Bottom1 || e.searchBarBottomWord === d.searchBarBottomWord.Bottom2 || k()) && b(),
            k() && T(E),
              function() {
                Z()
              }
        }
      ), [e, a, k, b]),
        (0,
          s.useEffect)((function() {
            var t;
            if (a() && (0 !== v.length && (Xe(),
            e.searchBarBottomWord === d.searchBarBottomWord.Bottom2))) {
              var n = q()(N, 50, {
                maxWait: 100
              });
              return t = m.listen(m.EVENT.tabContainerScroll, n),
                function() {
                  var e;
                  null === (e = t) || void 0 === e || e()
                }
            }
          }
        ), [v, a]),
        (0,
          s.useEffect)((function() {
            if (null != t && t.pathname && a())
              return e.searchBarBottomWord === d.searchBarBottomWord.Bottom2 && v.length > 0 && Xe(),
              k() && (b(),
                T(E)),
                function() {
                  Z()
                }
          }
        ), [null == t ? void 0 : t.pathname]),
        {
          bottomWordList: v,
          updateBottomWords: b,
          onBottomWordClick: C,
          showBottomWords: x,
          bottomWordLogIdRef: p
        }
    }
      , ft = n(8407);
    function ht(e, t, n) {
      var r = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {}
        , o = arguments.length > 4 ? arguments[4] : void 0
        , i = (0,
        s.useState)([])
        , a = (0,
        j.Z)(i, 2)
        , c = a[0]
        , u = a[1]
        , m = (0,
        s.useRef)([])
        , v = (0,
        s.useRef)(0)
        , f = (0,
        me.wu)()
        , h = f.searchParams
        , p = (0,
        s.useMemo)((function() {
          return (0,
            de.y$)(R)
        }
      ), [])
        , g = (0,
        s.useCallback)((function(e) {
          var t = e.currentTarget.dataset
            , n = t.text
            , r = t.index
            , i = t.id;
          p("relatedWordsClick", {
            words_source: "related_search",
            words_position: Number(r),
            words_content: n,
            raw_query: h.keyword,
            rank: 0,
            search_position: h.tab,
            query_id: h.from_group_id,
            group_id: i,
            sug_type: "normal_sug"
          }),
            o(n, "related_search_keywords", "", !1, !0)
        }
      ), [p, h]);
      return (0,
        s.useEffect)((function() {
          null != r && r.isSearchPage && (null == n ? void 0 : n.relatedSearchList) === d.RelatedSearchList.BottomWord && e && (0,
            G.Z)(le().mark((function n() {
              var r, o, i, a, s, c, d;
              return le().wrap((function(n) {
                  for (; ; )
                    switch (n.prev = n.next) {
                      case 0:
                        return n.next = 2,
                          ft.X({
                            query: t
                          });
                      case 2:
                        r = n.sent,
                          o = r.statusCode,
                          i = r.wordList,
                          a = e.current,
                          s = a.clientWidth,
                          c = Ee.y(i, s, "bottom"),
                          d = c.displayableNum,
                        !o && i.length > 0 && (m.current = i,
                          u(l()(i).call(i, 0, d)),
                          v.current = d),
                          i.length > 2 ? Xe() : ze();
                      case 10:
                      case "end":
                        return n.stop()
                    }
                }
              ), n)
            }
          )))()
        }
      ), [t, n]),
        (0,
          s.useEffect)((function() {
            0 !== c.length && (p("relatedTrendingShow", {
              words_num: c.length.toString(),
              words_source: "related_search",
              raw_query: h.keyword,
              rank: 0,
              search_position: h.tab
            }),
              ie()(c).call(c, (function(e, t) {
                  p("relatedWordsShow", {
                    words_source: "related_search",
                    words_position: t,
                    words_content: e.word,
                    raw_query: h.keyword,
                    rank: 0,
                    search_position: h.tab,
                    query_id: h.from_group_id,
                    group_id: e.id,
                    sug_type: "normal_sug"
                  })
                }
              )))
          }
        ), [c, p]),
        {
          bottomWords: c,
          onBottomWordClick: g
        }
    }
    var pt = ["sugStartTime", "sugFetchTime"];
    function gt(e, t) {
      var n = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : {}
        , o = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : {}
        , a = (0,
        ue.c)()
        , c = a.router
        , u = (0,
        s.useMemo)((function() {
          return (0,
            de.y$)(R)
        }
      ), [])
        , v = (0,
        me.wu)()
        , f = v.searchParams
        , h = v.changeKeyword
        , p = (0,
        ve.u)(e)
        , g = p.history
        , y = p.clearAll
        , w = p.deleteWord
        , _ = p.unshiftWord
        , E = (0,
        s.useMemo)((function() {
          return qe()
        }
      ), [])
        , k = E.hotSearchText
        , x = E.hotSearchKeyword
        , b = (0,
        s.useState)({
        sugList: [],
        query: ""
      })
        , C = (0,
        j.Z)(b, 2)
        , T = C[0]
        , Z = C[1]
        , S = (0,
        s.useState)("")
        , I = (0,
        j.Z)(S, 2)
        , L = I[0]
        , D = I[1]
        , B = (0,
        s.useState)("")
        , P = (0,
        j.Z)(B, 2)
        , V = P[0]
        , W = P[1]
        , K = (0,
        s.useState)("idle")
        , Y = (0,
        j.Z)(K, 2)
        , z = Y[0]
        , J = Y[1]
        , ee = (0,
        s.useState)(!1)
        , ne = (0,
        j.Z)(ee, 2)
        , oe = ne[0]
        , ae = ne[1]
        , se = (0,
        s.useState)([])
        , ce = (0,
        j.Z)(se, 2)
        , Ce = ce[0]
        , Ne = ce[1]
        , Te = (0,
        s.useState)(A)
        , Ze = (0,
        j.Z)(Te, 2)
        , Se = Ze[0]
        , Ie = Ze[1]
        , Le = (0,
        s.useState)(!1)
        , De = (0,
        j.Z)(Le, 2)
        , Me = De[0]
        , Be = De[1]
        , Ae = (0,
        s.useState)(null)
        , Pe = (0,
        j.Z)(Ae, 2)
        , Oe = Pe[0]
        , Ve = Pe[1]
        , We = (0,
        s.useState)([])
        , Re = (0,
        j.Z)(We, 2)
        , Fe = Re[0]
        , Ue = Re[1]
        , He = (0,
        s.useState)(!1)
        , Xe = (0,
        j.Z)(He, 2)
        , ze = Xe[0]
        , $e = Xe[1]
        , et = (0,
        s.useRef)()
        , tt = (0,
        s.useRef)()
        , nt = (0,
        s.useRef)()
        , rt = (0,
        s.useRef)({})
        , ot = (0,
        s.useMemo)((function() {
          return n.guessSearchAddOneMoreRow ? 8 : 6
        }
      ), [n.guessSearchAddOneMoreRow])
        , it = (0,
        s.useMemo)((function() {
          return n.bottomWordOpt === d.BottomWordOpt.NoDeDup || n.bottomWordOpt === d.BottomWordOpt.BarWordPrior || n.bottomWordOpt === d.BottomWordOpt.BottomWordPrior
        }
      ), [n.bottomWordOpt])
        , st = (0,
        s.useState)((function() {
          return X()((function() {}
          ), 1e3)
        }
      ))
        , ft = (0,
        j.Z)(st, 2)
        , gt = ft[0]
        , yt = ft[1]
        , wt = (0,
        s.useRef)({
        focusTime: 0,
        pressDownTime: 0,
        response: void 0,
        suggestionState: z,
        showText: V,
        inputText: L,
        inputFocus: oe,
        hotSearchText: k,
        hotSearchKeyword: x,
        guessText: Oe,
        guessTextId: "",
        router: c,
        tab: f.tab,
        history: g,
        sug: T,
        isPinyin: !1,
        isFirefox: !1,
        hotListLogId: "",
        searchBarWordLogId: "",
        guessListLogId: "",
        curVideoGroupId: "",
        hasGuessTextShown: !1,
        hasInsideWordShown: !1,
        guessList: [],
        existedSuggestWords: [],
        suggestWordsPreloadList: {},
        focusMethod: "",
        feedBarIds: "",
        hasHotListFetched: !1,
        underInboxMoreCursor: 0
      });
      wt.current = (0,
        H.Z)((0,
        H.Z)({}, wt.current), {}, {
        tab: f.tab,
        suggestionState: z,
        showText: V,
        inputText: L,
        inputFocus: oe,
        guessText: Oe,
        router: c,
        history: g,
        sug: T
      });
      var _t = (0,
        s.useCallback)((function() {
          return o.isModalVideo ? "modal_entrance" : ge.yW()
        }
      ), [o.isModalVideo])
        , Et = (0,
        s.useCallback)((function(e, n, r) {
          var i = arguments.length > 3 && void 0 !== arguments[3] && arguments[3]
            , a = !(arguments.length > 4 && void 0 !== arguments[4]) || arguments[4];
          if (null != e && Q()(e).call(e)) {
            var l = (0,
              fe.Z)()
              , s = performance.now()
              , c = "normal_search" === n ? i ? -2 : s - wt.current.pressDownTime : -1;
            if (u("searchAnti", {
              anti_id: l,
              anti_query_input_time: s - wt.current.focusTime,
              anti_search_press_duration: c,
              anti_search_viewport: r
            }),
            wt.current.router && "/Search/:keyword" === wt.current.router.match.path && et.current.blur(),
            a && _(e),
            wt.current.router && "/Search/:keyword" === wt.current.router.match.path && !o.isModalVideo)
              h(e, n, l);
            else {
              var d = _t() || "search_result"
                , m = (0,
                H.Z)({
                source: n,
                aid: l,
                enter_from: d,
                focus_method: wt.current.focusMethod
              }, ye.U());
              wt.current.curVideoGroupId && (m.gid = wt.current.curVideoGroupId),
              t && t(),
                Ke(e, m, tt.current, i)
            }
          }
        }
      ), [t])
        , kt = (0,
        s.useCallback)((function() {
          if (we.p())
            return !1;
          if (!_e.T())
            return !1;
          if (o.isModalVideo)
            return !1;
          if (o.isSearchPage)
            return !1;
          if (!ge.yW())
            return !1;
          var e = ge.yW();
          return !!$()(O).call(O, e)
        }
      ), [o.isModalVideo, o.isSearchPage])
        , xt = je({
        idle: 0,
        middle_page: Fe.length + Ce.length,
        sug: T.sugList.length
      }[z], wt.current.isPinyin, et.current, z, n, V, W)
        , bt = xt.keyboardNavIndex
        , Ct = xt.restKeyboardNavIndex
        , Nt = mt(n, o, Me, _t, wt, Ie)
        , Tt = Nt.insideWordList
        , Zt = Nt.updateInsideWord
        , St = Nt.showInsideWord
        , It = Nt.hideInsideWord
        , Lt = Nt.isInsideWordShow
        , Dt = vt(n, o, wt, _t, nt, Et, kt)
        , Mt = Dt.bottomWordList
        , Bt = (Dt.updateBottomWords,
        Dt.onBottomWordClick)
        , At = Dt.showBottomWords
        , Pt = Dt.bottomWordLogIdRef
        , Ot = ht(nt, f.keyword, n, o, Et)
        , Vt = Ot.bottomWords
        , Wt = Ot.onBottomWordClick;
      (0,
        s.useEffect)((function() {
          o.isModalVideo || (D(f.keyword),
            W(f.keyword),
            Ct())
        }
      ), [null == c ? void 0 : c.match, o.isModalVideo]),
        (0,
          s.useEffect)((function() {
            if (null !== bt) {
              if ("middle_page" === wt.current.suggestionState) {
                var e, t = N()(e = []).call(e, (0,
                  U.Z)(Fe), (0,
                  U.Z)(Ce));
                W(t[bt].word)
              }
              "sug" === wt.current.suggestionState && W(wt.current.sug.sugList[bt])
            }
          }
        ), [n, bt, Fe, Ce]),
        (0,
          s.useEffect)((function() {
            wt.current.isFirefox = /firefox/i.test(navigator.userAgent)
          }
        ), []);
      var Rt = (0,
        s.useCallback)((0,
        G.Z)(le().mark((function e() {
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      he.h.getVar({
                        name: "search_result_list_type",
                        defaultValue: d.SearchResultListType.Default
                      });
                  case 2:
                    return e.next = 4,
                      he.h.getVar({
                        name: "search_page_ssr",
                        defaultValue: d.SearchPageSSRABVal.Off
                      });
                  case 4:
                    return e.next = 6,
                      he.h.getVar({
                        name: "search_layout",
                        defaultValue: d.SearchLayout.Default
                      });
                  case 6:
                    return e.next = 8,
                      he.h.getVar({
                        name: "search_horizontal",
                        defaultValue: d.SearchHorizontal.Default
                      });
                  case 8:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      ))), []);
      (0,
        s.useEffect)((function() {
          Rt()
        }
      ), [Rt]);
      var Ft = (0,
        s.useCallback)((function() {
          var e;
          wt.current.guessText && (It(),
            Ie(""),
            Be(!0),
            wt.current.hasGuessTextShown = !0,
            u("guessWordShow", {
              impr_id: wt.current.searchBarWordLogId,
              enter_from: _t(),
              words_num: "1",
              words_position: 0,
              words_source: "search_bar_inner",
              words_content: null === (e = wt.current.guessText) || void 0 === e ? void 0 : e.word,
              group_id: wt.current.guessTextId
            }))
        }
      ), [u, _t, It])
        , Ut = (0,
        s.useCallback)((function() {
          var e;
          Me && (Ie((null === (e = wt.current.guessText) || void 0 === e ? void 0 : e.word) || A),
            Be(!1))
        }
      ), [Me])
        , Ht = (0,
        s.useCallback)(function() {
        var e = (0,
          G.Z)(le().mark((function e(t) {
            var n, r, i;
            return le().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return r = it ? ct : at,
                        wt.current.suggestWordsPreloadList[wt.current.curVideoGroupId] ? n = wt.current.suggestWordsPreloadList[wt.current.curVideoGroupId] : (n = r((0,
                          H.Z)({
                          from_group_id: wt.current.curVideoGroupId
                        }, t), {
                          isModalVideo: null == o ? void 0 : o.isModalVideo
                        }),
                          wt.current.suggestWordsPreloadList[wt.current.curVideoGroupId] = n),
                        e.next = 4,
                        n;
                    case 4:
                      return i = e.sent,
                        wt.current.searchBarWordLogId = i.logId,
                        Pt.current = i.logId,
                        e.abrupt("return", i.data);
                    case 8:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), [o, it, Pt])
        , Gt = (0,
        s.useCallback)(q()((function(e, t) {
          var n = it ? ct : at;
          wt.current.suggestWordsPreloadList[t.groupId] || (wt.current.suggestWordsPreloadList = (0,
            H.Z)((0,
            H.Z)({}, wt.current.suggestWordsPreloadList), {}, (0,
            r.Z)({}, t.groupId, n((0,
            H.Z)({
            from_group_id: t.groupId
          }, e), {
            isModalVideo: null == o ? void 0 : o.isModalVideo
          }))))
        }
      ), 500, {
        leading: !1
      }), [o, it])
        , jt = (0,
        s.useCallback)(function() {
        var e = (0,
          G.Z)(le().mark((function e(t) {
            var n, r, o;
            return le().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return r = {
                        count: ot,
                        query: null === (n = wt.current.guessText) || void 0 === n ? void 0 : n.word
                      },
                      t && (r.penetrate_params = (0,
                        H.Z)((0,
                        H.Z)({}, r.penetrate_params), {}, {
                        is_manual_change: t
                      })),
                      Mt.length > 0 && (r.penetrate_params = (0,
                        H.Z)((0,
                        H.Z)({}, r.penetrate_params), {}, {
                        pre_query_ids: i()(Mt).call(Mt, (function(e) {
                            return e.id
                          }
                        )).join(",")
                      })),
                        e.next = 5,
                        lt((0,
                          H.Z)({
                          from_group_id: wt.current.curVideoGroupId
                        }, r));
                    case 5:
                      return o = e.sent,
                        wt.current.guessListLogId = o.logId,
                        e.abrupt("return", o.data.barWords.words);
                    case 8:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), [Mt, ot])
        , Kt = (0,
        s.useCallback)((function(e) {
          wt.current.guessText = e,
            wt.current.guessTextId = null == e ? void 0 : e.id,
            Ve(e)
        }
      ), [])
        , qt = (0,
        s.useCallback)(function() {
        var e = (0,
          G.Z)(le().mark((function e(t) {
            var r, o, i, a, s, c;
            return le().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return e.next = 2,
                        jt(t);
                    case 2:
                      if (r = e.sent,
                        !(te()(r) && r.length > 0)) {
                        e.next = 14;
                        break
                      }
                      if (Ue(l()(r).call(r, 0, ot)),
                        wt.current.guessList = l()(r).call(r, 0, ot),
                      !kt() || n.searchBarBottomWord !== d.searchBarBottomWord.Inside) {
                        e.next = 14;
                        break
                      }
                      if (o = et.current) {
                        e.next = 10;
                        break
                      }
                      return e.abrupt("return");
                    case 10:
                      i = o.clientWidth - re()(getComputedStyle(o).paddingLeft) - re()(getComputedStyle(o).paddingRight),
                        a = Ee.y(r, i, "inside"),
                        s = a.displayableNum,
                        c = l()(r).call(r, 0, Math.min(s, 3)),
                        Zt(c);
                    case 14:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), [jt, n.searchBarBottomWord, kt, Zt, ot])
        , Yt = (0,
        s.useCallback)((0,
        G.Z)(le().mark((function e() {
          var t, n, r, o, a, s, c, u, d;
          return le().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    if (!wt.current.hasHotListFetched) {
                      e.next = 2;
                      break
                    }
                    return e.abrupt("return");
                  case 2:
                    return e.prev = 2,
                      wt.current.hasHotListFetched = !0,
                      e.next = 6,
                      ut({});
                  case 6:
                    t = e.sent,
                      n = t.statusCode,
                      r = t.data,
                      o = void 0 === r ? {} : r,
                      a = t.log_pb,
                      s = o.word_list,
                      c = void 0 === s ? [] : s,
                    !n && c.length > 0 && (d = i()(u = l()(c).call(c, 0, 6)).call(u, (function(e) {
                        return {
                          word: e.word,
                          word_type: e.word_type,
                          position: e.position,
                          group_id: e.group_id || ""
                        }
                      }
                    )),
                      wt.current.hotListLogId = null == a ? void 0 : a.impr_id,
                      Ne(d)),
                      e.next = 18;
                    break;
                  case 15:
                    e.prev = 15,
                      e.t0 = e.catch(2),
                      wt.current.hasHotListFetched = !1;
                  case 18:
                  case "end":
                    return e.stop()
                }
            }
          ), e, null, [[2, 15]])
        }
      ))), []);
      (0,
        s.useEffect)((function() {
          var e = m.listen(m.EVENT.postCurVideoInfo, (function(e) {
              if ((o.isModalVideo || "modal" !== e.scene) && (!o.isModalVideo || "modal" === e.scene))
                if (n.searchBarBottomWord !== d.searchBarBottomWord.Inside || !1 !== wt.current.hasInsideWordShown) {
                  var t = e.existedSuggestWords
                    , r = Ye(void 0 === t ? [] : t);
                  null != e && e.preload ? Gt({
                    penetrate_params: {
                      inbox_exist_word_id: r
                    }
                  }, e) : (wt.current.curVideoGroupId = e.groupId || "",
                    wt.current.feedBarIds = r,
                    Ht({
                      penetrate_params: {
                        inbox_exist_word_id: r
                      }
                    }).then((function(e) {
                        var t = e.barWords
                          , r = e.bottomWords
                          , o = e.underboxMore
                          , i = t.words[0]
                          , a = Je(r.words, o.words, wt.current.underInboxMoreCursor);
                        if (n.bottomWordOpt === d.BottomWordOpt.BarWordPrior) {
                          var s = Qe(i, a, "inbox");
                          i = s.dedupedInboxWords,
                            a = s.dedupedUnderboxWords
                        }
                        if (n.bottomWordOpt === d.BottomWordOpt.BottomWordPrior) {
                          var c = 999;
                          if (a.length > 0)
                            c = At(a, r.words.length).displayableNum;
                          var u = Qe(i, l()(a).call(a, 0, c), "underbox");
                          i = u.dedupedInboxWords,
                            a = u.dedupedUnderboxWords
                        }
                        Kt(i),
                        wt.current.inputFocus || (wt.current.guessText ? (D(""),
                          W(""),
                          Ft()) : Ut(),
                        it && a.length > 0 && n.bottomWordOpt !== d.BottomWordOpt.BottomWordPrior && At(a, r.words.length))
                      }
                    )).catch((function() {
                        return Ut()
                      }
                    )))
                } else
                  wt.current.hasInsideWordShown = !0
            }
          ));
          return function() {
            null == e || e()
          }
        }
      ), [n, o.isModalVideo, Kt, Ft, Ut, Gt, it, Ht, At]);
      var Xt = (0,
        s.useCallback)((function(e) {
          e.preventDefault(),
            wt.current.pressDownTime = performance.now()
        }
      ), [])
        , zt = (0,
        s.useCallback)((function() {
          D(""),
            W(""),
            Ct(),
            u("clearButtonClick", {
              enter_from: _t()
            })
        }
      ), [Ct, u])
        , Qt = (0,
        s.useCallback)((function(e) {
          var t, n, r, o;
          if (!V && wt.current.guessText)
            return Et(null === (n = wt.current.guessText) || void 0 === n ? void 0 : n.word, "search_bar_inner", "", !1, !0),
              void u("guessWordClick", {
                enter_from: _t(),
                impr_id: wt.current.searchBarWordLogId,
                words_content: null === (r = wt.current.guessText) || void 0 === r ? void 0 : r.word,
                words_num: "1",
                words_position: 0,
                words_source: "search_bar_inner",
                group_id: wt.current.guessTextId
              });
          Lt && Tt.length > 0 && (Et(Tt[0].word, "search_bar_inner", "", !1, !0),
            qt(),
            u("guessWordClick", {
              enter_from: _t(),
              impr_id: wt.current.guessListLogId,
              words_content: Tt[0].word,
              words_num: String(Tt.length),
              words_position: 0,
              words_source: "search_bar_inner",
              group_id: null === (o = Tt[0]) || void 0 === o ? void 0 : o.id
            }));
          Et(wt.current.showText || wt.current.hotSearchKeyword, "normal_search", N()(t = "".concat(null == e ? void 0 : e.pageX, ",")).call(t, null == e ? void 0 : e.pageY))
        }
      ), [Et, Se, V])
        , Jt = (0,
        s.useCallback)((function(e) {
          var t = ke.C(e);
          if ("ArrowUp" !== t && "ArrowDown" !== t || e.preventDefault(),
          "Enter" === t && !wt.current.isPinyin) {
            var n, r = wt.current.showText;
            if (r && wt.current.isFirefox || e.preventDefault(),
            !V && wt.current.guessText)
              return void Et(null === (n = wt.current.guessText) || void 0 === n ? void 0 : n.word, "search_bar_inner", "", !0, !0);
            if (null === bt)
              Et(r, "normal_search", "-2,-2", !0);
            else if ("sug" === wt.current.suggestionState)
              Et(r, "search_sug", "-1,-1"),
                u("sugClick", {
                  impr_id: wt.current.response.log_pb.impr_id,
                  search_keyword: r,
                  search_type: wt.current.tab,
                  sug_keyword: r
                }),
                u("trendingWordsClick", {
                  impr_id: wt.current.response.log_pb.impr_id,
                  words_position: bt,
                  words_content: r,
                  raw_query: r,
                  rank: bt + 1,
                  search_position: wt.current.tab,
                  query_id: wt.current.response.words_query_record.query_id,
                  group_id: wt.current.response.sug_list[bt].word_record.group_id
                });
            else if ("middle_page" === wt.current.suggestionState && (Fe.length > 0 || Ce.length > 0)) {
              var o, i;
              if (bt < Fe.length)
                Et(r, "recom_search", "-2,-2", !0, !0),
                  u("guessWordClick", {
                    impr_id: wt.current.guessListLogId,
                    enter_from: _t(),
                    words_num: String(Fe.length),
                    words_position: bt,
                    words_content: r,
                    group_id: (null === (o = Fe[bt]) || void 0 === o ? void 0 : o.id) || ""
                  });
              else
                Et(r, "hot_search_board", "-2,-2", !0, !1),
                  u("hotWordClick", {
                    impr_id: wt.current.hotListLogId,
                    enter_from: _t(),
                    words_num: String(Ce.length),
                    words_position: bt,
                    words_content: r,
                    group_id: (null === (i = Ce[bt - Fe.length]) || void 0 === i ? void 0 : i.group_id) || ""
                  })
            }
          }
        }
      ), [Et, bt, Fe, Ce, Se, u, V])
        , $t = (0,
        s.useCallback)((function(e) {
          var t = e.currentTarget.dataset
            , n = t.text
            , r = t.index;
          Et(n, "search_history", "-1,-1"),
            u("historyClick", {
              enter_from: _t(),
              words_num: String(g && g.length > 0 && Math.min(g.length, M) || 0),
              words_position: r,
              words_content: n
            })
        }
      ), [Et])
        , en = (0,
        s.useCallback)((function(e) {
          var t = e.currentTarget.dataset.text;
          Et(t, "search_cny_word", "-1,-1"),
            u("trendingWordsClick", {
              words_content: x
            })
        }
      ), [Et])
        , tn = (0,
        s.useCallback)((function(e) {
          var t = Number(e.currentTarget.dataset.index)
            , n = wt.current.sug.sugList[t];
          Et(n, "search_sug", "-1,-1"),
            u("sugClick", {
              impr_id: wt.current.response.log_pb.impr_id,
              search_keyword: wt.current.inputText,
              search_type: wt.current.tab,
              sug_keyword: n
            }),
            u("trendingWordsClick", {
              impr_id: wt.current.response.log_pb.impr_id,
              words_position: t,
              words_content: n,
              raw_query: wt.current.inputText,
              rank: -1,
              search_position: wt.current.tab,
              query_id: wt.current.response.words_query_record.query_id,
              group_id: wt.current.response.sug_list[t].word_record.group_id
            })
        }
      ), [Et]);
      (0,
        s.useEffect)((function() {
          oe && !L && (Boolean(null == g ? void 0 : g.length) || Boolean(null == Ce ? void 0 : Ce.length) || Boolean(null == Fe ? void 0 : Fe.length)) ? J("middle_page") : oe && Boolean(L) && Boolean(T.sugList.length) ? J("sug") : J("idle")
        }
      ), [oe, g, T, L, Ce, Fe]),
        (0,
          s.useEffect)((function() {
            if (oe && null === bt && (!T.sugList.length || T.query !== L)) {
              var e = performance.now();
              dt({
                keyword: L,
                source: "aweme_video_web",
                from_group_id: wt.current.curVideoGroupId
              }).then((function(t) {
                  var n, r, o = wt.current.tab;
                  wt.current.response = t;
                  var a = t.log_pb.impr_id
                    , l = t.extra.logId
                    , s = t.words_query_record.query_id
                    , c = (null === (n = t.sug_list) || void 0 === n ? void 0 : n.length) || 0
                    , d = performance.now();
                  rt.current[L] = {
                    sugStartTime: e,
                    sugFetchTime: d,
                    impr_id: a,
                    words_num: c,
                    search_type: o,
                    sug_keyword: L
                  },
                    u("sugShow", {
                      impr_id: a,
                      search_keyword: L,
                      search_type: o,
                      sug_keyword: L
                    }),
                    u("trendingShow", {
                      log_pb: t.log_pb,
                      impr_id: a,
                      search_id: l,
                      words_num: c,
                      raw_query: L,
                      search_position: o
                    }),
                    Z({
                      sugList: null == t ? void 0 : i()(r = t.sug_list).call(r, (function(e, t) {
                          return u("trendingWordsShow", {
                            impr_id: a,
                            search_id: l,
                            words_position: t,
                            words_content: e.content,
                            raw_query: L,
                            rank: -1,
                            search_position: o,
                            query_id: s,
                            group_id: e.word_record.group_id
                          }),
                            e.content
                        }
                      )),
                      query: L
                    })
                }
              )).catch((function() {
                  Z({
                    sugList: [],
                    query: L
                  })
                }
              ))
            }
          }
        ), [oe, L, bt]),
        (0,
          s.useEffect)((function() {
            if (T.query) {
              var e = performance.now()
                , t = rt.current[T.query] || {}
                , n = t.sugStartTime
                , r = t.sugFetchTime
                , o = (0,
                F.Z)(t, pt);
              u("searchSugLoadPerformance", (0,
                H.Z)((0,
                H.Z)({}, o), {}, {
                sug_fetch_duration: r - n,
                sug_render_duration: e - r,
                enter_from: _t()
              })),
                delete rt.current[T.query]
            }
          }
        ), [T]);
      var nn = (0,
        s.useCallback)((function() {
          y()
        }
      ), [])
        , rn = (0,
        s.useCallback)((function(e) {
          var t = e.target.value;
          D(t),
            W(t),
            Ct()
        }
      ), [])
        , on = (0,
        s.useCallback)((function(e) {
          e.stopPropagation();
          var t = e.currentTarget.dataset.text;
          w(t)
        }
      ), [])
        , an = (0,
        s.useCallback)((function(e) {
          e.stopPropagation();
          var t = e.currentTarget.dataset.text;
          D(t),
            W(t),
            Ct()
        }
      ), [])
        , ln = (0,
        s.useCallback)((function() {
          u("enterSearch", {
            enter_from: _t(),
            enter_from_second: _t(),
            click_method: wt.current.focusMethod
          }),
            wt.current.focusTime = performance.now(),
            wt.current.inputFocus = !0,
            Yt(),
            Ut(),
            It(),
            n.searchBarBottomWord === d.searchBarBottomWord.Inside && kt() ? wt.current.hasGuessTextShown && qt() : qt(),
            ae(!0),
            m.emit(m.EVENT.videoStopPlayNext),
            m.emit(m.EVENT.searchBarFocus)
        }
      ), [u, Ut, qt, It, _t, n.searchBarBottomWord, kt, Yt])
        , sn = (0,
        s.useCallback)((function() {
          wt.current.inputFocus = !1,
          n.searchBarBottomWord === d.searchBarBottomWord.Inside && kt() && !wt.current.hasGuessTextShown && !wt.current.showText && qt().then((function() {
              !wt.current.hasGuessTextShown && !wt.current.guessText && wt.current.guessList.length > 0 && St()
            }
          )),
            wt.current.guessText ? Ft() : Ut(),
            wt.current.focusMethod = "",
            ae(!1),
            Ct(),
            m.emit(m.EVENT.videoRemoveStopPlayNext),
            m.emit(m.EVENT.searchBarBlur)
        }
      ), [Ft, Ut, Ct, St, qt, n.searchBarBottomWord, kt])
        , cn = (0,
        s.useCallback)((function() {
          wt.current.isPinyin = !0
        }
      ), [])
        , un = (0,
        s.useCallback)((function() {
          wt.current.isPinyin = !1
        }
      ), [])
        , dn = (0,
        s.useCallback)((function(e) {
          var t, n = e.currentTarget.dataset, r = n.text, o = n.index;
          r && (Et(r, "hot_search_board", "", !1, !1),
            u("hotWordClick", {
              impr_id: wt.current.hotListLogId,
              enter_from: _t(),
              words_num: String((null == Ce ? void 0 : Ce.length) || 0),
              words_position: o,
              words_content: r,
              group_id: (null == Ce || null === (t = Ce[o]) || void 0 === t ? void 0 : t.group_id) || ""
            }))
        }
      ), [Et])
        , mn = (0,
        s.useCallback)((function(e) {
          var t, n = e.currentTarget.dataset, r = n.text, o = n.index;
          r && (Et(r, "recom_search", "", !1, !0),
            u("guessWordClick", {
              impr_id: wt.current.guessListLogId,
              enter_from: _t(),
              words_num: String(Fe.length || 0),
              words_position: Number(o),
              words_content: r,
              group_id: (null === (t = Fe[Number(o)]) || void 0 === t ? void 0 : t.id) || ""
            }))
        }
      ), [Et, u, Fe])
        , vn = (0,
        pe.x)((function() {
          u("trendingWordsShow", {
            words_content: x
          })
        }
      ))
        , fn = (0,
        pe.x)((function() {
          ie()(g).call(g, (function(e, t) {
              u("historyShow", {
                enter_from: _t(),
                words_num: String(g && g.length > 0 && Math.min(g.length, M) || 0),
                words_position: t,
                words_content: e
              })
            }
          ))
        }
      ))
        , hn = (0,
        pe.x)((function() {
          ie()(Ce).call(Ce, (function(e, t) {
              var n;
              u("hotWordShow", {
                impr_id: wt.current.hotListLogId,
                enter_from: _t(),
                words_num: String((null == Ce ? void 0 : Ce.length) || 0),
                words_position: t,
                words_content: e.word,
                group_id: (null == Ce || null === (n = Ce[t]) || void 0 === n ? void 0 : n.group_id) || ""
              })
            }
          ))
        }
      ))
        , pn = (0,
        pe.x)((function() {
          ie()(Fe).call(Fe, (function(e, t) {
              u("guessWordShow", {
                impr_id: wt.current.guessListLogId,
                enter_from: _t(),
                words_num: String(Fe.length || 0),
                words_position: t,
                words_content: e.word,
                group_id: e.id
              })
            }
          ))
        }
      ));
      (0,
        s.useEffect)((function() {
          var e = m.listen(m.EVENT.focusSearch, (function(e) {
              var t, n = null === (t = xe.Le.getConfig(xe.gI.IsInModalVideo)) || void 0 === t ? void 0 : t.isInModal;
              if (!(!o.isModalVideo && n || o.isModalVideo && !n)) {
                var r = null == e ? void 0 : e.isFocus;
                wt.current.guessText ? (wt.current.focusMethod = "hot_key",
                r && Qt(),
                  wt.current.focusMethod = "") : X()((function() {
                    r ? (wt.current.focusMethod = "hot_key",
                      et.current.focus()) : et.current.blur()
                  }
                ), 50)
              }
            }
          ));
          return function() {
            null == e || e()
          }
        }
      ), [Qt, ln, sn, o.isModalVideo]),
        (0,
          s.useEffect)((function() {
            be.H(Yt)
          }
        ), []),
        (0,
          s.useEffect)((function() {
            kt() && n.searchBarBottomWord === d.searchBarBottomWord.Inside && qt().then((function() {
                !wt.current.inputFocus && wt.current.guessList.length > 0 && St()
              }
            ))
          }
        ), [o.isModalVideo, o.isSearchPage, n, kt]),
        (0,
          s.useEffect)((function() {
            Kt(null),
              Ut()
          }
        ), [null == o ? void 0 : o.pathname]);
      var gn = (0,
        s.useCallback)((function() {
          yt((function() {
              return X()((function() {
                  qt(),
                    Yt(),
                    ae(!0),
                    m.emit(m.EVENT.videoStopPlayNext),
                    m.emit(m.EVENT.searchBarFocus)
                }
              ), 500)
            }
          ))
        }
      ), [qt, Yt])
        , yn = (0,
        s.useCallback)((function() {
          clearTimeout(gt),
            ae(!1),
            m.emit(m.EVENT.videoRemoveStopPlayNext),
            m.emit(m.EVENT.searchBarBlur)
        }
      ), [gt]);
      return {
        history: g,
        showText: V,
        hotSearchText: k,
        hotSearchKeyword: x,
        hotList: Ce,
        suggestionState: z,
        onFocus: ln,
        inputFocus: oe,
        onBlur: sn,
        onInputChange: rn,
        onSearchClick: Qt,
        onInputKeyDown: Jt,
        clearHistory: nn,
        onHistoryClick: $t,
        onHotWordClick: en,
        onSugClick: tn,
        onDeleteHistoryItem: on,
        sug: T,
        setInputText: D,
        onSetSug: an,
        preventDefault: Ge,
        onMouseDown: Xt,
        searchBarRef: nt,
        inputRef: et,
        formRef: tt,
        hotWordRef: vn,
        historyRef: fn,
        hotListRef: hn,
        guessListRef: pn,
        onCompositionStart: cn,
        onCompositionEnd: un,
        keyboardNavIndex: bt,
        onHotListWordClick: dn,
        onGuessListWordClick: mn,
        onInputClearButtonClick: zt,
        placeHolder: Se,
        isGuessTextShow: Me,
        guessText: Oe,
        guessList: Fe,
        bottomWordList: Mt,
        onBottomWordClick: Bt,
        isButtonHover: ze,
        setButtonHover: $e,
        insideWordList: Tt,
        isInsideWordShow: Lt,
        updateGuessList: qt,
        onMouseEnter: gn,
        onMouseLeave: yn,
        relatedWordList: Vt,
        onRelatedWordClick: Wt
      }
    }
    const yt = {
      hotView: "ECfNAnuN",
      searchBarContainer: "AFTy15pW",
      searchBar: "lPytbapz",
      activity: "QkLBoTmY",
      vsTransMode: "DcMccBwQ",
      searchBarGuessText: "eV6rINZw",
      transparent: "nihbySfV",
      inputClearButton: "rb7mtFl_",
      iconClose: "gMkV3yx8",
      input: "igFQqPKs",
      borderInput: "XClSex3D",
      button: "rB8dMXOc",
      buttonIcon: "FhOy97Hs",
      newMildInput: "sNMIp2gi",
      newAggresiveInput: "YSGlPSkR",
      modalSearchBar: "NBmn3s18",
      modalSearchBarIdle: "mnN5bEWt",
      searchIcon: "T9sNU2wZ",
      searchBarInputForm: "zyznJl4l",
      inputLanternIcon: "yLUSLRPP",
      searchBarHotIcon: "HtoEiInk",
      searchBarGuessTextWrapper: "rQK5s_5G",
      isActivity: "FZyRCCRa",
      activityIcon: "u8BJEVLC",
      searchBarInsideWord: "QEnWATW0",
      blur: "qYYUxsS2",
      hotInput: "zwPQYqPg",
      inputWithClearButton: "LfNI_GvG",
      borderInputSpec: "yKzPCGu9",
      suggestionContainer: "bMNdUnXg",
      suggestion: "qdBdEa5M",
      grayscale: "UIy2gpGc",
      hotLine: "SYsqE8WM",
      sugLanternIcon: "LlJUvkns",
      hotText: "c7ds0Iod",
      sugArrowRightIcon: "BLrmVLv5",
      titleView: "Bn9halsY",
      titleViewText: "RJ3jOaxm",
      hotBoardTitleViewText: "Ict4f2gg",
      refreshButtonView: "Y8iOISUm",
      refreshButtonText: "fBqC2_4f",
      suggestionItem: "mAxh4Myr",
      keyboardSelected: "QWsKM5ZL",
      suggestionItemContext: "zc76CbGr",
      queryMatch: "xjGxZvQd",
      queryMatchWeak: "vVcX3F4m",
      svgHover: "MqBTFh3s",
      guessListDouble: "qVKaKr1k",
      guessListItemWrapper: "lZVDVDUI",
      itemLeft: "WaH4na5z",
      itemRight: "ROQco5Dk",
      guessListItem: "c83o2HHV",
      guessListItemBg: "GlBGbioI",
      hotListItem: "_DBUEsrN",
      hotListItemBg: "DLMGiHDU",
      hotListItemWithNum: "_FLhmVcE",
      hotListItemText: "sib6lYLr",
      guessListItemText: "r4GRlgqE",
      guessListItemTextHighlight: "aZU1HeCW",
      guessListItemTextBold: "_X5zdgfz",
      hotListItemIcon: "SjOHS8N1",
      hotListItemNumberIcon: "EPnNp3c0",
      guessListItemIcon: "dgH2Pao8",
      guessListItemIconHot: "jHBrjtT1",
      guessListItemIconLive: "B2CLKUW6",
      bottomWord: "Lo8QPz5R"
    };
    var wt = n(92887)
      , _t = n(58778)
      , Et = n(39370);
    const kt = "G1wNaptA"
      , xt = "Hwa4NdpH"
      , bt = "nCWuTGbt"
      , Ct = "Gzyl1zZ2"
      , Nt = "oODOqrsZ"
      , Tt = "xVVBuUHj"
      , Zt = "yt2kqmdu"
      , St = "eo3_cSOv"
      , It = "Y2_zgfIU"
      , Lt = "ZFs_o_xH"
      , Dt = "ivS2xlnF";
    var Mt = n(52255)
      , Bt = (0,
      s.forwardRef)((function(e, t) {
        var n, o, a = e.history, c = e.onHistoryItemClick, d = e.customProps, m = e.onDeleteHistoryItem, v = e.limit, f = e.clearHistory, h = (0,
          s.useState)(v), p = (0,
          j.Z)(h, 2), g = p[0], y = p[1], w = (0,
          s.useState)(!1), _ = (0,
          j.Z)(w, 2), E = _[0], k = _[1], x = (o = (0,
          s.useMemo)((function() {
            return (0,
              de.y$)(R)
          }
        ), []),
          {
            buttonRef: (0,
              pe.x)((function() {
                return o("historyFoldButtonShow")
              }
            )),
            onButtonClick: (0,
              s.useCallback)((function() {
                return o("historyFoldButtonClick")
              }
            ), [o])
          }), b = x.buttonRef, C = x.onButtonClick, N = (0,
          s.useCallback)((function() {
            C(),
              k(!1),
              y(v)
          }
        ), [k, y, C, v]), T = (0,
          s.useCallback)((function() {
            for (var e, n, r = Se()((null == t || null === (e = t.current) || void 0 === e ? void 0 : e.children) || []), o = (null == t || null === (n = t.current) || void 0 === n ? void 0 : n.offsetWidth) || 0, i = 56, a = 0; a < r.length; a++) {
              var l = r[a];
              if (null == l || !l.offsetTop)
                break;
              if (0 !== a) {
                if (l.offsetTop === i + 64) {
                  var s = o - r[a - 1].offsetWidth + r[a - 1].offsetLeft;
                  y(s >= 22 ? a - 1 : a - 2),
                    k(!0);
                  break
                }
              } else
                i = l.offsetTop
            }
          }
        ), [t]);
        return (0,
          s.useEffect)((function() {
            return T(),
              window.addEventListener("resize", (function() {
                  return T()
                }
              )),
              window.removeEventListener("resize", (function() {
                  return T()
                }
              ))
          }
        ), [T]),
          s.createElement(s.Fragment, null, s.createElement("div", {
            className: kt
          }, s.createElement("span", {
            className: xt
          }, "\u5386\u53f2\u8bb0\u5f55"), s.createElement("div", {
            className: bt,
            onClick: f
          }, s.createElement(Mt.Z, {
            src: globalThis.getFilterXss().filterUrl(Et.Z, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            width: 14,
            height: 14,
            viewBox: "0 0 14 14"
          }), s.createElement("span", {
            className: Ct
          }, "\u6e05\u9664\u8bb0\u5f55"))), s.createElement("div", {
            className: Nt,
            ref: t,
            "data-e2e": "search-history-container"
          }, i()(n = l()(a).call(a, 0, g)).call(n, (function(e, t) {
              return s.createElement("div", {
                "data-text": e,
                "data-index": t,
                onClick: c,
                className: u()(Tt, (0,
                  r.Z)({}, Zt, null == d ? void 0 : d.isModalVideo)),
                key: e
              }, s.createElement("span", {
                className: Lt
              }, e), s.createElement("div", {
                className: St,
                "data-text": e,
                onClick: m
              }, s.createElement(Mt.Z, {
                src: globalThis.getFilterXss().filterUrl(wt.Z, null, {
                  logType: "js.href/src",
                  reportOnly: !1
                }),
                className: It,
                width: 14,
                height: 14,
                viewBox: "0 0 12 12"
              })))
            }
          )), E && s.createElement("div", {
            ref: b,
            onClick: N,
            className: Dt,
            style: {
              width: 22
            }
          }, s.createElement(Mt.Z, {
            src: globalThis.getFilterXss().filterUrl(_t.Z, null, {
              logType: "js.href/src",
              reportOnly: !1
            }),
            width: 12,
            height: 12,
            viewBox: "0 0 12 12"
          }))))
      }
    ))
      , At = function(e) {
      var t, n = e.words, r = e.query, o = e.matchClass, a = i()(t = n === r ? [""] : n.split(r)).call(t, (function(e, t) {
          return "" === e ? s.createElement("span", {
            key: t,
            className: o
          }, r) : e
        }
      ));
      return s.createElement("span", {
        className: yt.suggestionItemContext
      }, a)
    }
      , Pt = function(e) {
      var t, n, o, a, c, C, N, T = e.abTestData, Z = void 0 === T ? {} : T, I = e.userInfo, L = e.onSearchClick, B = e.onHistoryClick, A = e.onInputKeyDown, P = e.customProps, O = void 0 === P ? {} : P, V = [y.Z, w.Z, _.Z, E.Z, k.Z, x.Z, b.Z], W = function() {
        var e = (0,
          s.useState)(!1)
          , t = (0,
          j.Z)(e, 2)
          , n = t[0]
          , r = t[1];
        return (0,
          s.useEffect)((function() {
            (0,
              G.Z)(le().mark((function e() {
                var t;
                return le().wrap((function(e) {
                    for (; ; )
                      switch (e.prev = e.next) {
                        case 0:
                          return e.next = 2,
                            se.U2({
                              key: ce.TccKey.SearchPanelGrayscale,
                              defaultValue: ce.TCC_DEFAULT_VALUE_MAP.get(ce.TccKey.SearchPanelGrayscale),
                              namespace: se.m_.SEARCH
                            });
                        case 2:
                          t = e.sent,
                            r(t.grayscale);
                        case 4:
                        case "end":
                          return e.stop()
                      }
                  }
                ), e)
              }
            )))()
          }
        ), []),
          n
      }(), F = gt(null == I || null === (t = I.info) || void 0 === t ? void 0 : t.secUid, (function() {
          m.emit(m.EVENT.videoPause)
        }
      ), Z, O), U = F.inputRef, H = F.formRef, K = F.hotWordRef, q = F.showText, Y = F.hotSearchText, X = F.hotSearchKeyword, z = F.hotList, Q = F.suggestionState, J = F.keyboardNavIndex, $ = F.onFocus, ee = F.inputFocus, te = F.onBlur, ne = F.onInputChange, re = F.onMouseDown, oe = F.onSearchClick, ie = F.onInputKeyDown, ae = F.clearHistory, ue = F.onHistoryClick, me = F.onHotWordClick, ve = F.onSugClick, fe = F.history, he = F.sug, ge = F.onSetSug, ye = F.onDeleteHistoryItem, we = F.preventDefault, _e = F.onCompositionStart, Ee = F.onCompositionEnd, ke = F.onHotListWordClick, xe = F.onGuessListWordClick, be = F.onInputClearButtonClick, Ce = F.placeHolder, Ne = F.historyRef, Te = F.hotListRef, Ze = F.guessListRef, Se = F.isGuessTextShow, Ie = F.guessText, Le = F.guessList, De = F.bottomWordList, Me = F.onBottomWordClick, Be = F.isButtonHover, Ae = F.setButtonHover, Pe = F.insideWordList, Oe = F.isInsideWordShow, Ve = F.searchBarRef, We = F.relatedWordList, Re = F.onRelatedWordClick, Fe = F.updateGuessList, Ue = F.onMouseEnter, He = F.onMouseLeave, Ge = (N = (0,
        s.useMemo)((function() {
          return (0,
            de.y$)(R)
        }
      ), []),
        {
          refreshButtonRef: (0,
            pe.x)((function() {
              return N("recomSearchChangeButtonShow")
            }
          )),
          onRefreshButtonClick: (0,
            s.useCallback)((function() {
              return N("recomSearchChangeButtonClick")
            }
          ), [N])
        }), je = Ge.refreshButtonRef, Ke = Ge.onRefreshButtonClick, qe = (0,
        s.useMemo)((function() {
          return (null == O || !O.isModalVideo) && Z.searchBarStyleOpt === d.SearchBarStyleOpt.Mild
        }
      ), [Z.searchBarStyleOpt, null == O ? void 0 : O.isModalVideo]), Ye = (0,
        s.useMemo)((function() {
          return (null == O || !O.isModalVideo) && Z.searchBarStyleOpt === d.SearchBarStyleOpt.Aggressive
        }
      ), [Z.searchBarStyleOpt, null == O ? void 0 : O.isModalVideo]), Xe = (0,
        s.useCallback)((function(e) {
          var t = U.current.value;
          L && L(t) && oe(e)
        }
      ), [oe]), ze = ((0,
        s.useCallback)((function(e) {
          B && B(e) && ue(e)
        }
      ), [ue]),
        (0,
          s.useCallback)((function(e) {
            e.stopPropagation();
            var t = U.current.value;
            A && A(e, t) && ie(e)
          }
        ), [ie]));
      return (0,
        s.useEffect)((function() {
          var e = m.listen(m.EVENT.closeSearchSelect, (function() {
              U.current.blur()
            }
          ));
          return function() {
            e()
          }
        }
      ), []),
        s.createElement("div", {
          className: yt.searchBarContainer,
          onMouseEnter: Z.enableHoverToDisplay ? Ue : function() {}
          ,
          onMouseLeave: Z.enableHoverToDisplay ? He : function() {}
        }, s.createElement("div", {
          ref: Ve,
          className: u()(yt.searchBar, (n = {},
            (0,
              r.Z)(n, yt.borderInput, !(qe || Ye)),
            (0,
              r.Z)(n, yt.modalSearchBar, null == O ? void 0 : O.isModalVideo),
            (0,
              r.Z)(n, yt.modalSearchBarIdle, (null == O ? void 0 : O.isModalVideo) && !ee),
            (0,
              r.Z)(n, yt.activity, (null == O ? void 0 : O.isActivity) || (null == O ? void 0 : O.transparent)),
            (0,
              r.Z)(n, null == yt ? void 0 : yt[null == O ? void 0 : O.activityName], null == O ? void 0 : O.activityName),
            (0,
              r.Z)(n, yt.borderInputSpec, null == O ? void 0 : O.themeSwitch),
            (0,
              r.Z)(n, yt.newMildInput, qe),
            (0,
              r.Z)(n, yt.newAggresiveInput, Ye),
            (0,
              r.Z)(n, yt.transparent, null == O ? void 0 : O.transparent),
            n))
        }, !ee && Y && s.createElement("div", {
          className: yt.inputLanternIcon
        }), s.createElement("form", {
          className: u()(yt.searchBarInputForm, {
            isLight: null == O ? void 0 : O.isActivity
          }),
          action: "",
          target: "_blank",
          ref: H
        }, !q && !Se && Pe.length > 0 && Oe && s.createElement("div", {
          className: yt.searchBarInsideWord
        }, s.createElement(D, {
          wordList: Pe,
          active: Be,
          customProps: O
        })), !q && Se && Ie && s.createElement("div", {
          className: yt.searchBarGuessTextWrapper
        }, Ie.icon_info && s.createElement("img", {
          src: globalThis.getFilterXss().filterUrl(Ie.icon_info.icon_url, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          className: yt.activityIcon,
          style: {
            width: Ie.icon_info.icon_width || 20,
            height: Ie.icon_info.icon_height || 20
          }
        }), s.createElement("div", {
          className: u()(yt.searchBarGuessText, (0,
            r.Z)({}, yt.isActivity, Ie.icon_info))
        }, Ie.word)), q && ee && s.createElement("div", {
          onClick: be,
          onMouseDown: we,
          className: yt.inputClearButton,
          "data-e2e": "clear-search"
        }, s.createElement(f.Z, {
          className: yt.iconClose
        })), s.createElement("input", {
          ref: U,
          value: q,
          onFocus: $,
          onBlur: te,
          onChange: ne,
          onKeyDown: ze,
          onCompositionStart: _e,
          onCompositionEnd: Ee,
          className: u()(yt.input, (o = {},
            (0,
              r.Z)(o, yt.blur, !ee && !O.isSearchPage),
            (0,
              r.Z)(o, yt.hotInput, !ee && Y),
            (0,
              r.Z)(o, yt.inputWithClearButton, ee && q),
            o)),
          "data-e2e": "searchbar-input",
          type: "text",
          maxLength: 100,
          placeholder: Y || Ce || ""
        }), s.createElement("input", {
          type: "submit",
          value: "Submit",
          style: {
            display: "none"
          }
        })), s.createElement("button", {
          className: u()(yt.button, {
            isLight: null == O ? void 0 : O.isActivity
          }),
          "data-e2e": "searchbar-button",
          type: "button",
          onMouseDown: re,
          onClick: Xe,
          onMouseEnter: function() {
            return Ae(!0)
          },
          onMouseLeave: function() {
            return Ae(!1)
          }
        }, s.createElement(v.Z, {
          className: yt.buttonIcon
        }), s.createElement("span", {
          className: "btn-title"
        }, "\u641c\u7d22")), "middle_page" === Q && s.createElement("div", {
          className: yt.suggestionContainer
        }, s.createElement("div", {
          className: u()(yt.suggestion, (0,
            r.Z)({}, yt.grayscale, W)),
          onMouseDown: we
        }, Y && s.createElement("div", {
          className: yt.hotView
        }, s.createElement("div", {
          ref: K,
          "data-text": X,
          onClick: me,
          className: yt.hotLine
        }, s.createElement("div", {
          className: yt.sugLanternIcon
        }), s.createElement("p", {
          className: u()(yt.hotText, yt.suggestionItemContext)
        }, Y), s.createElement(p.Z, {
          width: 6,
          height: 11,
          viewBox: "0 0 17 33",
          className: yt.sugArrowRightIcon
        }))), fe && fe.length > 0 && s.createElement(Bt, {
          ref: Ne,
          history: fe,
          onDeleteHistoryItem: ye,
          onHistoryItemClick: ue,
          clearHistory: ae,
          customProps: O,
          limit: M
        }), Le.length > 0 && s.createElement(s.Fragment, null, s.createElement("div", {
          className: yt.titleView
        }, s.createElement("span", {
          className: yt.titleViewText
        }, "\u731c\u4f60\u60f3\u641c"), s.createElement("div", {
          ref: je,
          className: yt.refreshButtonView,
          onClick: function() {
            Fe(!0),
              Ke()
          }
        }, s.createElement(Mt.Z, {
          src: globalThis.getFilterXss().filterUrl(g.Z, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 14,
          height: 14,
          viewBox: "0 0 14 14"
        }), s.createElement("span", {
          className: yt.refreshButtonText
        }, "\u6362\u4e00\u6362"))), s.createElement("div", {
          ref: Ze,
          className: yt.guessListDouble,
          "data-e2e": "search-guess-container"
        }, i()(Le).call(Le, (function(e, t) {
            var n, o, i, a = "2" === e.words_type, l = "10" === e.words_type, c = 0 === t && Ie && Ie.icon_info && e.word === Ie.word;
            return s.createElement("div", {
              key: e.word,
              className: yt.guessListItemWrapper
            }, s.createElement("div", {
              className: u()(yt.guessListItem, t % 2 == 0 ? yt.itemLeft : yt.itemRight, (n = {},
                (0,
                  r.Z)(n, yt.keyboardSelected, t === J),
                (0,
                  r.Z)(n, yt.guessListItemBg, Z.guessSearchHoverBg),
                n)),
              "data-text": e.word,
              "data-index": t,
              onClick: xe
            }, s.createElement("span", {
              className: u()(yt.guessListItemText, (o = {},
                (0,
                  r.Z)(o, yt.guessListItemTextHighlight, t < 2 && Z.guessSearchFirstRowHighlight),
                (0,
                  r.Z)(o, yt.guessListItemTextBold, t < 2 && Z.guessSearchFirstRowBold),
                o))
            }, e.word), (a || l) && s.createElement("div", {
              className: u()(yt.guessListItemIcon, (i = {},
                (0,
                  r.Z)(i, yt.guessListItemIconHot, a),
                (0,
                  r.Z)(i, yt.guessListItemIconLive, l),
                i))
            }), c && s.createElement("img", {
              src: globalThis.getFilterXss().filterUrl(Ie.icon_info.icon_url, null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              className: yt.guessListItemIcon,
              style: {
                width: Ie.icon_info.icon_width || 20,
                height: Ie.icon_info.icon_height || 20
              }
            })))
          }
        )))), z && z.length > 0 && s.createElement(s.Fragment, null, s.createElement("div", {
          className: yt.titleView
        }, s.createElement("span", {
          className: u()(yt.titleViewText, yt.hotBoardTitleViewText)
        }, "\u6296\u97f3\u70ed\u70b9")), s.createElement("div", {
          ref: Te,
          "data-e2e": "search-hot-container"
        }, i()(z).call(z, (function(e, t, n) {
            var o, i = 14 === n[0].word_type ? t : t + 1, a = Le.length + t;
            return s.createElement("div", {
              className: u()(yt.hotListItem, (o = {},
                (0,
                  r.Z)(o, yt.hotListItemWithNum, i >= 4),
                (0,
                  r.Z)(o, yt.keyboardSelected, a === J),
                (0,
                  r.Z)(o, yt.hotListItemBg, Z.guessSearchHoverBg),
                o)),
              key: e.word,
              "data-text": e.word,
              "data-index": t,
              onClick: ke
            }, s.createElement(Mt.Z, {
              className: u()(yt.hotListItemIcon, (0,
                r.Z)({}, yt.hotListItemNumberIcon, i >= 4)),
              src: globalThis.getFilterXss().filterUrl(V[i], null, {
                logType: "js.href/src",
                reportOnly: !1
              }),
              width: i < 4 ? 20 : 23,
              height: i < 4 ? 20 : 24,
              viewBox: i < 4 ? "0 0 20 20" : "0 0 23 24"
            }), s.createElement("span", {
              className: yt.hotListItemText
            }, e.word))
          }
        )))))), "sug" === Q && s.createElement("div", {
          className: yt.suggestionContainer
        }, s.createElement("div", {
          className: u()(yt.suggestion, (0,
            r.Z)({}, yt.grayscale, W)),
          onMouseDown: we
        }, i()(a = l()(c = he.sugList).call(c, 0, M)).call(a, (function(e, t) {
            return s.createElement("div", {
              "data-index": t,
              onClick: ve,
              className: u()(yt.suggestionItem, (0,
                r.Z)({}, yt.keyboardSelected, t === J)),
              key: e
            }, s.createElement(At, {
              words: e,
              query: he.query,
              matchClass: Z.sugHighlightPosition ? yt.queryMatchWeak : yt.queryMatch
            }), !Z.enableSearchBarShuffling && s.createElement("div", {
              className: "icon",
              "data-text": e,
              onClick: ge
            }, s.createElement(h.Z, {
              className: yt.svgHover
            })))
          }
        ))))), s.createElement("div", {
          className: u()(yt.bottomWord, (C = {},
            (0,
              r.Z)(C, yt.activity, null == O ? void 0 : O.isActivity),
            (0,
              r.Z)(C, null == yt ? void 0 : yt[null == O ? void 0 : O.activityName], null == O ? void 0 : O.activityName),
            C))
        }, null != O && O.isSearchPage && Z.relatedSearchList === d.RelatedSearchList.BottomWord ? s.createElement(S, {
          wordList: We,
          onBottomWordClick: Re,
          customProps: O
        }) : s.createElement(S, {
          wordList: De,
          onBottomWordClick: Me,
          customProps: O
        })))
    };
    const Ot = Pt
  }
  ,
  64956: (e,t,n)=>{
    n.d(t, {
      U: ()=>ue
    });
    var r = n(65146)
      , o = n(32781)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a)
      , s = n(52172)
      , c = n(72565)
      , u = n(81963)
      , d = n(92557)
      , m = n(14513)
      , v = n(52125);
    const f = "s2O1MLsL"
      , h = "EtwJ505o"
      , p = "PGxyUaDj"
      , g = "zdyJ0jbb";
    var y = n(52255)
      , w = n(30906)
      , _ = n(64408)
      , E = n(5594)
      , k = n.n(E)
      , x = n(88438)
      , b = n.n(x)
      , C = n(5022)
      , N = n(72983)
      , T = n(52252)
      , Z = n(25083)
      , S = n(53607)
      , I = n(85938)
      , L = n(20389)
      , D = n(66231)
      , M = n(76659)
      , B = n(16655)
      , A = n(64644)
      , P = n(91954)
      , O = n(37541)
      , V = n(10534)
      , W = n(51652)
      , R = n(63090);
    const F = "G0S7YWl4"
      , U = "ZWfLfofK"
      , H = "KgDqPY_r"
      , G = "QFii_bPD"
      , j = "cuvUuj0g"
      , K = "lcYXJjtm"
      , q = "u28GXXK2"
      , Y = "RZbE4EGx"
      , X = "fnnsKPmK"
      , z = "impPwaFy";
    var Q, J;
    function $() {
      return $ = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        $.apply(this, arguments)
    }
    const ee = function(e) {
      return i.createElement("svg", $({
        width: 36,
        height: 36,
        viewBox: "0 0 36 36",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), Q || (Q = i.createElement("circle", {
        cx: 18,
        cy: 18,
        r: 18,
        fill: "#EFF0F3"
      })), J || (J = i.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M18 8.5a9.5 9.5 0 100 19 9.5 9.5 0 000-19zm-1.42 14.175c0 .73.611 1.325 1.363 1.325.753 0 1.363-.594 1.363-1.325s-.612-1.325-1.363-1.325c-.754 0-1.363.594-1.363 1.325zm3.318-4.47c.87-.72 1.438-1.286 1.705-1.703.265-.417.4-.86.397-1.327 0-.845-.361-1.585-1.087-2.22-.726-.637-1.7-.955-2.928-.955-1.165 0-2.108.314-2.826.942-.717.628-1.135 1.493-1.159 2.292-.023.798 1.89.632 1.96.238.074-.417.388-1.091.754-1.397.365-.305.82-.46 1.363-.46.562 0 1.012.148 1.343.441.332.295.5.647.5 1.058 0 .295-.096.566-.283.813-.121.156-.495.485-1.117.988-.622.501-1.038.954-1.246 1.357-.208.402-.312.914-.312 1.538l.003.184.006.321h1.94c-.01-.583.04-.988.148-1.213.109-.228.389-.527.84-.898z",
        fill: "#2F3035"
      })))
    };
    const te = new (n(37485).hD)({
      feedbackShow: {
        eventName: "feedback_show",
        params: {
          enter_from: ""
        }
      },
      feedbackClick: {
        eventName: "feedback_click",
        params: {
          enter_from: ""
        }
      }
    });
    var ne = n(10790)
      , re = n(59737);
    const oe = function(e) {
      var t, a = e.isXiguaDomain, s = e.version, c = void 0 === s ? "" : s, u = (0,
        i.useState)(!1), m = (0,
        o.Z)(u, 2), v = m[0], f = m[1], h = (0,
        i.useState)(""), p = (0,
        o.Z)(h, 2), g = p[0], E = p[1], x = (0,
        i.useRef)(null), Q = (0,
        i.useRef)(null), J = (0,
        i.useRef)(null), $ = (0,
        i.useRef)(T.p() ? null : document.createElement("div"));
      (0,
        i.useEffect)((function() {
          var e = localStorage.getItem("FeedBackFlag");
          E(e),
          "1" !== e && (te.sendLog("feedbackShow", {
            enter_from: Z.yW()
          }),
            b()((function() {
                localStorage.setItem("FeedBackFlag", "1"),
                  E("1")
              }
            ), 3e3))
        }
      ), []);
      var oe = (0,
        C.O)().isFullscreen
        , ie = (0,
        i.useCallback)(function() {
        var e = (0,
          _.Z)(k().mark((function e(t) {
            var r, o, i, a, l, s, u, d, m, v, h, p, g, y, _, E, b, C, T, V, F, U, H, G, j;
            return k().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return e.next = 2,
                        n.e(7569).then(n.t.bind(n, 57569, 23));
                    case 2:
                      if (s = e.sent,
                        t) {
                        e.next = 5;
                        break
                      }
                      return e.abrupt("return");
                    case 5:
                      return u = S.Q.getItem({
                        sKey: W.CookieKeys.Theme
                      }),
                        d = I.Dr(u),
                        m = S.Q.getItem({
                          sKey: W.CookieKeys.MonitorWebId
                        }),
                        v = S.Q.getItem({
                          sKey: W.CookieKeys.MonitorDeviceId
                        }),
                        e.next = 11,
                        (0,
                          N.d)();
                    case 11:
                      h = e.sent,
                        p = (h || []).join(","),
                        g = L.rp(),
                        y = g.device_manufacture,
                        _ = void 0 === y ? "" : y,
                        E = g.device_model,
                        b = void 0 === E ? "" : E,
                        C = g.guid,
                        T = void 0 === C ? "" : C,
                        V = g.version,
                        F = void 0 === V ? "" : V,
                        U = D.f(),
                        H = U.os,
                        G = s.default,
                        j = null === (r = M.Es()) || void 0 === r ? void 0 : r.user_unique_id,
                        x.current = new G(t,{
                          zIndex: R.FEEDBACK_Z_INDEX,
                          appId: B.DT() ? R.CLIENT_APP_ID.toString() : R.APP_ID.toString(),
                          bizId: R.BIDID,
                          webId: j,
                          appName: R.APPNAME,
                          extra_params: {
                            MONITOR_WEB_ID: m,
                            MONITOR_DEVICE_ID: v,
                            abTestVids: p,
                            manufacturer: _,
                            version: c,
                            device_model: b,
                            guid: T,
                            clientVersion: F,
                            os: H,
                            env: null === (o = M.Le.getConfig(M.gI.Env)) || void 0 === o ? void 0 : o.envService,
                            custom_field_info: {
                              env: null === (i = M.Le.getConfig(M.gI.Env)) || void 0 === i ? void 0 : i.envService,
                              os: H,
                              clientVersion: F
                            }
                          },
                          ext: {
                            headerToggle: !0
                          },
                          sdkUrl: R.SDKURL,
                          theme: d,
                          getFeedbackResult: function(e) {
                            if (e) {
                              var t = {
                                page: Z.yW(),
                                web_id: m,
                                devide_id: v
                              };
                              A.oe.event.info({
                                name: A.Mo.SubmitFeedBack,
                                report: (0,
                                  w.Z)({}, t)
                              }),
                                P.q.custom.emit(P.j.FeedBackSubmit, t),
                                ne.F.info("\u5df2\u7ecf\u63d0\u4ea4\u53cd\u9988")
                            }
                          },
                          getInterfaceError: function(e) {
                            e && ne.F.info("\u63a5\u53e3\u72b6\u6001\u5f02\u5e38")
                          },
                          onVisibleChange: function(e) {
                            var t, n = O.r() && document.getElementById("slideMode") || document.getElementsByClassName("xgplayer-fullscreen-parent")[0], r = null === (t = x.current) || void 0 === t ? void 0 : t._iframeContainer;
                            if (e) {
                              if (te.sendLog("feedbackClick", {
                                enter_from: Z.yW()
                              }),
                                !Q.current)
                                return;
                              n ? (r = n,
                                $.current.className = z,
                                $.current.appendChild(Q.current),
                                n.appendChild($.current)) : r.appendChild(Q.current)
                            } else {
                              var o, i, a, l;
                              if (!x.current)
                                return;
                              if (n)
                                null === (a = $.current) || void 0 === a || null === (l = a.remove) || void 0 === l || l.call(a);
                              Q.current = x.current._sdkIframeEle,
                              null === (o = x.current._sdkIframeEle) || void 0 === o || null === (i = o.remove) || void 0 === i || i.call(o)
                            }
                          }
                        }),
                        f(!0),
                        Q.current = x.current._sdkIframeEle,
                      null === (a = x.current._sdkIframeEle) || void 0 === a || null === (l = a.remove) || void 0 === l || l.call(a);
                    case 21:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }(), []);
      return (0,
        i.useEffect)((function() {
          var e, t, n, r;
          null === (e = x.current) || void 0 === e || null === (t = e.hide) || void 0 === t || t.call(e),
          null === (n = $.current) || void 0 === n || null === (r = n.remove) || void 0 === r || r.call(n)
        }
      ), [oe]),
        (0,
          i.useEffect)((function() {
            var e = d.listen(d.EVENT.showFeedback, (function() {
                var e, t;
                null === (e = J.current) || void 0 === e || null === (t = e.click) || void 0 === t || t.call(e)
              }
            ));
            return function() {
              return e()
            }
          }
        ), []),
        (0,
          i.useEffect)((function() {
            var e = d.listen(d.EVENT.changeTheme, (function() {
                var e, t;
                if (v) {
                  try {
                    var n, r;
                    null === (n = x.current) || void 0 === n || null === (r = n.destroy) || void 0 === r || r.call(n)
                  } catch (o) {}
                  null === (e = x.current) || void 0 === e || null === (t = e.destroy) || void 0 === t || t.call(e),
                    ie(J.current)
                }
              }
            ));
            return function() {
              return e()
            }
          }
        ), [ie, v]),
        (0,
          i.useEffect)((function() {
            return ie(J.current),
              function() {
                try {
                  var e, t;
                  null === (e = x.current) || void 0 === e || null === (t = e.destroy) || void 0 === t || t.call(e)
                } catch (n) {}
              }
          }
        ), []),
        i.createElement("div", {
          onMouseEnter: function() {
            te.sendLog("feedbackShow", {
              enter_from: Z.yW()
            })
          },
          ref: function(e) {
            J.current = e
          },
          className: l()(F, (t = {},
            (0,
              r.Z)(t, X, "1" !== g),
            (0,
              r.Z)(t, K, a),
            t))
        }, a && i.createElement(i.Fragment, null, i.createElement(re.e, {
          text: "\u53cd\u9988",
          isXiguaDomain: a
        }, i.createElement("div", {
          className: j
        }, i.createElement(y.Z, {
          src: globalThis.getFilterXss().filterUrl(V.Z, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 28,
          height: 28,
          viewBox: "-4 -4 28 28"
        }))), i.createElement("div", {
          className: q
        }), i.createElement("div", {
          className: Y
        })), !a && i.createElement("div", {
          className: U
        }, i.createElement("div", {
          className: H
        }, i.createElement(y.Z, {
          src: globalThis.getFilterXss().filterUrl(ee, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 36,
          height: 36
        })), i.createElement("div", {
          className: G
        }, i.createElement(y.Z, {
          src: globalThis.getFilterXss().filterUrl(ee, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 36,
          height: 36
        })), i.createElement("span", null, "\u610f\u89c1\u53cd\u9988")))
    };
    var ie = n(92024)
      , ae = n(97408)
      , le = n(32322)
      , se = c.d
      , ce = u.F;
    function ue(e) {
      var t = e.className
        , n = void 0 === t ? "" : t
        , a = e.showUpIconScrollY
        , c = e.children
        , u = e.isXiguaDomain
        , w = e.version
        , _ = e.nowPathName
        , E = e.SlardarInstance
        , k = (0,
        i.useState)(!1)
        , x = (0,
        o.Z)(k, 2)
        , b = x[0]
        , C = x[1]
        , N = (0,
        i.useState)(!1)
        , T = (0,
        o.Z)(N, 2)
        , Z = T[0]
        , S = T[1]
        , I = (0,
        i.useState)(null)
        , L = (0,
        o.Z)(I, 2)
        , D = L[0]
        , M = L[1]
        , B = (0,
        i.useCallback)((function(e) {
          C(e),
            d.emit(d.EVENT.isShowUp, e)
        }
      ), []);
      (0,
        i.useEffect)((function() {
          var e, t, n;
          S(Boolean(null === (e = window) || void 0 === e || null === (t = e.CSS) || void 0 === t || null === (n = t.supports) || void 0 === n ? void 0 : n.call(t, "--testName: 0")));
          var r = function() {
            ce(D || window).y > (a || 3 * window.innerHeight) ? !b && B(!0) : b && B(!1)
          };
          return (D || document).addEventListener("scroll", r),
            function() {
              (D || document).removeEventListener("scroll", r)
            }
        }
      ), [a, b, B, Z, D]),
        (0,
          i.useEffect)((function() {
            C(!1)
          }
        ), [_]),
        (0,
          i.useEffect)((function() {
            return d.commonEvent.on(d.EVENT.globalScrollEl, M),
              function() {
                d.commonEvent.off(d.EVENT.globalScrollEl, M)
              }
          }
        ), []);
      var A = s.a.useClientDetect();
      return i.createElement("div", {
        id: "douyin-sidebar",
        className: l()(f, n, (0,
          r.Z)({}, p, u))
      }, c, !A && Z && u && i.createElement(ie.x$, {
        TipComponent: ae.C,
        isXiguaDomain: u
      }), i.createElement(le.k, {
        Slardar: E,
        componentName: "FeedBackDom"
      }, i.createElement(oe, {
        isXiguaDomain: u,
        version: w
      })), u && b && i.createElement(re.e, {
        text: "\u56de\u5230\u9876\u90e8",
        isXiguaDomain: u
      }, i.createElement("div", {
        className: l()(h, (0,
          r.Z)({}, g, u)),
        onClick: function() {
          se(null != D ? D : window, 0, 500)
        }
      }, i.createElement(y.Z, {
        src: globalThis.getFilterXss().filterUrl(v.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: 32,
        height: 32,
        viewBox: "-7 -7 36 36"
      }))), !u && b && i.createElement("div", {
        className: l()(h, (0,
          r.Z)({}, g, u)),
        onClick: function() {
          se(null != D ? D : window, 0, 500)
        }
      }, i.createElement(y.Z, {
        src: globalThis.getFilterXss().filterUrl(m.Z, null, {
          logType: "js.href/src",
          reportOnly: !1
        }),
        width: 32,
        height: 32
      })))
    }
  }
  ,
  52255: (e,t,n)=>{
    n.d(t, {
      Z: ()=>m
    });
    var r = n(30906)
      , o = n(67161)
      , i = n(44503)
      , a = n(79705)
      , l = n.n(a)
      , s = n(52252);
    const c = "u1O5vnab";
    var u = ["src", "width", "height", "color", "viewBox", "className", "onClick", "onMouseEnter", "onMouseLeave", "onMouseDown", "onMouseUp", "style", "id"]
      , d = function(e) {
      var t = e.src
        , n = e.width
        , a = void 0 === n ? 18 : n
        , d = e.height
        , m = void 0 === d ? 18 : d
        , v = e.color
        , f = e.viewBox
        , h = e.className
        , p = void 0 === h ? "" : h
        , g = e.onClick
        , y = e.onMouseEnter
        , w = e.onMouseLeave
        , _ = e.onMouseDown
        , E = e.onMouseUp
        , k = e.style
        , x = e.id
        , b = (0,
        o.Z)(e, u)
        , C = v ? (0,
        r.Z)((0,
        r.Z)({}, b), {}, {
        fill: v
      }) : b;
      return s.p() ? i.createElement(i.Fragment, null) : i.createElement(t, (0,
        r.Z)((0,
        r.Z)({
        className: l()(v ? c : "", p),
        width: a,
        height: m,
        viewBox: f || "0 0 36 36",
        onClick: g,
        onMouseEnter: y,
        onMouseLeave: w,
        onMouseDown: _,
        onMouseUp: E
      }, C), {}, {
        style: k,
        id: x
      }))
    };
    const m = i.memo(d)
  }
  ,
  92024: (e,t,n)=>{
    n.d(t, {
      x$: ()=>q,
      c4: ()=>j,
      Ly: ()=>K
    });
    var r, o = n(65146), i = n(32781), a = n(88438), l = n.n(a), s = n(44503), c = n(79705), u = n.n(c), d = n(53607), m = n(85938), v = n(92557), f = n(25083), h = n(3345), p = n(85289), g = n(51652);
    function y() {
      return y = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        y.apply(this, arguments)
    }
    const w = function(e) {
      return s.createElement("svg", y({
        width: 24,
        height: 28,
        viewBox: "0 0 24 28",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), r || (r = s.createElement("path", {
        opacity: .7,
        d: "M20.414 5.613a6.718 6.718 0 01-2.886-4.39A6.808 6.808 0 0117.416 0h-4.732l-.008 19.29c-.079 2.16-1.827 3.895-3.969 3.895-.665 0-1.292-.17-1.845-.465a4.06 4.06 0 01-2.132-3.582c0-2.23 1.785-4.046 3.977-4.046.41 0 .802.07 1.174.187v-4.913a8.618 8.618 0 00-1.174-.087C3.907 10.28 0 14.254 0 19.14a8.898 8.898 0 003.718 7.255A8.557 8.557 0 008.708 28c4.803 0 8.71-3.974 8.71-8.86V9.357A11.12 11.12 0 0024 11.51V6.696a6.47 6.47 0 01-3.586-1.083z",
        fill: "#E7E7EC"
      })))
    };
    var _, E;
    function k() {
      return k = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        k.apply(this, arguments)
    }
    const x = function(e) {
      return s.createElement("svg", k({
        width: 16,
        height: 16,
        viewBox: "0 0 16 16",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), _ || (_ = s.createElement("path", {
        fillRule: "evenodd",
        clipRule: "evenodd",
        d: "M8 16A8 8 0 108 0a8 8 0 000 16z",
        fill: "#FE2C55"
      })), E || (E = s.createElement("path", {
        d: "M4 7.5a1 1 0 000 1.415l2.342 2.28a1 1 0 001.415 0l.008-.008 4.65-4.772A1 1 0 0011 5L7.05 9.073 5.414 7.5A1 1 0 004 7.5z",
        fill: "#fff"
      })))
    };
    var b;
    function C() {
      return C = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        C.apply(this, arguments)
    }
    const N = function(e) {
      return s.createElement("svg", C({
        width: 9,
        height: 9,
        viewBox: "0 0 9 9",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), b || (b = s.createElement("path", {
        d: "M8.805 1.471A.667.667 0 107.862.53L4.667 3.724 1.47.529a.667.667 0 10-.942.942l3.195 3.196L.529 7.862a.667.667 0 00.942.943l3.196-3.196 3.195 3.196a.667.667 0 10.943-.943L5.609 4.667 8.805 1.47z",
        fill: "#fff"
      })))
    };
    const T = new (n(37485).hD)({
      changeThemeSetting: {
        eventName: "change_theme_setting",
        params: {
          theme: "light",
          enter_from: ""
        }
      },
      themeSettingGuideConfirm: {
        eventName: "theme_setting_guide_confirm",
        params: {
          theme: "light"
        }
      },
      themeSettingGuideShow: {
        eventName: "theme_setting_guide_show",
        params: {
          theme: "light"
        }
      }
    })
      , Z = "JHraiF99"
      , S = "EtCcWLb5"
      , I = "nG9kzwxB"
      , L = "lMuW5qkn"
      , D = "HMJIOD8d"
      , M = "gnfYyz1O"
      , B = "tVgaIByW"
      , A = "Kx8aac8K"
      , P = "_8fqldc6"
      , O = "aB450Cfo"
      , V = "_BdQ0DrR"
      , W = "fwYhOTEP"
      , R = "FAiirZle"
      , F = "CuCn9bOg"
      , U = "L0BGw3mC";
    var H = n(52255)
      , G = n(59737)
      , j = function(e) {
      var t;
      (null === (t = document.cookie.match(/theme=(\w+);/g)) || void 0 === t ? void 0 : t.length) > 1 && d.Q.removeItem(g.CookieKeys.Theme, "/"),
        d.Q.setItem(g.CookieKeys.Theme, e ? g.ThemeValues.Dark : g.ThemeValues.Light, g.COOKIE_DEFAULT_EXPIRE_DURATION, "/", g.COOKIE_DOMAIN, "", !0)
    }
      , K = function(e) {
      var t, n, r, o = "dark", i = document.documentElement, a = document.getElementById("dark");
      e ? null == i || null === (t = i.setAttribute) || void 0 === t || t.call(i, o, "true") : (null == i || null === (n = i.removeAttribute) || void 0 === n || n.call(i, o),
      null == a || null === (r = a.removeAttribute) || void 0 === r || r.call(a, "id"))
    }
      , q = function(e) {
      var t = e.TipComponent
        , n = e.isXiguaDomain
        , r = d.Q.getItem({
        sKey: g.CookieKeys.Theme
      })
        , a = m.Dr(r) === g.ThemeValues.Dark
        , l = (0,
        s.useState)(a)
        , c = (0,
        i.Z)(l, 2)
        , y = c[0]
        , w = c[1]
        , _ = (0,
        s.useState)(!1)
        , E = (0,
        i.Z)(_, 2)
        , k = E[0]
        , x = E[1];
      return (0,
        s.useEffect)((function() {
          var e, t, n = document.documentElement;
          null == n || null === (e = n.setAttribute) || void 0 === e || e.call(n, "switch-theme", ""),
          null == n || null === (t = n.setAttribute) || void 0 === t || t.call(n, "video-opacity", "")
        }
      ), []),
        (0,
          s.useEffect)((function() {
            K(y),
            n && document.body.style.setProperty("--color-primary", "#fe3355"),
              v.emit(v.EVENT.changeTheme, {
                theme: y ? g.ThemeValues.Dark : g.ThemeValues.Light
              })
          }
        ), [y]),
        s.createElement(s.Fragment, null, s.createElement(t, {
          type: "left",
          showTip: k,
          tipClassName: F,
          content: s.createElement(Y, {
            setShowTip: x,
            isDark: y,
            setIsDark: w,
            setThemeCookie: j
          })
        }, n && s.createElement(G.e, {
          text: y ? "\u5207\u6362\u6d45\u8272\u5916\u89c2" : "\u5207\u6362\u6df1\u8272\u5916\u89c2",
          isXiguaDomain: n
        }, s.createElement("div", {
          className: u()(Z, (0,
            o.Z)({}, U, n)),
          onClick: function() {
            w((function(e) {
                return T.sendLog("changeThemeSetting", {
                  theme: e ? g.ThemeValues.Light : g.ThemeValues.Dark,
                  enter_from: f.yW()
                }),
                  j(!e),
                  !e
              }
            ))
          }
        }, s.createElement(H.Z, {
          src: globalThis.getFilterXss().filterUrl(p.Z, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 24.7,
          height: 20.3,
          viewBox: "0 0 22 19",
          color: "var(--color-text-1)"
        }))), !n && s.createElement("div", {
          className: u()(Z),
          onClick: function() {
            w((function(e) {
                return T.sendLog("changeThemeSetting", {
                  theme: e ? g.ThemeValues.Light : g.ThemeValues.Dark,
                  enter_from: f.yW()
                }),
                  j(!e),
                  !e
              }
            ))
          }
        }, s.createElement(H.Z, {
          src: globalThis.getFilterXss().filterUrl(h.Z, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 24.7,
          height: 20.3,
          viewBox: "0 0 22 19"
        }))))
    }
      , Y = function(e) {
      var t = e.isDark
        , n = e.setIsDark
        , r = e.setShowTip
        , i = e.setThemeCookie
        , a = function(e) {
        T.sendLog("themeSettingGuideConfirm", {
          theme: e ? g.ThemeValues.Dark : g.ThemeValues.Light
        })
      };
      return (0,
        s.useEffect)((function() {
          T.sendLog("themeSettingGuideShow", {
            theme: t ? g.ThemeValues.Dark : g.ThemeValues.Light
          })
        }
      ), []),
        s.createElement("div", {
          className: S
        }, s.createElement(H.Z, {
          className: I,
          onClick: function() {
            a(t),
              i(t),
              r(!1)
          },
          src: globalThis.getFilterXss().filterUrl(N, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 9,
          height: 9,
          viewBox: "0 0 9 9"
        }), s.createElement("div", {
          className: L
        }, "\u80cc\u666f\u5207\u6362"), s.createElement("div", {
          className: D
        }, "\u70b9\u51fb\u300c\u6362\u80a4\u300d\u6309\u94ae\u5207\u6362\u80cc\u666f\u8272"), s.createElement("div", {
          className: M
        }, s.createElement("div", {
          className: B
        }, s.createElement("div", {
          className: A,
          onClick: function() {
            a(!1),
              n(!1),
              i(!1),
              v.emit(v.EVENT.changeTheme, {
                theme: g.ThemeValues.Light
              }),
              l()((function() {
                  r(!1)
                }
              ), 2e3)
          }
        }, s.createElement(H.Z, {
          className: R,
          src: globalThis.getFilterXss().filterUrl(w, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 24,
          height: 28,
          viewBox: "0 0 24 28"
        }), s.createElement(H.Z, {
          className: u()(V, (0,
            o.Z)({}, W, t)),
          src: globalThis.getFilterXss().filterUrl(x, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 16,
          height: 16,
          viewBox: "0 0 16 16"
        }))), s.createElement("div", {
          className: O
        }, s.createElement("div", {
          className: P,
          onClick: function() {
            a(!0),
              n(!0),
              i(!0),
              v.emit(v.EVENT.changeTheme, {
                theme: g.ThemeValues.Dark
              }),
              l()((function() {
                  r(!1)
                }
              ), 2e3)
          }
        }, s.createElement(H.Z, {
          className: R,
          src: globalThis.getFilterXss().filterUrl(w, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 24,
          height: 28,
          viewBox: "0 0 24 28"
        }), s.createElement(H.Z, {
          className: u()(V, (0,
            o.Z)({}, W, !t)),
          src: globalThis.getFilterXss().filterUrl(x, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          width: 16,
          height: 16,
          viewBox: "0 0 16 16"
        })))))
    }
  }
  ,
  97408: (e,t,n)=>{
    n.d(t, {
      C: ()=>d
    });
    var r = n(44503);
    const o = {
      tooltipWrapper: "NRiH5zYV",
      tooltip: "BQT1A3Va",
      left: "Xtzbk1D8",
      right: "pBQCcTij",
      top: "mTNC2mtW",
      bottom: "yGdoJ_A9",
      icon: "RQ1fJbHb"
    };
    var i;
    function a() {
      return a = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        a.apply(this, arguments)
    }
    const l = function(e) {
      return r.createElement("svg", a({
        width: 4,
        height: 17,
        viewBox: "0 0 4 17",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), i || (i = r.createElement("path", {
        d: "M0 0a8 8 0 002.168 5.476l1.174 1.25a2 2 0 010 2.738l-1.174 1.25A8 8 0 000 16.19V0z",
        fill: "#323442"
      })))
    };
    var s = n(52255)
      , c = n(79705)
      , u = n.n(c)
      , d = function(e) {
      var t = e.type
        , n = void 0 === t ? "left" : t
        , i = e.hoverShow
        , a = void 0 !== i && i
        , c = e.showTip
        , d = e.setShowTip
        , m = e.content
        , v = e.className
        , f = e.tipClassName
        , h = e.iconClassName
        , p = e.otherHide
        , g = void 0 === p || p
        , y = e.children
        , w = (0,
        r.useRef)(null);
      return (0,
        r.useEffect)((function() {
          var e = function(e) {
            d(!1)
          }
            , t = function() {
            d(!1)
          }
            , n = function() {
            d(!0)
          }
            , r = a && w.current;
          return r && (w.current.addEventListener("mouseleave", t),
            w.current.addEventListener("mouseenter", n)),
          c && d && g && (document.addEventListener("scroll", e),
            document.addEventListener("click", e)),
            function() {
              var o, i;
              (document.removeEventListener("scroll", e),
                document.removeEventListener("click", e),
                r) && (null === (o = w.current) || void 0 === o || o.removeEventListener("mouseleave", t),
              null === (i = w.current) || void 0 === i || i.removeEventListener("mouseenter", n))
            }
        }
      ), [c, a, d]),
        r.createElement("div", {
          className: u()(o.tooltipWrapper, v),
          ref: w
        }, Boolean(c) && r.createElement("div", {
          className: u()(o.tooltip, o[n], f)
        }, r.createElement(s.Z, {
          width: 4,
          height: 17,
          src: globalThis.getFilterXss().filterUrl(l, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          className: u()(o.icon, o[n], h),
          viewBox: "0 0 4 17"
        }), m), y)
    }
  }
  ,
  10790: (e,t,n)=>{
    n.d(t, {
      F: ()=>L
    });
    var r = n(29529)
      , o = n(30906)
      , i = n(19049)
      , a = n(95508)
      , l = n(73316)
      , s = n(6670)
      , c = n(92482)
      , u = n(65146)
      , d = n(92012)
      , m = n.n(d)
      , v = n(21805)
      , f = n.n(v)
      , h = n(88438)
      , p = n.n(h)
      , g = n(88677)
      , y = n.n(g)
      , w = n(79705)
      , _ = n.n(w)
      , E = n(44503)
      , k = n(9)
      , x = n(37541);
    const b = "N4KSpGs0"
      , C = "Y58u3RjO"
      , N = "G8j0DJHl";
    var T = null
      , Z = null
      , S = null
      , I = {
      text: "",
      duration: 3e3
    }
      , L = function(e) {
      (0,
        s.Z)(n, e);
      var t = (0,
        c.Z)(n);
      function n() {
        var e, r;
        (0,
          i.Z)(this, n);
        for (var o = arguments.length, a = new Array(o), s = 0; s < o; s++)
          a[s] = arguments[s];
        return r = t.call.apply(t, m()(e = [this]).call(e, a)),
          (0,
            u.Z)((0,
            l.Z)(r), "state", {
            showToast: !1
          }),
          (0,
            u.Z)((0,
            l.Z)(r), "mouseCloseFn", (function(e) {
              r.handleCloseToast(),
                r.destroy(),
                Z = null
            }
          )),
          (0,
            u.Z)((0,
            l.Z)(r), "keyboardCloseFn", (function(e) {
              var t;
              f()(t = ["Escape", "ArrowUp", "ArrowDown"]).call(t, e.key) && (r.handleCloseToast(),
                r.destroy(),
                Z = null)
            }
          )),
          r
      }
      return (0,
        a.Z)(n, [{
        key: "handleShowToast",
        value: function(e) {
          var t, r, o = this;
          Z && (clearTimeout(Z),
            Z = null);
          var i = n.textList.shift();
          this.setState({
            showToast: !0,
            options: i
          }),
            Z = p()((function() {
                n.textList.length ? o.handleCloseToast((function() {
                    var e;
                    p()(y()(e = o.handleShowToast).call(e, o), 50)
                  }
                )) : (o.handleCloseToast(),
                  o.destroy()),
                  Z = null
              }
            ), e || i.duration),
          null === (t = document) || void 0 === t || t.addEventListener("keydown", this.keyboardCloseFn),
          null === (r = S) || void 0 === r || r.addEventListener("click", this.mouseCloseFn)
        }
      }, {
        key: "handleCloseToast",
        value: function(e) {
          this.setState({
            showToast: !1
          }, (function() {
              return e && e()
            }
          ))
        }
      }, {
        key: "destroy",
        value: function() {
          var e, t, n;
          null === (e = document) || void 0 === e || e.removeEventListener("keydown", this.keyboardCloseFn),
          null === (t = S) || void 0 === t || t.removeEventListener("click", this.mouseCloseFn),
          null === (n = S) || void 0 === n || n.remove(),
            T = null
        }
      }, {
        key: "render",
        value: function() {
          var e = this.state
            , t = e.showToast
            , n = e.options
            , r = t && n && E.createElement("div", {
            className: _()(C, n.className, (0,
              u.Z)({}, N, x.r() || !n.className && n.root)),
            "data-e2e": "toast"
          }, n.text);
          return E.createElement(E.Fragment, null, n && n.root ? k.createPortal(r, n.root) : r)
        }
      }], [{
        key: "create",
        value: function(e) {
          if (T)
            return e && e(T);
          document.querySelector("#toastContainer") || ((S = document.createElement("div")).className = b,
            S.id = "toastContainer",
            document.body.appendChild(S)),
            k.render(E.createElement(n, {
              ref: function(t) {
                T = t,
                e && e(T)
              }
            }), S)
        }
      }, {
        key: "info",
        value: function(e, t, n) {
          var i = (0,
            o.Z)({}, I);
          "string" == typeof e ? (i.text = e,
            i.root = (null == t ? void 0 : t.current) || t) : "object" === (0,
            r.Z)(e) && null !== e && (i = (0,
            o.Z)((0,
            o.Z)({}, I), {}, {
            root: (null == t ? void 0 : t.current) || t
          }, e));
          var a = document.querySelector(".xgplayer-fullscreen-parent");
          x.r() && a && !i.root && (i.root = a),
            this.textList.push(i),
            this.create((function(e) {
                Z || e && e.handleShowToast(n)
              }
            ))
        }
      }]),
        n
    }(E.Component);
    (0,
      u.Z)(L, "textList", [])
  }
  ,
  59737: (e,t,n)=>{
    n.d(t, {
      e: ()=>_
    });
    var r = n(65146)
      , o = n(30906)
      , i = n(32781)
      , a = n(88438)
      , l = n.n(a)
      , s = n(21805)
      , c = n.n(s)
      , u = n(44503)
      , d = n(9);
    const m = {
      tooltipWrapper: "Wn5rJXak",
      tooltip: "Lf6MwTlM",
      xiguaTooltip: "DTV6OxM_",
      icon: "zi4zRGj1",
      left: "UQZybSAr",
      right: "NgpOGWLI",
      top: "a5rCXbcN",
      bottom: "p0ESuZn8"
    };
    var v;
    function f() {
      return f = Object.assign ? Object.assign.bind() : function(e) {
        for (var t = 1; t < arguments.length; t++) {
          var n = arguments[t];
          for (var r in n)
            Object.prototype.hasOwnProperty.call(n, r) && (e[r] = n[r])
        }
        return e
      }
        ,
        f.apply(this, arguments)
    }
    const h = function(e) {
      return u.createElement("svg", f({
        width: 4,
        height: 17,
        viewBox: "0 0 4 17",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg"
      }, e), v || (v = u.createElement("path", {
        d: "M0 0a8 8 0 002.168 5.476l1.174 1.25a2 2 0 010 2.738l-1.174 1.25A8 8 0 000 16.19V0z",
        fill: "#323442"
      })))
    };
    var p, g = n(52255), y = n(79705), w = n.n(y);
    !function(e) {
      e.left = "top",
        e.right = "top",
        e.top = "left",
        e.bottom = "left"
    }(p || (p = {}));
    var _ = function(e) {
      var t = e.type
        , n = void 0 === t ? "left" : t
        , a = e.text
        , s = e.offsetArrow
        , v = e.offsetContainer
        , f = e.className
        , y = e.children
        , _ = e.isXiguaDomain
        , E = (0,
        u.useState)({
        width: 0,
        height: 0
      })
        , k = (0,
        i.Z)(E, 2)
        , x = k[0]
        , b = k[1]
        , C = (0,
        u.useState)(n)
        , N = (0,
        i.Z)(C, 2)
        , T = N[0]
        , Z = N[1]
        , S = (0,
        u.useState)(!1)
        , I = (0,
        i.Z)(S, 2)
        , L = I[0]
        , D = I[1]
        , M = (0,
        u.useState)({})
        , B = (0,
        i.Z)(M, 2)
        , A = B[0]
        , P = B[1]
        , O = (0,
        u.useState)(s)
        , V = (0,
        i.Z)(O, 2)
        , W = V[0]
        , R = V[1]
        , F = (0,
        u.useRef)(null)
        , U = (0,
        u.useRef)()
        , H = (0,
        u.useRef)(null)
        , G = function() {
        clearTimeout(H.current),
          H.current = l()((function() {
              D(!1)
            }
          ), 200)
      }
        , j = (0,
        u.useCallback)((function() {
          var e, t, r, i;
          if (!F.current)
            return {};
          var a = U.current.getBoundingClientRect()
            , l = a.x
            , s = a.y
            , u = a.width
            , d = a.height
            , m = l
            , f = s
            , h = (x.width - u) / 2
            , p = (x.height - d) / 2;
          if (c()(e = ["left", "right"]).call(e, n)) {
            switch (n) {
              case "left":
                m -= x.width + 10;
                break;
              case "right":
                m += u + 10
            }
            f += "number" == typeof v ? v : -p
          } else if (c()(t = ["top", "bottom"]).call(t, n)) {
            switch (n) {
              case "top":
                f -= x.height + 10;
                break;
              case "bottom":
                f += d + 10
            }
            m += "number" == typeof v ? v : -h
          }
          var g = function() {
            var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 0
              , t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0
              , n = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : 0
              , r = arguments.length > 3 && void 0 !== arguments[3] ? arguments[3] : 0
              , o = window.innerWidth
              , i = window.innerHeight;
            return {
              left: e < 0 ? e : 0,
              top: t < 0 ? t : 0,
              right: e + n > o ? o - e - n : 0,
              bottom: t + r > i ? i - t - r : 0
            }
          }(m, f, x.width, x.height)
            , y = g.top
            , w = g.left
            , _ = g.right
            , E = g.bottom;
          return Z(n),
            c()(r = ["left", "right"]).call(r, n) ? (y && (f -= y),
            E && (f += E),
            w && !_ && (m += x.width + 20 + u,
              Z("right")),
            _ && !w && (m -= x.width + 20 + u,
              Z("left"))) : c()(i = ["top", "bottom"]).call(i, n) && (w && (R(w),
              m -= w),
            _ && (R(_),
              m += _),
            y && !E && (f += x.height + 20 + d,
              Z("bottom")),
            E && !y && (f -= x.height + 20 + d,
              Z("top"))),
            (0,
              o.Z)((0,
              o.Z)({}, A), {}, {
              left: "".concat(m, "px"),
              top: "".concat(f, "px")
            })
        }
      ), [A, x])
        , K = (0,
        u.useCallback)((function() {
          var e = u.Children.only(y);
          return u.cloneElement(e, {
            onMouseEnter: function(e) {
              clearTimeout(H.current),
                D(!0),
              U.current || (U.current = e.target),
                P(j())
            },
            onMouseLeave: function() {
              G()
            }
          })
        }
      ), [x]);
      return (0,
        u.useEffect)((function() {
          var e = function(e) {
            L && P(j())
          };
          return document.addEventListener("scroll", e, !0),
            function() {
              document.removeEventListener("scroll", e, !0)
            }
        }
      ), [j]),
        (0,
          u.useEffect)((function() {
            F.current && b(F.current.getBoundingClientRect())
          }
        ), [L]),
        (0,
          u.useEffect)((function() {
            U.current && P(j())
          }
        ), [x]),
        u.createElement(u.Fragment, null, L && d.createPortal(u.createElement("div", {
          ref: F,
          style: (0,
            o.Z)({
            position: "fixed"
          }, A),
          onMouseEnter: function(e) {
            clearTimeout(H.current)
          },
          onMouseLeave: function() {
            G()
          },
          className: w()(m.tooltip, m[n], f, (0,
            r.Z)({}, m.xiguaTooltip, _))
        }, u.createElement(g.Z, {
          width: 4,
          height: 17,
          src: globalThis.getFilterXss().filterUrl(h, null, {
            logType: "js.href/src",
            reportOnly: !1
          }),
          style: (0,
            r.Z)({}, p[T], W && "calc(50% - ".concat(W, "px)")),
          className: w()(m.icon, m[T]),
          viewBox: "0 0 4 17"
        }), u.createElement("span", {
          className: ""
        }, a)), document.body), K())
    }
  }
  ,
  7266: (e,t,n)=>{
    n.d(t, {
      C: ()=>r
    });
    var r = (0,
      n(44503).createContext)({})
  }
  ,
  54416: (e,t,n)=>{
    n.r(t),
      n.d(t, {
        Context: ()=>d,
        reducer: ()=>m,
        effect: ()=>v,
        initialData: ()=>f
      });
    var r, o = n(64408), i = n(30906), a = n(5594), l = n.n(a), s = n(44503), c = n(37485), u = n(53246), d = (0,
      s.createContext)(null), m = {
      setUserInfo: function(e, t) {
        var n;
        return (0,
          c.D$)(null == t || null === (n = t.userInfo) || void 0 === n ? void 0 : n.uid, null == t ? void 0 : t.isLogin),
          (0,
            i.Z)((0,
            i.Z)({}, e), {}, {
            isLogin: t.isLogin,
            info: t.userInfo,
            statusCode: t.statusCode
          })
      }
    }, v = {
      updateUserInfo: (r = (0,
          o.Z)(l().mark((function e(t, n, r) {
            var o, a, s, c, d;
            return l().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return e.next = 2,
                        u.b();
                    case 2:
                      if (a = e.sent,
                        s = a.isLogin,
                        c = a.user,
                        d = a.statusCode,
                      s !== (null == r ? void 0 : r.isLogin) || (null == c ? void 0 : c.uid) !== (null == r || null === (o = r.info) || void 0 === o ? void 0 : o.uid)) {
                        e.next = 8;
                        break
                      }
                      return e.abrupt("return", r);
                    case 8:
                      return n({
                        type: "setUserInfo",
                        payload: (0,
                          i.Z)((0,
                          i.Z)({}, r), {}, {
                          userInfo: c,
                          isLogin: s,
                          statusCode: d
                        })
                      }),
                        e.abrupt("return", (0,
                          i.Z)((0,
                          i.Z)({}, r), {}, {
                          isLogin: s,
                          user: c
                        }));
                    case 10:
                    case "end":
                      return e.stop()
                  }
              }
            ), e)
          }
        ))),
          function(e, t, n) {
            return r.apply(this, arguments)
          }
      )
    }, f = {
      isLogin: void 0,
      isSpider: !1,
      info: {},
      webcastInfo: {},
      statusCode: 0
    }
  }
  ,
  34301: (e,t,n)=>{
    n.d(t, {
      O: ()=>r,
      x: ()=>C
    });
    var r, o = n(30906), i = n(64408), a = n(32781), l = n(5594), s = n.n(l), c = n(62310), u = n.n(c), d = n(67827), m = n.n(d), v = n(81711), f = n.n(v), h = n(57617), p = n.n(h), g = n(44503), y = n(10790), w = n(96411), _ = n(51652), E = n(53607), k = n(72983), x = n(22983), b = n(76659);
    !function(e) {
      e.LogTrace = "87A38998227CBBC23DCAD51CD7F76AB2",
        e.UserInfo = "87A38998227CBBC23DCAD51CD7F76AB2_user_beta"
    }(r || (r = {}));
    var C = function() {
      var e = (0,
        g.useState)([])
        , t = (0,
        a.Z)(e, 2)
        , n = t[0]
        , l = t[1]
        , c = function(e) {
        var t, n, r = window.localStorage.getItem(null == w || null === (t = _) || void 0 === t ? void 0 : t.LOG_TRACE) || "";
        if (r) {
          var o = JSON.parse(r)
            , i = (n = o,
            u()(n).call(n, (function(e, t) {
                return new Date(t.time).getTime() - new Date(e.time).getTime()
              }
            )))
            , a = m()(i);
          e && e({
            logTraceStr: a,
            logTraceJSON: i
          })
        }
      }
        , d = function() {
        var e = (0,
          i.Z)(s().mark((function e(t) {
            var n, i, a, l, u, d, v, h, g, w, C, N, T, Z, S, I, L;
            return s().wrap((function(e) {
                for (; ; )
                  switch (e.prev = e.next) {
                    case 0:
                      return n = (t || {}).key,
                        i = void 0 === n ? r.LogTrace : n,
                        e.prev = 1,
                        a = E.Q.getItem({
                          sKey: _.CookieKeys.MonitorWebId
                        }) || "",
                        l = E.Q.getItem({
                          sKey: _.CookieKeys.MonitorDeviceId
                        }) || "",
                        e.next = 6,
                        (0,
                          k.d)();
                    case 6:
                      u = e.sent,
                        d = (u || []).join(","),
                        i === r.LogTrace ? c((function(e) {
                            var t = e.logTraceJSON
                              , n = {};
                            f()(t).call(t, (function(e) {
                                n[null == e ? void 0 : e.url] || (n[null == e ? void 0 : e.url] = []),
                                  n[null == e ? void 0 : e.url].push((0,
                                    o.Z)((0,
                                    o.Z)({}, e), {}, {
                                    monitorWebId: a,
                                    monitorDeviceId: l,
                                    abTestVids: d
                                  }))
                              }
                            ));
                            var r = m()(n);
                            x.J(r),
                              y.F.info("\u5df2\u590d\u5236\u8c03\u8bd5\u4fe1\u606f\u5230\u526a\u5207\u677f")
                          }
                        )) : i === r.UserInfo && (I = 0 === p()((null === (v = window) || void 0 === v ? void 0 : v.SSR_RENDER_DATA) || {}).length ? null === (h = window) || void 0 === h ? void 0 : h.SSR_RENDER_DATA : null === (g = window) || void 0 === g ? void 0 : g.SSR_RENDER_DATA_DOC,
                          L = {
                            version: null === (w = window) || void 0 === w ? void 0 : w.version,
                            ab: d,
                            slardar: null === (C = window) || void 0 === C || null === (N = C.slardar) || void 0 === N || null === (T = N.config) || void 0 === T ? void 0 : T.call(N),
                            odin: b.Es(),
                            ssr: I,
                            uuid: null === (Z = b.Es()) || void 0 === Z ? void 0 : Z.user_unique_id,
                            uid: null === (S = b.Es()) || void 0 === S ? void 0 : S.user_id,
                            wid: a,
                            did: l
                          },
                          x.J(m()(L)),
                          y.F.info("\u5df2\u590d\u5236\u8c03\u8bd5\u4fe1\u606f\u5230\u526a\u5207\u677f")),
                        e.next = 14;
                      break;
                    case 11:
                      e.prev = 11,
                        e.t0 = e.catch(1),
                        y.F.info("\u8c03\u8bd5\u4fe1\u606f\u590d\u5236\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5");
                    case 14:
                    case "end":
                      return e.stop()
                  }
              }
            ), e, null, [[1, 11]])
          }
        )));
        return function(t) {
          return e.apply(this, arguments)
        }
      }();
      return (0,
        g.useEffect)((function() {
          try {
            c((function(e) {
                var t = e.logTraceJSON;
                l(t)
              }
            ))
          } catch (e) {}
        }
      ), []),
        [n, d]
    }
  }
  ,
  26395: (e,t,n)=>{
    n.d(t, {
      P: ()=>l
    });
    var r = n(32781)
      , o = n(88438)
      , i = n.n(o)
      , a = n(44503);
    function l() {
      var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {}
        , t = e.delayDisappear
        , n = void 0 === t ? 200 : t
        , o = e.delayShow
        , l = void 0 === o ? 0 : o
        , s = (0,
        a.useState)("")
        , c = (0,
        r.Z)(s, 2)
        , u = c[0]
        , d = c[1]
        , m = (0,
        a.useRef)(0)
        , v = (0,
        a.useRef)(0)
        , f = function(e) {
        clearTimeout(m.current),
          l ? v.current = i()((function() {
              d(e)
            }
          ), l) : d(e)
      }
        , h = function() {
        m.current = i()((function() {
            d("")
          }
        ), n),
          clearTimeout(v.current)
      }
        , p = function(e, t) {
        t ? d(e) : e ? f(e) : h()
      }
        , g = function() {
        return clearTimeout(v.current)
      }
        , y = function() {
        return clearTimeout(m.current)
      };
      return {
        type: u,
        setType: d,
        changeType: p,
        showTimer: v,
        disappearTimer: m,
        clearShowTimer: g,
        clearDisappearTimer: y
      }
    }
  }
  ,
  9988: (e,t,n)=>{
    n.d(t, {
      U: ()=>l
    });
    var r = n(88438)
      , o = n.n(r)
      , i = n(89176)
      , a = n(44503);
    function l(e) {
      var t = e.enterDelay
        , n = void 0 === t ? 0 : t
        , r = e.leaveDelay
        , l = void 0 === r ? 200 : r
        , s = e.onMouseEnter
        , c = e.onMouseLeave
        , u = (0,
        a.useRef)()
        , d = (0,
        i.Z)((function(e) {
          var t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {
            immediate: !1
          }
            , r = t.immediate;
          window.clearTimeout(u.current),
            r || 0 === n ? s(e) : u.current = o()((function() {
                s(e)
              }
            ), n)
        }
      ))
        , m = (0,
        i.Z)((function(e) {
          var t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {
            immediate: !1
          }
            , n = t.immediate;
          window.clearTimeout(u.current),
          (n || 0 === l) && (null == c || c(e)),
            u.current = o()((function() {
                null == c || c(e)
              }
            ), l)
        }
      ));
      return (0,
        a.useEffect)((function() {
          return function() {
            window.clearTimeout(u.current)
          }
        }
      ), []),
        {
          onMouseEnter: d,
          onMouseLeave: m
        }
    }
  }
  ,
  26637: (e,t,n)=>{
    n.d(t, {
      o: ()=>s
    });
    var r = n(44503)
      , o = n(37610)
      , i = n(78867)
      , a = n(92289)
      , l = n(23141)
      , s = function(e, t) {
      var n, s = (0,
        o.k6)(), c = null == s || null === (n = s.location) || void 0 === n ? void 0 : n.pathname, u = (0,
        l.j)();
      return {
        isHorizontalLayout: (0,
          r.useMemo)((function() {
            return function(e, t, n, r) {
              return n ? new RegExp("^/user/self/?$").test(e) ? r : new RegExp(a.JO).test(e) : t === i.HasHorizontalHeader.FullScene ? new RegExp(a.jc).test(e) : t === i.HasHorizontalHeader.OnlySearchScene || t === i.HasHorizontalHeader.OnlySearchSceneAndRemoveRightColumn ? new RegExp(a.XR).test(e) : new RegExp(a.jZ).test(e)
            }(c, null != e ? e : i.HasHorizontalHeader.Default, t, u)
          }
        ), [c, e, t, u])
      }
    }
  }
  ,
  88848: (e,t,n)=>{
    n.d(t, {
      u: ()=>c
    });
    var r, o = n(32781), i = n(88438), a = n.n(i), l = n(44503), s = n(92557);
    function c(e) {
      var t, n, i = e.initImSDK, c = void 0 === i || i, u = e.initNoticeSDK, d = void 0 === u || u, m = (0,
        l.useState)(null !== (t = r) && void 0 !== t ? t : c), v = (0,
        o.Z)(m, 2), f = v[0], h = v[1], p = (0,
        l.useState)(null !== (n = r) && void 0 !== n ? n : d), g = (0,
        o.Z)(p, 2), y = g[0], w = g[1];
      return (0,
        l.useEffect)((function() {
          r || a()((function() {
              r = !0,
                h(!0),
                w(!0)
            }
          ), 9500)
        }
      ), []),
        (0,
          l.useEffect)((function() {
            var e = s.listen(s.EVENT.initIMNoticeSDK, (function(e) {
                r = !0,
                  h(!0),
                  w(!0)
              }
            ));
            return function() {
              return e()
            }
          }
        ), []),
        (0,
          l.useEffect)((function() {
            var e = s.listen(s.EVENT.initImSDK, (function(e) {
                r = !0,
                  h(!0)
              }
            ));
            return function() {
              return e()
            }
          }
        ), []),
        (0,
          l.useEffect)((function() {
            var e = s.listen(s.EVENT.initNoticeSDK, (function(e) {
                r = !0,
                  w(!0)
              }
            ));
            return function() {
              return e()
            }
          }
        ), []),
        {
          initImSDK: f,
          initNoticeSDK: y,
          setInitImSDK: h,
          setNoticeSDK: w
        }
    }
  }
  ,
  29978: (e,t,n)=>{
    n.d(t, {
      L: ()=>v
    });
    var r = n(64408)
      , o = n(32781)
      , i = n(82371)
      , a = n.n(i)
      , l = n(5594)
      , s = n.n(l)
      , c = n(44503)
      , u = n(85938)
      , d = n(9070)
      , m = n(73750)
      , v = function(e, t, n) {
      var i = (0,
        c.useState)(n)
        , l = (0,
        o.Z)(i, 2)
        , v = l[0]
        , f = l[1]
        , h = (0,
        c.useMemo)((function() {
          return u.RF(t, v)
        }
      ), [v, t]);
      return (0,
        c.useEffect)((function() {
          if (a()(n)) {
            var t = !1;
            return (0,
              r.Z)(s().mark((function n() {
                var r;
                return s().wrap((function(n) {
                    for (; ; )
                      switch (n.prev = n.next) {
                        case 0:
                          return n.next = 2,
                            d.U2({
                              key: m.TccKey.PageGrayscale,
                              defaultValue: m.TCC_DEFAULT_VALUE_MAP.get(m.TccKey.PageGrayscale),
                              namespace: e
                            });
                        case 2:
                          r = n.sent,
                          !t && f(r);
                        case 4:
                        case "end":
                          return n.stop()
                      }
                  }
                ), n)
              }
            )))(),
              function() {
                t = !0
              }
          }
        }
      ), []),
        h
    }
  }
  ,
  27117: (e,t,n)=>{
    n.d(t, {
      L: ()=>a
    });
    var r = n(30906)
      , o = n(44503)
      , i = n(76659);
    function a() {
      var e = (0,
        o.useRef)(null);
      return {
        setModalCardInfo: function() {
          e.current = i.Le.getConfig(i.gI.PlayerCardInfo),
            i.Le.setConfig(i.gI.PlayerCardInfo, {
              cardType: "chat",
              isActive: !0
            })
        },
        restoreModalCardInfo: function() {
          e.current && (i.Le.setConfig(i.gI.PlayerCardInfo, (0,
            r.Z)({}, e.current)),
            e.current = null)
        }
      }
    }
  }
  ,
  85284: (e,t,n)=>{
    n.d(t, {
      R: ()=>w,
      M: ()=>_
    });
    n(65146);
    var r = n(92012)
      , o = n.n(r)
      , i = n(44503)
      , a = (n(79705),
      n(97050))
      , l = n(26395)
      , s = n(55861)
      , c = n(36539)
      , u = n(4592)
      , d = n(92557)
      , m = n(7829)
      , v = n(76953)
      , f = n(79757)
      , h = n(51382)
      , p = "dlb-login-guide-active"
      , g = i.forwardRef((function(e, t) {
        var n = e.hint
          , r = e.changeType
          , l = e.enterMethod;
        return i.createElement("div", {
          className: m.Z.imLoginGuidePanelWrapper
        }, i.createElement("div", {
          ref: t,
          className: m.Z.imLoginGuidePanel
        }, i.createElement("p", {
          className: m.Z.desc
        }, n), i.createElement("div", {
          className: m.Z.loginBtn,
          onClick: function() {
            var e, t, i;
            null == r || r("", !0),
              (0,
                a.navShowAccount)({
                success: function() {
                  window.location.reload()
                },
                headerText: n,
                next: o()(e = "".concat(null == c ? void 0 : u.tJ)).call(e, null === (t = window) || void 0 === t || null === (i = t.location) || void 0 === i ? void 0 : i.host),
                enterMethod: l,
                teaEvtParams: {
                  is_guide: "1",
                  enter_method: l
                }
              })
          }
        }, "\u7acb\u5373\u767b\u5f55")))
      }
    ));
    var y = function(e) {
      var t = e.customProps
        , n = e.dlgName
        , r = e.hint
        , o = e.entryIcon
        , a = e.enterMethod
        , c = e.iconText
        , u = e.avatarWidth
        , v = e.avatarHeight
        , f = e.viewBox
        , y = e.transparent
        , w = (0,
        l.P)({
        delayDisappear: 200,
        delayShow: 100
      })
        , _ = w.type
        , E = w.changeType
        , k = w.clearShowTimer
        , x = (0,
        i.useCallback)((function() {
          s.n.loginGuideShowed && s.n.destroy(),
            E(p),
            d.emit(d.EVENT.showHeaderPopUp, {
              type: n,
              isShow: !0
            })
        }
      ), [_])
        , b = (0,
        i.useCallback)((function() {
          var e = arguments.length > 0 && void 0 !== arguments[0] && arguments[0];
          _ ? E(void 0, !0 === e) : k()
        }
      ), [_]);
      return i.createElement(i.Fragment, null, i.createElement("div", {
        "data-e2e": "".concat(n, "-entry"),
        className: m.Z.cicleButtonWithText
      }, i.createElement(h.Y, {
        type: "circleButtonWithText",
        text: c,
        onMouseEnter: function() {
          x()
        },
        onMouseLeave: function() {
          b()
        },
        avatarUrl: o,
        avatarWidth: u,
        avatarHeight: v,
        viewBox: f,
        activityName: null == t ? void 0 : t.activityName,
        headerPopupName: n,
        className: m.Z.polymorphicButton,
        transparent: y
      }, _ === p && i.createElement(g, {
        hint: r,
        changeType: E,
        enterMethod: a
      }))))
    };
    function w(e) {
      var t = e.customProps
        , n = e.transparent;
      return i.createElement(y, {
        customProps: t,
        dlgName: "im",
        hint: "\u767b\u5f55\u540e\u5373\u53ef\u67e5\u770b\u79c1\u4fe1\u6d88\u606f",
        entryIcon: v.Z,
        avatarWidth: 11,
        avatarHeight: 12,
        viewBox: "0 0.5 11.5 11",
        enterMethod: "IM",
        iconText: "\u79c1\u4fe1",
        transparent: n
      })
    }
    function _(e) {
      var t = e.customProps
        , n = e.transparent;
      return i.createElement(y, {
        customProps: t,
        dlgName: "notice",
        hint: "\u767b\u5f55\u540e\u5373\u53ef\u67e5\u770b\u901a\u77e5\u6d88\u606f",
        entryIcon: f.Z,
        avatarWidth: 20,
        avatarHeight: 32,
        viewBox: "0 1 16 16",
        enterMethod: "interact",
        iconText: "\u901a\u77e5",
        transparent: n
      })
    }
  }
  ,
  4014: (e,t,n)=>{
    n.d(t, {
      s: ()=>g
    });
    var r = n(19049)
      , o = n(95508)
      , i = n(65146)
      , a = n(99860)
      , l = n.n(a)
      , s = n(81711)
      , c = n.n(s)
      , u = n(84891)
      , d = n.n(u)
      , m = n(41265)
      , v = n.n(m)
      , f = n(92637)
      , h = n.n(f)
      , p = n(51465)
      , g = new (function() {
      function e() {
        (0,
          r.Z)(this, e),
          (0,
            i.Z)(this, "playerMap", void 0),
          (0,
            i.Z)(this, "playerSceneMap", void 0),
          (0,
            i.Z)(this, "playerCbMap", void 0),
          (0,
            i.Z)(this, "playerEntryMap", void 0),
          (0,
            i.Z)(this, "playerPageFullscreenMap", void 0),
          (0,
            i.Z)(this, "playerRegisterList", void 0),
          this.playerMap = new (l()),
          this.playerCbMap = new (l()),
          this.playerSceneMap = new (l()),
          this.playerEntryMap = new (l()),
          this.playerPageFullscreenMap = new (l()),
          this.playerRegisterList = []
      }
      return (0,
        o.Z)(e, [{
        key: "lastRegisterPlayerId",
        get: function() {
          return this.playerRegisterList[this.playerRegisterList.length - 1]
        }
      }, {
        key: "register",
        value: function(e) {
          var t = e.player
            , n = e.scene
            , r = t.playerId;
          this.playerMap.set(r, t),
            this.playerSceneMap.set(r, n),
            this.playerRegisterList.push(r);
          var o = this.playerCbMap.get(p.Lw.OnRegister);
          return (null == o ? void 0 : o.length) > 0 && c()(o).call(o, (function(e) {
              null == e || e({
                scene: n,
                playerId: r
              })
            }
          )),
            r
        }
      }, {
        key: "unRegister",
        value: function(e) {
          var t, n, r = e.id;
          if (void 0 === r)
            return !1;
          var o = this.playerSceneMap.get(r)
            , i = this.playerCbMap.get(p.Lw.OnUnRegister);
          (null == i ? void 0 : i.length) > 0 && c()(i).call(i, (function(e) {
              null == e || e({
                scene: o,
                playerId: r
              })
            }
          ));
          var a = this.playerMap.delete(r);
          this.playerSceneMap.delete(r),
            this.playerEntryMap.delete(r),
            this.playerPageFullscreenMap.delete(r);
          var l = d()(t = this.playerRegisterList).call(t, (function(e) {
              return e === r
            }
          ));
          return l > -1 && v()(n = this.playerRegisterList).call(n, l, 1),
            a
        }
      }, {
        key: "getPlayer",
        value: function(e) {
          return this.playerMap.get(e) || null
        }
      }, {
        key: "getPlayerScene",
        value: function(e) {
          return this.playerSceneMap.get(e)
        }
      }, {
        key: "getPlayersByScene",
        value: function(e) {
          var t, n = this;
          return h()(t = this.getAllPlayer()).call(t, (function(t) {
              return n.getPlayerScene(t.playerId) === e
            }
          ))
        }
      }, {
        key: "getAllPlayer",
        value: function() {
          var e, t = [];
          return c()(e = this.playerMap).call(e, (function(e) {
              return t.push(e)
            }
          )),
            t
        }
      }, {
        key: "setPlayerCardEntry",
        value: function(e) {
          var t = e.id
            , n = e.info;
          return !!this.playerMap.get(t) && (this.playerEntryMap.set(t, n),
            !0)
        }
      }, {
        key: "getPlayerCardEntry",
        value: function(e) {
          return (this.playerEntryMap.get(e) || {}).cardEntry
        }
      }, {
        key: "pauseOtherPlayer",
        value: function(e) {
          var t;
          c()(t = this.playerMap).call(t, (function(t) {
              var n;
              t.playerId !== e && (null === (n = t.pause) || void 0 === n || n.call(t))
            }
          ))
        }
      }, {
        key: "addCb",
        value: function(e) {
          var t = this
            , n = e.event
            , r = e.cb
            , o = this.playerCbMap.get(n);
          return o ? o.push(r) : this.playerCbMap.set(n, [r]),
            function() {
              t.removeCb(e)
            }
        }
      }, {
        key: "removeCb",
        value: function(e) {
          var t = e.event
            , n = e.cb
            , r = this.playerCbMap.get(t);
          if (r) {
            var o = d()(r).call(r, (function(e) {
                return e === n
              }
            ));
            o > -1 && v()(r).call(r, o, 1)
          }
        }
      }, {
        key: "setPageFullscreen",
        value: function(e) {
          var t = e.playerId
            , n = e.isPageFullscreen
            , r = this.playerPageFullscreenMap.get(t) || {
            isPageFullscreen: !1
          };
          r.isPageFullscreen = n,
            this.playerPageFullscreenMap.set(t, r)
        }
      }, {
        key: "getPlayerIsPageFullscreen",
        value: function(e) {
          var t;
          return (null === (t = this.playerPageFullscreenMap.get(e)) || void 0 === t ? void 0 : t.isPageFullscreen) || !1
        }
      }, {
        key: "getIsPageFullscreen",
        value: function() {
          var e, t = !1;
          return c()(e = this.playerPageFullscreenMap).call(e, (function(e) {
              e.isPageFullscreen && (t = !0)
            }
          )),
            t
        }
      }]),
        e
    }())
  }
  ,
  53540: (e,t,n)=>{
    n.d(t, {
      j1: ()=>L,
      pL: ()=>D,
      Q4: ()=>M,
      gE: ()=>B
    });
    var r = n(30906)
      , o = n(32781)
      , i = n(64408)
      , a = n(80051)
      , l = n.n(a)
      , s = n(92012)
      , c = n.n(s)
      , u = n(88438)
      , d = n.n(u)
      , m = n(5594)
      , v = n.n(m)
      , f = n(52252)
      , h = n(36539)
      , p = n(4592)
      , g = n(72983)
      , y = n(43478)
      , w = n(16655)
      , _ = n(78867)
      , E = n(76659)
      , k = n(25083)
      , x = n(82016)
      , b = n(37541)
      , C = n(47482)
      , N = n(45627)
      , T = n(1021)
      , Z = n(4014)
      , S = !1
      , I = function() {
      var e = (0,
        i.Z)(v().mark((function e() {
          var t;
          return v().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      Promise.all([n.e(7835), n.e(7727)]).then(n.bind(n, 67835)).then((function(e) {
                          return e.default
                        }
                      ));
                  case 2:
                    if (t = e.sent,
                      !S) {
                      e.next = 5;
                      break
                    }
                    return e.abrupt("return");
                  case 5:
                    t.use(),
                      S = !0;
                  case 8:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , L = function() {
      var e = (0,
        i.Z)(v().mark((function e() {
          var t, r, i, a;
          return v().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return t = Promise.all([n.e(8860), n.e(336)]).then(n.bind(n, 10336)),
                      e.next = 3,
                      I();
                  case 3:
                    return e.next = 5,
                      l().all([t]);
                  case 5:
                    return r = e.sent,
                      i = (0,
                        o.Z)(r, 1),
                      a = i[0],
                      e.abrupt("return", a.default);
                  case 9:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , D = function() {
      var e, t, n;
      return f.p() ? "" : c()(e = "".concat(null == h ? void 0 : p.tJ)).call(e, null === (t = window) || void 0 === t || null === (n = t.location) || void 0 === n ? void 0 : n.host)
    }
      , M = function() {
      var e = (0,
        i.Z)(v().mark((function e() {
          var t, n;
          return v().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return e.next = 2,
                      l().all([g.h.getVar({
                        name: "short_link_login_new",
                        defaultValue: 0
                      })]);
                  case 2:
                    return t = e.sent,
                      n = (0,
                        o.Z)(t, 1),
                      n[0],
                      e.abrupt("return", {
                        appName: "\u6296\u97f3 Web \u7ad9",
                        aid: 6383,
                        isFrontier: !0,
                        frontierUrl: p.uZ ? "" : "wss://frontier100-normal.zijieapi.com",
                        isStopCheckWhenHide: !0,
                        isBoe: p.uZ,
                        mobileCodeLength: 6,
                        isOversea: !1,
                        globalMobileSupport: !0,
                        region: "cn",
                        scope: "sso",
                        captchaHost: y.r0.captchaHost,
                        generalParams: {
                          device_platform: w.HA()
                        },
                        isShortLink: !1,
                        acrawler: p.uZ ? 0 : "1"
                      });
                  case 6:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function() {
        return e.apply(this, arguments)
      }
    }()
      , B = function() {
      var e = (0,
        i.Z)(v().mark((function e(t) {
          var n, i, a, s, c, u, m, y, w, S, I, L, B, A, P, O, V, W, R, F, U, H;
          return v().wrap((function(e) {
              for (; ; )
                switch (e.prev = e.next) {
                  case 0:
                    return c = t.success,
                      u = t.host,
                      m = t.next,
                      y = t.ScanCodeDescription,
                      w = t.enterMethod,
                      S = t.refreshNumber,
                      I = void 0 === S ? 2 : S,
                      L = t.teaEvtParams,
                      B = void 0 === L ? {} : L,
                      A = t.videoGuideFunc,
                      P = void 0 === A ? null : A,
                      O = t.operationCallback,
                      V = t.scanCodeNeedLogo,
                      W = void 0 !== V && V,
                      e.next = 3,
                      M();
                  case 3:
                    return R = e.sent,
                      e.next = 6,
                      l().all([g.h.getVar({
                        name: "check_qr_code_delay_time",
                        defaultValue: _.CheckQrCodeDelayTimeABVal.Normal
                      })]);
                  case 6:
                    return F = e.sent,
                      U = (0,
                        o.Z)(F, 1),
                      H = U[0],
                      e.abrupt("return", (0,
                        r.Z)((0,
                        r.Z)({}, R), {}, {
                        scanCodeNeedLogo: W,
                        checkQrCodeDelayTime: H,
                        device_id: null === (n = E.Es()) || void 0 === n ? void 0 : n.user_unique_id,
                        slardarContext: {
                          enter_method: w,
                          enter_from: k.vM() || "",
                          page_type: k.yW() || "",
                          delay_time: H.toString() || "0",
                          is_short_link: (null == R ? void 0 : R.isShortLink.toString()) || "false"
                        },
                        refreshNumber: I,
                        teaConfig: {
                          appId: 6383,
                          config: {
                            evtParams: (0,
                              r.Z)({
                              page_type: k.yW() || "",
                              enter_method: w,
                              enter_from: k.vM() || "",
                              url_path: f.p() ? "" : null === (i = window) || void 0 === i || null === (a = i.location) || void 0 === a ? void 0 : a.pathname,
                              is_guide: "1",
                              video_detail_enter_from: x.z("web_link"),
                              previous_page: k.yW("previous_page"),
                              is_active: "0",
                              is_video_guide: "0",
                              is_topknot: "0",
                              is_full_screen: b.r() ? "1" : "0",
                              is_full_webscreen: Z.s.getIsPageFullscreen() ? "1" : "0"
                            }, B),
                            videoGuideFunc: P,
                            ug_source: C.Rs("ug_source"),
                            sem_keyword: C.Rs("sem_keyword"),
                            browser_is_360: N.a2() ? "1" : "0"
                          }
                        },
                        host: u || (null == h || null === (s = p.k4) || void 0 === s ? void 0 : s.sso) || "https://sso.douyin.com",
                        next: m || D() || "https://www.douyin.com/",
                        loginType: ["LOGIN_SCAN_CODE"],
                        ScanCodeDescription: y,
                        operationCallback: O,
                        textConfig: {
                          scanCodeLoginText: {
                            refreshCode: "\u4e8c\u7ef4\u7801\u5df2\u5931\u6548",
                            getCodeFailed: "\u4e8c\u7ef4\u7801\u5df2\u5931\u6548",
                            refreshBtnText: "\u70b9\u51fb\u5237\u65b0",
                            codeFailedBtnText: "\u70b9\u51fb\u5237\u65b0"
                          }
                        },
                        success: function(e) {
                          null == c || c(e),
                            d()((function() {
                                (0,
                                  T.tokenBeatInit)()
                              }
                            ), 800)
                        }
                      }));
                  case 10:
                  case "end":
                    return e.stop()
                }
            }
          ), e)
        }
      )));
      return function(t) {
        return e.apply(this, arguments)
      }
    }()
  }
  ,
  50790: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = {
      container: "xWPMYXKp",
      header: "as6Is8fx",
      rightContent: "jBznOiN_",
      electronDrag: "cZXI0Cgq",
      pushMessageEntry: "LI3Qb5Gw",
      fixed: "gOSlkVoB",
      electron: "Hdnzr7ZA",
      headerNoDragArea: "JmGtWqk3",
      electronMacInner: "fKioNiHC",
      pwaDivider: "M2OddgI4",
      imModalVideo: "aGIMqkll",
      grayscale: "adeS852H",
      activity: "AKgRu2ef",
      blur: "P6UP3mPi",
      isSpringSkin: "fi8E3e7M",
      skinBack: "ELcL6mXw",
      logoCt: "wTSNJym2",
      logo: "sfZOz62F",
      detailLogoText: "w5sOx18c",
      searchCt: "pYtLoHol",
      searchBar: "k11STNQn",
      newSearchBar: "ZGEpVbMV",
      searchBlank: "tKyfsEFi",
      searchPageCt: "mUJ88uHM",
      searchClientCt: "y0FTTWsE",
      searchMacClientCt: "RdAaa7_1",
      searchClientWithButtonCt: "rqd7Ul5q",
      searchMacClientWithButtonCt: "C1feNZqc",
      menuCt: "cA2cEKVo",
      floatRight: "HGpANr58",
      isVsHeader: "Eg06iJ0B",
      transmode: "kjFbeAlu",
      isNormalHeader: "imItpCwi",
      fadeIn: "LCZkAaJx",
      searchBarCenterLayout: "cSbcB2l6"
    }
  }
  ,
  74474: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = {
      isLight: "sPU39i5w",
      dark: "VbKfIC0z",
      isDark: "dPxYKMxc",
      container: "iwzpXgQ3",
      isVsHeader: "sAwvCdl4",
      transmode: "y_0iP_ba",
      header: "ePAmHZ9n",
      rightContentInner: "y4Jb5f1C",
      electronDrag: "co6fXiMO",
      pushMessageEntry: "WvX0NZjv",
      fixed: "oJArD0aS",
      searchLightActivity: "nkXDuzA4",
      logoCt: "R35PYAeO",
      logo: "HFXyaoZL",
      transparentLogo: "xMxzuI6Y",
      foldWrap: "oZVIncTC",
      expandIcon: "Q0OFEVPt",
      searchCt: "gi8dveFW",
      searchBar: "PH5Y_vRb",
      newSearchBar: "bxdD9erE",
      searchBlank: "aAzQ4d0g",
      menuCt: "iqHX00br",
      floatRight: "lC4tlkED",
      rightContent: "IuGYRqPB",
      basicHeight: "s9bzS93E",
      clientRightContent: "YkTBMc6k",
      pwaDivider: "NSjLk5Jn",
      imModalVideo: "du5ElX10",
      activity: "oFLS6cdv",
      transparent: "I7ffFawZ",
      containerNew: "lXuWkeYW",
      isNormalHeader: "DAJOGppR",
      fadeIn: "_fFi1vd0",
      isFixed: "dSNgkU25",
      isVideoOrVsHeader: "nsv2qaIn",
      isSearchHeader: "C3PgeKkg",
      grayscale: "lDy0g1sc",
      rightContentInnerNew: "GSBPs9bN",
      foldable: "OaUEPdOk",
      searchBarCenterLayout: "K4TZD9ct"
    }
  }
  ,
  2758: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = {
      avatar: "v6b8U9mW",
      hoverPolyfill: "NJCJidcf",
      hoverBlackPolyfill: "_myc7NDE",
      clientSvg: "TFMeIANk",
      clientSvg2: "cKEjosjb",
      container: "S4fezOdY",
      more: "iZmyqmpk",
      menuIcon: "f0BIEwpd",
      activity: "XwAZh_Qf",
      vsTransMode: "IEfHgwYQ",
      transparent: "npBKtGqQ",
      circleLoginAva: "f5lbMjoD",
      avataUserMini: "UrwnwwQf",
      imPlaceHolder: "OoYjm8w7",
      publishSub: "g_Fuugpm",
      downloadGuideMini: "QheX_ba3",
      guidePanel: "dXmr_wXe",
      menu: "Btx_YQcJ",
      isActivity: "g7C0zLp1",
      createMenu: "SEV11UjY",
      explictShow: "K6rPMPcS",
      loginSub: "aWPyBtLA",
      downloadGuide: "Z4LwukWk",
      userMenuPanelCollect: "qisYjt2z",
      userMsgBox: "pA5nqHCZ",
      userMsgWrap: "o4uqW09b",
      userMsg: "n8V_sfme",
      title: "OFQ_Yb0Z",
      count: "ylJtd3fY",
      countText: "qNPS41BS",
      verticalDivider: "mcbDmOpc",
      userMsgPanel: "NljuyTiL",
      userMsgPanelLogout: "PgyU4yAD",
      userMenuPanelNoCollect: "N3tuKnpn",
      hoverBold: "y94wMITO",
      hoverEnlarge: "jhaTpFsr",
      loginBtnWrapper: "_p4XfyuB",
      loginBtnWrapperNew: "VEvSk9tg",
      miniMenuDropdownContainer: "tkAiNdhA",
      active: "IU2NTosY",
      shadowChange: "VXadlSgn",
      overflowChange: "tYnHvPel",
      menuSub: "Tpw1XZrP",
      dropDownListInCenterChange: "aDdXLA_O",
      miniHomeMenu: "Zb_UAvVr",
      avataUserCt: "zZCTxOgu",
      dropdownContainer: "LhQ4swYG",
      oldactive: "dvyAI5v1",
      userMenuSub: "V4Yzxf_I",
      year100: "FI9iatGG",
      publishCt: "qC6TbH1B",
      aboutHome: "DFt22uBj",
      publishBtn: "ngsLPe6d",
      loginBtn: "Rgs0Nduq",
      isVsTabTrans: "SoR_03Wj",
      downloadMenu: "HHaCi3G_",
      userPanelCollect: "G8y4xI1l",
      narrowMargin: "zUSFk0DZ",
      show: "EpuHNq8Q",
      hidden: "PGkRWDIK",
      newHeaderContainer: "MFb3tP0s",
      menuItem: "JTui1eE0",
      menuItemContent: "IJoYqlbD",
      clientHeaderContainer: "X4Jhp3H6",
      downloadMenuUl: "OCnIecKb",
      clientAvatarLi: "FdrrUXA3",
      clientAvatr: "_lSBtPda",
      springBtnGg: "uYeOUShg",
      clientAvataUserCt: "i_w6to1W",
      goToRecommendTipWrapper: "f2_Mwi9E",
      goToRecommendTip: "Audm_4ET",
      delta: "iuuJYj1A",
      buttonWithTextContainer: "_bpGHYWu",
      imEntryWrapper: "sbsB1MYq",
      isLogout: "k0LXUXqM",
      miniScreenCooperationDropdownContainerFirstLevel: "wGeFVhGV",
      isLogin: "SkmaEi5R",
      miniScreen: "JumcTCiA",
      wideScreen: "y8n88fK5",
      wideAndMiniScreen: "y8pluWpo",
      inPageWithBackToHome: "E79LoGmO",
      miniScreenCooperationDropdownContainer: "bsFS1Fty",
      buttonNoTextContainer: "XG6cC33C",
      textLinkContainer: "mRBPvSuV",
      fixedToHeaderBelow: "IRX9e_93",
      originMiniScreenDownloadGuideContainer: "L4O8Mf7F",
      originHoverToShowMiniDownloadGuideFixed: "cHBb3E3F",
      originHoverToShowMiniDownloadGuide: "E2KK2Set",
      originDownloadText: "EHPkQyNo",
      miniScreenDownloadGuideContainer: "AzEUH_xb",
      hoverToShowMiniDownloadGuideContainer: "PDlxIZNW",
      hoverToShowMiniDownloadGuide: "bB4zzJJ0",
      flexColumnCenter: "uaGzVRKT",
      originHoverToSHowDownloadGuideBadge: "winAxbAY",
      conversationDtailAnimationKeyframes: "p3ICCmZo",
      dropDownListInNoCenterChange: "HJ9t1u6K",
      showDeleteAllMessageModal: "Kk7JQFBt",
      dropDownListInNoCenterLeftTopChange: "y3wjFYjy",
      dropDownListOutChange: "JoyQD29U",
      backToHomepage: "pev4TY5l"
    }
  }
  ,
  55717: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = {
      icon: "MOB6aWRv",
      hidden: "d_U4I_82",
      iconDark: "wgiDTgSZ",
      iconLight: "dki5MdEh",
      tab: "fuy_wmct",
      textWrap: "Hn1a7lpc",
      yellowPoint: "BR0rQm90",
      redPoint: "Oxwxk5t9",
      newRedPoint: "RDH0PrmQ",
      liveRedPoint: "d96_zlEE",
      numberYellowPoint: "wnWWZubH",
      moreCount: "BxYyDMoK",
      numberRedPoint: "vXRPN9Nt",
      numberYellowPointPosText2: "xkdCyo8O",
      numberYellowPointPosText3: "PZM366wi",
      digitsNumberYellowPoint: "HVgmsdv9",
      digitsNumberRedPoint: "tJShiVlw",
      text: "xPz2YtoZ",
      activeClickable: "fFvA7aLB",
      itemLink: "qShuAbdm",
      active: "LXX79le5",
      borderNone: "wfyh1Wz6",
      searchTabWrap: "RWHJXAjL",
      isFold: "HXp7qYMY"
    }
  }
  ,
  7829: (e,t,n)=>{
    n.d(t, {
      Z: ()=>r
    });
    const r = {
      entryImg: "Fl0kqiow",
      activity: "hxObzeVk",
      vsTransMode: "o2d9ZsaW",
      transparent: "yfKWg9Sv",
      popNum: "cNAhsrSo",
      PopStyle: "IyJcvQVk",
      digitsNumberPop: "zMJW4Vx0",
      numberPoint: "Ri4zG0dK",
      newCharacterPop: "QrMYjyZV",
      imLoginGuidePanelWrapper: "S2flOjWR",
      imLoginGuidePanel: "MYCMYVH1",
      dropDownListInCenterChange: "t7l_Fkw4",
      desc: "B5vV1GJY",
      loginBtn: "llyXa0VC",
      circleButtonNoText: "lSs8pUz9",
      polymorphicButton: "FxXQWshl",
      cicleButtonWithText: "ijmpbxwC",
      textLink: "w_t2UeQ0",
      shadowChange: "ajqDqrxY",
      overflowChange: "nCsrzcNJ",
      conversationDtailAnimationKeyframes: "PJOQYpeI",
      dropDownListInNoCenterChange: "yMugd459",
      showDeleteAllMessageModal: "R4c0llcJ",
      dropDownListInNoCenterLeftTopChange: "rnhULFrG",
      dropDownListOutChange: "czkoyWDk"
    }
  }
  ,
  68378: e=>{
    e.exports = JSON.parse('{"v":"5.6.10","fr":25,"ip":24,"op":92,"w":306,"h":200,"nm":"\u5927\u5934\u718a\u732b\u4ea4\u4ed8-\u5408\u5e76\u56fe\u5c42","ddd":0,"assets":[{"id":"image_0","w":68,"h":66,"u":"images/","p":"img_0.png","e":0},{"id":"image_1","w":10,"h":10,"u":"images/","p":"img_1.png","e":0},{"id":"image_2","w":22,"h":21,"u":"images/","p":"img_2.png","e":0},{"id":"image_3","w":49,"h":49,"u":"images/","p":"img_3.png","e":0},{"id":"image_4","w":10,"h":10,"u":"images/","p":"img_4.png","e":0},{"id":"image_5","w":22,"h":21,"u":"images/","p":"img_5.png","e":0},{"id":"image_6","w":50,"h":48,"u":"images/","p":"img_6.png","e":0},{"id":"image_7","w":130,"h":78,"u":"images/","p":"img_7.png","e":0},{"id":"image_8","w":25,"h":19,"u":"images/","p":"img_8.png","e":0},{"id":"image_9","w":20,"h":14,"u":"images/","p":"img_9.png","e":0},{"id":"image_10","w":163,"h":144,"u":"images/","p":"img_10.png","e":0},{"id":"image_11","w":47,"h":43,"u":"images/","p":"img_11.png","e":0},{"id":"image_12","w":45,"h":46,"u":"images/","p":"img_12.png","e":0},{"id":"image_13","w":83,"h":120,"u":"images/","p":"img_13.png","e":0},{"id":"comp_0","layers":[{"ddd":0,"ind":1,"ty":2,"nm":"right eye","parent":2,"refId":"image_1","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.99},"o":{"x":0.901,"y":0.005},"t":25,"s":[8,10,0],"to":[0.417,0.042,0],"ti":[-0.417,-0.042,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.167,"y":0.167},"t":36,"s":[10.5,10.25,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":65,"s":[10.5,10.25,0],"to":[-0.417,-0.042,0],"ti":[0.417,0.042,0]},{"t":77,"s":[8,10,0]}],"ix":2},"a":{"a":0,"k":[5,5,0],"ix":1},"s":{"a":1,"k":[{"i":{"x":[0.438,0.438,0.438],"y":[1.01,1.01,1]},"o":{"x":[0.901,0.901,0.901],"y":[-0.005,-0.005,0]},"t":25,"s":[100,100,100]},{"i":{"x":[0.438,0.438,0.438],"y":[1,1,1]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":36,"s":[163,163,100]},{"i":{"x":[0.833,0.833,0.833],"y":[1,1,1]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":65,"s":[163,163,100]},{"t":77,"s":[100,100,100]}],"ix":6}},"ao":0,"ip":-4,"op":334,"st":109,"bm":0},{"ddd":0,"ind":2,"ty":2,"nm":"right white eye","parent":3,"refId":"image_2","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.99},"o":{"x":0.901,"y":0.005},"t":25,"s":[19,24.5,0],"to":[0.833,0.083,0],"ti":[-0.833,-0.083,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[24,25,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[24,25,0],"to":[-0.833,-0.083,0],"ti":[0.833,0.083,0]},{"t":74,"s":[19,24.5,0]}],"ix":2},"a":{"a":0,"k":[11,10.5,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":3,"ty":2,"nm":"right black","parent":10,"refId":"image_3","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.998},"o":{"x":0.901,"y":0.001},"t":25,"s":[117.5,73.5,0],"to":[0.25,-1.333,0],"ti":[-0.25,1.333,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[119,65.5,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[119,65.5,0],"to":[-0.25,1.333,0],"ti":[0.25,-1.333,0]},{"t":74,"s":[117.5,73.5,0]}],"ix":2},"a":{"a":0,"k":[24.5,24.5,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":4,"ty":2,"nm":"left eye","parent":5,"refId":"image_4","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.991},"o":{"x":0.901,"y":0.004},"t":25,"s":[8,10,0],"to":[0.375,0.208,0],"ti":[-0.375,-0.208,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.167,"y":0.167},"t":36,"s":[10.25,11.25,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":65,"s":[10.25,11.25,0],"to":[-0.375,-0.208,0],"ti":[0.375,0.208,0]},{"t":77,"s":[8,10,0]}],"ix":2},"a":{"a":0,"k":[5,5,0],"ix":1},"s":{"a":1,"k":[{"i":{"x":[0.438,0.438,0.438],"y":[0.99,0.99,1]},"o":{"x":[0.901,0.901,0.901],"y":[0.005,0.005,0]},"t":25,"s":[100,100,100]},{"i":{"x":[0.438,0.438,0.438],"y":[1,1,1]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":36,"s":[163,163,100]},{"i":{"x":[0.833,0.833,0.833],"y":[1,1,1]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":65,"s":[163,163,100]},{"t":77,"s":[100,100,100]}],"ix":6}},"ao":0,"ip":-4,"op":334,"st":109,"bm":0},{"ddd":0,"ind":5,"ty":2,"nm":"left white eye","parent":6,"refId":"image_5","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.99},"o":{"x":0.901,"y":0.005},"t":25,"s":[20,22.5,0],"to":[0.833,0.083,0],"ti":[-0.833,-0.083,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[25,23,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[25,23,0],"to":[-0.833,-0.083,0],"ti":[0.833,0.083,0]},{"t":77,"s":[20,22.5,0]}],"ix":2},"a":{"a":0,"k":[11,10.5,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":6,"ty":2,"nm":"left black","parent":10,"refId":"image_6","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.998},"o":{"x":0.901,"y":0.001},"t":25,"s":[53,58,0],"to":[0.25,-1.333,0],"ti":[-0.25,1.333,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[54.5,50,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[54.5,50,0],"to":[-0.25,1.333,0],"ti":[0.25,-1.333,0]},{"t":77,"s":[53,58,0]}],"ix":2},"a":{"a":0,"k":[25,24,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":7,"ty":2,"nm":"rouge","parent":10,"refId":"image_7","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.996},"o":{"x":0.901,"y":0.002},"t":25,"s":[84,70,0],"to":[0.5,-1.167,0],"ti":[-0.5,1.167,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[87,63,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[87,63,0],"to":[-0.5,1.167,0],"ti":[0.5,-1.167,0]},{"t":77,"s":[84,70,0]}],"ix":2},"a":{"a":0,"k":[65,39,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":8,"ty":2,"nm":"nose","parent":10,"refId":"image_8","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":1,"k":[{"i":{"x":0.438,"y":0.998},"o":{"x":0.901,"y":0.001},"t":25,"s":[82.5,78.5,0],"to":[0.25,-1.5,0],"ti":[-0.25,1.5,0]},{"i":{"x":0.438,"y":0.438},"o":{"x":0.682,"y":0.682},"t":36,"s":[84,69.5,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.411,"y":1},"o":{"x":0.682,"y":0},"t":62,"s":[84,69.5,0],"to":[-0.25,1.5,0],"ti":[0.25,-1.5,0]},{"t":77,"s":[82.5,78.5,0]}],"ix":2},"a":{"a":0,"k":[12.5,9.5,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":9,"ty":2,"nm":"tongue","parent":8,"refId":"image_9","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[11,19,0],"ix":2},"a":{"a":0,"k":[10,7,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"hasMask":true,"masksProperties":[{"inv":false,"mode":"a","pt":{"a":1,"k":[{"i":{"x":0.231,"y":1},"o":{"x":0.551,"y":0},"t":35,"s":[{"i":[[-0.431,-0.356],[-9.5,-2.193],[-2.718,7.326],[11.205,2.587]],"o":[[0.431,0.356],[10.474,2.418],[2.718,-7.326],[-9.308,-2.149]],"v":[[7.24,-11.549],[9.993,6.534],[21.049,-5.795],[14.285,-4.278]],"c":true}]},{"i":{"x":0.213,"y":1},"o":{"x":0.645,"y":0},"t":60,"s":[{"i":[[-0.431,-0.356],[-16.508,-4.068],[-2.718,7.326],[11.205,2.587]],"o":[[0.431,0.356],[10.438,2.572],[2.718,-7.326],[-9.308,-2.149]],"v":[[-2.542,-2.518],[8.249,17.421],[23.671,8.409],[14.285,-4.278]],"c":true}]},{"t":83,"s":[{"i":[[-0.431,-0.356],[-9.5,-2.193],[-2.718,7.326],[11.205,2.587]],"o":[[0.431,0.356],[10.474,2.418],[2.718,-7.326],[-9.308,-2.149]],"v":[[7.24,-11.549],[9.993,6.534],[21.049,-5.795],[14.285,-4.278]],"c":true}]}],"ix":1},"o":{"a":0,"k":100,"ix":3},"x":{"a":0,"k":0,"ix":4},"nm":"\u8499\u7248 1"}],"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":10,"ty":2,"nm":"head","refId":"image_10","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":1,"k":[{"i":{"x":[0.438],"y":[1.011]},"o":{"x":[0.167],"y":[0]},"t":25,"s":[-12]},{"i":{"x":[0.289],"y":[0.977]},"o":{"x":[0.682],"y":[0.018]},"t":36,"s":[0]},{"i":{"x":[0.833],"y":[1]},"o":{"x":[0.729],"y":[0.001]},"t":43,"s":[3]},{"i":{"x":[0.289],"y":[0.987]},"o":{"x":[0.682],"y":[0.011]},"t":47,"s":[0]},{"i":{"x":[0.372],"y":[0.993]},"o":{"x":[0.728],"y":[0.025]},"t":51,"s":[3]},{"i":{"x":[0.222],"y":[1.001]},"o":{"x":[0.739],"y":[0.008]},"t":59.815,"s":[0]},{"t":74,"s":[-12]}],"ix":10},"p":{"a":1,"k":[{"i":{"x":0.833,"y":0.833},"o":{"x":0.167,"y":0.167},"t":-14,"s":[79.5,84.5,0],"to":[0,0,0],"ti":[0,0,0]},{"t":74,"s":[79.5,84.5,0]}],"ix":2},"a":{"a":0,"k":[81.5,72,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":11,"ty":2,"nm":"ear-l","parent":10,"refId":"image_11","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":1,"k":[{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":25,"s":[0]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":41,"s":[74]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":46,"s":[101]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":52,"s":[50]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":59,"s":[80]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":64,"s":[47]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":69,"s":[80]},{"t":79,"s":[0]}],"ix":10},"p":{"a":1,"k":[{"i":{"x":0.667,"y":1},"o":{"x":0.333,"y":0},"t":25,"s":[48,19,0],"to":[-0.375,0.042,0],"ti":[0.375,-0.042,0]},{"i":{"x":0.667,"y":0.667},"o":{"x":0.333,"y":0.333},"t":36,"s":[45.75,19.25,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.667,"y":1},"o":{"x":0.167,"y":0},"t":70,"s":[45.75,19.25,0],"to":[0.375,-0.042,0],"ti":[-0.375,0.042,0]},{"t":79,"s":[48,19,0]}],"ix":2},"a":{"a":0,"k":[27,29,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":12,"ty":2,"nm":"ear-r","parent":10,"refId":"image_12","sr":1,"ks":{"o":{"a":0,"k":100,"ix":11},"r":{"a":1,"k":[{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":25,"s":[0]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":41,"s":[74]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":46,"s":[100]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":52,"s":[-14]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":59,"s":[32]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":64,"s":[-1]},{"i":{"x":[0.667],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":69,"s":[32]},{"t":79,"s":[0]}],"ix":10},"p":{"a":1,"k":[{"i":{"x":0.667,"y":1},"o":{"x":0.333,"y":0},"t":25,"s":[142,41.5,0],"to":[-0.375,0.042,0],"ti":[0.375,-0.042,0]},{"i":{"x":0.667,"y":0.667},"o":{"x":0.333,"y":0.333},"t":36,"s":[139.75,41.75,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.667,"y":1},"o":{"x":0.167,"y":0},"t":70,"s":[139.75,41.75,0],"to":[0.375,-0.042,0],"ti":[-0.375,0.042,0]},{"t":79,"s":[142,41.5,0]}],"ix":2},"a":{"a":0,"k":[17,27.5,0],"ix":1},"s":{"a":0,"k":[100,100,100],"ix":6}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0}]}],"layers":[{"ddd":0,"ind":1,"ty":2,"nm":"hand-front","refId":"image_0","sr":1,"ks":{"o":{"a":1,"k":[{"i":{"x":[0.833],"y":[0.833]},"o":{"x":[0.167],"y":[0.167]},"t":5,"s":[0]},{"t":7.5,"s":[100]}],"ix":11,"x":"var $bm_rt;\\nfunction quadOut(t, tMin, tMax, value1, value2) {\\n    if (arguments.length !== 5)\\n        return value;\\n    var a = $bm_sub(value2, value1);\\n    var b = $bm_sub(tMax, tMin);\\n    var c = clamp($bm_div($bm_sub(t, tMin), b), 0, 1);\\n    return $bm_sum($bm_mul($bm_mul($bm_neg(a), c), $bm_sub(c, 2)), value1);\\n}\\n;\\nvar animationStartTime = 1;\\nvar animationEndTime = 2;\\nvar startValue = value;\\nvar endValue = $bm_mul(value, 2);\\nif (numKeys > 0) {\\n    var nearestKeyIndex = nearestKey(time).index;\\n    if (key(nearestKeyIndex).time > time)\\n        nearestKeyIndex--;\\n    if (nearestKeyIndex === 0 || nearestKeyIndex === numKeys) {\\n        startValue = endValue = value;\\n    } else {\\n        animationStartTime = key(nearestKeyIndex).time;\\n        animationEndTime = key($bm_sum(nearestKeyIndex, 1)).time;\\n        startValue = key(nearestKeyIndex).value;\\n        endValue = key($bm_sum(nearestKeyIndex, 1)).value;\\n    }\\n}\\n$bm_rt = quadOut(time, animationStartTime, animationEndTime, startValue, endValue);"},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[237,136.5,0],"ix":2},"a":{"a":0,"k":[34,33,0],"ix":1},"s":{"a":1,"k":[{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":5,"s":[60,60,100]},{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":7.5,"s":[70,90,100]},{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":10,"s":[100,91.111,100]},{"t":12,"s":[100,100,100]}],"ix":6,"x":"var $bm_rt;\\nfunction quadOut(t, tMin, tMax, value1, value2) {\\n    if (arguments.length !== 5)\\n        return value;\\n    var a = $bm_sub(value2, value1);\\n    var b = $bm_sub(tMax, tMin);\\n    var c = clamp($bm_div($bm_sub(t, tMin), b), 0, 1);\\n    return $bm_sum($bm_mul($bm_mul($bm_neg(a), c), $bm_sub(c, 2)), value1);\\n}\\n;\\nvar animationStartTime = 1;\\nvar animationEndTime = 2;\\nvar startValue = value;\\nvar endValue = $bm_mul(value, 2);\\nif (numKeys > 0) {\\n    var nearestKeyIndex = nearestKey(time).index;\\n    if (key(nearestKeyIndex).time > time)\\n        nearestKeyIndex--;\\n    if (nearestKeyIndex === 0 || nearestKeyIndex === numKeys) {\\n        startValue = endValue = value;\\n    } else {\\n        animationStartTime = key(nearestKeyIndex).time;\\n        animationEndTime = key($bm_sum(nearestKeyIndex, 1)).time;\\n        startValue = key(nearestKeyIndex).value;\\n        endValue = key($bm_sum(nearestKeyIndex, 1)).value;\\n    }\\n}\\n$bm_rt = quadOut(time, animationStartTime, animationEndTime, startValue, endValue);"}},"ao":0,"ip":-36,"op":230,"st":5,"bm":0},{"ddd":0,"ind":2,"ty":0,"nm":"l","refId":"comp_0","sr":1,"ks":{"o":{"a":1,"k":[{"i":{"x":[0.833],"y":[0.833]},"o":{"x":[0.167],"y":[0.167]},"t":12,"s":[0]},{"t":15,"s":[100]}],"ix":11},"r":{"a":0,"k":0,"ix":10},"p":{"a":0,"k":[153,196,0],"ix":2},"a":{"a":0,"k":[78,187,0],"ix":1},"s":{"a":1,"k":[{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":12,"s":[80,80,100]},{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":15,"s":[90,104,100]},{"i":{"x":[0.833,0.833,0.833],"y":[0.833,0.833,0.833]},"o":{"x":[0.167,0.167,0.167],"y":[0.167,0.167,0.167]},"t":21,"s":[102,98.5,100]},{"t":25,"s":[100,100,100]}],"ix":6,"x":"var $bm_rt;\\nvar animationStartTime = 1;\\nvar animationEndTime = 2;\\nvar startValue = value;\\nvar endValue = $bm_mul(value, 2);\\nif (numKeys > 0) {\\n    var nearestKeyIndex = nearestKey(time).index;\\n    if (key(nearestKeyIndex).time > time)\\n        nearestKeyIndex--;\\n    if (nearestKeyIndex === 0 || nearestKeyIndex === numKeys) {\\n        startValue = endValue = value;\\n    } else {\\n        animationStartTime = key(nearestKeyIndex).time;\\n        animationEndTime = key($bm_sum(nearestKeyIndex, 1)).time;\\n        startValue = key(nearestKeyIndex).value;\\n        endValue = key($bm_sum(nearestKeyIndex, 1)).value;\\n    }\\n}\\n$bm_rt = easeOut(time, animationStartTime, animationEndTime, startValue, endValue);"}},"ao":0,"w":168,"h":156,"ip":0,"op":9999,"st":0,"bm":0},{"ddd":0,"ind":3,"ty":2,"nm":"hand-inside 2","refId":"image_13","sr":1,"ks":{"o":{"a":1,"k":[{"i":{"x":[0.833],"y":[0.833]},"o":{"x":[0.167],"y":[0.167]},"t":7,"s":[0]},{"t":9.5,"s":[100]}],"ix":11},"r":{"a":1,"k":[{"i":{"x":[0.833],"y":[1]},"o":{"x":[0.167],"y":[0]},"t":25,"s":[-14]},{"i":{"x":[0.289],"y":[0.994]},"o":{"x":[0.682],"y":[0.005]},"t":36,"s":[-14]},{"i":{"x":[0.395],"y":[1.005]},"o":{"x":[0.729],"y":[0]},"t":41,"s":[-0.833]},{"i":{"x":[0.401],"y":[1]},"o":{"x":[0.821],"y":[-0.003]},"t":46,"s":[-21.949]},{"i":{"x":[0.075],"y":[1]},"o":{"x":[0.333],"y":[0]},"t":51,"s":[0]},{"i":{"x":[0.833],"y":[1]},"o":{"x":[0.167],"y":[0]},"t":59,"s":[-24.862]},{"t":68,"s":[-14]}],"ix":10},"p":{"a":1,"k":[{"i":{"x":0.564,"y":1},"o":{"x":0.184,"y":0},"t":25,"s":[107,138.5,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.841,"y":1},"o":{"x":0.377,"y":0},"t":36,"s":[108.5,131.5,0],"to":[0,0,0],"ti":[0,0,0]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":59,"s":[107,138.5,0],"to":[1.417,1.333,0],"ti":[0,0,0]},{"t":68,"s":[107,138.5,0]}],"ix":2},"a":{"a":0,"k":[60.5,100.5,0],"ix":1},"s":{"a":1,"k":[{"i":{"x":[0.833,0.833,0.833],"y":[1,1,1]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":7,"s":[70,70,100]},{"i":{"x":[0.833,0.833,0.833],"y":[1,1,0.913]},"o":{"x":[0.167,0.167,0.167],"y":[0,0,0]},"t":12,"s":[109.794,96.955,100]},{"i":{"x":[0.655,0.572,0.667],"y":[0.292,0.999,1]},"o":{"x":[0.325,0.246,0.333],"y":[-0.92,0.704,0]},"t":25,"s":[109.794,96.955,100]},{"i":{"x":[0.655,0.572,0.667],"y":[1,1,1]},"o":{"x":[0.281,0.333,0.333],"y":[0,0,0]},"t":36,"s":[107.419,125.985,100]},{"i":{"x":[0.833,0.833,0.833],"y":[1,1,1]},"o":{"x":[0.281,0.333,0.333],"y":[0,0,0]},"t":59,"s":[107.419,125.985,100]},{"t":68,"s":[109.794,96.955,100]}],"ix":6}},"ao":0,"hasMask":true,"masksProperties":[{"inv":false,"mode":"a","pt":{"a":1,"k":[{"i":{"x":0.833,"y":1},"o":{"x":0.901,"y":0},"t":25,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-20.596,6.143],[-2.315,8.382],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.894,-5.039],[2.315,-8.382],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[36.801,87.697],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":26,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-24.77,7.745],[-2.318,8.402],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.827,-5.261],[2.314,-8.382],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[36.83,87.761],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":27,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-28.395,10.555],[-2.365,8.685],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.525,-6.143],[2.298,-8.386],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[37.229,88.642],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":28,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-26.788,9.482],[-2.412,8.968],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.628,-5.842],[2.282,-8.39],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[38.778,89.576],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":29,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-25.18,8.41],[-2.459,9.251],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.731,-5.541],[2.266,-8.394],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[37.887,90.483],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.438,"y":1},"o":{"x":0.167,"y":0},"t":30,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-23.573,7.337],[-2.505,9.534],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.834,-5.24],[2.251,-8.398],[-12.045,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[38.423,91.286],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.682,"y":0},"t":36,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-20.596,6.143],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[16.894,-5.039],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[0.199,108.986],[33.42,95.158],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":38,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-16.268,5.415],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.254],[16.728,-5.568],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[1.137,110.145],[33.751,95.817],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":39,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-19.704,9.131],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[15.996,-7.413],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[2.135,118.749],[35.531,97.305],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":40,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-20.629,10.319],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[15.768,-7.887],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[2.135,118.749],[35.999,97.513],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":41,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-20.629,10.319],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[15.768,-7.887],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[2.135,118.749],[35.511,98.3],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":42,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-20.629,10.319],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[15.768,-7.887],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[2.135,118.749],[35.511,98.3],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":43,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-21.235,9.007],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[19.094,-8.099],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[1.442,116.113],[36.18,96.355],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":44,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-17.398,4.203],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[23.55,-5.689],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-5.01,108.535],[34.09,93.637],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":45,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-28.995,4.4],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[24.897,-3.778],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-5.01,108.535],[33.079,91.402],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":46,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-28.995,4.4],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[24.897,-3.778],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-9.051,105.246],[33.079,91.402],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":48,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-32.584,8.204],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[24.42,-6.149],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-9.051,105.246],[33.079,91.402],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":49,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-37.073,15.255],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[23.287,-9.583],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-7.048,108.353],[35.081,94.509],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":50,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-37.745,18.166],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[22.691,-10.921],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-1.369,126.316],[36.465,95.724],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":51,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-31.552,17.333],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[22.071,-12.125],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-1.369,126.316],[36.465,95.724],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":52,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-32.502,15.477],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[23.927,-11.394],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-1.369,126.316],[36.275,94.528],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":53,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-34.448,10.454],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[28.669,-8.7],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-1.369,126.316],[33.891,92.341],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":54,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-34.745,9.42],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[29.289,-7.941],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-1.369,126.316],[32.595,90.541],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":55,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.254,7.285],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.496,-6.302],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-10.563,108.445],[32.66,89.287],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":56,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.254,7.285],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.496,-6.302],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-10.719,107.742],[32.504,88.584],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":57,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.528,5.806],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[31.8,-5.197],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-11.922,106.631],[31.301,87.473],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":58,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.528,5.806],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[31.8,-5.197],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-11.499,106.797],[31.724,87.639],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":59,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.564,5.584],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.969,-4.863],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-11.71,106.714],[31.513,87.556],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":60,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.564,5.584],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.969,-4.863],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-16.033,99.464],[31.513,87.556],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":61,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-30.751,5.801],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.805,-5.812],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-16.245,103.215],[32.617,86.49],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":62,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-30.751,5.801],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.805,-5.812],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-14.186,106.633],[34.013,86.42],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":63,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-30.862,8.026],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.339,-7.89],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-13.735,105.432],[32.875,86.648],[71.088,73.726],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":65,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-30.963,8.645],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[30.194,-8.43],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-9.001,111.42],[35.555,86.532],[70.884,68.936],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":66,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-35.603,15.655],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[28.697,-12.618],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-15.14,94.609],[30.75,88.319],[70.918,68.292],[49.836,-8.809]],"c":true}]},{"i":{"x":0.833,"y":1},"o":{"x":0.167,"y":0},"t":67,"s":[{"i":[[32.584,1.227],[-3.533,3.255],[-33.857,14.813],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[28.72,-12.566],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-16.492,88.61],[31.145,89.41],[70.868,64.861],[49.836,-8.809]],"c":true}]},{"t":68,"s":[{"i":[[32.584,1.227],[-3.533,3.254],[-30.583,11.707],[-3.541,15.797],[12.045,11.373]],"o":[[-32.584,-1.227],[3.533,-3.255],[29.277,-11.207],[1.902,-8.485],[-12.046,-11.373]],"v":[[10.347,-12.783],[-2.474,116.182],[32.047,88.335],[70.984,67.01],[49.836,-8.809]],"c":true}]}],"ix":1},"o":{"a":0,"k":100,"ix":3},"x":{"a":0,"k":0,"ix":4},"nm":"\u8499\u7248 1"}],"ip":-4,"op":230,"st":5,"bm":0}],"markers":[]}')
  }
}]);
