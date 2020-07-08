$(function () {
    let $btnSave = $('#btn-pub-group');
    $btnSave.click(function () {
        let $sGroupId = $(this).data('group-id');
        let $sGroupName = $('#group_name').val();
        let $sPermissions = $('#group-permissions').val();
        if (!$sGroupName) {
            message.showError('请输入用户组名称！');
            return
        }
        if (!$sPermissions) {
            message.showError('请选择该用户组的权限');
            return
        }
        let data = {
            'name': $sGroupName,
            'group_permission': $sPermissions
        };
        $.ajax({
            url: $sGroupId ? '/admin/group/' + $sGroupId + '/' : '/admin/group/add/',
            type: $sGroupId ? "PUT" : "POST",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                if ($sGroupId) {
                    fAlert.alertSuccessCallback('用户组更新成功', function () {
                        window.location.href = '/admin/group/';
                    })
                } else {
                    fAlert.alertSuccessCallback('用户组添加成功', function () {
                        window.location.href = '/admin/group/';
                    })
                }
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