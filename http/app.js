'use strict'

var app = new function() {
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

            $('#app').html(Mustache.render(t_app, res));

            $('button.submit').on('click', function(e) {
                var app_list = $('div.app');
                var data = [];

                for (var i = 0; i < app_list.size(); i++) {
                    var id = $(app_list[i]).attr('appid');
                    var answer = $(app_list[i]).find('.answer').val();
                    data.push({'id': id, 'answer': answer});
                }

                ajax_start();

                $.post('/spt/d/application_answer', {
                    'class_type': class_type,
                    'data': JSON.stringify(data)
                }, function(res) {
                    if (res.status == 'SUCCESS') {
                        show_message('報名資料已成功送出。');
                        reload_page('/spt/indiv/');
                    }
                    if (res.status == 'PERMISSION DENIED')
                        show_message('尚未完成規則測驗（或前測）。');
                    else if (res.status == 'ERROR')
                        show_message('系統錯誤！');
                    ajax_done();
                });
            });

            $('button.close').on('click', function(e) {
                reload_page('/spt/indiv/');
            });

            ajax_done();
        });
    }; 
}
