'use strict'

var as = new function() {
    var that = this;

    that.load = function() {
        var t_login = $('#login-templ').html();
        var t_dash = $('#dash-templ').html();
        var t_qa = $('#qa-templ').html();
        var t_poll = $('#poll-templ').html();
        var t_req = $('#req-templ').html();
        var j_as = $('#as');

        $.post('/spt/d/mg', {}, function(res) {
            if(res.status != 'SUCCESS'){
                j_as.html(Mustache.render(t_login));
                $('#login').on('click', function(e) {
                    var mail = $('#mail').val();
                    var passwd = $('#passwd').val();

                    $.post('/spt/d/login', {
                        'mail':mail,
                        'passwd':passwd,
                    }, function(res) {
                        location.reload();
                    });
                });
            }else{
                j_as.html(Mustache.render(t_dash));
                $('a.expand').on('click', function(e) {
                    var j_this = $(this);
                    
                    if (j_this.attr('toggle') != 'true') {
                        j_this.attr('toggle','true');
                        j_this.find('h2 > span').text('[-]');   
                        j_this.siblings('div.cont').show();
                    } else {
                        j_this.attr('toggle','false');
                        j_this.find('h2 > span').text('[+]');
                        j_this.siblings('div.cont').hide();
                    }

                    return false;
                });
            }
        }).done(function() {
            $.post('/spt/d/mg/qa', {}, function(res) {
                var i;

                $('div.qa > div.cont').html(Mustache.render(t_qa,res));

                if (res.data != null) {
                    for (i = 0; i < res.data.length; i++) {
                        $('[qaid="' + res.data[i].id + '"]').data('qa', res.data[i]);
                    }
                }

                $('div.qa div.edit > button.submit').on('click', function(e) {
                    var qa_id = $('div.qa div.edit').attr('qaid');
                    if (qa_id == undefined)
                        qa_id = -1;
                    var question = $('div.qa div.edit > input.question').val();
                    var order = parseInt($('div.qa div.edit > input.order').val());
                    var answer = $('div.qa div.edit > textarea').val();
                    console.log(qa_id);
                    $.post('/spt/d/mg/qa_add', {
                        'id': qa_id,
                        'question': question,
                        'answer': answer,
                        'order': order
                    }, function(res) {
                        location.reload();
                    });
                });
                $('div.qa div.edit > button.cancel').on('click', function(e) {
                    location.reload();
                });
                $('div.qa div.list button.modify').on('click', function(e) {
                    var qa = $(this).parent().data('qa');
                    $('div.qa div.edit').attr('qaid', qa.id);
                    $('div.qa div.edit > input.question').val(qa.question);
                    $('div.qa div.edit > input.order').val(qa.order);
                    $('div.qa div.edit > textarea').val(qa.answer);
                });
                $('div.qa div.list button.delete').on('click', function(e) {
                    $.post('/spt/d/mg/qa_del', {
                        'id': $(this).parent().attr("qaid"),
                    }, function(res) {
                        location.reload();
                    });
                });
            });
            $.post('/spt/d/mg/poll', {}, function(res) {
                var i;

                $('div.poll > div.cont').html(Mustache.render(t_poll,res));

                if(res.data != null) {
                    for(i = 0; i < res.data.length; i++) {
                        $('[pollid="' + res.data[i].id + '"]').data('poll', res.data[i]);
                    }
                }

                $('div.poll div.edit > button.submit').on('click', function(e) {
                    var id = $('div.poll div.edit').attr('pollid');
                    if (id == undefined)
                        id = -1;
                    var order = parseInt($('div.poll div.edit > input.order').val());
                    var year = parseInt($('div.poll div.edit > input.year').val());
                    var subject = $('div.poll div.edit > textarea.subject').val();
                    var body = $('div.poll div.edit > textarea.body').val();

                    $.post('/spt/d/mg/poll_add', {
                        'id': id,
                        'order': order,
                        'year': year,
                        'subject': subject,
                        'body': body,
                    }, function(res) {
                        location.reload();
                    });
                });
                $('div.poll div.edit > button.cancel').on('click', function(e) {
                    location.reload();
                });
                $('div.poll div.list button.modify').on('click', function(e) {
                    var poll = $(this).parent().data('poll');
                    $('div.poll div.edit').attr('pollid', poll.id);
                    $('div.poll div.edit > input.order').val(poll.order);
                    $('div.poll div.edit > input.year').val(poll.year);
                    $('div.poll div.edit > textarea.subject').val(poll.subject);
                    $('div.poll div.edit > textarea.body').val(poll.body);
                });
                $('div.poll div.list button.delete').on('click', function(e) {
                    $.post('/spt/d/mg/poll_del', {
                        'id': $(this).parent().attr("pollid")
                    }, function(res) {
                        location.reload();
                    });
                });
            });
        });
    };
}
