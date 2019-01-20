function toString(date) {
    return date.getHours() +":"+ ((date.getMinutes() < 10)?"0":"") + date.getMinutes() +":"+ ((date.getSeconds() < 10)?"0":"") + date.getSeconds();
}

$(document).ready(function() {


$("table tbody").sortable({

    // aktivace presouvani radku v tabulce kategorie

    placeholder: "ui-state-highlight"
}).disableSelection();


/** TLACITKO PRIRADIT CASY */
$('button.js-assign-times').click(function() {

    // distribuce casu mezi jednotlive zavodniky

    var form = $(this).closest('.form');
    var tbody = form.closest('.ui.grid').find('tbody');

    var startTime = form.find('.js-start-time').val();
    var start = new Date('2000-01-01T' + startTime);
    var kolik = parseInt(form.find('.js-group-size option:selected').val());
    var rozdil = parseInt(form.find('.js-time-gap').val());

    tbody.children('tr').each(function(index, el) {
        $(this).find("input[name$='startovni_cas']").val(toString(start));

        // inkrement casu
        if ((index+1) % kolik == 0) {
            start.setSeconds(start.getSeconds() + rozdil);
        }
    });
});


/** TLACITKO PRIRADIT CISLA */
$('button.js-assign-numbers').click(function() {

    // distribuce cisel mezi jednotlive zavodniky

    var form = $(this).closest('.form');
    var tbody = form.closest('.ui.grid').find('tbody');

    var cislo = parseInt(form.find('.js-first-number').val());

    tbody.children('tr').each(function(index, el) {
        $(this).find("input[name$='cislo']").val(cislo);
        cislo += 1;
    });
});


/** KLIKNUTI NA TLACITKO VEDLE HODNOTY KATEGORIE */
$('button.js-copy-values').click(function() {

    // rozkopirovani hodnot do jinych kategorii

    var what = $(this).closest('.field').attr('class');
    var input = $(this).prev();
    var value = input.val();
    what = '.' + what.replace(' ', '.');
    $(what + ' input, ' + what + ' select').val(value);
    message
        .show()
        .removeClass('error')
        .addClass('success')
        .text("Hodnota rozkopírována do ostatních kategorií")
        .fadeOut(3000);
});


/** ODESLANI FORMULARE PRES AJAX */
$('#start_times form').submit(function (event) {
    event.preventDefault();
    var $form = $(this);
    $.ajax({
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize(),
        success: function (data) {
            var $message = $form.find('.js-ajax-message');
            $message.replaceWith(data);
        },
        fail: function (data) {
            var $message = $form.find('.js-ajax-message');
            $message.replaceWith(data);
        }
    });
});

});