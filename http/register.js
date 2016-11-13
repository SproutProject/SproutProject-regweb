'use strict'

var register = new function() {
    var that = this;

    that.load = function() {
        var t_options = $('#options-templ').html();
        var t_school_options = $('#school-options-templ').html();
        var j_gender = $('#gender');
        var j_school_type = $('#school_type');
        var j_grade = $('#grade');

        function set_grade_option(e) {
            var max_grade = parseInt(j_school_type.find(':selected').attr('max_grade'));
            var data = [];
            for (var i = 1; i <= max_grade; i++)
                data.push({'id': i, 'value': i});
            j_grade.html(Mustache.render(t_options, {'data': data}));
        }

        j_school_type.on('change', set_grade_option);

        $.post('/spt/d/register_options', {}, function(res) {
            if (res.status == 'SUCCESS') {
                j_gender.html(Mustache.render(t_options, {'data': res.data.gender}));
                j_school_type.html(Mustache.render(t_school_options, {'data': res.data.school_type}));
                set_grade_option(undefined);
            }
            ajax_done();
        });

        $('#submit').on('click', function(e) {
            var params = window.location.search.replace('?', '').split('&');
            var data = {};
            params.forEach(function(param) {
                var arr = param.split('=');
                data[arr[0]] = arr[1];
            });

            var done = true;
            var fields = ['full_name', 'gender', 'school', 'school_type', 'grade', 'address', 'phone'];
            fields.forEach(function(name) {
                data[name] = $('#' + name).val();
                if (data[name] == "")
                    done = false;
            });

            if (done) {
                ajax_start();
                $.post('/spt/d/register_data', data, function(res) {
                    if (res.status == 'SUCCESS')
                        $('span.err-msg').html('基本資料填寫完成，請回個人頁面登入後進行報名。');
                    else if (res.status == 'FAILED')
                        $('span.err-msg').html('參數錯誤！');
                    else if (res.status == 'ERROR')
                        $('span.err-msg').html('系統錯誤！');
                    ajax_done();
                });
            } else {
                $('span.err-msg').html('尚有欄位未填寫完成');
            }
        });
    };
};

