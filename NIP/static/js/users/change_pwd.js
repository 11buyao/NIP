$(function () {

    let isMobileReady = false,
        send_flag = true;
    let $mobile = $('#mobile');
    $mobile.blur(check_mobile);

    function check_mobile() {
        isMobileReady = false;
        send_flag = true;
        let sMobile = $mobile.val();
        if (sMobile === "") {
            message.showError('手机号为空，请重新输入');
            return;
        }
        if (!(/^1[345789]\d{9}/).test(sMobile)) {
            message.showError('手机号格式不正确，请重新输入！');
            return;
        }
        $.ajax({
            url: '/mobile/' + sMobile + '/',
            type: 'GET',
            dataType: 'json',
        }).done(function (res) {
            if (res.data.count !== 1) {
                message.showError('该手机号未注册，请先注册');
            } else {
                isMobileReady = true;
            }

        }).fail(function () {
            message.showInfo('服务器超时，请重试！')
        })
    }

    //发送短信
    let $smsCodeBtn = $('.form-item .sms-captcha');

    $smsCodeBtn.click(function () {
        if (send_flag) {
            send_flag = false;
            if (!isMobileReady) {
                check_mobile();
                return;
            }

            let sDataParams = {
                'mobile': $mobile.val(),
                'flag': 0

            };
            $.ajax({
                url: '/sms_code/',
                type: "PUT",
                headers: {
                    "X-CSRFToken": getCookie('csrftoken')
                },
                'data': JSON.stringify(sDataParams),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
            }).done(function (res) {
                if (res.errno === "0") {
                    message.showSuccess('短信验证码发送成功');

                    let num = 60;
                    let t = setInterval(function () {
                        if (num === 1) {
                            clearInterval(t);
                            $smsCodeBtn.html('获取短信验证码');
                            send_flag = true;
                        }
                        else {
                            num -= 1;
                            $smsCodeBtn.html(num + "秒")
                        }
                    }, 1000)
                } else {
                    message.showError(res.errmsg);
                    send_flag = true;
                }
            }).fail(function () {
                message.showError('服务器超时，请重试')
            });
        }
    });

    //修改密码逻辑
    let $register = $('.form-contain'); //获取表单
    $register.submit(function (e) {
        e.preventDefault();
        let sMobile = $mobile.val();
        let sOldpassword = $('input[name=old_password]').val();
        let sPassword = $('input[name=password]').val();
        let sPassword_repeat = $('input[name=password_repeat]').val();
        let smsCodeText = $('#input_smscode').val();

        if (!isMobileReady) {
            check_mobile();
            return
        }

        if ((!sPassword) || (!sPassword_repeat) || (!sOldpassword)) {
            message.showError('密码不能为空');
            return
        }
        if (sPassword == sOldpassword) {
            message.showError('新密码和原始密码不能一致');
            return
        }
        if (!/^[a-zA-Z0-9]{6,20}/.test(sPassword)) {
            message.showError('请输入6-20位密码');
            return
        }
        if (sPassword !== sPassword_repeat) {
            message.showError('请确保两次密码输入一致');
            return
        }
        if (!smsCodeText) {
            message.showError('请输入验证码');
            return
        }
        if (!(/^\d{6}$/).test(smsCodeText)) {
            message.showError('短信验证码格式不正确，必须为6位数字！');
            return
        }
        let sDataParams = {
            'mobile': sMobile,
            'old_password': sOldpassword,
            'password': sPassword,
            'password_repeat': sPassword_repeat,
            'smsCodeText': smsCodeText
        };
        $.ajax({
            url: '/users/change_pwd/',
            type: "POST",
            contentType: 'application/json;charset=utf-8;',
            data: JSON.stringify(sDataParams),
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            dataType: 'json'
        }).done(function (res) {
            if (res.errno === '0') {
                message.showSuccess('密码修改成功，请重新登录');
                setTimeout(function () {
                    window.location.href = '/users/login';
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
})
;