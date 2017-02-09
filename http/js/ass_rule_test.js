'use strict'

var ass_rule_test = ass_rule_test || {};

ass_rule_test.load = function() {
    $.post('/spt/d/rule_test/get_question', {}, ass_rule_test.render_data);
};

ass_rule_test.render_data = function(res) {
    var template = $('#question-templ').html();
    res.is_answer_value = function() {
        return (this.is_answer) ? 'checked' : '';
    };
    res.description_value = function() {
        return this.description.slice(0, 10) + '...';
    }

    $('#ass_rule_test').html(Mustache.render(template, res));
    if (ass_mode_on) resizeSpecial();

    ass_rule_test.init_modify_button();
    ass_rule_test.init_open_button();
    ass_rule_test.init_close_button();
    ass_rule_test.init_delete_button();
    ass_rule_test.init_add_option_button();
    ass_rule_test.init_delete_option_button();

    ajax_done();
};

ass_rule_test.init_modify_button = function() {
    $('button.modify').on('click', function(e) {
        ass_rule_test.modify_quesiton($(this).parent());
    });
};

ass_rule_test.modify_quesiton = function(j_edit) {
    var qid = j_edit.attr('qid');
    if (qid == undefined)
        qid = -1;
    var order = j_edit.find('.order').val();
    var description = j_edit.find('.description').val();

    var options = [];
    var radio_list = j_edit.find('input[type="radio"]');
    var answer_list = j_edit.find('input[type="text"]');
    for (var i = 0; i < radio_list.size(); i++) {
        var element = {'answer': $(answer_list[i]).val()};
        if (radio_list[i].checked)
            element['is_answer'] = 1;
        options.push(element);
    }
    var data = {
        'id': qid,
        'order': order,
        'description': description,
        'options': options
    };

    ajax_start();
    $.post('/spt/d/rule_test/add_question', data, ass_rule_test.handle_result);
};

ass_rule_test.init_open_button = function() {
    $('button.open').on('click', function(e) {
        var j_edit = $(this).parent().next();
        $('div.edit.active').removeClass('active');
        j_edit.addClass('active');
    });
};

ass_rule_test.init_close_button = function() {
    $('button.close').on('click', function(e) {
        $('div.edit.active').removeClass('active');
    });
};

ass_rule_test.init_delete_button = function() {
    $('div.title > button.delete').on('click', function(e) {
        if (confirm('確認刪除此問題？')) {
            var qid = $(this).parent().attr('qid');
            ajax_start();
            $.post('/spt/d/rule_test/del_question', {'id': qid}, ass_rule_test.handle_result);
        }
    });
};

ass_rule_test.init_add_option_button = function() {
    $('button.add_option').on('click', function(e) {
        var last_option = $(this).parent().find('div.option').last();
        var new_option = last_option.clone();
        new_option.find('input[type="radio"]').attr('value', -1);
        new_option.find('input[type="text"]').attr('placeholder', 'answer').val('');
        new_option.find('button.delete').on('click', function(e) {
            if (confirm('確認刪除此選項？'))
                $(this).parent().remove();
        });

        last_option.after(new_option);
    });
};

ass_rule_test.init_delete_option_button = function() {
    $('div.option > button.delete').on('click', function(e) {
        if (confirm('確認刪除此選項？'))
            $(this).parent().remove();
    });
};

ass_rule_test.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        reload_page('/spt/ass_rule_test/');
    } else if (res.status == 'NOT LOGINED') {
        show_message('尚未登入');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('權限不足。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};
