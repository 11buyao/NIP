$(() => {
    //添加分类标签
    let $tagAdd = $('#btn-add');
    $tagAdd.click(function () {
        fAlert.alertOneInput({
            title: '请输入标签名',
            type: 'input',
            text: '长度限制在20字内',
            placeholder: '请输入标签名',
            confirmCallback: function confirmCallback(inputValue) {
                let sData = {
                    'name': inputValue
                };
                $.ajax({
                    url: "/admin/tag/",
                    type: 'POST',
                    data: JSON.stringify(sData),
                    dataType: 'json',
                    contentType: 'application/json;charset=utf-8;',
                }).done(function (res) {
                    if (res.errno === '0') {
                        fAlert.alertSuccessToast('添加标签成功');
                        setTimeout(function () {
                            window.location.reload()
                        }, 800)
                    }
                    else {
                        swal.showInputError(res.errmsg);
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
    //编辑分类标签
    let $btnEdit = $('.btn-edit');
    $btnEdit.click(function () {
        let _this = this;
        let sTagId = $(this).parents('tr').data('id');
        let sTagName = $(this).parents('tr').data('name');
        fAlert.alertOneInput({
            title: '修改分类名称',
            text: '正在修改 【' + sTagName + '】 分类',
            placeholder: '请输入需要修改的名称',
            confirmCallback: function confirmCallback(inputValue) {
                if (inputValue === sTagName) {
                    swal.showInputError('该分类已存在,请重新输入')
                }
                else {
                    let sData = {
                        'name': inputValue
                    };
                    $.ajax({
                        url: '/admin/tag/' + sTagId + '/',
                        type: "PUT",
                        data: JSON.stringify(sData),
                        dataType: 'json',
                        contentType: 'applicaion/json;charset=utf-8'
                    }).done(function (res) {
                        if (res.errno === '0') {
                            fAlert.alertSuccessToast('分类信息修改成功');
                            $(_this).parents('tr').find('td:nth-child(2)').val(inputValue)
                        }
                        else {
                            swal.showInputError(res.errmsg);
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

            }
        })
    });
    //批量删除分类标签
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
            'tag_id': $data_id
        };
        $.ajax({
            url: '/admin/tag/',
            type: 'DELETE',
            data: JSON.stringify(sData),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('所有选中的分类删除成功');
                setTimeout(function () {
                    window.location.reload()
                }, 1000)
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
    //单个删除分类标签
    let $tagDel = $('.btn-del');
    $tagDel.click(function () {
        let _this = this;
        let sTagId = $(this).parents('tr').data('id');
        let sTagName = $(this).parents('tr').data('name');
        fAlert.alertConfirm({
            title: '确认删除【' + sTagName + '】吗？',
            type: 'error',
            confirmCallback: function confirmCallback() {
                let sData = {
                    'tag_id': sTagId
                };
                $.ajax({
                    url: '/admin/tag/',
                    type: "DELETE",
                    data: JSON.stringify(sData),
                    dataType: 'json',
                    contentType: 'application/json;charset=utf-8'
                }).done(function (res) {
                    if (res.errno === '0') {
                        fAlert.alertSuccessToast('删除【' + sTagName + '】成功');
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