'use strict'

var ass_indiv = ass_indiv || {};

ass_indiv.load = function() {
    var template = $('#indiv-data-templ').html();
    $('#ass_indiv').html(Mustache.render(template));
    if (ass_mode_on) resizeSpecial();

    ass_indiv.init_buttons();
    ass_indiv.init_show_button();

    ajax_done();
};

ass_indiv.init_buttons = function() {
    $('#rule_test').on('click', function(e) {
        reload_page('/spt/ass_rule_test/');
    });

    $('#c_class').on('click', function(e) {
        reload_page('/spt/ass_app/?type=1');
    });
    $('#python_class').on('click', function(e) {
        reload_page('/spt/ass_app/?type=2');
    });
    $('#algorithm_class').on('click', function(e) {
        reload_page('/spt/ass_app/?type=3');
    });
};

ass_indiv.init_show_button = function() {
    $('#show_indiv_data').on('click', function(e) {
        ajax_start();
        $.post('/spt/d/user/get_all_user_data', {}, ass_indiv.handle_user_data);
    });
};

ass_indiv.handle_user_data = function(res) {
    var template = $('#user-data-templ').html();
    res.power_value = function() {
        if (this.power == -1)
            return '未完成註冊'
        var arr = ['一般', '管理者', '神'];
        return arr[this.power];
    };
    res.signup_status_value = function() {
        var res = [];
        if (this.signup_status & 1)
            res.push('C');
        if (this.signup_status & 2)
            res.push('Py');
        if (this.signup_status & 4)
            res.push('Algo');
        return res.join(', ');
    };
    res.rule_test_value = function() {
        return (this.rule_test) ? '通過' : '未通過';
    };
    res.pre_test_value = function() {
        return (this.pre_test) ? '通過' : '未通過';
    };

    $("#sign_up").hide();
    $('#ass_indiv').append(Mustache.render(template, res));

    ass_indiv.init_user_data_buttons();

    ajax_done();
};

ass_indiv.init_user_data_buttons = function() {
    $('button.open').on('click', function(e) {
        var j_edit = $(this).parent().next();
        $("div.edit.active").removeClass('active');
        j_edit.addClass('active');
    });

    $('button.close').on('click', function(e) {
        $("div.edit.active").removeClass('active');
    });

    $('button#return_sign_up').on('click', function(e) {
        $("#user_data").remove();
        $("#sign_up").show();
    });
};
