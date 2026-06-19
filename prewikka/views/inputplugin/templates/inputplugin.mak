<%!
  from prewikka import hookmanager, utils
  import json
%>

  <link rel="stylesheet" type="text/css" href="inputplugin/css/inputplugin.css" />

  <div class="container">
    <div class="widget" role="dialog" aria-labelledby="dialogLabel" aria-hidden="true" data-backdrop="false" data-draggable="true" data-widget-options="modal-lg">
         <div class="modal-body">
           <form class="form-horizontal" id="inputplugin_form" method="POST">
           <div class="form-group">
             <label for="selfile" class="col-sm-2 control-label">${ _("Scenarios:") }</label>
             <div class="col-sm-10">
               <select id="selfile" class="form-control" name="selfile" size="6" required>
               % for idmefv2 in idmefv2files:
                 <option value="${ idmefv2[0] }_${ len(json.loads(idmefv2[2])) }">${ idmefv2[1] }</option>
               % endfor
               </select>
             </div>
           </div>
           <div class="form-group">
               <div class="col-sm-1">
                 <button type="submit" class="btn btn-primary" form="inputplugin_form" formaction="${ url_for('.inputplugin_delete_file') }"><i class="fa fa-save"></i> ${ _("Delete") }</button>
               </div>
           </div>
           <div class="form-group">
             <label for="create_time" class="col-sm-2 control-label"></label>
             <div class="col-sm-6">
               <label class="list-group-item">
                 <input type="checkbox" id="create_time" name="create_time" value="1" class="pull-left" style="margin-right:10px;">
                   Incidents date starting now
                   <span class="badge pull-right"></span>
             </div>
           </div>
           <div class="form-group">
             <div class="col-sm-3">
             <label for="step_time" class="col-sm-2 control-label">Step (in ms)</label>
             </div>
             <div class="col-sm-3">
                 <input type="text" id="step_time" name="step_time" value="0" class="form-control">
             </div>
             <div class="col-sm-3">
                 <button type="submit" class="btn btn-primary" form="inputplugin_form" formaction="${ url_for('.inputplugin_run_file') }"><i class="fa fa-save"></i> ${ _("Run") }</button>
             </div>
           </div>
           <div class="form-group">
             <div class="col-sm-3">
             <label for="n_step" class="col-sm-2 control-label" id="label_n_step">Run step by step. Please select a file.</label>
              <input type="hidden" id="n_step" name="n_step" value="0" class="form-control">
                 <a id="next_step" class="btn btn-primary disabled" myaction="${ url_for('.inputplugin_run_step') }"><i class="fa fa-save"></i> ${ _("Next step") }</a>
             </div>
           </div>
           </form>
           <div class="divider">&nbsp;</div>
           <hr style="border-top: 1px solid #ccc;" />
           <form class="form-horizontal" action="${ url_for('.inputplugin_add_file') }" method="POST" enctype="multipart/form-data">
             <div class="form-group">
               <label for="addfile" class="col-sm-2 control-label">${ _("New file:") }</label>
               <div class="col-sm-10">
                 <div class="input-group">
                   <label class="input-group-btn">
                     <span class="btn btn-default btn-sm">
                       ${ _("Browse") }
                       <input type="file" widht="100" id="addfile" name="file" class="form-control" required>
                     </span>
                   </label>
                   <input type="text" class="form-control input-sm" readonly>
                 </div>
               </div>
             </div>
             <div class="form-group">
               <div class="col-sm-10"></div>
               <div class="col-sm-2">
                 <button type="submit" class="btn btn-primary" value="submit"><i class="fa fa-save"></i> ${ _("Upload") }</button>
               </div>
             </div>
           </form>
         </div>
     </div>
  </div>

  <script type="text/javascript">
    $LAB
      .script("inputplugin/js/inputplugin.js")
      .wait(function () {
      });
  </script>
