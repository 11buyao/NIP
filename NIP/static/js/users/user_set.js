$(function () {
    $('.setted').hover(function () {
        $(this).find('.cancel-bind').css('display', 'inline-block');
    }, function () {
        $(this).find('.cancel-bind').css('display', 'none');
    });
    //更换头像
    let $btnAvatar = $('.btn-hollow input');
    $btnAvatar.change(function () {
        let file = this.files[0];
        let sFormData = new FormData();
        sFormData.append('image_files', file);

        $.ajax({
            'url': '/admin/upload/',
            type: "POST",
            data: sFormData,
            processData: false,
            contentType: false,
        }).done(function (res) {
            if (res.errno === '0') {
                message.showSuccess(res.errmsg);

                $('.avatar img').attr('src', res.data['image_url']);
            }
            else {
                message.showError(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });
    //发送短信验证码
    let $btn_send_msg = $('.btn-in-resend');
    $btn_send_msg.click(function () {
        let $mobile = $('input[name=mobile]').val();
        let $local_mobile = $('.setted div').text();
        if (!$mobile) {
            message.showError('请输入手机号');
            return;
        }
        if (!/^1[345789]\d{9}/.test($mobile)) {
            message.showError('输入的手机号不合法，请重试输入');
            return
        }
        if ($mobile === $local_mobile) {
            message.showError('该手机号已绑定，请更换新的手机号');
            return;
        }
        let data = {
            'mobile': $mobile,
            'flag': 1
        };
        $.ajax({
            url: '/sms_code/',
            type: "PUT",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                message.showSuccess('短信验证码发送成功');
            }
            else {
                message.showError(res.errmsg);
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });
    //更换绑定手机号
    let $btn_change_mobile = $('.sign-in-btn');
    $btn_change_mobile.click(function () {
        let $mobile = $('input[name=mobile]').val();
        let $sms_code = $('input[name=security]').val();
        if (!$mobile) {
            message.showError('请输入手机号');
            return
        }
        if (!/^1[345789]\d{9}/.test($mobile)) {
            message.showError('输入的手机号不合法，请重试输入');
            return
        }
        if (!$sms_code) {
            message.showError('请输入验证码');
            return
        }

        if (!/\d{6}/.test($sms_code)) {
            message.showError('请输入正确的验证码');
            return
        }

        let data = {
            'mobile': $mobile,
            'sms_code': $sms_code
        };
        $.ajax({
            url: '/users/change_mobile/',
            type: 'POST',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utd-8'
        }).done(function (res) {
            if (res.errno === '0') {
                $('.modal-content .close').click();
                $('.setted div').text($mobile.replace($mobile.substring(3, 7), '****'));
                message.showSuccess('手机号修改成功');
            } else {
                message.showError(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })

    });
    //信息保存
    let $btnSave = $('.settings-save');
    $btnSave.click(function () {
        let $sUserName = $('input[name=username]').val();
        let $avatar_url = $('.avatar img').attr('src');

        if (!$sUserName) {
            message.showError('用户名不能为空');
            return
        }
        if (!(/^[\w_\u4e00-\u9fa5]{2,20}/).test($sUserName)) {
            message.showError('用户名格式不正确,请重新输入!');
            return;
        }
        if (!$avatar_url) {
            message.showError('请上传用户图片');
            return
        }
        let data = {
            'username': $sUserName,
            'avatar_url': $avatar_url
        };
        $.ajax({
            url: '/users/fit/',
            type: 'POST',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                $('input[name=username]').val($sUserName);
                $('.avatar img').attr('src', $avatar_url);
                $('.login-box .author img').attr('src', $avatar_url);
                message.showSuccess('用户信息更新成功')
            } else {
                message.showError(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    })


});