<%inherit file="/prewikka/views/statistics/templates/embeddedstats.mak" />

<%block name="dashboard_intro">
  <h4>${ _("Information") }</h4>
  <div class="col-container">
    <div class="col-md-6">
      % for label, value in label_list:
        % if value:
        <div class="list-group-item">
          <label>${ label }</label> ${ value }
        </div>
        % endif
      % endfor
    </div>
    <div class="col-md-6 text-center">
      <label>${ _("Alerts by severity") }</label>
      <p>
        % for label, severity, klass in ((_("High:"), "high", "danger"), (_("Medium:"), "medium", "warning"), (_("Low:"), "low", "success"),  (_("Info:"), "info", "info")):
        <label class="label label-${ klass } peruser">${ label } ${ alerts[severity] }</label>
        <br/>
        % endfor
      </p>
    </div>
  </div>
  <br/><h4>${ _( graph_title ) }</h4>
</%block>

<%block name="dashboard_styles_extension">
/* Adjust col*/
.col-container {
    display: table;
    width: 100%;
    margin-right: 10px;
    margin-left: 10px;
}
.col {
    display: table-cell;
    padding: 16px;
    background: #f5f5f5;
}

.label.peruser {
    min-width: 200px;
    display: inline-block;
}
</%block>
