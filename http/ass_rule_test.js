'use strict'

var ass_rule_test = new function() {
    var that = this;

    that.load = function() {
        var t_question = $('#question-templ').html();

        window.history.replaceState({}, "2017 資訊之芽", "/spt/ass_rule_test/");

        $.post('/spt/d/rule_question', {}, function(res) {
            res.is_answer_value = function() {
                return (this.is_answer) ? 'checked' : '';
            };

            res.description_value = function() {
                return this.description.slice(0, 10) + '...';
            }

            $('#ass_rule_test').html(Mustache.render(t_question, res));
            if (ass_mode_on) resizeSpecial();

            $('button.modify').on('click', function(e) {
                var j_edit = $(this).parent();
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

                $.post('/spt/d/mg/rule_question_add', {
                    'id': qid,
                    'order': order,
                    'description': description,
                    'options': options
                }, function(res) {
                    reload_page('/spt/ass_rule_test/');
                });
            });

            $('button.open').on('click', function(e) {
                var j_edit = $(this).parent().next();
                $('div.edit.active').removeClass('active');
                j_edit.addClass('active');
            });

            $('button.close').on('click', function(e) {
                $('div.edit.active').removeClass('active');
            });

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

            $('div.question > button.delete').on('click', function(e) {
                if (confirm('確認刪除此問題？')) {
                    var qid = $(this).parent().attr('qid');

                    $.post('/spt/d/mg/rule_question_del', {
                        'id': qid
                    }, function(res) {
                        reload_page('/spt/ass_rule_test/');
                    });
                }
            });

            $('div.option > button.delete').on('click', function(e) {
                if (confirm('確認刪除此選項？'))
                    $(this).parent().remove();
            });
        });
    };
}
