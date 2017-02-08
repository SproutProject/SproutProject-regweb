'use strict'

var qa = qa || {};

qa.load = function() {
    $.post('/spt/d/qa/get_all', {}, qa.render_data);
}

qa.render_data = function(res) {
    var template = $('#template').html();
    $('#list').html(Mustache.render(template, res));

    ajax_done();
}