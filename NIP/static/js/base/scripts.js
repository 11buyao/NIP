$('body').show();
$('.version').text(NProgress.version);
NProgress.start();
setTimeout(function () {
    NProgress.done();
    $('.fade').removeClass('out')
}, 1000);
(function () {
    $('img').attr('draggable', 'false');
    $('a').attr('draggable', 'false')
})();


// function getsec(str) {
//     var str1 = str.substring(1, str.length) * 1;
//     var str2 = str.substring(0, 1);
//     if (str2 == "s") {
//         return str1 * 1000
//     } else if (str2 == "h") {
//         return str1 * 60 * 60 * 1000
//     } else if (str2 == "d") {
//         return str1 * 24 * 60 * 60 * 1000
//     }
// }

$("#gotop").hide();
$(window).scroll(function () {
    if ($(window).scrollTop() > 100) {
        $("#gotop").fadeIn()
    } else {
        $("#gotop").fadeOut()
    }
});
$("#gotop").click(function () {
    $('html,body').animate({
        'scrollTop': 0
    }, 500)
});
// # 侧栏固定
$(window).scroll(function () {
    var sidebar = $('.sidebar');
    var sidebarHeight = sidebar.height();
    var windowScrollTop = $(window).scrollTop();
    if (windowScrollTop > sidebarHeight - 60 && sidebar.length) {
        $('.fixed').css({
            'position': 'fixed',
            'top': '70px',
            'width': '360px'
        })
    } else {
        $('.fixed').removeAttr("style")
    }
});




