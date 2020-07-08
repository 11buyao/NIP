$(function () {
    $('.login_admin').each(function () {
        let $val = $(this).val();
        if ($val === 'True') {
            fn_load_label_from($(this).parent());
        }
    });
    let $isOn = $('.is_on');
    $isOn.click(function () {
        fn_load_label_from($(this));
    });

    function fn_load_label_from(object) {
        object.toggleClass('label-form-onswitch');
        object.find('em').toggleClass('label-form-onswitch em');
        object.find('i').toggleClass('label-form-onswitch i');
        object.find('input').toggleClass('label-form-onswitch i');
        if (object.find('em').text() === '否') {
            object.find('em').text('是');
            object.find('input').val('True');
        }
        else {
            object.find('em').text('否');
            object.find('input').val('False');
        }
    }

    //编辑用户
    let $btnSave = $('#btn-edit-user');
    $btnSave.click(function () {
        let $IsStaff = $('input[name="login_admin"]').val();
        let $IsSuperUser = $('input[name="is_superuser"]').val();
        let $IsActive = $('input[name="is_active"]').val();
        let $IsVIP = $('input[name="is_VIP"]').val();
        let $sUesrId = $(this).data('user-id');
        let $groups = [];
        $('.fa-check-square').each(function () {
            $groups.push($(this).data('group-id'))
        });

        let data = {
            'is_staff': $IsStaff === 'False' ? 0 : 1,
            'is_superuser': $IsSuperUser === 'False' ? 0 : 1,
            'is_active': $IsActive === 'False' ? 0 : 1,
            'is_VIP': $IsVIP === 'False' ? 0 : 1,
            'groups': $groups
        };
        $.ajax({
            url: '/admin/users/' + $sUesrId + '/',
            type: 'PUT',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessCallback('用户权限信息更新成功', function () {
                    window.location.href = '/admin/users/';
                })
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
    //批量删除用户
    let $userBatchDel = $('#btn-del');
    $userBatchDel.click(function () {
        let $data_id = [];
        let $tab = $('table')[0];
        for (let i = 1; i < $tab.rows.length; i++) {
            if ($('.check')[i].className.indexOf('fa-check-square') > 0) {
                $data_id.push(parseInt($('.check').parents('tr')[$('.check').parents('tr').length - i - 1].dataset.id, 10))
            }
        }
        let data = {
            'user_list': $data_id
        };
        $.ajax({
            url: '/admin/users/',
            type: 'DELETE',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=urf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('选中的所有用户均已被删除');
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
        let $sUserId = $(this).parents('tr').data('id');
        let $sUserName = $(this).parents('tr').data('name');
        let data = {
            'user_list': $sUserId
        };
        fAlert.alertConfirm({
            title: '确定删除【' + $sUserName + '】吗？',
            type: 'error',
            confirmCallback: function () {
                $.ajax({
                    url: '/admin/users/',
                    type: 'DELETE',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: 'application/json;charset=utf-8'
                }).done(function (res) {
                    if (res.errno === '0') {
                        fAlert.alertSuccessToast('用户删除成功');
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
    });

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
