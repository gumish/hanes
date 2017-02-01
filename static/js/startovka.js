$(document)
  .ready(function() {
    var message = $('#ajax_messages');

    $('#startovni_listina i.save.icon').click(function() {
        $(this).submit();
    });

    // odeslani zavodnika ajaxem
    $('#startovni_listina form.tr').submit(function() { // catch the form's submit event
        var form = $(this);
        form.find('.red.label').remove(); // odmazani starych chybovych hlasek
        $.ajax({ // create an AJAX call...
            data: $(this).serialize(), // get the form data
            type: $(this).attr('method'), // GET or POST
            url: $(this).attr('action'), // the file to call
            success: function (data) {
                form.removeClass('error').addClass('success');
                $.each(data, function(name, val){
                    form.find('input[name$="'+name+'"]').val(val);
                });
                message
                    .show()
                    .removeClass('error')
                    .addClass('success')
                    .text("řádek uložen v pořádku")
                    .fadeOut(3000);
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

    // aktualizace dat dle databaze
    $('#startovni_listina form.tr i.refresh.icon').click(function(){
        var el = $(this);
        var tr = $(this).closest('form.tr');
        $.ajax({
            url: el.attr('data-url'),
            success: function(data){
                $.each(data, function(name, value){
                    var input = tr.find('input[name$="'+name+'"]');
                    value = value ? value : "";
                    if (input.val() != value) {
                        input
                            .prop('title', 'hodnota byla zaktualizována dle databáze (původní hodnota pole: '+input.val()+')')
                            .addClass('actualized')
                            .val(value);
                    }
                });
                message
                    .show()
                    .removeClass('error')
                    .addClass('success')
                    .text("řádek aktualizován")
                    .fadeOut(3000);
            }
        });
    });

    // smazani zavodnika
    $('#startovni_listina i.trash.icon').click(function(){
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
});