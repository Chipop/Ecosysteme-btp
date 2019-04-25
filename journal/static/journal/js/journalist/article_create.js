

$("#modal-submit").click(function(){
    $("#modal-form-submit").click();
});

function success_hide() {
    $("#modal-success").hide();
}
function danger_hide() {
    $("#modal-danger").hide();
}
function progress_hide() {
    $("#modal-progress").hide();
}


$(".form-delete-image").submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-submit-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(data.message == "success") {
			    $(data.tr).remove();
            }
		}
    });
});

success_hide();
danger_hide();

