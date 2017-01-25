'use strict'

var set_password = new function() {
    var that = this;
    
    that.load = function() {
        $('#submit').on('click', function(e) {
            var password = $('#password').val();
            var password2 = $('#password2').val();
            if (password != password2) {
                show_message('兩次輸入密碼不符。');
                return true;
            }

            var params = window.location.search.replace('?', '').split('&');
            var data = {'password': password};
            params.forEach(function(param) {
                var arr = param.split('=');
                data[arr[0]] = arr[1];
            });

            ajax_start();
            $.post('/spt/d/set_password', data, function(res) {
                if (res.status == 'SUCCESS') {
                    show_message('密碼重設完成。');
                    reload_page('/spt/indiv/');
                }
                else if (res.status == 'FAILED')
                    show_message('參數錯誤！');
                else if (res.status == 'ERROR')
                    show_message('系統錯誤！');
                ajax_done();
            });
        });

        ajax_done();
    }
}

