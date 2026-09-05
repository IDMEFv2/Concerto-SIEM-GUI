<%inherit file="/prewikka/views/statistics/templates/widgetedition.mak" />

<%block name="form_scripts">
    $(".widgetedition").off("submit_prepare", "form").on("submit_prepare", "form", function(event, obj) {
        $.extend(obj, {
            title: $('#graph-name').val() || $('#view-name option:selected').text(),
            url: $('#view-name option:selected').data('url'),
            view: $('#view-name').val()
        });
    });
</%block>

<%block name="form_options">
  <div class="form-group">
    <label for="view-name" class="col-sm-3 control-label input-sm">${ _("View:") }</label>
    <div class="col-sm-9">
      <select class="form-control input-sm" id="view-name" required>
        % for section in viewlist:
        <optgroup label="${ section.group_label }">
          % for option in section.options:
          <option value="${ option.value }" data-url="${ url_for(option.value) }" ${ selected(option.value == widget.get('view')) }>${ option.label }</option>
          % endfor
        </optgroup>
        % endfor
      </select>
    </div>
  </div>
</%block>
