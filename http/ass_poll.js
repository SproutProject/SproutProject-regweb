'use strict'

var ass_poll = new function() {
    var that = this;

    that.load = function() {
        var t_poll = $('#poll-templ').html();
        var j_ass_poll = $('#ass_poll');

        $.post('/spt/d/mg/poll', {}, function(res) {
            var i;

            $('#ass_poll').html(Mustache.render(t_poll, res));
            if (ass_mode_on) resizeSpecial();

            $('button.modify').on('click', function(e) {
                if (confirm('確認修改？')) {
                    var j_edit = $(this).parent();
                    var poll_id = j_edit.attr('pollid');
                    if (poll_id == undefined)
                        poll_id = -1;
                    var order = j_edit.find('input.order').val();
                    var year = j_edit.find('input.year').val();
                    var subject = j_edit.find('textarea.subject').val();
                    var body = j_edit.find('textarea.body').val();
                    ajax_start();

                    $.post('/spt/d/mg/poll_add', {
                        'id': poll_id,
                        'order': order,
                        'year': year,
                        'subject': subject,
                        'body': body,
                    }, function(res) {
                        reload_page('/spt/ass_poll/');
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
                if (confirm('確認刪除？')) {
                    ajax_start();
                    $.post('/spt/d/mg/poll_del', {
                        'id': $(this).parent().attr('pollid'),
                    }, function(res) {
                        reload_page('/spt/ass_poll/');
                    });
                }
            });

            ajax_done();
        });
    }; 
}
