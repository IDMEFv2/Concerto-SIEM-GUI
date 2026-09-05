<%inherit file="/prewikka/views/statistics/templates/statistics.mak"/>

<%block name="statistics_view_parameters_extension">

<%block name="dashboard_view_parameters_extension">
</%block>

% if options["editable"]:
  <p>
    <input id="edit-mode" class="checkbox-edit" type="checkbox" name="edition_enabled" ${ checked(options["edit_mode"]) } />
    <label for="edit-mode" class="list-group-item label-edit"><span class="badge"><a></a></span>${ _("Edition") }</label>
  </p>
  <p>
    <input class="btn btn-default btn-block add-widget" type="button" data-toggle="modal" data-target="#add-widget-dialog" value="${ _('Add widget') }" ${ disabled(not options["edit_mode"]) } />
  </p>
  <p class="btn-group btn-block">
    <input class="btn btn-default col-xs-6 export-grid" type="button" value="${ _('Export') }" />
    <input class="btn btn-default col-xs-6 import-grid" type="button" value="${ _('Import') }" ${ disabled(not options["edit_mode"]) } data-confirm="${ _('You\'re about to import a dashboard. All the current widgets will be replaced.') }" />
  </p>
  <p>
    <input class="btn btn-danger btn-block reset-grid" type="button" data-toggle="modal" data-target="#reset-dialog" value="${ _('Erase') }" ${ disabled(not options["edit_mode"]) } />
  </p>
% endif
</div>

</%block>

<%block name="statistics_header">

<link rel="stylesheet" type="text/css" href="dashboard/css/dashboard.css">

<%block name="dashboard_header">
</%block>

<div id="empty-dashboard-dialog" class="modal fade">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&#215;</button>
        <h5 class="modal-title">${ _("Init dashboard") }</h5>
      </div>
      <div class="modal-body">
        <p>${ _("It seems that the current dashboard is empty. Would you like us to fill it with the default widgets?") }</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-default" data-dismiss="modal">${ _("No thanks, I'll do it") }</button>
        <button class="btn btn-primary" data-dismiss="modal" id="confirm-init">${ _("Yes, please") }</button>
      </div>
    </div>
  </div>
</div>

<div id="reset-dialog" class="modal fade">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&#215;</button>
        <h5 class="modal-title">${ _("Erase dashboard") }</h5>
      </div>
      <div class="modal-body">
        <p>${ _("You're about to erase the dashboard. All the current widgets will be deleted.") }</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-default" data-dismiss="modal">${ _("Cancel") }</button>
        <button class="btn btn-danger" data-dismiss="modal" id="confirm-reset">${ _("Reset") }</button>
      </div>
    </div>
  </div>
</div>

<div id="add-widget-dialog" class="modal fade">
  <div class="modal-dialog">
    <div class="modal-content">
      <%include file="/prewikka/views/statistics/templates/widgetcreation.mak"/>
    </div>
  </div>
</div>

</%block>
