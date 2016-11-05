'use strict'

var ass_poll = new function() {
    var that = this;

    that.load = function() {
        var t_poll = $('#poll-templ').html();

        $.post('/spt/d/mg/poll', {}, function(res) {
            var i;

            $('#ass_poll').html(Mustache.render(t_poll, res));

            if(res.data != null) {
                for(i = 0; i < res.data.length; i++) {
                    $('[pollid="' + res.data[i].id + '"]').data('poll', res.data[i]);
                }
            }

            $('#ass_poll div.edit > button.submit').on('click', function(e) {
                var id = $('#ass_poll div.edit').attr('pollid');
                if (id == undefined)
                    id = -1;
                var order = parseInt($('#ass_poll div.edit > input.order').val());
                var year = parseInt($('#ass_poll div.edit > input.year').val());
                var subject = $('#ass_poll div.edit > textarea.subject').val();
                var body = $('#ass_poll div.edit > textarea.body').val();

                $.post('/spt/d/mg/poll_add', {
                    'id': id,
                    'order': order,
                    'year': year,
                    'subject': subject,
                    'body': body,
                }, function(res) {
                    reload_page('/spt/ass_poll/');
                });
            });
            $('#ass_poll div.edit > button.cancel').on('click', function(e) {
                reload_page('/spt/ass_poll/');
            });
            $('#ass_poll div.list button.modify').on('click', function(e) {
                var poll = $(this).parent().data('poll');
                $('#ass_poll div.edit').attr('pollid', poll.id);
                $('#ass_poll div.edit > input.order').val(poll.order);
                $('#ass_poll div.edit > input.year').val(poll.year);
                $('#ass_poll div.edit > textarea.subject').val(poll.subject);
                $('#ass_poll div.edit > textarea.body').val(poll.body);
            });
            $('#ass_poll div.list button.delete').on('click', function(e) {
                $.post('/spt/d/mg/poll_del', {
                    'id': $(this).parent().attr("pollid")
                }, function(res) {
                    reload_page('/spt/ass_poll/');
                });
            });
        });
    }; 
}
