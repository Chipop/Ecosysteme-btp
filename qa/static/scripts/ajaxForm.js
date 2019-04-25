$( ".formLike" ).submit(function( event ) {
	event.preventDefault();
	var form = $(this);
    $.ajax({
		url: form.attr("data-validate-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			$(data.id).html(data.number);
			$(data.div).css('display', 'none');
		}
    });
});