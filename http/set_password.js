'use strict'

var set_password = new function() {
    var that = this;
    
    that.load = function() {
        $('#submit').on('click', function(e) {
            var password = $('#password').val();
            var password2 = $('#password2').val();
            if (password != password2) {
                $('span.err-msg').html('兩次輸入密碼不符。');
                return true;
            }

            var params = window.location.search.replace('?', '').split('&');
            var data = {'password': password};
            params.forEach(function(param) {
                var arr = param.split('=');
                data[arr[0]] = arr[1];
            });

            $.post('/spt/d/set_password', data, function(res) {
                if (res.status == 'SUCCESS')
                    $('span.err-msg').html('密碼重設完成。');
                else if (res.status == 'FAILED')
                    $('span.err-msg').html('參數錯誤！');
                else if (res.status == 'ERROR')
                    $('span.err-msg').html('系統錯誤！');
            });
        });
    }
}

