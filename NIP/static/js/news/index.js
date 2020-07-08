$(function () {
    // 新闻列表功能
    let $newsLi = $(".content .title .more a");
    let iPage = 1;  //默认第1页
    let iTotalPage = 1; //默认总页数为1
    let sCurrentTagId = 0; //默认分类标签为0
    let bIsLoadData = false;   // 是否正在向后台加载数据
    // 加载新闻列表信息
    fn_load_content();
    $newsLi.click(function () {
        $(this).addClass('active').siblings('a').removeClass('active');

        let sClickTagId = $(this).attr('data-id');
        if (sClickTagId !== sCurrentTagId) {
            sCurrentTagId = sClickTagId;
            iPage = 1;
            iTotalPage = 1;
            fn_load_content();
        }
    });
    //页面滚动加载相关
    $(window).scroll(function () {
        // 浏览器窗口高度
        let showHeight = $(window).height();

        // 整个网页的高度
        let pageHeight = $(document).height();

        // 页面可以滚动的距离
        let canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        let nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // 判断页数，去更新新闻数据
            if (!bIsLoadData) {
                bIsLoadData = true;
                // 如果当前页数据如果小于总页数，那么才去加载数据
                if (iPage < iTotalPage) {
                    iPage += 1;
                    $(".btn-more").remove();  // 删除标签
                    // 去加载数据
                    fn_load_content()
                } else {
                    message.showInfo('已全部加载，没有更多内容！');
                    $(".btn-more").remove();  // 删除标签
                    $(".news-list").append($('<a href="javascript:void(0);" class="btn-more">已全部加载，没有更多内容！</a>'))

                }
            }
        }
    });
    // 新闻轮播图功能
    fn_load_banner();
    /*=== bannerStart ===*/
    let $banner = $('#focusslide');
    let $picLi = $("#focusslide .carousel-inner li");
    let $prev = $('#focusslide .prev');
    let $next = $('#focusslide .next');
    let $tabLi = $('#focusslide .carousel-indicators li');
    let index = 0;

    // 小原点
    $tabLi.click(function () {
        index = $(this).index();
        $(this).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    });
    // 点击切换上一张
    $prev.click(function () {
        index--;
        if (index < 0) {
            index = $tabLi.length - 1
        }
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    }).mousedown(function () {
        return false
    });

    $next.click(function () {
        auto();
    }).mousedown(function () {
        return false
    });

    //  图片向前滑动
    function auto() {
        index++;
        index %= $tabLi.length;
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(3000).siblings('li').fadeOut(3000);
    }

    // 定时器
    let timer = setInterval(auto, 2000);
    $banner.hover(function () {
        clearInterval(timer)
    }, function () {
        auto();
    });

    // 定义向后端获取新闻列表数据的请求
    function fn_load_content() {
        // let sCurrentTagId = $('.active a').attr('data-id');

        // 创建请求参数
        let sDataParams = {
            "tag_id": sCurrentTagId,
            "page": iPage
        };

        // 创建ajax请求
        $.ajax({
            // 请求地址
            url: "/news/",  // url尾部需要添加/
            // 请求方式
            type: "GET",
            data: sDataParams,
            // 响应数据的格式（后端返回给前端的格式
        })
            .done(function (res) {
                if (res.errno === "0") {
                    iTotalPage = res.data.total_pages;  // 后端传过来的总页数
                    if (iPage === 1) {
                        $(".news-list").html("")
                    }
                    // 需要修改 href  接收后台传来的id号 响应详情页  /news/${one_news.id}/
                    res.data.news.forEach(function (one_news) {
                        let content = `
                                <article class="excerpt excerpt-1" style="">
                    <a class="focus" href="/news/${one_news.id}/" title="${one_news.title}" target="_blank">
                    <img class="thumb" data-original="${one_news.image_url}" src="${one_news.image_url}" alt="${one_news.title}" style="display: inline;"></a>
                    <header><a class="cat" href="#" title="${one_news.tag_name}">${one_news.tag_name}<i></i></a>
                        <h2><a href="/news/${one_news.id}/" title="${one_news.title}" target="_blank">${one_news.title}</a>
                        </h2>
                    </header>
                    <p class="meta">
                        <time class="time"><i class="glyphicon glyphicon-time"></i> ${one_news.update_time}</time>
                        <span class="views"><i class="glyphicon glyphicon-eye-open"></i> ${one_news.clicks}</span>
                        <a class="comment" href="#" title="评论" target="_blank"><i class="glyphicon glyphicon-comment"></i> 4</a>
                    </p>
                    <p> ${one_news.digest}</p>
                </article>`;
                        $(".news-list").append(content)
                    });
                    // $(".news-list").append($('<a href="javascript:void(0);" class="btn-more">滚动加载更多</a>'));
                    // 数据加载完毕，设置正在加载数据的变量为false，表示当前没有在加载数据
                    for (var i = 0; i < res.data.comment_count.length; i++) {
                        $('.news-list .time')[i].innerHTML = '<i class="glyphicon glyphicon-time"></i> ' + $('.news-list .time')[i].innerText.slice(0, 10);
                        $('.news-list .comment')[i].innerHTML = '<i class="glyphicon glyphicon-comment"></i> ' + res.data.comment_count[i];
                    }

                    bIsLoadData = false;

                } else {
                    // 登录失败，打印错误信息
                    message.showError(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });
    }

    function fn_load_banner() {
        $.ajax({
            // 请求地址
            url: "/news/banners/",  // url尾部需要添加/
            // 请求方式
            type: "GET",
            async: false
        })
            .done(function (res) {
                if (res.errno === "0") {
                    let content = ``;
                    let tab_content = ``;   //按钮
                    res.data.banner.forEach(function (one_banner, index) {
                        if (index === 0) {
                            // 需要修改 href  接收后台传来的id号 响应详情页  one_banner.news_id
                            content = `
                 <div class="item active">
                    <a href="/news/${one_banner.news_id}" target="_blank" title="${one_banner.news_title}">
                        <img src="${one_banner.image_url}" alt="${one_banner.news_title}"
                             class="img-responsive"></a>
                </div>
              `;
                            tab_content = `<li class="active"></li>`;
                        } else {
                            content = `
              <div class="item">
                   <a href="/news/${one_banner.news_id}" target="_blank" title="${one_banner.news_title}">
                        <img src="${one_banner.image_url}" alt="${one_banner.news_title}"
                             class="img-responsive"></a>
                </div>
              `;
                            tab_content = `<li></li>`;
                        }

                        $(".carousel-inner").append(content);  // 内容
                        $(".carousel-indicators").append(tab_content); // 标签
                    });

                } else {
                    // 登录失败，打印错误信息
                    message.showError(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });
    }
});