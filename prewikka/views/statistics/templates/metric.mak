<%inherit file="/prewikka/views/statistics/templates/widgetedition.mak" />

<%block name="form_options">
  <div class="form-group">
    <label for="graph-subtitle" class="col-sm-3 control-label input-sm">${ _("Legend:") }</label>
    <div class="col-sm-9">
      <input id="graph-subtitle" type="text" class="form-control input-sm" value="${ widget.get('subtitle') }" placeholder="${ _('Additional text') }">
    </div>
  </div>
</%block>
