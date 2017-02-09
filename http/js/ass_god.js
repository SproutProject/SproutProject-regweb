'use strict'

var ass_god = ass_god || {};

ass_god.load = function() {
    if (ass_mode_on) resizeSpecial();
    ass_god.init_submit_button();
    ajax_done();
};

ass_god.init_submit_button = function() {
    $('#submit').on('click', function(e) {
        var mail = $('#mail').val();
        var power = $('#power').val();
        var data = {
            'mail': mail,
            'power': power,
        };

        ajax_start();
        $.post('/spt/d/user/set_power', data, ass_god.handle_result);
    });
};

ass_god.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('Done.');
    } else if (res.status == 'NOT LOGIN') {
        show_message('Not login.');
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('You are not ASS god!');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};
