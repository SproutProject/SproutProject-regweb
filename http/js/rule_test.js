'use strict'

var rule_test = new function() {
    var that = this;

    that.load = function() {
        var t_question = $('#question-templ').html();

        $.post('/spt/d/rule_test/get_question', {}, function(res) {
            $('#rule_test').html(Mustache.render(t_question, res));

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
                $.post('/spt/d/rule_test/answer', {
                    'data': JSON.stringify(data)
                }, function(res) {
                    if (res.status == 'SUCCESS') {
                        show_message('恭喜完成作答！');
                        reload_page('/spt/indiv/');
                    }
                    else if (res.status == 'WRONG')
                        show_message('答案錯誤！');
                    else if (res.status == 'ERROR')
                        show_message('系統錯誤！');
                    else if (res.status == 'PERMISSION DENIED')
                        show_message('不合法的行為。');                        
                    ajax_done();
                });
            });

            ajax_done();
        });
    };
}
