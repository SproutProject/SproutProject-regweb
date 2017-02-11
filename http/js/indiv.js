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
    $.post('/spt/d/user/get_indiv_data', {}, indiv_data.render_data);
};

indiv_data.render_data = function(res) {
    if (res.status == 'SUCCESS') {
        var template = $('#indiv-data-templ').html();
        $('#indiv').html(Mustache.render(template, res.data));

        indiv_data.init_rule_test_button();
        indiv_data.init_logout_button();
        indiv_data.init_return_indiv_data_button();
        indiv_data.init_return_sign_up_button();
        indiv_data.init_modify_button();

        if (res.data.rule_test == 1) {
            indiv_data.init_app_button('c', 1);
            indiv_data.init_app_button('python', 2);
            indiv_data.init_contest_button('pre_test');
            indiv_data.get_pre_test_score();
        }

        if (res.data.pre_test == 1) {
            indiv_data.init_app_button('algorithm', 3);
        }

        if (res.data.signup_status & 1) {
            indiv_data.add_app_suffix('c');
        }
        if (res.data.signup_status & 2) {
            indiv_data.add_app_suffix('python');
        }
        if (res.data.signup_status & 4) {
            indiv_data.add_app_suffix('algorithm');
            indiv_data.init_app_button('algorithm', 3);
            indiv_data.init_contest_button('entrance');
            $('div#entrance_area').show();
        }
    }
    ajax_done();
};

indiv_data.init_app_button = function(class_name, class_type) {
    $('#' + class_name + '_class').removeClass('btn-disabled');
    $('#' + class_name + '_class').addClass('btn-pri');
    $('#' + class_name + '_class').on('click', function(e) {
        reload_page('/spt/app/?type=' + class_type);
    });
};

indiv_data.add_app_suffix = function(class_name) {
    var suffix_msg = '<b>資料修改</b>';
    $('#' + class_name + '_class').append(suffix_msg);
};

indiv_data.init_contest_button = function(contest_name) {
    $('#' + contest_name).removeClass('btn-disabled');
    $('#' + contest_name).addClass('btn-pri');

    $('#' + contest_name).on('click', function(e) {
        $.ajax({
            type: 'POST',
            url: '/spt/d/token/' + contest_name,
            dataType: 'json',
            async: false
        }).done(function(res) {
            $('form#' + contest_name + '_form').attr('action', res.url);
            $('form#' + contest_name + '_form input[name="username"]').attr('value', res.username);
            $('form#' + contest_name + '_form input[name="password"]').attr('value', res.password);
            $('form#' + contest_name + '_form input[name="realname"]').attr('value', res.realname);
            if (res.status == 'SUCCESS') {
                $('form#' + contest_name + '_form').submit();
            } else if (res.status == 'NOT LOGINED') {
                show_message('尚未登入。');
            } else if (res.status == 'FAILED') {
                show_message('尚未完成前置條件。');
            }
        });
    });
};

indiv_data.init_rule_test_button = function() {
    $('#rule_test').on('click', function(e) {
        reload_page('/spt/rule_test/');
    });
};

indiv_data.init_logout_button = function() {
    $('.logout').on('click', function(e) {
        ajax_start();
        $.post('/spt/d/user/logout', {}, function(res) {
            if (res.status == 'SUCCESS') {
                window.location.reload();
            }
        });
    });
};

indiv_data.init_return_indiv_data_button = function() {
    $('#return_indiv_data').on('click', function(e) {
        $('#sign_up').hide();
        $('#indiv_data').show();
    });
};

indiv_data.init_return_sign_up_button = function() {
    $('#return_sign_up').on('click', function(e) {
        $('#indiv_data').hide();
        $('#sign_up').show();
    });
};

indiv_data.init_modify_button = function() {
    $('#submit').on('click', function(e) {
        var phone = $('#phone').val();
        var address = $('#address').val();
        var data = {
            'phone': phone,
            'address': address
        };

        ajax_start();
        $.post('/spt/d/user/modify_indiv_data', data, indiv_data.handle_modify_result);
    });
};

indiv_data.handle_modify_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('修改成功！');
    } else if (res.status == 'NOT LOGINED') {
        show_message('登入已失效，請重新登入。');
    } else if (res.status == 'ERROR') {
        show_message('系統錯誤！');
    }
    ajax_done();
};

indiv_data.get_pre_test_score = function(res) {
    $.post('/spt/d/token/pre_test_score', {}, function(res) {
        if (res.status == 'SUCCESS') {
            if (res.score >= 0.0) {
                $('#pre_test').append(' (' + res.score + ' / 300)');
            }
            if (res.score >= 300.0) {
                indiv_data.init_app_button('algorithm', 3);
            }
        } else if (res.status == 'NOT LOGINED') {
            show_message('尚未登入。');
        } else if (res.status == 'FAILED') {
            show_message('尚未完成前置條件。');
        }
    });
};
