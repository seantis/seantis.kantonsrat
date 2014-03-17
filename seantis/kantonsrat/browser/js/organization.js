load_libraries(['_', 'jQuery'], function(_, $) {
    "use strict";

    var enable_form_overlays = function(selector, before_close) {
        $(selector).prepOverlay({
            subtype: 'ajax',
            filter: '#content > *',
            formselector: 'form',
            closeselector: '[name="form.buttons.cancel"]',
            noform: function() {
                if (before_close) {
                    before_close();
                }
                return 'close';
            },
            config: {
                onBeforeLoad : function (e) {
                    if (! $(e.target).find('form').length) {
                        e.preventDefault();
                        reload_memberships();
                    }
                }
            }
        });
    };

    var reload_memberships = function() {
        var url = document.URL +  ' #kantonsrat-memberships-block';
        $('#kantonsrat-memberships-block').load(url, setup_events);
    };

    var setup_events = function() {
        enable_form_overlays('.kantonsrat-actions a', reload_memberships);
        enable_form_overlays(
            'a.contenttype-seantis-kantonsrat-membership', reload_memberships
        );
    };

    $(document).ready(function() {
        setup_events();
    });
});