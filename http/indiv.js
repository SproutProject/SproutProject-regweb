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

                        $('#return_indiv_data').on('click', function(e) {
                            $('#sign_up').hide();
                            $('#indiv_data').show();
                        });

                        $('#return_sign_up').on('click', function(e) {
                            $('#indiv_data').hide();
                            $('#sign_up').show();
                        });

                        $('.logout').on('click', function(e) {
                            $.post('/spt/d/logout', {}, function(res) {
                                if (res.status == 'SUCCESS') {
                                    window.location.reload();
                                }
                            });
                        });

                        $('#submit').on('click', function(e) {
                            var phone = $('#phone').val();
                            var address = $('#address').val();

                            $.post('/spt/d/modify_indiv_data', {
                                'phone': phone,
                                'address': address
                            }, function(res) {
                                if (res.status == 'SUCCESS')
                                    $('span.err-msg').html('修改成功！');
                                else if (res.status == 'NOT LOGINED')
                                    $('span.err-msg').html('登入已失效，請重新登入。');
                                else if (res.status == 'ERROR')
                                    $('span.err-msg').html('系統錯誤！');
                            });
                        });

                        $('#rule_test').on('click', function(e) {
                            reload_page('/spt/rule_test/');
                        });
                    }
                });
            }
        });
    }
}

