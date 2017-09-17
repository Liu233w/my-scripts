// ==UserScript==
// @name        增加二维码弹框面积
// @namespace   appadmin.liu233w.com
// @match     https://portal.shadowsocks.la/clientarea.php*
// @version     1
// @grant       none
// ==/UserScript==
$('body').bind('DOMNodeInserted', function () {
  let frame = $('.layui-layer')
  frame.css('width', '400px')
  frame.css('height', '500px')
})
