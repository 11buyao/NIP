// $.fn.navSmartFloat = function () {
//     var position = function (element) {
//         var top = element.position().top,
//             pos = element.css("position");
//         $(window).scroll(function () {
//             var scrolls = $(this).scrollTop();
//             if (scrolls > top) {
//                 $('.header-topbar').fadeOut(0);
//                 if (window.XMLHttpRequest) {
//                     element.css({
//                         position: "fixed",
//                         top: 0
//                     }).addClass("shadow")
//                 } else {
//                     element.css({
//                         top: scrolls
//                     })
//                 }
//             } else {
//                 $('.header-topbar').fadeIn(500);
//                 element.css({
//                     position: pos,
//                     top: top
//                 }).removeClass("shadow")
//             }
//         })
//     };
//     return $(this).each(function () {
//         position($(this))
//     })
// };
$("#navbar").navSmartFloat();

$("img.thumb").lazyload({
    placeholder: "../..static/images/occupying.png",
    effect: "fadeIn"
});
$(".single .content img").lazyload({
    placeholder: "../..static/images/occupying.png",
    effect: "fadeIn"
});
$('[data-toggle="tooltip"]').tooltip();
jQuery.ias({
    history: false,
    container: '.content',
    item: '.excerpt',
    pagination: '.pagination',
    next: '.next-page a',
    trigger: '查看更多',
    loader: '<div class="pagination-loading"><img src="../../static/images/loading.gif" /></div>',
    triggerPageThreshold: 5,
    onRenderComplete: function () {
        $('.excerpt .thumb').lazyload({
            placeholder: '../../static/images/occupying.png',
            threshold: 400
        });
        $('.excerpt img').attr('draggable', 'false');
        $('.excerpt a').attr('draggable', 'false')
    }
});