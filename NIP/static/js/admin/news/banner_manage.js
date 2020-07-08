$(() => {
    let $btnSave = $('.update-btn');
    let $btnDel = $('.close-btn');
    let $sImageUrl = $('.banner-image');
    let $btnAdd = $('#banner-add-btn');
    let $sImageFileSelect = $('input[name="banner-image-select"]');

    $sImageUrl.click(function () {
        $(this).prev().show();
    });
    $sImageFileSelect.change(function () {
        let _this = this;
        let file = this.files[0];
        let sFormData = new FormData();
        sFormData.append('image_files', file);

        $.ajax({
            url: '/admin/upload/',
            type: 'POST',
            data: sFormData,
            processData: false,
            contentType: false
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('图片上传成功');
                console.log($(_this).next().attr('src'));
                $('.banner-image').attr('src', res['data']['image_url']);
            } else {
                fAlert.alertErrorToast(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });
    //更新轮播图
    $btnSave.click(function () {
        let $sPriority = $(this).parents('li').find('#priority').val();
        let $sBannerId = $(this).parents('li').data('banner-id');
        let $sImageUrl = $(this).parents('li').find('.banner-image').attr('src');

        //当前轮播图优先级和图片url
        let $localImageUrl = $(this).data('image-url');
        let $localPriority = $(this).data('priority');

        if (!$sImageUrl) {
            message.showError('请选择轮播图图片');
            return
        }
        if ($sPriority === $localPriority & $sImageUrl === $localImageUrl) {
            message.showError('未修改任何值');
            return
        }
        let data = {
            'image_url': $sImageUrl,
            'priority': $sPriority
        };
        $.ajax({
            url: '/admin/banner/' + $sBannerId + '/',
            type: "PUT",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('轮播图添加成功');
                setTimeout(function () {
                    window.location.reload();
                }, 800)
            } else {
                fAlert.alertErrorToast(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
            if (res.data.redirect_url) {
                setTimeout(function () {
                    window.location.href = res.data.redirect_url;
                }, 1500)
            }
        })
    });
    //删除轮播图
    $btnDel.click(function () {
        let _this = this;

        let $sBannerId = $(this).parents('li').data('banner-id');
        fAlert.alertConfirm({
            title: '确认删除该轮播图吗？',
            type: 'error',
            showConfirmButton: true,
            confirmCallback: function () {
                $.ajax({
                    url: '/admin/banner/' + $sBannerId + '/',
                    type: "DELETE",
                })
                    .done(function (res) {
                        if (res.errno === '0') {
                            fAlert.alertSuccessToast('轮播图删除成功');
                            setTimeout(function () {
                                $(_this).parents('li').remove();
                            }, 800);
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
            }
        });

    });
    //添加轮播图
    $btnAdd.click(function () {
        if ($('.banner-list').find('li').length < 6) {
            window.location.href = '/admin/banner/add/';
        } else {
            message.showError('轮播图最多允许添加6张');
        }
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