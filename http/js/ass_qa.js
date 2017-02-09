'use strict'

var ass_qa = ass_qa || {};

ass_qa.load = function() {
    $.post('/spt/d/qa/get_all', {}, ass_qa.render_data);
};

ass_qa.render_data = function(res) {
    var template = $('#qa-templ').html();
    res.question_value = function() {
        return this.question.slice(0, 10) + '...';
    }

    $('#ass_qa').html(Mustache.render(template, res));
    if (ass_mode_on) resizeSpecial();

    ass_qa.init_modify_button();
    ass_qa.init_open_button();
    ass_qa.init_close_button();
    ass_qa.init_delete_button();

    ajax_done();
};

ass_qa.init_modify_button = function() {
    $('button.modify').on('click', function(e) {
        if (confirm('確認修改？')) {
            ass_qa.modify_qa($(this).parent());
        }
    });
};

ass_qa.modify_qa = function(j_edit) {
    var qa_id = j_edit.attr('qaid');
    if (qa_id == undefined) {
        qa_id = -1;
    }
    var question = j_edit.find('input.question').val();
    var order = parseInt(j_edit.find('input.order').val());
    var answer = j_edit.find('textarea').val();
    var data = {
        'id': qa_id,
        'question': question,
        'answer': answer,
        'order': order
    };
    
    ajax_start();
    $.post('/spt/d/qa/add', data, ass_qa.handle_result);
};

ass_qa.init_open_button = function() {
    $('button.open').on('click', function(e) {
        var j_edit = $(this).parent().next();
        $("div.edit.active").removeClass('active');
        j_edit.addClass('active');
    });
};

ass_qa.init_close_button = function() {
    $('button.close').on('click', function(e) {
        $("div.edit.active").removeClass('active');
    });
};

ass_qa.init_delete_button = function() {
    $('button.delete').on('click', function(e) {
        if (confirm('確認刪除？')) {
            var data = {
                'id': $(this).parent().attr('qaid'),
            };
            ajax_start();
            $.post('/spt/d/qa/del', data, ass_qa.handle_result);
        }
    });
};

ass_qa.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        reload_page('/spt/ass_qa/');
    } else if (res.status == 'NOT LOGINED') {
        show_message('尚未登入');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('權限不足。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};
