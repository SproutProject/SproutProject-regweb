'use strict'

var ass = new function() {
    var that = this;

    that.load = function() {
        var t_permission_denied = $('#permission-denied-templ').html();
        var j_ass = $('#ass');

        $.post('/spt/d/mg', {}, function(res) {
            if(res.status != 'SUCCESS'){
                j_ass.html(Mustache.render(t_permission_denied));
                resizeYoutubeEmbed();
                $(window).resize(resizeYoutubeEmbed);
            }
        });
    };
}

function resizeYoutubeEmbed() {
    $("iframe").height($("iframe").width() * (9 / 16));
}
