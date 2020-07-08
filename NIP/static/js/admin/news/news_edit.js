$(function () {
    //图片上传到fdfs服务器
    let $upload = $('#upload-news-thumbnail');
    let $Image_url = $('#news-thumbnail-url');
    $upload.change(function () {
        let file = this.files[0];
        let sFormData = new FormData();
        sFormData.append('image_files', file);

        $.ajax({
            url: '/admin/upload/',
            type: "POST",
            data: sFormData,
            processData: false,
            contentType: false,
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast(res.errmsg);

                $Image_url.val(res['data']['image_url']);
            }
            else fAlert.alertErrorToast(res.errmsg)
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });
    //文章发布
    let $btn_pub = $('#btn-pub-news');
    $btn_pub.click(function () {
        let title = $('#news-title').val();
        let digest = $('#news-desc').val();
        let tag = $('#news-category').val();
        let image_url = $('#news-thumbnail-url').val();
        let content = $('.markdown-body').html();
        if (!title) {
            message.showError('请输入标题');
            return
        }
        if (!digest) {
            message.showError('请输入摘要');
            return
        }
        if (!tag || tag === '0') {
            message.showError('请选择文章分类');
            return
        }
        if (!image_url) {
            message.showError('请上传文章缩略图');
            return
        }
        if (!content || content === '<p><br></p>') {
            message.showError('请编辑文本内容');
            return
        }
        let $news_id = $(this).data('news-id');
        let data = {
            'title': title,
            'digest': digest,
            'tag': tag,
            'image_url': image_url.indexOf('http://') !== -1 ? image_url : 'http://127.0.0.1:8000' + image_url,
            'content': content
        };
        $.ajax({
            url: $news_id ? '/admin/news/' + $news_id + '/' : '/admin/news/pub/',
            type: $news_id ? "PUT" : "POST",
            data: JSON.stringify(data),
            dataType: 'json',
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '0') {
                fAlert.alertSuccessToast(res.errmsg);
                setTimeout(function () {
                    window.location.href = '/admin/news/';
                }, 800)
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