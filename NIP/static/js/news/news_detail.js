$(function () {
    let $zanBtn = $('.zan');
    // let $reply_submit_btn = $('.reply_btn');
    let $comment_btn = $('#comment-submit');

    $('.comment-header h3 span').html($('.comment-item').length);
    $('span.article-meta-comment').html('<i class="glyphicon glyphicon-comment"></i> ' + $('.comment-item').length);
    //回复框显示与隐藏
    $('#comment_list').delegate('span,input', 'click', function () {
        let sClassValue = $(this).prop('class');

        if (sClassValue.indexOf('reply') >= 0) {
            if ($(this).children().length > 0) {
                $(this).next().toggle(200);
            }
            if (sClassValue === 'child-reply') {
                $hr = $(this).parent().parent().next();
            } else {
                $hr = $(this).parent().next();
            }
            if ($hr.css('display') === 'none') {
                $hr.css({'display': 'block'})
            }
            else {
                $hr.css({'display': 'none'})
            }
        }

        if (sClassValue.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle(200);
            $(this).parents('.comment-reply').next().css({'display': 'block'})
        }

        if (sClassValue.indexOf('reply_btn') >= 0) {
            // 获取新闻id、评论id、评论内容
            let $this = $(this);
            let news_id = $this.parent().attr('news-id');
            let parent_id = $this.parent().attr('comment-id');
            let content = $this.prev().val();

            if (!content) {
                message.showError('请输入评论内容！');
                return
            }
            // 定义发给后端的参数
            let sDataParams = {
                "content": content,
                "parent_id": parent_id
            };
            $.ajax({
                url: "/news/" + news_id + "/comments/",
                type: "POST",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(sDataParams),
                dataType: "json",
            })
                .done(function (res) {
                    if (res.errno === "0") {
                        window.location.reload();
                        $this.prev().val('');   // 请空输入框
                        $this.parent().hide();  // 关闭评论框

                    } else if (res.errno === "4101") {
                        // 用户未登录
                        message.showError(res.errmsg);
                        setTimeout(function () {
                            // 重定向到打开登录页面
                            window.location.href = "/user/login/";
                        }, 800)
                    } else {
                        // 失败，打印错误信息
                        message.showError(res.errmsg);
                    }
                })
                .fail(function () {
                    message.showError('服务器超时，请重试！');
                });
        }
    });
    //点赞功能实现
    $zanBtn.click(function () {
        let params = {
            'comment_id': $(this).parent().find('.reply_form').attr('comment-id'),
        };
        let _this = this;
        $.ajax({
            url: '/news/comments/thumbsup/',
            type: 'POST',
            data: JSON.stringify(params),
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json;charset=utf-8',
        }).done(function (res) {
            if (res.errno === '0') {
                $(_this).html(`<span class="zan"><i class="iconfont icon-zan"></i> ` + res.data.clicks + `</span>`);

                if (res.data.is_add) {
                    message.showSuccess('点赞成功');
                    $(_this).css({'color': '#ec7259'})
                }
                else {
                    message.showSuccess('取消赞成功');
                    $(_this).css({'color': '#b0b0b0'})
                }


            } else if (res.errno === '4101') {
                message.showError('请登录后再操作');
                setTimeout(function () {
                    window.location.href = '/users/login/';
                }, 800)
            }
            else {
                message.showError(res.errmsg)
            }
        }).fail(function () {
            message.showError('服务器超时，请重试')
        })
    });


    //评论功能实现
    $comment_btn.click(function (e) {
        e.preventDefault();
        let $content = $('#comment-textarea').val();
        let $news_id = $('#comment-form').attr('news-id');
        if (!$content) {
            message.showError('评论内容不能为空');
            return
        }
        let params = {
            'content': $content,
            'news_id': $news_id
        };
        $.ajax({
            url: '/news/' + $news_id + '/comments/',
            type: "POST",
            data: JSON.stringify(params),
            dataType: "json",
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json;charset=utf-8;'
        }).done(function (res) {
            if (res.errno === '0') {
                window.location.reload();

            }
            else if (res.errno === '4101') {
                message.showError('请先登录再评论');
                setTimeout(function () {
                    window.location.href = '/users/login/';
                }, 800)
            }
            else {
                message.showError(res.errmsg);
            }
        }).fail(function () {
            message.showError("服务器超时，请重试")
        })
    });

    //点击播放声音问题
    let $btnB = $('.btn-play');
    var interval;
    $btnB.click(function () {
        let $words = $('article .content').text();
        let $per = $('.sound-select').val();
        let $spd = $('.sound-speed .text').text();
        let $col = $('.sound-column .text').text();
        let $song_length = $('.sound-length').text();
        if (!$per || $per === '0') {
            $per = 4
        }
        if (!$spd) {
            $spd = 5
        }
        if (!$col) {
            $col = 5
        }
        if (!$song_length) {
            $song_length = 0
        }

        let data = {
            'words': $words,
            'per': $per,
            'speed': $spd,
            'column': $col,
            'song_length': $song_length
        };
        $.ajax({
            url: '/voice/',
            type: "POST",
            data: JSON.stringify(data),
            dataType: 'json',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            contentType: 'application/json;charset=utf-8'
        }).done(function (res) {
            if (res.errno === '4101') {
                message.showError('请登录后再操作');
                setTimeout(function () {
                    window.location.href = '/users/login/';
                })
            }
            if (res.errno === '0') {
                let time = res['data']['song_length'];
                if (time === 0) {
                    clearInterval(interval);
                    $('.sound-length').text('');
                    return
                }
                interval = setInterval(function () {
                    if (time === 0) {
                        clearInterval(interval);
                        $('.sound-length').text('');
                    }
                    else {
                        time--;
                        $('.sound-length').text(time);
                    }
                }, 1000)
            }
            else {
                message.showError(res.errmsg)
            }
        })
            .fail(function () {
                message.showError('服务器超时，请重试')
            })
    });
    //进度条动态
    $(function () {
        var tag = false, ox = 0, left = 0, bgleft = 0;
        $('.progress_btn').mousedown(function (e) {
            ox = e.pageX - left;
            tag = true;
        });
        $(document).mouseup(function () {
            tag = false;
        });
        $('.progress_main').mousemove(function (e) {//鼠标移动
            if (tag) {
                console.log(e.pageX);
                left = e.pageX - ox;
                if (left <= 0) {
                    left = 0;
                } else if (left > $(this).parents('div').width()) {
                    left = $(this).width();
                }
                $(this).find('.progress_btn').css('left', left);
                $(this).find('.progress_bar').width(left);
                $(this).find('.text').html(parseInt((left / $(this).width()) * 10));
            }
        });
        $('.progress_bg').click(function (e) {//鼠标点击
            if (!tag) {
                bgleft = $(this).offset().left;
                left = e.pageX - bgleft;
                if (left <= 0) {
                    left = 0;
                } else if (left > $(this).parents('div').width()) {
                    left = $(this).parents('div').width();
                }
                $(this).next().css('left', left);
                $(this).find('.progress_bar').animate({width: left}, $(this).parents('div').width());
                $(this).parent().find('.text').html(parseInt((left / $(this).parents('div').width()) * 10));
            }
        });
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