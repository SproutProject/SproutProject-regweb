'use strict'

var ass_app = new function() {
    var that = this;

    that.load = function() {
        var t_app = $('#app-templ').html();

        $.post('/spt/d/application', {
            'class_type': class_type
        }, function(res) {
            res.title_value = function() {
                var arr = ['C 語法班', 'Python 語法班', '算法班'];
                return arr[class_type - 1];
            }

            res.description_value = function() {
                return this.description.slice(0, 10) + '...';
            }

            $('#ass_app').html(Mustache.render(t_app, res));
            if (ass_mode_on) resizeSpecial();

            $('button.modify').on('click', function(e) {
                if (confirm('確認修改？')) {
                    var j_edit = $(this).parent();
                    var app_id = j_edit.attr('appid');
                    if (app_id == undefined)
                        app_id = -1;
                    var order = parseInt(j_edit.find('input.order').val());
                    var description = j_edit.find('textarea').val();
                    ajax_start();

                    $.post('/spt/d/mg/application_add', {
                        'id': app_id,
                        'order': order,
                        'class_type': class_type,
                        'description': description
                    }, function(res) {
                        reload_page('/spt/ass_app/?type=' + class_type);
                    });
                }
            });

            $('button.open').on('click', function(e) {
                var j_edit = $(this).parent().next();
                $('div.edit.active').removeClass('active');
                j_edit.addClass('active');
            });

            $('button.close').on('click', function(e) {
                $('div.edit.active').removeClass('active');
            });

            $('button.delete').on('click', function(e) {
                if (confirm('確認刪除？')) {
                    ajax_start();
                    $.post('/spt/d/mg/application_del', {
                        'id': $(this).parent().attr('appid'),
                    }, function(res) {
                        reload_page('/spt/ass_app/?type=' + class_type);
                    });
                }
            });

            ajax_done();
        });
    }; 
}
