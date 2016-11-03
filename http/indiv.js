'use strict'

var indiv = new function() {
    var that = this;
    
    that.load = function() {
        var t_login = $('#login-templ').html();
        var t_forget = $('#forget-templ').html();
        var t_register = $('#register-templ').html();
        var t_indiv_data = $('#indiv-data-templ').html();
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
                        $('#password').val('');
                        if (res.status == 'SUCCESS')
                            location.reload();
                        else if (res.status == 'FAILED')
                            $('span.err-msg').html('信箱或密碼錯誤！');
                        else if (res.status == 'ERROR')
                            $('span.err-msg').html('系統錯誤！');
                    });
                });

                $('#forget').on('click', function(e) {
                    j_indiv.html(Mustache.render(t_forget));

                    $('#submit').on('click', function(e) {
                        var mail = $('#mail').val();

                        $.post('/spt/d/forget', {
                            'mail': mail,
                        }, function(res) {
                            if (res.status == 'SUCCESS')
                                $('span.err-msg').html('已發送修改密碼連結至註冊信箱。');
                            else if (res.status == 'FAILED')
                                $('span.err-msg').html('未註冊的信箱。');
                            else if (res.status == 'ERROR')
                                $('span.err-msg').html('系統錯誤！');
                        });
                    });
                });

                $('#register').on('click', function(e) {
                    j_indiv.html(Mustache.render(t_register));

                    $('#submit').on('click', function(e) {
                        var mail = $('#mail').val();
                        var password = $('#password').val();
                        var password2 = $('#password2').val();
                        if (password != password2) {
                            $('span.err-msg').html('兩次輸入密碼不符。');
                            return;
                        }

                        $.post('/spt/d/register', {
                            'mail': mail,
                            'password': password,
                        }, function(res) {
                            if (res.status == 'SUCCESS')
                                $('span.err-msg').html('已發送確認信至您的信箱。');
                            else if (res.status == 'FAILED')
                                $('span.err-msg').html('此信箱已被註冊。');
                            else if (res.status == 'WRONG MAIL')
                                $('span.err-msg').html('信箱格式錯誤！');
                            else if (res.status == 'ERROR')
                                $('span.err-msg').html('系統錯誤！');
                        });
                    });
                });
            } else {
                $.post('/spt/d/indiv_data', {}, function(res) {
                    if (res.status == 'SUCCESS') {
                        j_indiv.html(Mustache.render(t_indiv_data, res.data));
                    }
                });
            }
        });
    }
}

