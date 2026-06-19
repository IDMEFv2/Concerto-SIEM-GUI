document.addEventListener("change", function(e) {
    if (e.target.matches("#selfile")) {

// document.getElementById("selfile").addEventListener("change", function() {
    document.getElementById("n_step").value = 0;
    let label = document.getElementById("label_n_step");
    label.textContent = "Run step by step. Actual step: 0/" + document.getElementById('selfile').value.split('_')[1];
    document.getElementById("next_step").classList.remove("disabled");
    }
});

document.addEventListener("click", function(e) {
if (e.target.matches("#next_step")) {
//document.getElementById("next_step").addEventListener("click", function(e) {
    e.preventDefault();
    if (document.getElementById("n_step").value ==  document.getElementById('selfile').value.split('_')[1] ) {
        return;
    }
    let input = document.getElementById("n_step");
    input.value = parseInt(input.value || 0) + 1;
    if (document.getElementById("n_step").value ==  document.getElementById('selfile').value.split('_')[1] ) {
        document.getElementById("next_step").classList.add("disabled");
    }
    let label = document.getElementById("label_n_step");
    label.textContent = "Run step by step. Actual step: " + input.value + "/" + document.getElementById('selfile').value.split('_')[1];
    $.ajax({
        type: 'GET',
        url: document.getElementById("next_step").getAttribute('myaction'),
        data: $("#inputplugin_form :input").serializeArray(),
        prewikka: {spinner: false, error: false},
        success: function(data) {
        },
        error: function(xhr, status, error) {
        },
        complete: function() {
        }
    });
    }
});
