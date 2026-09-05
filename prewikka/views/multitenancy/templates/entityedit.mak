<div class="container">
  <div class="widget ui-front" role="dialog" aria-labelledby="dialogLabel" aria-hidden="true" data-backdrop="false" data-draggable="true" data-widget-options="modal-lg">

  <script type="text/javascript">
    $(".entity-database").select2_container();
    prewikka_autocomplete("select[data-ajax--url]");
  </script>

  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
    <h5 class="modal-title" id="dialogLabel">${ _("Entity %s") % tenant.name if tenant.name else _("New entity") }</h5>
  </div>

  <form class="form-horizontal" id="entity" action="${ url_for('.save', name=tenant.name) }" method="POST">
    <input type="hidden" name="tenantid" value="${tenant.id}" />

    <div class="modal-body content">

      <div class="panel panel-theme">
        <div class="panel-heading">
          <h3 class="panel-title">${_("Entity information")}</h3>
        </div>
        <div class="panel-body">

          <div class="form-group">
            <label for="entity-name" class="col-sm-2 control-label">${ _("Name:") }</label>
            <div class="col-sm-10">
              <input class="form-control" type="text" name="name" id="entity-name" value="${tenant.name}" placeholder="${ _("Name") }" required />
            </div>
          </div>

          <div class="form-group">
            <label for="entity-contact" class="col-sm-2 control-label">${ _("Contact:") }</label>
            <div class="col-sm-10">
              <input class="form-control" type="text" name="contact" id="entity-contact" value="${tenant.contact}" placeholder="${ _("Emergency phone number or email address to contact") }" />
            </div>
          </div>

          <div class="form-group">
            <label for="users[]" class="col-sm-2 control-label">${ _("Users:") }</label>
            <div class="col-sm-10">
              <select name="users[]" multiple class="form-control" data-ajax--url="${ url_for("UserListingAjax.search") }">
                % for user in tenant.users:
                <option name="${ user }" selected>${ user }</option>
                % endfor
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="groups[]" class="col-sm-2 control-label">${ _("Groups:") }</label>
            <div class="col-sm-10">
              <select name="groups[]" multiple class="form-control" data-ajax--url="${ url_for("GroupListingAjax.search") }">
                % for group in tenant.groups:
                <option name="${ group }" selected>${ group }</option>
                % endfor
              </select>
            </div>
          </div>

          <!-- Extra settings -->
          % for i in extra_content :
          ${ i }
          % endfor
          <!-- -->
        </div>
      </div>

      <div class="panel panel-theme">
        <div class="panel-heading">
          <h3 class="panel-title">${_("Databases")}</h3>
        </div>
        <div class="panel-body">

          % for datatype in sorted(datatypes):
          <div class="form-group">
            <label class="col-sm-2 control-label">${ _(env.dataprovider.get_label(datatype)) }</label>
            <div class="col-sm-10">
              <select class="form-control entity-database" name="database[${datatype}]" data-placeholder="${ _("Select a database") }">
                % for db in alldatabases[datatype]:
                <option value="${ db }" ${ selected(db == tenant.db.get(datatype)) }>${ db }</option>
                % endfor
              </select>
            </div>
          </div>
          % endfor

        </div>
      </div>

    </div>

    <div class="modal-footer">
      <button type="button" class="btn btn-default" data-dismiss="modal">${ _("Cancel") }</button>
      <button type="submit" class="btn btn-primary save"><i class="fa fa-save"></i> ${ _("Save") }</button>
    </div>
  </form>
</div>

</div>
