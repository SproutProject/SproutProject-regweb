'use strict'

var indiv = indiv || {};

indiv.load = function() {
    // check login first
    $.post('/spt/d/user/check_login', {}, function(res) {
        if (res.status != 'LOGINED') {
            indiv.render_login_page();
            ajax_done();
        } else {
            indiv_data.load();
        }
    });
};

indiv.render_login_page = function() {
    var template = $('#login-templ').html();
    $('#indiv').html(Mustache.render(template));

    indiv_login.init_button();
    indiv_forget.init_button();
    indiv_register.init_button();
};

var indiv_login = indiv_login || {};

indiv_login.init_button = function() {
    $('#login').on('click', function(e) {
        var mail = $('#mail').val();
        var password = $('#password').val();
        var data = {
            'mail': mail,
            'password': password,
        };

        ajax_start();
        $.post('/spt/d/user/login', data, indiv_login.handle_result);
        return false;
    });
};

indiv_login.handle_result = function(res) {
    $('#password').val('');
    if (res.status == 'SUCCESS') {
        location.reload();
        return;
    } else if (res.status == 'PERMISSION DENIED') {
        show_message('尚未完成註冊流程，請至註冊信箱收取確認信完成註冊流程。');
    } else if (res.status == 'FAILED') {
        show_message('信箱或密碼錯誤！');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};

var indiv_forget = indiv_forget || {};

indiv_forget.init_button = function() {
    $('#forget').on('click', function(e) {
        var template = $('#forget-templ').html();
        $('#indiv').html(Mustache.render(template));
        indiv_forget.init_submit_button();
        indiv_forget.init_return_button();
        return false;
    });
};

indiv_forget.init_submit_button = function() {
    $('#submit').on('click', function(e) {
        var mail = $('#mail').val();
        var data = {
            'mail': mail,
        };

        ajax_start();
        $.post('/spt/d/reset_password/get_mail', data, indiv_forget.handle_result);
    });
};

indiv_forget.init_return_button = function() {
    $('#return').on('click', function(e) {
        indiv.load();
    });
};

indiv_forget.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('已發送修改密碼連結至註冊信箱。');
    } else if (res.status == 'FAILED') {
        show_message('未註冊的信箱。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};

var indiv_register = indiv_register || {};

indiv_register.init_button = function() {
    $('#register').on('click', function(e) {
        var template = $('#register-templ').html();
        $('#indiv').html(Mustache.render(template));
        indiv_register.init_submit_button();
        indiv_register.init_return_button();
        return false;
    });
};

indiv_register.init_submit_button = function() {
    $('#submit').on('click', function(e) {
        var mail = $('#mail').val();
        var password = $('#password').val();
        var password2 = $('#password2').val();
        if (password != password2) {
            show_message('兩次輸入密碼不符。');
            return;
        }
        var data = {
            'mail': mail,
            'password': password,
        };

        ajax_start();
        $.post('/spt/d/register/first', data, indiv_register.handle_result);
    });
};

indiv_register.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('已發送確認信至您的信箱，請至信件內網址繼續完成報名。');
        reload_page('/spt/indiv/');
    } else if (res.status == 'FAILED') {
        show_message('此信箱已被註冊。');
    } else if (res.status == 'WRONG') {
        show_message('信箱格式錯誤！');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};

indiv_register.init_return_button = function() {
    $('#return').on('click', function(e) {
        indiv.load();
    });
};

var indiv_data = indiv_data || {};

indiv_data.load = function() {
    ajax_start();
    $.post('/spt/d/user/get_indiv_data', {}, function(res) {
        if (res.status == 'SUCCESS') {
            var template = $('#indiv-data-templ').html();
            $('#indiv').html(Mustache.render(template, res.data));

            if (res.data.rule_test == 1) {
                // $("#rule_test").append(' (已完成)');
                var _res = res;

                $.post('/spt/d/token/pretest', {}, function(res) {
                    var token_time = +new Date();
                    if (res.status == 'SUCCESS') {
                        $('form#pre_test_from').attr('action', res.url);
                        $('form#pre_test_from input[name="username"]').attr('value', res.username);
                        $('form#pre_test_from input[name="password"]').attr('value', res.password);
                        $('form#pre_test_from input[name="realname"]').attr('value', res.realname);
                        if (res.score >= 0.0) {
                            $('#pre_test').append(' (' + res.score + ' / 300)');
                        }
                        if (_res.data.pre_test == 0 && res.score >= 300.0) {
                            $('#algorithm_class').removeClass('btn-disabled');
                            $('#algorithm_class').addClass('btn-pri');
                            $('#algorithm_class').on('click', function(e) {
                                reload_page('/spt/app/?type=3');
                            });
                        }
                        $('#pre_test').removeClass('btn-disabled');
                        $('#pre_test').addClass('btn-pri');
                        $('#pre_test').on('click', function(e) {
                            if (+new Date() - token_time > 30000){
                                token_time = +new Date();
                                $.post('/spt/d/cms_token', {}, function(res) {
                                    $('input[name="password"]').attr('value', res.password);
                                    if (res.status == 'SUCCESS') {
                                        $('form#pre_test_from').submit();
                                    } else {
                                        show_message('cms 系統錯誤！');
                                    }
                                });
                            } else {
                                $('form#pre_test_from').submit();
                            }
                        });
                    } else if (res.status == 'ERROR') {
                        show_message('cms 系統錯誤！');
                    } else {
                        // show_message('尚未通過規則測驗。');
                    }
                });

                $('#c_class').removeClass('btn-disabled');
                $('#c_class').addClass('btn-pri');
                $('#c_class').on('click', function(e) {
                    reload_page('/spt/app/?type=1');
                });

                $('#python_class').removeClass('btn-disabled');
                $('#python_class').addClass('btn-pri');
                $('#python_class').on('click', function(e) {
                    reload_page('/spt/app/?type=2');
                });
            }

            if (res.data.signup_status & 4) {
                // $("#pre_test").append(' (已完成)');

                $('#algorithm_class').removeClass('btn-disabled');
                $('#algorithm_class').addClass('btn-pri');
                $('#algorithm_class').on('click', function(e) {
                    reload_page('/spt/app/?type=3');
                });

                $('div#entrance_area').show();
                $('#entrance').on('click', function(e) {
                    $.ajax({
                        type: 'POST',
                        url: '/spt/d/token/entrance',
                        dataType: 'json',
                        async: false
                    }).done(function(res) {
                        console.log(res);
                        $('form#entrance_form').attr('action', res.url);
                        $('form#entrance_form input[name="username"]').attr('value', res.username);
                        $('form#entrance_form input[name="password"]').attr('value', res.password);
                        $('form#entrance_form input[name="realname"]').attr('value', res.realname);
                        if (res.status == 'SUCCESS') {
                            $('form#entrance_form').submit();
                        } else {
                            show_message('cms 系統錯誤！');
                        }
                    });
                });
            }

            /*
            if (res.data.signup_status & 1)
                $("#c_class").append(' (已完成)');
            if (res.data.signup_status & 2)
                $("#python_class").append(' (已完成)');
            if (res.data.signup_status & 4)
                $("#algorithm_class").append(' (已完成)');
            */

            var suffix_msg = '<b>資料修改</b>'
            if (res.data.signup_status & 1)
                $("#c_class").append(suffix_msg);
            if (res.data.signup_status & 2)
                $("#python_class").append(suffix_msg);
            if (res.data.signup_status & 4)
                $("#algorithm_class").append(suffix_msg);

            $('#return_indiv_data').on('click', function(e) {
                $('#sign_up').hide();
                $('#indiv_data').show();
            });

            $('#return_sign_up').on('click', function(e) {
                $('#indiv_data').hide();
                $('#sign_up').show();
            });

            $('.logout').on('click', function(e) {
                ajax_start();
                $.post('/spt/d/user/logout', {}, function(res) {
                    if (res.status == 'SUCCESS') {
                        window.location.reload();
                    }
                });
            });

            $('#submit').on('click', function(e) {
                var phone = $('#phone').val();
                var address = $('#address').val();
                ajax_start();

                $.post('/spt/d/user/modify_indiv_data', {
                    'phone': phone,
                    'address': address
                }, function(res) {
                    if (res.status == 'SUCCESS')
                        show_message('修改成功！');
                    else if (res.status == 'NOT LOGINED')
                        show_message('登入已失效，請重新登入。');
                    else if (res.status == 'ERROR')
                        show_message('系統錯誤！');
                    ajax_done();
                });
            });

            $('#rule_test').on('click', function(e) {
                reload_page('/spt/rule_test/');
            });
        }
        ajax_done();
    });
};
