$(function () {
    let $newsLi = $('.trigger-menu li');
    let sCurrentTagId = 0;
    $newsLi.click(function () {
        // alert($(this).text());
        $(this).addClass('active').siblings('li').removeClass('active');
        console.log($(this).data('id'));
        // console.log(this);
        // let sClickTagId = $(this).data('id');
        // if (sClickTagId !== sCurrentTagId) {
        //     sCurrentTagId = sClickTagId;
        // }
    });
});