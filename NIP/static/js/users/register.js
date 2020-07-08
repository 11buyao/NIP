$(function () {
    let $img = $('.form-item .captcha-graph-img img');
    let sImageCodeId = '';
    let isUsernameReady = false,

        isMobileReady = false,
        send_flag = true;
    generate();
    $img.click(generate);

    function generate() {
        sImageCodeId = generateUUID();
        let imageCodeUrl = '/image_code/' + sImageCodeId + '/';
        $img.attr('src', imageCodeUrl)
    }

    // 生成图片UUID验证码
    function generateUUID() {
        let d = new Date().getTime();
        if (window.performance && typeof window.performance.now === "function") {
            d += performance.now(); //use high-precision timer if available
        }
        let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        return uuid;
    }

    let $username = $('#user_name');
    $username.blur(check_username);

    function check_username() {
        isUsernameReady = false;
        send_flag = true;
        let sUsername = $username.val();
        if (sUsername === "") {
            message.showError('用户名不能为空！');
            return;
        }
        if (!(/^[\w_\u4e00-\u9fa5]{2,20}$/).test(sUsername) || sUsername.length > 20 || sUsername.length < 2) {
            message.showError('用户名格式不正确,请重新输入!');
            return;
        }
        $.ajax({
            url: '/username/' + sUsername + '/',
            type: "GET",
            dataType: 'json',
        }).done(function (res) {
            if (res.data.count !== 0) {
                message.showError('【' + res.data.username + '】已注册，请重新输入！');
            } else {
                message.showSuccess('【' + res.data.username + '】可以正常使用');
                isUsernameReady = true;

            }
        }).fail(function () {
            message.showError('服务器异常，请重试！')
        })
    }

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
        if (!(/^1[345789]\d{9}$/).test(sMobile) || sMobile.length != 11) {
            message.showError('手机号格式不正确，请重新输入！');
            return;
        }
        $.ajax({
            url: '/mobile/' + sMobile + '/',
            type: 'GET',
            dataType: 'json',
        }).done(function (res) {
            if (res.data.count === 1) {
                message.showError('【' + res.data.mobile + '】已注册，请重新输入！');

            } else {
                message.showSuccess('【' + res.data.mobile + '】可以正常使用');
                isMobileReady = true;

            }

        }).fail(function () {
            message.showInfo('服务器超时，请重试！')
        })
    }

    //发送短信
    let $smsCodeBtn = $('.form-item .sms-captcha');
    let $imgCodeText = $('#input_captcha');

    $smsCodeBtn.click(function () {
        if (send_flag) {
            send_flag = false;
            if (!isMobileReady) {
                check_mobile();
                return;
            }
            let text = $imgCodeText.val();
            if (!text) {
                message.showError('请填写验证码！');
                return;
            }
            if (!sImageCodeId) {
                message.showError('图片UUID为空！');
                return;
            }
            let sDataParams = {
                'mobile': $mobile.val(),
                'text': text,
                'image_code_id': sImageCodeId
            };
            $.ajax({
                url: '/sms_code/',
                type: "POST",
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

    //注册逻辑
    let $register = $('.form-contain'); //获取注册表单
    $register.submit(function (e) {
        e.preventDefault();
        let sUsername = $username.val();
        let sPassword = $('input[name=password]').val();
        let sPassword_repeat = $('input[name=password_repeat]').val();
        let sMobile = $mobile.val();
        let smsCode = $('#input_smscode').val();

        if (!isUsernameReady) {
            check_username();
            return;
        }
        if (!isMobileReady) {
            check_mobile();
            return
        }
        if ((!sPassword) || (!sPassword_repeat)) {
            message.showError('密码或确认密码不能为空');
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
        if (!smsCode) {
            message.showError('请输入验证码');
            return
        }
        if (!(/^\d{6}$/).test(smsCode)) {
            message.showError('短信验证码格式不正确，必须为6位数字！');
            return
        }
        let sDataParams = {
            'username': sUsername,
            'password': sPassword,
            'password_repeat': sPassword_repeat,
            'mobile': sMobile,
            'smsCode': smsCode
        };
        $.ajax({
            url: '/users/register/',
            type: "POST",
            contentType: 'application/json;charset=utf-8;',
            data: JSON.stringify(sDataParams),
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            dataType: 'json'
        }).done(function (res) {
            if (res.errno === '0') {
                message.showSuccess('恭喜您，注册成功');
                setTimeout(function () {
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
                    console.log(cookieValue);
                    break;
                }
            }
        }
        return cookieValue;
    }
})
;