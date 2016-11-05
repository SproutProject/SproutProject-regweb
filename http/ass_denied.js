'use strict'

var ass_denied = new function() {
    var that = this;

    that.load = function() {
        var t_permission_denied = $('#permission-denied-templ').html();
        var t_original_nav = $('#original-nav-templ').html();

        $('#ass_denied').html(Mustache.render(t_permission_denied));
        $('#nav').html(Mustache.render(t_original_nav));

        resizeYoutubeEmbed();
        $(window).resize(resizeYoutubeEmbed);
    };
}

function resizeYoutubeEmbed() {
    $('iframe').height($('iframe').width() * (9 / 16));
}
