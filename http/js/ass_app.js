'use strict'

var ass_app = ass_app || {};

ass_app.load = function() {
    $.post('/spt/d/application/get_all',
        {'class_type': class_type},
        ass_app.render_data
    )
};

ass_app.render_data = function(res) {
    var template = $('#app-templ').html();
    res.title_value = function() {
        var arr = ['C 語法班', 'Python 語法班', '算法班'];
        return arr[class_type - 1];
    }
    res.description_value = function() {
        return this.description.slice(0, 10) + '...';
    }

    $('#ass_app').html(Mustache.render(template, res));
    if (ass_mode_on) resizeSpecial();

    ass_app.init_modify_button();
    ass_app.init_open_button();
    ass_app.init_close_button();
    ass_app.init_delete_button();

    ajax_done();
};

ass_app.init_modify_button = function() {
     $('button.modify').on('click', function(e) {
        if (confirm('確認修改？')) {
            ass_app.update_question($(this).parent());
        }
    });
};

ass_app.update_question = function(j_edit) {
    var app_id = j_edit.attr('appid');
    if (app_id == undefined)
        app_id = -1;
    var order = parseInt(j_edit.find('input.order').val());
    var description = j_edit.find('textarea').val();

    var data = {
        'id': app_id,
        'order': order,
        'class_type': class_type,
        'description': description
    };

    ajax_start();
    $.post('/spt/d/application/update_question', data, ass_app.handle_result);
};

ass_app.init_open_button = function() {
    $('button.open').on('click', function(e) {
        var j_edit = $(this).parent().next();
        $('div.edit.active').removeClass('active');
        j_edit.addClass('active');
    });
};

ass_app.init_close_button = function() {
    $('button.close').on('click', function(e) {
        $('div.edit.active').removeClass('active');
    });
};

ass_app.init_delete_button = function() {
    $('button.delete').on('click', function(e) {
        if (confirm('確認刪除？')) {
            var data = {
                'id': $(this).parent().attr('appid'),
            };

            ajax_start();
            $.post('/spt/d/application/del_question', data, ass_app.handle_result);
        }
    });
};

ass_app.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        reload_page('/spt/ass_app/?type=' + class_type);
    } else if (res.status == 'NOT LOGINED') {
        show_message('尚未登入');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('權限不足。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};
