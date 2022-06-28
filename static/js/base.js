function printPage(url) {
    var div = document.getElementById("printerDiv");
    div.innerHTML = '<iframe src="' + url + '" onload="this.contentWindow.print();"></iframe>';
};

$(document)
    .ready(function() {

        message = $('#ajax_messages');

        $('.message .close')
            .on('click', function() {
                $(this)
                    .closest('.message')
                    .transition('fade');
            });

        $('.ui.sticky')
            .sticky({
                context: '#content',
            });

        $('.dropdown').dropdown();

        $("#id_form-0-cislo").focus();

        $('#backup_database').click(function() {
            var el = $(this);
            $.ajax({
                url: el.attr('href'),
                success: function(data) {
                    message
                        .show()
                        .removeClass('error')
                        .addClass('success')
                        .text(data)
                        .fadeOut(3000);
                },
                error: function() {
                    message
                        .show()
                        .removeClass('success')
                        .addClass('error')
                        .text("CHYBA: databáze nebyla zálohována !");
                }
            });
            return false;
        });

        // lide autocomplete
        $("#zavodnici_forms input[name$='prijmeni']").each(function() {
            // pri focusu vycisteni pole i ID
            // $(this).focus(function(){
            //     $(this).val('');
            // });
            $(this).devbridgeAutocomplete({
                serviceUrl: clovek_autocomplete_url,
                minChars: 2,
                noCache: true,
                deferRequestBy: 0,
                maxHeight: 600,
                preventBadQueries: false,
                triggerSelectOnValidInput: false,
                groupBy: 'klub',
                width: 300,
                formatResult: function(suggestion, currentValue) {
                    // zformatovani vystupu do napovedy
                    // console.log(suggestion.data);
                    data = suggestion.data;
                    base = data.prijmeni + ' ' + data.jmeno + '  (' + data.narozen + ')';
                    if (data.zavodnik) {
                        return '<i class="ui warning sign red icon"></i><span style="color:red;" title="závodník se už účastní tohoto závodu!">' + base + ' #' + data.zavodnik + '</span>';
                    } else {
                        return base
                    }
                },
                onSelect: function(suggestion) {
                    // vyplneni ostatnich poli formulare pomoci dat
                    data = suggestion.data;
                    var tr = $(this).parent().parent().parent();
                    tr.find("input[name$='jmeno']").val(data.jmeno);
                    tr.find("input[name$='narozen']").val(data.narozen);
                    tr.find("select[name$='pohlavi']").val(data.pohlavi);
                    tr.find("input[name$='klub_nazev']").val(data.klub);
                    tr.next().find("input[name$='cislo']").focus();
                    // vyplneni 'clovek_id' do autocomplete klubu
                    tr.find("input[name$='klub_nazev']").devbridgeAutocomplete().setOptions({
                        params: { clovek_id: data.clovek_id }
                    });
                }
            });
            $(this).devbridgeAutocomplete().clear();
        });

        // kluby autocomplete
        $("#zavodnici_forms input[name$='klub_nazev'], input#id_presunout_do").each(function() {
            $(this).devbridgeAutocomplete({
                serviceUrl: klub_autocomplete_url,
                minChars: 0,
                deferRequestBy: 0,
                maxHeight: 600,
                preventBadQueries: false,
                triggerSelectOnValidInput: false,
                groupBy: 'skupina',
                noCache: true,
                width: 300,
                onSelect: function(suggestion) {
                    // vyplneni ostatnich poli formulare pomoci dat
                    data = suggestion.data;
                    $(this).parent().parent().parent().next().find("input[name$='cislo']").focus();
                }
            });
            $(this).devbridgeAutocomplete().clear();
        });

        // cisla autocomplete
        $("#cilovy_formular input[name$='-cislo']").each(function() {
            $(this).devbridgeAutocomplete({
                serviceUrl: cislo_autocomplete_url,
                minChars: 1,
                deferRequestBy: 0,
                maxHeight: 600,
                preventBadQueries: false,
                triggerSelectOnValidInput: false,
                noCache: true,
                width: 500,
                formatResult: function(suggestion, currentValue) {
                    // zformatovani vystupu do napovedy
                    data = suggestion.data;
                    base = suggestion.value + '   -   ' + data.jmeno;
                    if (data.cas) {
                        base = base + '  <span style="color:red;" title="závodník má již zapsán čas!"><i class="ui warning sign red icon"></i> čas:' + data.cas + '</span>';
                    }
                    if (data.nedokoncil) {
                        base = base + '  <span style="color:orange;"><i class="ui warning sign orange icon"></i> ' + data.nedokoncil + '</span>';
                    }
                    return base
                },
            });
            $(this).devbridgeAutocomplete().clear();
        });

        // smaz data ze radku
        $('form .remove.red.icon.js-smaz-inputy').click(function() {
            var tr = $(this).closest('tr');
            // tr.remove();
            tr.find('input, select').val(null);
            tr.find('.red.pointing.label').remove();
        });

    });