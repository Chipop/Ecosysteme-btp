function addPost(e, frm) {
    e.preventDefault();

    if ($("#statut").val() == "" && $(frm).find("#IMGST").get(0).files.length === 0 && $(frm).find("#VIDST").get(0).files.length === 0 && $(frm).find("#DOCST").get(0).files.length === 0) {
        swal("Veuiller ajouter un statut");
        return;
    }

    $("#btAddPost").css('cursor', 'no-drop');
    $("#btAddPost").html('<img src="{% static "SocialMedia/img/YX5xG_s-200x150.gif" %}" width=30 height=30 />');

    var form_data = new FormData($(frm)[0]);
    addStatutURL = "{% url 'SocialMedia:addStatutMyProfil' %}";

    $.ajax({
        url: addStatutURL,
        type: 'POST',
        processData: false,
        contentType: false,
        data: form_data,
        beforeSend: function (xhr, settings) {
            var csrftoken = getCookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            $("#statut").val('');
            {% if not statuts %}
            location.reload();
            {% endif %}
            $("#AddedStatut").prepend(data);
            $(".LinkPreview").hide();
            $("#chargementPreview").hide();
            $("#IMAGESTATUT").attr('src', '');
            $("#IMGST").val('');
            $("#VIDEOSTATUT").attr('src', '');
            $("#VIDST").val('');
            $("#DOCSTATUT").text('');
            $("#DOCST").val('');
            $("#PHOTOPOST").fadeOut(150);
            $("#VIDEOPOST").fadeOut(150);
            $("#DOCPOST").fadeOut(150);
            $("#statut").slideUp(350);
            $(".btstatutHIDESHOW").slideDown(350);
        },
        error: function () {
        },
        complete: function () {
            $("#btAddPost").html('Publier');
            $("#btAddPost").css('cursor', 'pointer');
            $("#CLEARINTUSER").fadeOut();
            $(".LinkPreview").hide();
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });
}