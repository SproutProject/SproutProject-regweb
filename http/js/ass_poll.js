'use strict'

var ass_poll = ass_poll || {};

ass_poll.load = function() {
    $.post('/spt/d/poll/get_all', {}, ass_poll.render_data);
};

ass_poll.render_data = function(res) {
    var template = $('#poll-templ').html();
    res.subject_value = function() {
        return this.subject.slice(0, 10) + '...';
    };

    $('#ass_poll').html(Mustache.render(template, res));
    if (ass_mode_on) resizeSpecial();

    ass_poll.init_modify_button();
    ass_poll.init_open_button();
    ass_poll.init_close_button();
    ass_poll.init_delete_button();

    ajax_done();
};

ass_poll.init_modify_button = function() {
    $('button.modify').on('click', function(e) {
        if (confirm('確認修改？')) {
            ass_poll.modify_poll($(this).parent());
        }
    });
};

ass_poll.modify_poll = function(j_edit) {
    var poll_id = j_edit.attr('pollid');
    if (poll_id == undefined)
        poll_id = -1;
    var order = j_edit.find('input.order').val();
    var year = j_edit.find('input.year').val();
    var subject = j_edit.find('textarea.subject').val();
    var body = j_edit.find('textarea.body').val();
    var data = {
        'id': poll_id,
        'order': order,
        'year': year,
        'subject': subject,
        'body': body,
    };

    $.post('/spt/d/poll/add', data, ass_poll.handle_result);
};

ass_poll.init_open_button = function() {
    $('button.open').on('click', function(e) {
        var j_edit = $(this).parent().next();
        $("div.edit.active").removeClass('active');
        j_edit.addClass('active');
    });
};

ass_poll.init_close_button = function() {
    $('button.close').on('click', function(e) {
        $("div.edit.active").removeClass('active');
    });
};

ass_poll.init_delete_button = function() {
    $('button.delete').on('click', function(e) {
        if (confirm('確認刪除？')) {
            var data = {
                'id': $(this).parent().attr('pollid'),
            };

            ajax_start();
            $.post('/spt/d/poll/del', data, ass_poll.handle_result);
        }
    });
};

ass_poll.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        reload_page('/spt/ass_poll/');
    } else if (res.status == 'NOT LOGIN') {
        show_message('尚未登入');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('權限不足。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};