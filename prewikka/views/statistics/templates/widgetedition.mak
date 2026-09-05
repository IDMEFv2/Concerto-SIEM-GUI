<%!
  import re
  from collections import OrderedDict
%>

<%
  labels = dict((label, _(label)) for label in (
      N_("No title"),
  ))
%>

<%def name="multiple()">
  <% return False %>
</%def>

<%def name="path_select(typ, default_paths, all_paths)">
    <select class="${typ}-paths" style="display:none">
        <optgroup label="${_('Default paths')}">
            % for label, path in default_paths.values():
            <option value="${path.path}" data-type="${path.type.__name__}">${_(label)}</option>
            % endfor
        </optgroup>
        <optgroup label="${_('All paths')}">
            % for path in all_paths:
            <option value="${path.path}" data-type="${path.type.__name__}">${path.path}</option>
            % endfor
        </optgroup>
    </select>
</%def>

<div class="container">
  <div class="widget ui-front widgetedition" role="dialog" aria-labelledby="dialogLabel" aria-hidden="true" data-draggable="true">

    <link rel="stylesheet" type="text/css" href="dashboard/css/dashboard.css">

    <script type="text/javascript">
      $LAB.script("dashboard/js/widgetedition.js").wait(function() {
            prewikka_resource_register(WidgetEdition($(".widgetedition"), ${ html.escapejs(labels) }));
            <%block name="form_scripts" />
      });
    </script>

    <form>
      <%
        if categories[category].filterable:
            default_paths = {}
            all_paths = {}

            for typ, label in datatypes:
                default_paths = OrderedDict()
                for label, path in env.dataprovider.get_common_paths(typ):
                    default_paths[path] = (_(label), env.dataprovider.get_path_info(path))

                all_paths = []
                for path in env.dataprovider.get_paths(typ):
                    if path not in default_paths:
                        all_paths.append(env.dataprovider.get_path_info(path))
                path_select(typ, default_paths, all_paths)
      %>

      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&#215;</button>
        <h5 class="modal-title">${ _("Edit widget") if widget else _("Add widget") }</h5>
      </div>

      <div class="modal-body category-${ category }">
        <input type="hidden" id="graph-category" value="${ category }"/>
        <input type="hidden" id="graph-id" value="${ widget.get('id') }"/>

        <%block name="form_header" />
        <% multiple = self.multiple() %>

        <div class="form-horizontal">

          <div class="panel panel-theme">
            <div class="panel-heading">
              <h3 class="panel-title">${ _("General") }</h3>
            </div>
            <div class="panel-body">
              <div class="form-group">
                <label for="graph-name" class="col-sm-3 control-label input-sm">${ _("Name:") }</label>
                <div class="col-sm-9">
                  <input id="graph-name" type="text" class="form-control input-sm" value="${ widget.get('title') }" placeholder="${ _('Name of the widget') }">
                </div>
              </div>
              <div class="form-group">
                <label for="graph-name" class="col-sm-3 control-label input-sm">${ _("Description:") }</label>
                <div class="col-sm-9">
                  <textarea id="graph-description" class="form-control input-sm vresize" placeholder="${ _('Description of the widget') }">${ widget.get('description') }</textarea>
                </div>
              </div>
              % if graphtypes:
              <div class="form-group">
                <label for="graph-type" class="col-sm-3 control-label input-sm">${ _("Graph type:") }</label>
                <div class="col-sm-9">
                  <select class="form-control input-sm" id="graph-type">
                    % for type in sorted(graphtypes):
                    <option value="${ type }" ${ selected(type == widget.get('type')) }>${ type }</option>
                    % endfor
                  </select>
                </div>
              </div>
              % endif
              <%block name="form_options" />

            </div>
          </div>

          % if categories[category].query:
          <div class="panel panel-theme query-panel ${ 'multiple' if multiple else '' }">
            <div class="panel-heading">
              <h3 class="panel-title">
                ${ _("Query") }
                <button type="button" class="add-instance btn btn-default input-sm" title="${_('Add a new query')}">
                  <i class="fa fa-plus"></i>
                </button>
              </h3>
            </div>
            <div class="panel-body">
              % for query in widget.get("query", [{}]):
              <%
                datatype = query.get("datatype", query["path"][0].split(".")[0] if query.get("path") else None)
              %>
              <div class="query-instance ${ 'instance' if multiple else '' }">
                <h4>
                  <span class="input-group-btn" style="float: right; width: auto;">
                    <button type="button" class="del-instance btn btn-default input-sm" title="${_('Delete the query')}">
                      <i class="fa fa-trash"></i>
                    </button>
                   </span>
                </h4>
                <div class="form-group">
                  <label class="col-sm-3 control-label input-sm">${ _("Data type:") }</label>
                  <div class="col-sm-9">
                    <select class="form-control input-sm data-type">
                      % for value, label in sorted(datatypes):
                      <option value="${ value }" ${ selected(value == datatype) }>${ _(label) }</option>
                      % endfor
                    </select>
                  </div>
                </div>
                % if categories[category].aggregation:
                <%
                  aggreg_func, aggreg_path = re.split("[()]", query.get("aggregate", "count(1)").replace("count(distinct", "count_distinct"))[:2]
                  if aggreg_path == "1":
                      aggreg_path = None
                %>
                <div class="form-group">
                  <label class="col-sm-3 control-label input-sm">${ _("Aggregation:") }</label>
                  <div class="col-sm-3">
                    <select class="form-control input-sm aggreg-type">
                      % for value, label, types in aggregtypes:
                      <option value="${ value }" data-types="${ ' '.join(typ.__name__ for typ in (types or [])) }" ${ selected(value == aggreg_func) }>${ _(label) }</option>
                      % endfor
                    </select>
                  </div>
                  <div class="col-sm-6" style="${ 'display: none;' if aggreg_func == 'count' else '' }">
                    <select class="data-paths form-control input-sm aggreg-path" value="${ aggreg_path }" data-placeholder="${_('Select a path...')}"></select>
                  </div>
                </div>
                % endif
                % if categories[category].grouping:
                <div class="form-group">
                  <label class="col-sm-3 control-label input-sm">${ _("Group by:") }</label>
                  <div class="col-sm-9">
                    % for path in query.get("path", [None]):
                    <div class="input-group repeat-entry">
                      <select class="data-paths form-control input-sm groupby-path" value="${ path }" data-placeholder="${_('Select a path...')}"></select>
                      <span class="input-group-btn">
                        <div class="add_entry_row btn btn-default input-sm"><i class="fa fa-plus"></i></div>
                        <div class="del_entry_row btn btn-default input-sm"><i class="fa fa-minus"></i></div>
                      </span>
                    </div>
                    % endfor
                  </div>
                </div>
                <div class="form-group">
                  <label class="col-sm-3 control-label input-sm">${ _("Limit:") }</label>
                  <div class="col-sm-9">
                    <input type="number" class="form-control input-sm graph-limit" min="-1" max="${ 2**31-1 }" value="${ query.get('limit') }" placeholder="${_('Let empty to use the limit of the page')}"/>
                  </div>
                </div>
                <div class="form-group">
                  <label class="col-sm-3 control-label input-sm">${ _("Order:") }</label>
                  <div class="col-sm-9">
                    <select class="form-control input-sm graph-order">
                      <option value="desc" ${ selected(query.get('order') == 'desc') }>${ _("Descending") }</option>
                      <option value="asc" ${ selected(query.get('order') == 'asc') }>${ _("Ascending") }</option>
                    </select>
                  </div>
                </div>
                % endif
              </div>
              % endfor
            </div>
          </div>
          % endif

          % if categories[category].filterable:
          <div class="panel panel-theme">
            <div class="panel-heading">
              <h3 class="panel-title">${ _("Filtering") }</h3>
            </div>
            <div class="panel-body">
              ${ mainmenu }
            </div>
          </div>
          % endif

        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal" aria-hidden="true">${ _("Cancel") }</button>
        <button type="submit" class="btn btn-primary" aria-hidden="true">${ _("OK") }</button>
      </div>

    </form>
  </div>
</div>
