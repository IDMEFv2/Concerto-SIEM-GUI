<%inherit file="/prewikka/views/statistics/templates/widgetedition.mak" />

<%def name="multiple()">
  <% return len(widget.get("query", [])) > 0 and "path" not in widget["query"][0] %>
</%def>

<%block name="form_header">
  <ul class="nav nav-pills nav-justified">
    <li class="${ 'active' if not self.multiple() else '' }"><a data-multiple="no">${ _("Per value") }</a></li>
    <li class="${ 'active' if self.multiple() else '' }"><a data-multiple="yes">${ _("Per query") }</a></li>
  </ul>
</%block>

<%block name="form_options">
  <div class="form-group">
    <label for="graph-scale" class="col-sm-3 control-label input-sm">${ _("Scale:") }</label>
    <div class="col-sm-9">
      <select class="form-control input-sm" id="graph-scale">
        % for scale in (N_("linear"), N_("logarithmic")):
        <option value="${ scale }" ${ selected(scale == widget.get('scale')) }>${ _(scale) }</option>
        % endfor
      </select>
    </div>
  </div>
</%block>
