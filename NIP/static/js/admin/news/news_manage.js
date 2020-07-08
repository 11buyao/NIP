$(function () {
    let $startTime = $("input[name=start_time]");
    let $endTime = $("input[name=end_time]");
    const config = {
        // 自动关闭
        autoclose: true,
        // 日期格式
        format: 'yyyy/mm/dd',
        // 选择语言为中文
        language: 'zh-CN',
        // 优化样式
        showButtonPanel: true,
        // 高亮今天
        todayHighlight: true,
        // 是否在周行的左侧显示周数
        calendarWeeks: true,
        // 清除
        clearBtn: true,
        // 0 ~11  网站上线的时候
        startDate: new Date(2018, 10, 1),
        // 今天
        endDate: new Date(),
    };
    $startTime.datepicker(config);
    $endTime.datepicker(config);
    let $btnClear = $('#btn-clear');
    $btnClear.click(function () {
        let $title = $('input[name=title]');
        let $author = $('input[name=author_name]');
        let $tagId = $('select[name=tag_id]');
        $startTime.val("");
        $endTime.val("");
        $title.val("");
        $author.val("");
        $tagId.val("");
    });

    //输入跳转页面
    let $btnMove = $('#btn-move');
    $btnMove.click(function () {
        let page = $('#input-move').val();
        let other_params = $('#input-move').data('other_params').split('&');
        let start_time =
            other_params[0].split('=')[-1] === undefined ? '' : other_params[0].split('=')[-1];
        let end_time = other_params[1].split('=')[-1] === undefined ? '' : other_params[1].split('=')[-1];
        let title = other_params[2].split('=')[-1] === undefined ? '' : other_params[2].split('=')[-1];
        let author = other_params[3].split('=')[-1] === undefined ? '' : other_params[3].split('=')[-1];
        let tag_id = other_params[4].split('=')[-1] === undefined ? 0 : other_params[4].split('=')[-1];
        window.location.href = '/admin/news/?page=' + page + '&start_time=' + start_time + '&end_time=' + end_time +
            '&title=' + title + '&author=' + author + '&tag_id=' + tag_id;
    });
    //批量删除文章标签
    let $tagBatchDel = $('#btn-del');
    $tagBatchDel.click(function () {
        let $data_id = [];
        let $tab = $('table')[0];
        for (let i = 1; i < $tab.rows.length; i++) {
            if ($('.check')[i].className.indexOf('fa-check-square') > 0) {
                $data_id.push(parseInt($('.check').parents('tr')[$('.check').parents('tr').length - i - 1].dataset.id, 10))
            }
        }
        let sData = {
            'news_id': $data_id
        };
        $.ajax({
            url: '/admin/news/',
            type: 'DELETE',
            data: JSON.stringify(sData),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('所有选中的文章删除成功');
                setTimeout(function () {
                    window.location.reload()
                }, 1000)
            }
            else {
                fAlert.alertErrorToast(res.errmsg)
                if (res.data.redirect_url) {
                    setTimeout(function () {
                        window.location.href = res.data.redirect_url;
                    }, 1500)
                }
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });
    //单个删除分类标签
    let $tagDel = $('.btn-del');
    $tagDel.click(function () {
        let _this = this;
        let sNewsId = $(this).parents('tr').data('id');
        let sNewsTitle = $(this).parents('tr').data('name');
        fAlert.alertConfirm({
            title: '确认删除【' + sNewsTitle + '】吗？',
            type: 'error',
            confirmCallback: function confirmCallback() {
                let sData = {
                    'news_id': sNewsId
                };
                $.ajax({
                    url: '/admin/news/',
                    type: "DELETE",
                    data: JSON.stringify(sData),
                    dataType: 'json',
                    contentType: 'application/json;charset=utf-8'
                }).done(function (res) {
                    if (res.errno === '0') {
                        fAlert.alertSuccessToast('删除【' + sNewsTitle + '】成功');
                        $(_this).parents('tr').remove();
                    }
                    else {
                        fAlert.alertErrorToast(res.errmsg);
                        if (res.data.redirect_url) {
                            setTimeout(function () {
                                window.location.href = res.data.redirect_url;
                            }, 1500)
                        }
                    }
                }).fail(function () {
                    message.showError('服务器超时，请重试')
                })
            }
        })
    });

    // get cookie using jQuery
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    // Setting the token on the AJAX request
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

});