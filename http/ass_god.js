'use strict'

var ass_god = new function() {
    var that = this;
    
    that.load = function() {
        $('#submit').on('click', function(e) {
            var mail = $('#mail').val();
            var power = $('#power').val();

            ajax_start();
            $.post('/spt/d/mg/set_power', {
                'mail': mail,
                'power': power,
            }, function(res) {
                if (res.status == 'SUCCESS')
                    show_message('Done.');
                else if (res.status == 'FAILED')
                    show_message('You are not ASS god!');
                else if (res.status == 'ERROR')
                    show_message('系統錯誤！');
                ajax_done();
            });
        });

        ajax_done();
    }
}

