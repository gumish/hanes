// rozsireni tridy Date o novou metodu
// Date.prototype.timeNow = function () {
//     var desetina = Math.round(this.getMilliseconds()/100);
//     if (desetina == 10) {
//         var increment = 1;
//         desetina = 0;
//     } else {
//         var increment = 0;
//     }
//     return this.getHours() +":"+ ((this.getMinutes() < 10)?"0":"") + this.getMinutes() +":"+ ((this.getSeconds() < 10)?"0":"") + (this.getSeconds() + increment) +","+ desetina;
// }

function activate_button(button) {
    button.siblings().removeClass('active');
    button.addClass('active');
}


$(document).ready(function() {

    // nastaveni tlacitek dle hidden inputu
    $('.odstartoval input').each(function() {
        var val = $(this).val();
        var button = $(this).next().find("button[value='"+val+"']");
        activate_button(button);
    });

    // zaznam casu pri zmacknuti ANO
    $('.odstartoval button').click(function() {
        // var date = new Date();
        var button = $(this);
        var value = button.val();
        // var input = button.closest('td').prev().find('input');
        // if (Boolean(parseInt(value))) {
        //     if ($('#zaznam_casu').is(':checked')) {
        //         input.val(date.timeNow());
        //     }
        //     input.removeClass('error');
        // } else {
        //     if (input.val()) {
        //         input.addClass('error');
        //         message
        //             .show()
        //             .removeClass('success')
        //             .addClass('error')
        //             .text("Startovní čas nadbytečný")
        //             .fadeOut(3000);
        //     }
        // }
        button.parent().prev().val(value);
        activate_button(button);
    });

    // smazani startovniho casu tlacitkem
    // $('.startovni_cas button').click(function() {
    //     $(this).prev().val('');
    // });

});