'use strict'

var ass_qa = new function() {
    var that = this;

    that.load = function() {
        var t_qa = $('#qa-templ').html();

        $.post('/spt/d/mg/qa', {}, function(res) {
            var i;

            $('#ass_qa').html(Mustache.render(t_qa, res));

            if (res.data != null) {
                for (i = 0; i < res.data.length; i++) {
                    $('[qaid="' + res.data[i].id + '"]').data('qa', res.data[i]);
                }
            }

            $('#ass_qa div.edit > button.submit').on('click', function(e) {
                var qa_id = $('#ass_qa div.edit').attr('qaid');
                if (qa_id == undefined)
                    qa_id = -1;
                var question = $('#ass_qa div.edit > input.question').val();
                var order = parseInt($('#ass_qa div.edit > input.order').val());
                var answer = $('#ass_qa div.edit > textarea').val();
                console.log(qa_id);
                $.post('/spt/d/mg/qa_add', {
                    'id': qa_id,
                    'question': question,
                    'answer': answer,
                    'order': order
                }, function(res) {
                    reload_page('/spt/ass_qa/');
                });
            });
            $('#ass_qa div.edit > button.cancel').on('click', function(e) {
                reload_page('/spt/ass_qa/');
            });
            $('#ass_qa div.list button.modify').on('click', function(e) {
                var qa = $(this).parent().data('qa');
                $('#ass_qa div.edit').attr('qaid', qa.id);
                $('#ass_qa div.edit > input.question').val(qa.question);
                $('#ass_qa div.edit > input.order').val(qa.order);
                $('#ass_qa div.edit > textarea').val(qa.answer);
            });
            $('#ass_qa div.list button.delete').on('click', function(e) {
                $.post('/spt/d/mg/qa_del', {
                    'id': $(this).parent().attr("qaid"),
                }, function(res) {
                    reload_page('/spt/ass_qa/');
                });
            });
        });
    }; 
}
