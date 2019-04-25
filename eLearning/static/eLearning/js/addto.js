var cart = {
    'add': function(id_course, logged) {
        if(logged === "True") {
            var form = $('#formAddToCart'+id_course);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === "")
                        swal({title: "Succès!", text: "Cours ajouté au panier !", icon: "success"});
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        }
        else
            swal({title: "Erreur!", text: "Vous devez se connecter", icon: "error"});
    },
    'remove':function(id_course) {
        var form = $('#formRemoveFromCart'+id_course);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "")
                    swal({title: "Succès!", text: "Cours retiré de votre panier!", icon: "success"});
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    }
};
var wishlist = {
    'add': function(id_course, logged) {
        if(logged === "True") {
            var form = $('#formAddToWish'+id_course);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === "")
                        swal({title: "Succès!", text: "Cours ajouté au favoris !", icon: "success"});
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        }
        else
            swal({title: "Erreur!", text: 'Vous devez se connecter', icon: "error"});
    },
    'remove':function(id_course) {
        var form = $('#formRemoveFromWish'+id_course);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "")
                    swal({title: "Succès!", text: "Cours retiré de votre panier!", icon: "success"});
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    }
};
var progress = {
    'add': function(id_chapter, logged) {
        if(logged === "True") {
            var form = $('#formProgress'+id_chapter);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === ""){
                        $(".last_seen").css('color', '#555');
                        $("#video_link"+id_chapter).css('color', '#ea4c0f').css('font-weight', 'bold').addClass('last_seen');
                        var percentage_progress = parseInt(data.progress);
                        var progress_bar = $("#progress_course");
                        progress_bar.css("width", percentage_progress+"%");
                        progress_bar.html('<b style="font-weight: initial">' + percentage_progress + '%</b>');
                    }
                    else
                    {

                    }
                }
            });
        }
    }
};