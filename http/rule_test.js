'use strict'

var rule_test = new function() {
    var that = this;

    that.load = function() {
        var t_question = $('#question-templ').html();

        $.post('/spt/d/rule_question', {}, function(res) {
            $('#rule_test').html(Mustache.render(t_question, res));

            $('button.submit').on('click', function(e) {
                var data = {};
                var question_list = $('div.question');
                for (var i = 0; i < question_list.size(); i++) {
                    var qid = $(question_list[i]).attr('qid');
                    var aid = $(question_list[i]).find('input:checked').val();
                    if (aid == undefined) {
                        $('span.err-msg').html('尚未完成作答。');
                        return;
                    }
                    data[qid] = aid;
                }

                $.post('/spt/d/rule_test', {
                    'data': JSON.stringify(data)
                }, function(res) {
                    if (res.status == 'SUCCESS') {
                        alert('恭喜完成作答！');
                        window.location = '/spt/indiv/';
                    }
                    else if (res.status == 'WRONG')
                        $('span.err-msg').html('答案錯誤！');
                    else if (res.status == 'ERROR')
                        $('span.err-msg').html('系統錯誤！');
                });
            });
        });
    };
}