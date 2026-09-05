<script type="text/javascript">
    var grid = CommonListing('table#entities', {'title': "${_('Entities')}", 'search': "${_('Search:')}" }, {
        colModel: [
            {name: 'name', label: "${ _('Name') }", width: 20, key: true},
            {name: 'contact', label: "${ _('Contact') }", width: 20},
            {name: 'users', label: "${ _('Users') }", width: 20},
            {name: 'groups', label: "${ _('Groups') }", width: 20},
            % for datatype in sorted(datatypes):
            {name: '${datatype}', label: "${ _('Database (%s)') % env.dataprovider.get_label(datatype) }", width: 20},
            % endfor
        ],
        data: ${ html.escapejs(data) },
        deleteLink: "${url_for('.delete')}",
        globalSearch: true,
    }, ${html.escapejs(env.request.parameters["jqgrid_params_entities"])});
</script>

<table id="entities"></table>

<div class="footer-buttons">
  <a href="${ url_for('.edit') }" class="btn btn-primary"><i class="fa fa-plus"></i> ${ _("Create") }</a>
  <button type="button" class="btn btn-danger needone button-delete" data-confirm="${ _("Delete the selected entities?") }"><i class="fa fa-trash"></i> ${ _("Delete") }</button>
</div>
