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

                $.post('/spt/d/application_answer', {
                    'class_type': class_type,
                    'data': JSON.stringify(data)
                }, function(res) {
                    if (res.status == 'SUCCESS')
                        $('span.err-msg').html('報名資料已成功送出。');
                    if (res.status == 'PERMISSION DENIED')
                        $('span.err-msg').html('尚未完成規則測驗（或前測）。');
                    else if (res.status == 'ERROR')
                        $('span.err-msg').html('系統錯誤！');
                });
            });
        });
    }; 
}
