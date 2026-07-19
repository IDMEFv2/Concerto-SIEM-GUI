<%def name="filter_add_entry(value)">
    <div class="repeat-entry">
        <div class="input-group">
            <select name="existing_filter[]" class="form-control">
                <option value=""></option>
            % for f, activated in available_filters:
                <option value="${ f }" ${ selected(f == value) }>${ f }</option>
            % endfor
            </select>

            <span class="input-group-btn">
                <div class="add_entry_row btn btn-default"><i class="fa fa-plus"></i></div>
                <div class="del_entry_row btn btn-default"><i class="fa fa-minus"></i></div>
            </span>
        </div>
    </div>
</%def>


<div class="form-group">
    <label for="prohibitive_filter_input" class="col-sm-2 control-label">${ _("Prohibitive Filter:") }</label>
    <div class="col-sm-10" id="prohibitive_filter">
      % for owner, name in other_users_filters:
       <tr style="font-size: 10px;">
        <th>${ _("External filter set by:") } <b>${ owner }</b></th>
        <td colspan=3><b>${ name }</b></td>
       </tr>
      % endfor

      <% num = 0 %>

      % for f, activated in available_filters:
       % if activated:
         ${ filter_add_entry(f) }
         <% num += 1 %>
       % endif
      % endfor

      % if num == 0:
       ${ filter_add_entry("") }
      % endif
    </div>
</div>
