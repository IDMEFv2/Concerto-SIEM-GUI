<%
  root_id = 'main_menu_ng' if inline else 'main_menu_ng_block'
%>

<div>
  <label>${ _("DataSource:") }</label>
</div>

<div>
  <script>
      $("#${root_id} select[name=datasource]").select2_container({
          dropdownAutoWidth: true
      })
      .on("select2:close", function() {
          // Prevent tooltip from staying after closing the select
          setTimeout(function() {
              $(":focus").blur();
          }, 1);
      });

      // Handle the tooltip ourselves
      $("#${root_id} .dropdown-tenant .select2-container").tooltip({
          title: "${_("Available entities")}",
          container: "#main"
      });
      $("#${root_id} .dropdown-tenant .select2-selection__rendered").removeAttr("title");
  </script>

  <div class="dropdown dropdown-fixed dropdown-tenant">
    <select name="datasource" class="form-control input-${ input_size }">
    % if period_optional:
      <option value="">${ _("None") }</option>
    % endif
    % if tenants:
      <optgroup label="${ _("Entities") }">
      % for name in tenants:
        <option value="tenant:${ name }" ${ selected("tenant:%s" % name == current_source) }>${ name }</option>
      % endfor
      </optgroup>
    % endif
    % if databases:
      <optgroup label="${ _("Databases") }">
      % for name in databases:
        <option value="database:${ name }" ${ selected("database:%s" % name == current_source) }>${ name }</option>
      % endfor
      </optgroup>
    % endif
    </select>
  </div>

</div>
