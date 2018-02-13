// funkce pro zabliknuti pozadi
var blink = function (element, color) {
    var original_color = element.css('background');
    element.css("background", color);
    setTimeout(function () {
        element.css("background", original_color);
    }, 900);
}

$(document)
  .ready(function() {
    var message = $('#ajax_messages');

    $('#startovni_listina').on('click', 'i.save.icon', function(){
        $(this).submit();
    });

    // odeslani zavodnika ajaxem
    $('#startovni_listina').on('submit', 'form.tr', function(){ // catch the form's submit event
        var form = $(this);
        form.find('.red.label').remove(); // odmazani starych chybovych hlasek
        $.ajax({ // create an AJAX call...
            data: $(this).serialize(), // get the form data
            type: $(this).attr('method'), // GET or POST
            url: $(this).attr('action'), // the file to call
            success: function (html) {
                var new_form = $(html);
                form.replaceWith(new_form);
                message
                    .show()
                    .removeClass('error')
                    .addClass('success')
                    .text("řádek uložen v pořádku")
                    .fadeOut(3000);
                blink(new_form, '#65ff00');
            },
            error: function(data, status) {
                form.removeClass('success').addClass('error');
                var errors_dict = jQuery.parseJSON(data.responseText);
                $.each(errors_dict, function(name, value){
                    var input = form.find('input[name$="'+name+'"]');
                    input.addClass('error').after("<div class='ui red pointing above ui label'>"+value[0]+"</div>");
                });
                message
                    .show()
                    .removeClass('success')
                    .addClass('error')
                    .text("vyskytle se CHYBA !!");
            }
        });
        return false;
    });

    // smazani zavodnika
    $('#startovni_listina').on('click', 'i.trash.icon', function(){
        var el = $(this);
        $.ajax({
            url: el.attr('data-url'),
            success: function(){
                var tr = el.closest('form.tr');
                tr.addClass('removed').prop('title', 'ZÁVODNÍK SMAZÁN !');
                tr.find('.input, input, .icon').remove();
                message
                    .show()
                    .removeClass('error')
                    .addClass('success')
                    .text("řádek smazán")
                    .fadeOut(3000);
            }
        });
    });

    // aktualizace dat dle databaze
    $('#startovni_listina').on('click', 'i.refresh.icon', function(){
        var form = $(this).closest('form.tr');
        $.get(
            $(this).attr('data-url'),
            {},
            function (html) {
                var new_form = $(html);
                form.replaceWith(new_form);
                message
                    .show()
                    .removeClass('error')
                    .addClass('success')
                    .text("řádek aktualizován")
                    .fadeOut(3000);
                blink(new_form, '#8ebbdc');
            },
        );
    });
});