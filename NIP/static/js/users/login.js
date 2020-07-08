$(function () {
    let $login = $('.form-contain');
    $login.submit(function (e) {
        e.preventDefault();
        let sUsername = $('input[name=telephone]').val();
        let sPassword = $('input[name=password]').val();
        if (!sUsername) {
            message.showError('请输入用户名');
            return
        }
        if (!/^[\u4e00-\u9fa5\w_]{2,20}/.test(sUsername)) {
            message.showError('用户名格式不正确');
            return
        }
        if (!sPassword) {
            message.showError('请输入密码');
            return
        }
        if (sPassword.length < 6 || sPassword.length > 20) {
            message.showError('密码长度为6-20位');
            return
        }
        let sTatus = $('input[name=remember]').is(':checked');
        let parmas = {
            'username': sUsername,
            'password': sPassword,
            'remember': sTatus,
        };
        $.ajax({
            url: '/users/login/',
            type: 'POST',
            data: JSON.stringify(parmas),
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json;charset=utf-8;'
        }).done(function (res) {
            if (res.errno === '0') {
                message.showSuccess('登录成功');

                setTimeout(() => {
                    console.log(res.data['referer']);
                    if (res.data['referer'] === null || res.data['referer'] === '' || res.data['referer'].indexOf('admin') > 0) {
                        window.location.href = '/';
                    } else {
                        window.location.href = res.data['referer'];
                    }
                }, 1500)
            }
            else {
                message.showError(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
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
});