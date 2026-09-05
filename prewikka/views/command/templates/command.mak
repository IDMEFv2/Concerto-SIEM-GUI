<div class="container">
  <div class="widget" role="dialog" aria-labelledby="dialogLabel" aria-hidden="true" data-widget-options="modal-lg">

    <script type="text/javascript">
        prewikka_EventSource({
            url: "${ url_for('Command.cmdajax', command=command, value=value) }",
            message: function(data) {
                $("div.fixed").append(data);
            }
        });
    </script>

    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal">&times;</button>
      <h5 class="modal-title">${ _("Prelude command") }</h5>
    </div>

    <div class="modal-body fixed"></div>

    <div class="modal-footer">
      <button class="btn btn-default widget-only" aria-hidden="true" data-dismiss="modal">${ _("Close") }</button>
    </div>
  </div>
</div>
