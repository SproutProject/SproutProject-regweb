'use strict'

var ass_indiv = new function() {
    var that = this;
    
    that.load = function() {
        var t_indiv_data = $('#indiv-data-templ').html();
        var t_user_data = $('#user-data-templ').html();
        var j_indiv = $('#ass_indiv');

        j_indiv.html(Mustache.render(t_indiv_data));
        if (ass_mode_on) resizeSpecial();

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

        $('#show_indiv_data').on('click', function(e) {
            $.post('/spt/d/mg/user_data', {}, function(res) {
                res.power_value = function() {
                    var arr = ['一般', '管理者'];
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
                j_indiv.append(Mustache.render(t_user_data, res));

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
            });
        });
    }
}

