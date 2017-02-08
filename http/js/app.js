'use strict'

var app = app || {};

app.load = function() {
    $.post('/spt/d/application/get_all',
        {'class_type': class_type},
        app.render_data
    );
}

app.render_data = function(res) {
    var template = $('#app-templ').html();
    res.title_value = function() {
        var arr = ['C 語法班', 'Python 語法班', '算法班'];
        return arr[class_type - 1];
    }
    $('#app').html(Mustache.render(template, res));

    app.init_submit_button();
    app.init_close_button();

    ajax_done();
}

app.init_submit_button = function() {
    $('button.submit').on('click', function(e) {
        app.submit_data();
    });
}

app.submit_data = function() {
    var app_list = $('div.app');
    var app_data = [];

    for (var i = 0; i < app_list.size(); i++) {
        var id = $(app_list[i]).attr('appid');
        var answer = $(app_list[i]).find('.answer').val();
        app_data.push({'id': id, 'answer': answer});
    }

    ajax_start();

    var data = {
        'class_type': class_type,
        'data': JSON.stringify(app_data)
    }

    $.post('/spt/d/application/answer', data, app.handle_result);
}

app.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('報名資料已成功送出。');
        reload_page('/spt/indiv/');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('尚未完成規則測驗（或前測）。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    } else if (res.status == 'DEADLINE') {
        show_message('報名期限已過！');
    }

    ajax_done();
}

app.init_close_button = function() {
    $('button.close').on('click', function(e) {
        reload_page('/spt/indiv/');
    });
}