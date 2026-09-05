<%inherit file="/prewikka/views/statistics/templates/widgetedition.mak" />

<%block name="form_scripts">
    $(".widgetedition").off("submit_prepare", "form").on("submit_prepare", "form", function(event, obj) {
        $.extend(obj, {
            title: $('#graph-name').val() || $('#image-url').val(),
            url: $('#image-url').val()
        });
    });
</%block>

<%block name="form_options">
  <div class="form-group">
    <label for="image-url" class="col-sm-3 control-label input-sm">${ _("URL:") }</label>
    <div class="col-sm-9">
      <input id="image-url" type="text" class="form-control input-sm" value="${ widget.get('url') }" placeholder="${ _('URL of the image') }">
    </div>
  </div>
</%block>
