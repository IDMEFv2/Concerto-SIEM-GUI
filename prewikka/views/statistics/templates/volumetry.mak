<%inherit file="/prewikka/views/statistics/templates/statistics.mak" />

<%block name="statistics_view_parameters_extension">
    <p class="list-group-item">
        <label for="reference_date">${ _("Reference date") }</label>
        <input id="reference_date" class="form-control" title="${ _("Start date for the reference curves") }" data-name="reference_date" data-toggle="tooltip" data-container="body" data-trigger="hover" />
    </p>
</%block>

<%block name="statistics_scripts_extension">
    var options = {
       "dateFormat": "${ date_format }",
       "timeFormat": "HH:mm:ss",
       "maxDate": "now"
    };

    DatetimePicker($("#reference_date"), "${ reference_date }", options);
</%block>
