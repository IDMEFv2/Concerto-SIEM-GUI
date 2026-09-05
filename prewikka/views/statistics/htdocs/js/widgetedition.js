"use strict";

function WidgetEdition(root, labels) {

    function _css_filter(key, value) {
        return "[" + key + "='" + (value || "").replace(/'/g, "\\'") + "']";
    }

    function _init_paths(select) {
        select.select2_container({
            tags: true
        });
    }

    function _datatype_changed(elem) {
        elem.closest(".query-instance").find("select.data-paths").each(function() {
            var types = null;
            var aggreg = $(this).parent().prev().find(".aggreg-type");
            if ( aggreg.length > 0 )
                types = _get_allowed_types(aggreg);
            _update_paths($(this), elem.val(), types);
        });
    }

    function _aggregation_changed(elem) {
        _update_paths(elem.parent().next().find("select.data-paths"), null, _get_allowed_types(elem));
    }

    function _get_allowed_types(elem) {
        /* Return the types accepted by the selected aggregation function */
        var types = elem.find("option:selected").data("types");
        return types ? types.split(" ") : [];
    }

    function _get_available_types(elem) {
        /* Return the different path types available for the selected datatype */
        var types = [];
        elem.find("option").each(function() {
            var type = $(this).data("type");
            if ( types.indexOf(type) == -1 ) {
                types.push(type);
            }
        });
        return types;
    }

    function _update_paths(elem, datatype, aggregtypes) {
        /*
         * Update available paths depending on the data type
         * and the types accepted by the aggregation function
         */
        var aggreg = elem.parent().prev().find(".aggreg-type");
        var selected_value = elem.find("option:selected").prop("value");
        var default_value = null;
        var initial_value = elem.attr("value");

        // Force finding the datatype to reinitialize the paths select
        if ( ! datatype )
            datatype = elem.parent().parent().prev().find(".data-type").val();

        if ( datatype ) {
            var select = $("select." + datatype + "-paths");
            elem.html(select.html());
            default_value = select.find("option").first().prop("value");
        }

        // Only show aggregation types for which paths are available
        var pathtypes = _get_available_types(elem);
        aggreg.find("option").each(function() {
            var option = $(this);
            var types = option.data("types");
            var show;
            if ( ! types ) {
                show = true;
            }
            else {
                show = false;
                $.each(types.split(' '), function(i, v) {
                    if ( pathtypes.indexOf(v) != -1 ) {
                        show = true;
                        return false;
                    }
                });
            }
            option.toggle(show);
        });

        if ( aggregtypes ) {
            if ( aggregtypes.length == 0 )
                elem.find("option").removeClass("hidden");

            else {
                elem.find("option").addClass("hidden");
                $.each(aggregtypes, function(i, v) {
                    elem.find("option[data-type='" + v + "']").removeClass("hidden");
                });

                // Remove default paths if the optgroup is empty
                var optgroup = elem.find("optgroup:eq(0)");
                if ( optgroup.find("option:not(.hidden)").length == 0 ) {
                    optgroup.remove();
                }

                // If there are no paths, fallback to "count" aggregation type
                if ( elem.find("option:not(.hidden)").length == 0 ) {
                    aggreg.val("count");
                }
            }
            if ( elem.find("option:not(.hidden)" + _css_filter("value", selected_value)).length > 0 ) {
                // Keep the previous value if it is compatible
                default_value = selected_value;
            }
            else {
                default_value = elem.find("option:not(.hidden)").first().prop("value");
            }
        }

        if ( initial_value && elem.find("option:not(.hidden)" + _css_filter("value", initial_value)).length == 0 ) {
            // Add an entry for the initial value if it is not present (for instance, indexed fields)
            elem.append(new Option(initial_value, initial_value, false, false));
        }

        elem.val(initial_value || default_value)
            .removeAttr("value")
            .trigger("change");

        elem.parent().toggle(aggreg.val() != "count");
    }

    function _update_filters() {
        var select = root.find("select[name=filter]");
        select.find("option[class!='no-filter']").addClass("hidden");

        var types = [];
        $(".data-type").each(function() {
            var type = $(this).val();
            if ( $.inArray(type, types) == -1 ) {
                types.push(type);
                select.find("option[data-type*='" + type + "']").removeClass("hidden");
            }
        });

        if ( select.find("option:selected").hasClass("hidden") )
            select.val("").trigger("change");
    }

    function _get_query() {
        var ret = [];
        $(".query-instance").each(function() {
            ret.push({
                'datatype': $(this).find('.data-type').val() || undefined,
                'path': _get_paths(this),
                'aggregate': _get_aggregation(this),
                'limit': _get_limit(this),
                'order': $(this).find('.graph-order').val() || undefined
            });
        });

        if ( ret.length == 0 )
            return null;

        return ret;
    }

    function _get_paths(selector) {
        var ret = [];
        $(selector).find('.groupby-path').each(function() {
            if ( $(this).next().is(":visible") )
                ret.push($(this).val());
        });

        if ( ret.length > 0 )
            return ret;
    }

    function _get_aggregation(selector) {
        var func = $(selector).find('.aggreg-type').val();
        if ( !func )
            return null;

        var path = $(selector).find('.aggreg-path').val();

        // The path may be null if no paths are compatible with the aggregation type
        if ( func == "count" || !path )
            return "count(1)";
        else if ( func == "count_distinct" )
            return "count(distinct(" + path + "))";
        else
            return func + "(" + path + ")";
    }

    function _get_limit(selector) {
        var value = $(selector).find('.graph-limit').val();
        if ( value )
            return parseInt(value);
    }

    function _get_period() {
        var mode = root.find("[name=timeline_mode]").val();
        if ( mode === "" ) {
            return null;
        }

        else if ( mode === "custom" ) {
            return {
                'mode': "custom",
                'start': parseInt(root.find("[name=timeline_start]").val()),
                'end': parseInt(root.find("[name=timeline_end]").val())
            };
        }

        return {
            'mode': mode,
            'value': parseInt(root.find("[name=timeline_value]").val()),
            'unit': root.find("[name=timeline_unit]").val(),
            'offset': parseInt(root.find("[name=timeline_offset]").val()),
        };
    }

    function _destroy() {
        $('select.data-paths').select2('destroy');
    }


    root.on('click', 'a[data-multiple]', function() {
        $(this).closest("ul.nav").children().toggleClass("active");

        var multiple = $(this).data("multiple") == "yes";
        $("div.query-panel").toggleClass("multiple", multiple);
        $("div.query-instance").toggleClass("instance", multiple);

        if ( ! multiple )
            $(".query-instance:gt(0)").remove();
    });

    root.on('change', '.data-type', function() {
        if ( root.find(".modal-body").hasClass("category-diagram") ) {
            var value = $(this).val();
            $(".data-type").each(function() {
                $(this).val(value);
                _datatype_changed($(this));
            });
        }
        else
            _datatype_changed($(this));

        _update_filters();
    });

    root.on('change', '.aggreg-type', function() {
        _aggregation_changed($(this));
    });

    root.on('reset_row', ".repeat-entry", function() {
        if ( $(this).siblings(".repeat-entry").length > 0 ) {
            $(this).find(".select2-container").remove();
            _init_paths($(this).find("select.data-paths"));
        }
    });

    root.on('click', '.add-instance', function() {
        var instance = $(this).closest(".panel-heading").siblings(".panel-body").find(".instance").last();
        var new_instance = instance.clone();
        new_instance.find(".select2-container").remove();
        new_instance.find(".data-type").val(instance.find(".data-type").val());
        instance.after(new_instance);
        _init_paths(new_instance.find("select.data-paths"));
        new_instance.find(".aggreg-type").trigger("change");
    });

    root.on('click', '.del-instance', function() {
        var instance = $(this).closest(".query-instance");
        if ( instance.siblings(".query-instance").length > 0 )
            instance.remove();

        _update_filters();
    });

    root.on('submit_prepare', 'form', function(event, obj) {
        $.extend(obj, {
            type: $('#graph-type').val(),
            title: $('#graph-name').val() || labels['No title'],
            subtitle: $('#graph-subtitle:visible').val() || null,
            scale: $('#graph-scale:visible').val() || null,
            unit: $('#graph-unit:visible').val() || null,
            query: _get_query(),
            datatype: null,
            path: null,
            aggregate: null,
            limit: null,
            order: null,
            filter: root.find('select[name=filter]').val() || null,
            period: _get_period(),
            datasource: root.find('input[name=datasource]').val() || null
        });
    });

    root.on('submit', 'form', function() {
        var widget = {};
        $(this).trigger("submit_prepare", [widget]);
        widget.id = $('#graph-id').val();
        widget.category = $('#graph-category').val();
        widget.description = $('#graph-description').val() || null;
        widget.save = true;
        $(".widget-listener").trigger("addWidget", [widget]);
        $(this).closest(".modal").modal("hide");

        return false;
    });

    _init_paths($("select.data-paths"));
    $("select.data-type").each(function() {
        _datatype_changed($(this));
    });
    _update_filters();

    return {destroy: _destroy};
}
