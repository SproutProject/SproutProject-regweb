'use strict'

var register = register || {};

register.load = function() {
    $.post('/spt/d/register/get_options', {}, register.render_data);
};

register.render_data = function(res) {
    if (res.status == 'SUCCESS') {
        $('#gender').html(Mustache.render(t_options, {'data': res.data.gender}));
        $('#school_type').html(Mustache.render(t_school_options, {'data': res.data.school_type}));
        $('#school_type').on('change', set_grade_option);
        register.set_grade_option(undefined);
        register.init_submit_button();
    }
    ajax_done();
};

register.set_grade_option = function(event) {
    var max_grade = parseInt(j_school_type.find(':selected').attr('max_grade'));
    var data = [];
    for (var i = 1; i <= max_grade; i++)
        data.push({'id': i, 'value': i});
    $('#grade').html(Mustache.render(t_options, {'data': data}));
};

register.init_submit_button = function() {
    $('#submit').on('click', function(event) {
        if (confirm('確認送出？')) {
            var data = {}
            if (register.set_submit_data(data)) {
                ajax_start(data);
            } else {
                show_message('尚有欄位未填寫完成');
            }
        }
    });
};

register.set_submit_data = function(data) {
    var params = window.location.search.replace('?', '').split('&');
    params.forEach(function(param) {
        var arr = param.split('=');
        data[arr[0]] = arr[1];
    });

    var fields = ['full_name', 'gender', 'school', 'school_type', 'grade', 'address', 'phone'];
    fields.forEach(function(name) {
        data[name] = $('#' + name).val();
        if (data[name] == '') {
            return false;
        }
    });

    return true;
};

register.submit_data = function(data) {
    ajax_start();
    $.post('/spt/d/register/second', data, register.handle_result);
};

register.handle_result = function(res) {
    if (res.status == 'SUCCESS') {
        show_message('基本資料填寫完成，請回個人頁面登入後進行報名。');
        reload_page('/spt/indiv/');
    }
    else if (res.status == 'FAILED')
        show_message('參數錯誤！');
    else if (res.status == 'ERROR')
        show_message('系統錯誤！');
    ajax_done();
};
