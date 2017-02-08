'use strict'

var poll = poll || {};

poll.load = function() {
    $.post('/spt/d/poll/get_all', {}, poll.render_data);
};

poll.render_data = function(res) {
    var template = $('#template').html();
    $('#list').html(Mustache.render(template, res));

    poll.init_poll();
    poll.init_close_button();

    ajax_done();
};

poll.init_poll = function() {
    $('#list div.item').on('click', function(e) {
        var poll_item = $(this);
        $('#list').find('div.subject').hide();
        poll_item.addClass('active');
    });
};

poll.init_close_button = function() {
    $('#list button.close').on('click', function(e) {
        var poll_item = $(this).parents('div.item');
        $('#list').find('div.subject').show();
        poll_item.removeClass('active');
        return false;
    });
};
