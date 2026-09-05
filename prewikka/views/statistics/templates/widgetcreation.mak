<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal">&#215;</button>
  <h5 class="modal-title">${ _("New widget") }</h5>
</div>
<div class="modal-body">
  <p>${ _("Please choose the type of widget to be created:") }</p>
  <div class="list-group">
    % for name, category in categories.items():
    % if category.is_enabled():
    <a href="${ url_for('WidgetEdition.edit', category=name) }" class="list-group-item" data-dismiss="modal">
      <h4><i class="fa ${ category.icon }"></i> ${ _(category.label) }</h4>
      ${ _(category.description) }
    </a>
    % endif
    % endfor
  </div>
</div>
