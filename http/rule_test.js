'use strict'

var rule_test = new function() {
    var that = this;

    that.load = function() {
        var t_question = $('#question-templ').html();

        $.post('/spt/d/rule_question', {}, function(res) {
            $('#rule_test').html(Mustache.render(t_question, res));
        });
    };
}
