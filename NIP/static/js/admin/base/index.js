$(() => {
    let $check = $('.check');
    //多选框选择
    $check.click(function () {
        if ($(this).attr('id') === 'check') {
            $('.check').toggleClass('fa-check-square');
        }
        else {
            if ($('#check').hasClass('fa-check-square')) {
                $('#check').toggleClass('fa-check-square')
            }
            $(this).toggleClass('fa-check-square');
        }

    });

    let $desc = $('.fa-sort-desc');
    let $asc = $('.fa-sort-asc');
    //降序
    $desc.click(function () {
        alert('这是降序')

    });
    //升序
    $asc.click(function () {
        alert('这是升序')
    });

    function sortAsc(row_index) {
        let data = getData(row_index);
        data.sort(function (a, b) {
            return a - b
        });
        for (let i = 0; i < data.length; i++) {
            $('table')[0].rows[i + 1].cells[$row_index].innerText = data[i];
        }
    }

    function sortDesc(row_index) {
        let data = getData(row_index);
        data.sort(function (a, b) {
            return a - b
        });
        for (let i = 0; i < data.length; i++) {
            $('table')[0].rows[i + 1].cells[$row_index].innerText = data[i];
        }
    }

    //获取排序数据
    function getData(row_index) {
        let $table = $('table')[0];
        let $data_count = [];
        for (let i = 1; i < $table.rows.length; i++) {
            $data_count.push($table.rows[i].cells[row_index].innerText);
        }
        return $data_count
    }
});