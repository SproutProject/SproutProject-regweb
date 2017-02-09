'use strict'

var rule_test = rule_test || {};

rule_test.load = function() {
    $.post('/spt/d/rule_test/get_question', {}, rule_test.render_data);
};

rule_test.render_data = function(res) {
    var template = $('#question-templ').html();
    $('#rule_test').html(Mustache.render(template, res));
    rule_test.init_submit_button();
    ajax_done();
};

rule_test.init_submit_button = function() {
    $('button.submit').on('click', function(e) {
        var data = {};
        var question_list = $('div.question');
        for (var i = 0; i < question_list.size(); i++) {
            var qid = $(question_list[i]).attr('qid');
            var aid = $(question_list[i]).find('input:checked').val();
            if (aid == undefined) {
                show_message('尚未完成作答。');
                return;
            }
            data[qid] = aid;
        }

        ajax_start();
        $.post('/spt/d/rule_test/answer', {'data': JSON.stringify(data)}, rule_test.handle_result);
    });
};

rule_test.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('恭喜完成作答！');
        reload_page('/spt/indiv/');
    } else if (res.status == 'WRONG') {
        show_message('答案錯誤！');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('不合法的行為。');
    }
    ajax_done();
};
