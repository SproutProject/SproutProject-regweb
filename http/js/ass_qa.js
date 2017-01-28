'use strict'

var ass_qa = new function() {
    var that = this;

    that.load = function() {
        var t_qa = $('#qa-templ').html();

        $.post('/spt/d/qa/get_all', {}, function(res) {
            var i;

            res.question_value = function() {
                return this.question.slice(0, 10) + '...';
            }

            $('#ass_qa').html(Mustache.render(t_qa, res));
            if (ass_mode_on) resizeSpecial();

            $('button.modify').on('click', function(e) {
                if (confirm('確認修改？')) {
                    var j_edit = $(this).parent();
                    var qa_id = j_edit.attr('qaid');
                    if (qa_id == undefined)
                        qa_id = -1;
                    var question = j_edit.find('input.question').val();
                    var order = parseInt(j_edit.find('input.order').val());
                    var answer = j_edit.find('textarea').val();
                    ajax_start();

                    $.post('/spt/d/qa/add', {
                        'id': qa_id,
                        'question': question,
                        'answer': answer,
                        'order': order
                    }, function(res) {
                        reload_page('/spt/ass_qa/');
                    });
                }
            });

            $('button.open').on('click', function(e) {
                var j_edit = $(this).parent().next();
                $("div.edit.active").removeClass('active');
                j_edit.addClass('active');
            });

            $('button.close').on('click', function(e) {
                $("div.edit.active").removeClass('active');
            });

            $('button.delete').on('click', function(e) {
                ajax_start();
                if (confirm('確認刪除？')) {
                    $.post('/spt/d/qa/del', {
                        'id': $(this).parent().attr('qaid'),
                    }, function(res) {
                        reload_page('/spt/ass_qa/');
                    });
                }
            });

            ajax_done();
        });
    }; 
}
