'use strict'

var ass_denied = ass_denied || {};

ass_denied.load = function() {
    ass_denied.render_data();
};

ass_denied.render_data = function() {
    var t_permission_denied = $('#permission-denied-templ').html();
    var t_original_nav = $('#original-nav-templ').html();

    $('#ass_denied').html(Mustache.render(t_permission_denied));
    $('#nav').html(Mustache.render(t_original_nav));

    ass_denied.resize_youtube_embed();
    $(window).resize(ass_denied.resize_youtube_embed);

    ajax_done();
};

ass_denied.resize_youtube_embed = function() {
    $('iframe').height($('iframe').width() * (9 / 16));
};
