'use strict'

var indiv = new function() {
    var that = this;
    
    that.load = function() {
        var t_login = $('#login-templ').html();
        var j_indiv = $('#indiv');

        $.post('/spt/d/check_login', {}, function(res) {
            if (res.status != 'LOGINED') {
                j_indiv.html(Mustache.render(t_login));

                $('#login').on('click', function(e) {
                    var mail = $('#mail').val();
                    var password = $('#password').val();

                    $.post('/spt/d/login', {
                        'mail': mail,
                        'password': password,
                    }, function(res) {
                        if (res.status == 'SUCCESS')
                            location.reload();
                        else if (res.status == 'FAILED')
                            $('span.err-msg').html('信箱或密碼錯誤！');
                    });
                })
            }
        })
    }
}

