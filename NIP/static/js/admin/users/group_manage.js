$(function () {
    //批量删除
    let $groupBatchDel = $('#btn-del');
    $groupBatchDel.click(function () {
        let $data_id = [];
        let $tab = $('table')[0];
        for (let i = 1; i < $tab.rows.length; i++) {
            if ($('.check')[i].className.indexOf('fa-check-square') > 0) {
                $data_id.push(parseInt($('.check').parents('tr')[$('.check').parents('tr').length - i - 1].dataset.id, 10))
            }
        }
        let data = {
            'group_list': $data_id
        };
        $.ajax({
            url: '/admin/group/',
            type: 'DELETE',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=urf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('选中的用户组删除成功');
                setTimeout(function () {
                    window.location.reload();
                }, 800);
            } else {
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
    });
    //单个删除
    let $btnDel = $('.btn-del');
    $btnDel.click(function () {
        let _this = this;
        let $sGroupId = $(this).parents('tr').data('id');
        let $sGroupName = $(this).parents('tr').data('name');
        let data = {
            'group_list': $sGroupId
        };
        fAlert.alertConfirm({
            title: '确定删除【' + $sGroupName + '】吗？',
            type: 'error',
            confirmCallback: function () {
                $.ajax({
                    url: '/admin/group/',
                    type: 'DELETE',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: 'application/json;charset=utf-8'
                }).done(function (res) {
                    if (res.errno === '0') {
                        fAlert.alertSuccessToast('用户组删除成功');
                        $(_this).parents('tr').remove()
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
        });

    })

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