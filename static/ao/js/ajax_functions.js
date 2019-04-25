$(".bookmark-button").click(function() {
	let form = $(this).parents('form:first');
    $.ajax({
		url: form.attr("data-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(!data.status){
			    $(this).click();
            }
		}
    });
});

$(".add_save").click(function() {
	let form = $(this).parents('form:first');
    $.ajax({
		url: form.attr("data-url"),
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
			if(!data.status){
			    $(this).click();
            }
		}
    });
});

$("#subscribe_submit").click(function() {
	let form = $(this).parents('form:first');
    $.ajax({
		url: form.attr("data-url"),
        data: form.serialize(),
        dataType: 'json',
        type: 'post',
        success: function (data) {
			if(data.status){
			    Snackbar.show({
                    text: 'Votre inscription a été efectué avec Succès',
                });
            } else if(!data.status) {
			    Snackbar.show({
                    text: 'Inscription non effectué, veuillez réssayer',
                });
            }
		}
    });
});
