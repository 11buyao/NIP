$(() => {
    let $btnSave = $('#save-btn');
    let $sImageUrl = $('.banner-image');
    let $sImageUrlSelect = $('input[name=banner-image-select]');
    let $sTagSelect = $('#category-select');
    let $sNewsSelect = $('#news-select');

    $sImageUrl.click(function () {
        $(this).prev().show();
    });
    $sImageUrlSelect.change(function () {
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
                message.showSuccess('图片添加成功');
                $(_this).parent().next().attr('src', res['data']['image_url'])
            } else {
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

    $sTagSelect.change(function () {
        let sTagId = $(this).val();
        if (sTagId === '0') {
            $sNewsSelect.children('option').remove();
            $sNewsSelect.append(`<option value="0">--请选择文章--</option>`);
            return
        }

        $.ajax({
            url: '/admin/tag/' + sTagId + '/news/',
            type: 'GET'
        }).done(function (res) {
            if (res.errno === '0') {
                $sNewsSelect.children('option').remove();
                $sNewsSelect.append(`<option value="0">--请选择文章--</option>`);
                res.data.news.forEach(function (one_news) {
                    let content = `<option value="${one_news.id}">${one_news.title}</option>`;
                    $sNewsSelect.append(content)
                })
            } else {
                fAlert.alertErrorToast(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    })

    $btnSave.click(function () {
        let $newsId = $sNewsSelect.val();
        let $tagId = $sTagSelect.val();
        let $priority = $('#priority').val();
        let $imageUrl = $sImageUrl.attr('src');
        if (!$sImageUrl) {
            message.showError('请选择轮播图图片');
            return;
        }
        if ($priority === 0 || $tagId === 0 || $newsId === 0) {
            message.showError('优先级、文章分类、文章均要选择')
            return
        }
        let data = {
            'news_id': $newsId,
            'image_url': $imageUrl,
            'priority': $priority
        };
        $.ajax({
            url: '/admin/banner/add/',
            type: 'POST',
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast('轮播图添加成功');
                setTimeout(function () {
                    window.location.href = '/admin/banner';
                }, 1500)
            } else {
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