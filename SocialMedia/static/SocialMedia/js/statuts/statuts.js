function displayStatut(bt) {
    $(bt).fadeOut(0);
    $('#statut').fadeIn(0);
    $('#statut').focus();
}


function hideStatut(txtbox) {
    if ($(txtbox).val().length === 0) {
        $(txtbox).fadeOut(0);
        $(".btstatutHIDESHOW").fadeIn();
    }
}


function add_statut(e, frm) {
    e.preventDefault();

    //alert(addStatutURL);

    console.log("heyy")

    if ($("#statut").val() == "") {
        swal("Veuiller ajouter un contenu au statut.");
        return;
    }

    //Enable inputs before  submiting the form
    enable_st_upload_icons();
    var form_data = new FormData($(frm)[0]);


    $.ajax({
        url: addStatutURL,
        type: 'POST',
        cache: false,
        processData: false,
        contentType: false,
        data: form_data,
        beforeSend: function (xhr, settings) {
            var csrftoken = getCookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }

            $("#st_btn_add_statut").css('cursor', 'no-drop');
            $("#st_btn_add_statut").html(spinner);

        },
        success: function (added_statut) {

            $(frm)[0].reset();

            $("#filActualite").prepend(added_statut);
            $(".LinkPreview").hide();

            $("#st_link_preview_loading").hide();
            $("#st_link_preview_error").hide();
            $("#st_link_preview_details").hide();

            $("#st_publier_video").parent().hide();
            $("#st_publier_images").parent().hide();
            $("#st_publier_fichiers").parent().hide();


            $("#statut").slideUp(350);

            $(".btstatutHIDESHOW").slideDown(350);
            remove_link_preview_displayed();
        },
        error: function () {
            disable_st_upload_icons();
        },
        complete: function () {
            $("#st_btn_add_statut").html('Publier');
            $("#st_btn_add_statut").css('cursor', 'pointer');
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}

function add_comment(e, frm) {
    e.preventDefault();

    //alert(addStatutURL);
    if ($(frm).find('.st_comment_input').val() === "") {
        swal("Veuiller ajouter un contenu au commentaire.");
        return;
    }

    let data_id = $(frm).attr("data-id");
    var form_data = new FormData($(frm)[0]);
    form_data.append('type_st', $(frm).attr("data-type"));
    form_data.append('id', data_id);

    $.ajax({
        url: add_comment_url,
        type: 'POST',
        cache: false,
        processData: false,
        contentType: false,
        data: form_data,
        beforeSend: function (xhr, settings) {
            var csrftoken = getCookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }

            $(frm).find('button[type="submit"]').css('cursor', 'no-drop');
            $(frm).find('button[type="submit"]').html(spinner);

            st_comment_clear_input($(frm).find('.st_comment_input').val(""));
            st_close_comment_img_preview($('.st_comment_img_close_div[data-id=' + data_id + ']'), $('.st_comment_input[data-id=' + data_id + ']'));

        },
        success: function (response) {
            $('.st_comments[data-id=' + data_id + ']').prepend(response.comment);
            $('.st_nb_comments[data-id=' + data_id + ']').text(response.nb_comments);

            $('.clgp').each(function () {
                data_id = ($(this).attr('data-id'));
                if (loaded.indexOf(data_id) === -1) {
                    lightGallery(this, {
                        thumbnail: true
                    });
                    loaded.push(data_id);
                }
            });

        },
        error: function () {

        },
        complete: function () {
            $(frm).find('button[type="submit"]').html('Publier');
            $(frm).find('button[type="submit"]').css('cursor', 'pointer');
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}


function add_comment_reply(e, frm) {
    e.preventDefault();

    //alert(addStatutURL);
    if ($(frm).find('.st_comment_input').val() === "") {
        swal("Veuiller ajouter un contenu au commentaire.");
        return;
    }

    let data_id = $(frm).attr("data-id");
    let type_st = $(frm).attr("data-type");
    let form_data = new FormData($(frm)[0]);

    console.log(type_st)

    form_data.append('id', data_id);
    form_data.append('type_st', type_st);

    $.ajax({
        url: add_comment_reply_url,
        type: 'POST',
        cache: false,
        processData: false,
        contentType: false,
        data: form_data,
        beforeSend: function (xhr, settings) {
            var csrftoken = getCookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }

            $(frm).find('button[type="submit"]').css('cursor', 'no-drop');
            $(frm).find('button[type="submit"]').html(spinner);

            st_comment_clear_input($(frm).find('.st_comment_reply_input').val(""));
            st_close_comment_img_preview($('.st_comment_reply_img_close_div[data-id=' + data_id + ']'), $('.st_comment_reply_input[data-id=' + data_id + ']'));

        },
        success: function (response) {
            $('.st_comment_replies[data-id=' + data_id + ']').prepend(response.comment);
            $('.st_comment_nb_replies[data-id=' + data_id + ']').text(response.nb_replies);
        },
        error: function () {

        },
        complete: function () {
            $(frm).find('button[type="submit"]').html('Publier');
            $(frm).find('button[type="submit"]').css('cursor', 'pointer');
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}

function url_in_text(text) {
    // Kill whitespace.

    protocolExp = /^http(s?):\/\/(\w+:{0,1}\w*)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/i;
    urlExp = /(((?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})/gi;
    secure = window.location.protocol === 'https:' ? true : false;

    text = $.trim(text);

    //ignore the status it's blank.
    if (text === '') {
        return null;
    }

    // Simple regex to make sure the url with a protocol is valid.
    var matches = text.match(protocolExp);


    // see if we have a url
    var url = matches ? matches[0] : null;

    //No urls is the status. Try for urls without scheme i.e. example.com
    if (url === null) {
        matches = text.match(urlExp);

        // S'il y a un url dans le lien on prends le dernier url
        // Premier url = matches[0]
        url = matches ? 'http://' + matches[matches.length - 1] : null;
    }

    url = $.trim(url);


    if (url === "") {
        return null;
    }
    //Note that in both cases we only grab the first URL.
    return url;
}

let link_preview_displayed = false; // Si un lien est deja affiché on n'affiche pas un autre
let link_preview_enabled = true; // Si on upload une image ou video on le desactive

function remove_link_preview_displayed() {
    link_preview_displayed = false;
    let st_link_preview_details = $('#st_link_preview_details');
    st_link_preview_details.hide();
    st_link_preview_details.attr("data-displayed", false);

    $('#st_input_link_title').prop("disabled", true);
    $('#st_input_link_description').prop("disabled", true);
    $('#st_input_link_icon').prop("disabled", true);
    $('#st_input_link_link').prop("disabled", true);
}


function display_link_preview(event, area, check_link_url = "") {


    if (check_link_url !== "" && area !== undefined) {

        if (event.keyCode === 32 || event.keyCode === 8) {

            url = url_in_text(area.value);
            let valid_url = !(url === null);
            let link_preview_enabled = $('#st_link_preview_details').attr("data-enabled");

            if (valid_url && link_preview_displayed === false && link_preview_enabled) {
                $.ajax({
                    url: check_link_url,
                    dataType: "json",
                    data: {url: url},
                    beforeSend: function () {
                        $("#st_link_preview_loading").fadeIn();
                    },
                    success: function (response) {
                        if (!response.error) {
                            let title = response.title;
                            let description = response.description;
                            let icon = response.icon === null ? "/static/SocialMedia/img/icon_web_orange.png" : response.icon;
                            let link = response.url;

                            let st_link_preview_details = $('#st_link_preview_details');

                            st_link_preview_details.find("#st_link_preview_image").attr("src", icon);
                            st_link_preview_details.find("#st_preview_link_title").text(title);
                            st_link_preview_details.find("#st_preview_link_description").text(description);

                            $("#st_link_preview_loading").fadeOut();
                            st_link_preview_details.fadeIn();

                            link_preview_displayed = true;

                            st_link_preview_details.attr("data-displayed", true);

                            $('#st_input_link_title').val(title);
                            $('#st_input_link_description').val(description);
                            $('#st_input_link_icon').val(icon);
                            $('#st_input_link_link').val(link);

                            $('#st_input_link_title').prop("disabled", false);
                            $('#st_input_link_description').prop("disabled", false);
                            $('#st_input_link_icon').prop("disabled", false);
                            $('#st_input_link_link').prop("disabled", false);

                        } else {
                            $("#st_link_preview_loading").hide();
                            $("#st_link_preview_error").fadeIn(200);

                            setTimeout(function () {
                                $("#st_link_preview_error").fadeOut();
                            }, 5000);
                        }
                    },
                    complete: function () {
                    }
                });
            }
        }

    }
}

//Read Uploaded images and preview them

// Multiple images preview in browser
function imagesPreview(input, placeToInsertImagePreview) {


    if (input.files) {
        placeToInsertImagePreview.text('');

        placeToInsertImagePreview.parent().hide();
        placeToInsertImagePreview.parent().attr("data-enabled", 'false');

        var filesAmount = input.files.length;

        for (i = 0; i < filesAmount; i++) {
            var reader = new FileReader();

            reader.onload = function (event) {
                $($.parseHTML('<img>')).attr('src', event.target.result).addClass('st_publier_image').appendTo(placeToInsertImagePreview);

            };
            reader.readAsDataURL(input.files[i]);

            placeToInsertImagePreview.parent().show();
            disable_st_upload_icons();
            placeToInsertImagePreview.parent().attr("data-enabled", 'true');
        }
    }

};

function imagePreview(input, placeToInsertImagePreview) {

    if (input.files) {
        placeToInsertImagePreview.text('');

        placeToInsertImagePreview.parent().hide();
        placeToInsertImagePreview.parent().attr("data-enabled", 'false');

        let reader = new FileReader();

        reader.onload = function (event) {
            $($.parseHTML('<img>')).attr('src', event.target.result).addClass('st_comment_img_preview').appendTo(placeToInsertImagePreview);

        };

        reader.readAsDataURL(input.files[0]);

        placeToInsertImagePreview.parent().show();
    }

};

function filesPreview(input, placeToInsertImagePreview) {

    placeToInsertImagePreview.text('');

    if (input.files) {
        var filesAmount = input.files.length;

        for (i = 0; i < filesAmount; i++) {
            var reader = new FileReader();

            placeToInsertImagePreview.append('<p><i class="st_publier_fichier_icon fa fa-paperclip"></i> <span class="st_publier_fichier">' + input.files[i].name + '</span></p>');
            reader.readAsDataURL(input.files[i]);
        }
        placeToInsertImagePreview.parent().show();
        disable_st_upload_icons();
        placeToInsertImagePreview.parent().attr("data-enabled", 'true');

    }

};

function videoPreview(input, placeToInsertVideoPreview) {

    placeToInsertVideoPreview.text('');

    var fileUrl = window.URL.createObjectURL(input.files[0]);

    let video_html = '<div style="display:none;" id="st_video_{{ statut.id }}">\n' +
        '                      <video class="lg-video-object lg-html5" controls preload="none">\n' +
        '                          <source src="{% static \'SocialMedia/media/vid.mp4\' %}" type="video/mp4">\n' +
        '                               Votre navigateur ne support pas l\'affichage vidéos.\n' +
        '                       </video>\n' +
        '                  </div>\n' +
        '                   <ul id="st_initialise_video_{{ statut.id }}">\n' +
        '                        <li class="st_video" data-poster="{% static \'SocialMedia/img/office_orange_1920p.jpg\' %}" data-sub-html="Video Captions à modifier" data-html="#st_video_{{ statut.id }}">\n' +
        '                                 <img src="{% static \'SocialMedia/img/office_orange_1920p.jpg\' %}"/>\n' +
        '                                  <img class="st_video_play_img"src="{% static \'SocialMedia/img/video-play.png\' %}" alt="">\n' +
        '                          </li>\n' +
        '                   </ul>'

    let vid = '<video width="100%" controls>\n' +
        '  <source src="' + fileUrl + '" id="video_here">\n' +
        '    Your browser does not support HTML5 video.\n' +
        '</video>'

    placeToInsertVideoPreview.append(vid);
    disable_st_upload_icons();

    placeToInsertVideoPreview.parent().show();
    placeToInsertVideoPreview.parent().attr("data-enabled", 'true');
}

function st_publier_fichiers_close(div, input) {

    $('.st_uploading_file_container').text("");
    $(div).parent().hide();
    $(div).parent().attr("data-enabled", 'false');
    enable_st_upload_icons();

    input.val("");

}

function st_close_comment_img_preview(div, input) {

    $(div).parent().hide();
    input.val("");

}


function disable_st_upload_icons() {
    $('#st_upload_image_icon').addClass("st_upload_icon_disabled");
    $('#st_upload_video_icon').addClass("st_upload_icon_disabled");
    $('#st_upload_file_icon').addClass("st_upload_icon_disabled");
    //inputs
    $('#st_input_upload_video').prop("disabled", true);
    $('#st_input_upload_files').prop("disabled", true);
    $('#st_input_upload_images').prop("disabled", true);


}

function enable_st_upload_icons() {
    $('#st_upload_image_icon').removeClass("st_upload_icon_disabled");
    $('#st_upload_video_icon').removeClass("st_upload_icon_disabled");
    $('#st_upload_file_icon').removeClass("st_upload_icon_disabled");

    $('#st_input_upload_video').prop("disabled", false);
    $('#st_input_upload_files').prop("disabled", false);
    $('#st_input_upload_images').prop("disabled", false);


    $("#st_publier_video").text("");
    $("#st_publier_images").text("");
    $("#st_publier_fichiers").text("");


}


//params : url_like
function st_like(element) {
    type_statut = $(element).attr("data-type");
    id = $(element).attr("data-id");
    liked = $(element).attr("data-liked");
    type_action = liked === "false" ? "like" : "unlike";

    let data = {'type': type_statut, 'id': id, 'type_action': type_action};

    if (liked === "false") {
        // Like
        $.ajax({
            url: url_like,
            type: 'GET',
            data: data,
            success: function (response) {
                if (type_statut === "shared") {
                    $('.st_shared_nb_likes[data-id="' + id + '"]').text(response.nb_likes);

                }
                else {
                    $('.st_nb_likes[data-id="' + id + '"]').text(response.nb_likes);
                }
                $(element).attr("data-liked", true);
                $(element).addClass("st_social_button_active");
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });

    }
    else {
        //Unlike
        $.ajax({
            url: url_like,
            type: 'GET',
            data: data,
            success: function (response) {
                if (type_statut === "shared") {
                    $('.st_shared_nb_likes[data-id="' + id + '"]').text(response.nb_likes);

                }
                else {
                    $('.st_nb_likes[data-id="' + id + '"]').text(response.nb_likes);
                }
                $(element).attr("data-liked", false);
                $
                (element).removeClass("st_social_button_active")
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });
    }

}

function like_comment(element) {

    id = $(element).attr("data-id");
    liked = $(element).attr("data-liked");
    type_action = liked === "false" ? "like" : "unlike";

    let data = {'id': id, 'type_action': type_action};

    if (liked === "false") {
        // Like
        $.ajax({
            url: url_like_comment,
            type: 'GET',
            data: data,
            success: function (response) {
                $('.st_comment_nb_likes[data-id="' + id + '"]').text(response.nb_likes)
                $(element).attr("data-liked", true);
                $(element).addClass("st_social_button_active");
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });

    }
    else {
        //Unlike
        $.ajax({
            url: url_like_comment,
            type: 'GET',
            data: data,
            success: function (response) {
                $('.st_comment_nb_likes[data-id="' + id + '"]').text(response.nb_likes);
                $(element).attr("data-liked", false);
                $(element).removeClass("st_social_button_active")
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });
    }

}


function like_comment_reply(element) {

    id = $(element).attr("data-id");
    liked = $(element).attr("data-liked");
    type_action = liked === "false" ? "like" : "unlike";

    let data = {'id': id, 'type_action': type_action};

    if (liked === "false") {
        // Like
        $.ajax({
            url: url_like_comment,
            type: 'GET',
            data: data,
            success: function (response) {
                $('.st_comment_reply_nb_likes[data-id="' + id + '"]').text(response.nb_likes)
                $(element).attr("data-liked", true);
                $(element).addClass("st_social_button_active");
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });

    }
    else {
        //Unlike
        $.ajax({
            url: url_like_comment,
            type: 'GET',
            data: data,
            success: function (response) {
                $('.st_comment_reply_nb_likes[data-id="' + id + '"]').text(response.nb_likes);
                $(element).attr("data-liked", false);
                $(element).removeClass("st_social_button_active")
            },
            error: function () {
                swal("Une erreur est survenue...", "Error", "error");
            },
            stop: function (e) {
                swal("Un problème de connexion est survenu...", "Fatal error", "error");
            }
        });
    }

}

function st_comment_focus(element) {
    id = $(element).attr("data-id");

    $('.st_comment_input[data-id="' + id + '"]').focus();
}


function st_comment_clear_input(input) {
    input.val("");
}


function st_comment_reply_focus(element) {
    id = $(element).attr("data-id");

    $('.st_comment_reply_input[data-id="' + id + '"]').focus();
}


function st_get_likers(element) {
    $('#likers_modal_body').text("");
    let data_id = $(element).attr("data-id");
    let st_type = $(element).attr("data-type");
    let data = {"data_id": data_id, 'st_type': st_type};


    $.ajax({
        url: st_get_likers_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {
            $('#likers_modal_body').html(spinner);
            //$('#likers_modal').show();
        },
        success: function (response) {
            $('#likers_modal_nb_likes').text(response.nb_likes)
            $('#likers_modal_body').html(response.modal_body)
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}


function comment_get_likers(element) {
    $('#likers_modal_body').text("");
    let data_id = $(element).attr("data-id");
    let data = {"data_id": data_id};


    $.ajax({
        url: comment_get_likers_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {
            $('#likers_modal_body').html(spinner);
            //$('#likers_modal').show();
        },
        success: function (response) {
            $('#likers_modal_nb_likes').text(response.nb_likes)
            $('#likers_modal_body').html(response.modal_body)
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}


function st_get_more_comments(element) {

    let data_id = $(element).attr("data-id");
    let data_page = $(element).attr("data-page");
    let data_max = $(element).attr("data-max");
    let data_type = $(element).attr("data-type");

    if (data_page == 0) {
        return;
    }

    let data = {"data_id": data_id, 'data_page': data_page, 'data_max': data_max, 'data_type': data_type};


    $.ajax({
        url: st_get_more_comments_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {
            //$('#likers_modal').show();
        },
        success: function (response) {

            $('.st_comments[data-id=' + data_id + ']').append(response.comments);

            $('.clgp').each(function () {
                data_id = ($(this).attr('data-id'));
                if (loaded.indexOf(data_id) === -1) {
                    lightGallery(this, {
                        thumbnail: true
                    });
                    loaded.push(data_id);
                }
            });

            let st_comments_span = $('.st_comments_count_more[data-id=' + data_id + ']');
            let st_comments_more = $('.st_comments_load_more[data-id=' + data_id + ']');


            if (response.next_page == 0) {

                st_comments_span.attr("data-page", "0");
                st_comments_span.attr("onclick", "");

                st_comments_more.attr("data-page", "0");
                st_comments_more.attr("onclick", "");

                st_comments_more.hide();

            }
            else {
                st_comments_more.show();

                st_comments_more.attr("data-page", response.next_page);
                st_comments_span.attr("data-page", response.next_page);

            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}

function st_copy_link(element) {
    /* Get the text field */
    let url = $(element).attr("data-link");


    var $temp = $("<input>");

    $("body").append($temp);
    value = url;
    $temp.val(value).select();

    /* Select the text field */
    $temp.select();

    /* Copy the text inside the text field */
    document.execCommand("copy");

    const toast = swal.mixin({
        toast: true,
        position: 'bottom-right',
        showConfirmButton: false,
        timer: 3000
    });

    toast({
        type: 'success',
        title: 'Le lien du statut a été copié avec succès.'
    })

}

function st_update_content_call_modal(element) {
    data_id = $(element).attr("data-id");
    data_type = $(element).attr("data-type");
    content = $('.st_contenu[data-id=' + data_id + ']').text().trim();
    $('#st_update_content_input').text(content);
    $('#st_update_content_input').attr("data-id", data_id);
    $('#st_update_content_input').attr("data-type", data_type);
}

function st_update_content() {
    let data_id = $('#st_update_content_input').attr("data-id");
    let data_type = $('#st_update_content_input').attr("data-type");
    let data_content = $('#st_update_content_input').val();

    let data = {'data_id': data_id, 'data_content': data_content, 'data_type': data_type};


    $.ajax({
        url: st_update_content_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {
            //$('#likers_modal').show();
        },
        success: function (response) {

            if (response.success === "success") {

                $('#st_update_content_modal').modal("hide");
                $('.st_contenu[data-id=' + data_id + ']').text(data_content);

                const toast = swal.mixin({
                    toast: true,
                    position: 'bottom-right',
                    showConfirmButton: false,
                    timer: 3000
                });

                toast({
                    type: 'success',
                    title: 'Le statut a été modifié avec succès.'
                })
            }
            else {
                swal("Une erreur est survenu...", "Error", "error");
            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });
}

function st_signal_call_modal(element) {
    data_id = $(element).attr("data-id");
    data_type = $(element).attr("data-type");
    $('#st_signal_content_input').attr("data-id", data_id);
    $('#st_signal_content_input').attr("data-type", data_type);
}

function st_signal() {
    let data_type = $('#st_signal_content_input').attr("data-type");
    let data_id = $('#st_signal_content_input').attr("data-id");
    let data_content = $('#st_signal_content_input').val();

    let data = {'data_id': data_id, 'data_content': data_content, 'data_type': data_type};


    $.ajax({
        url: st_signal_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {
            //$('#likers_modal').show();
        },
        success: function (response) {

            if (response.success === "success") {
                $('#st_signal_modal').modal("hide");
                $('.st[data-id=' + data_id + ']').text("");
                initialize_infinite_scrol();

                const toast = swal.mixin({
                    toast: true,
                    position: 'bottom-right',
                    showConfirmButton: false,
                    timer: 3000
                });

                toast({
                    type: 'success',
                    title: 'Le statut a été signalé avec succès.'
                })

            }
            else {
                swal("Une erreur est survenu...", "Error", "error");
            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });
}


function st_delete(element) {

    let data_id = $(element).attr("data-id");
    let data_type = $(element).attr("data-type");
    let data = {'data_id': data_id, 'data_type': data_type};


    swal({
        title: 'Supprimer le statut',
        text: "Êtes-vous sûr(e) de vouloir supprimer définitivement ce statut?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Supprimer',
        cancelButtonText: 'Annuler',
        reverseButtons: true,
    }).then((result) => {
        if (result.value === true) {
            $.ajax({
                url: st_delete_url,
                type: 'GET',
                data: data,
                success: function (response) {
                    if (response.success == "success") {
                        $('.st[data-id=' + data_id + ']').remove();
                        swal(
                            'Operation effectuée',
                            'Le statut a été supprimé avec succès',
                            'success'
                        )
                        initialize_infinite_scrol();
                    }
                },
                error: function () {
                },
                complete: function () {
                },
                stop: function (e) {
                    swal("Un problème de connexion est survenu. Veuillez réessayer plus tard.", "Erreur Fatale", "error");
                }
            });
        } else {
            //$("#dropdown-"+statutID).fadeOut();
        }
    });
}

/* comments */

function comment_update_content_call_modal(element) {
    data_id = $(element).attr("data-id");
    data_type = $(element).attr("data-type");
    if (data_type === "comment") {
        content = $('.st_comment_content[data-id=' + data_id + ']').text().trim();
    }
    else if (data_type === "reply") {
        content = $('.st_comment_reply_content[data-id=' + data_id + ']').text().trim();
    }
    else {
        return;
    }

    $('#comment_update_content_input').text(content);
    $('#comment_update_content_input').attr("data-id", data_id);
    $('#comment_update_content_input').attr("data-type", data_type);
}

function comment_update_content() {
    let data_id = $('#comment_update_content_input').attr("data-id");
    let data_content = $('#comment_update_content_input').val();
    let data_type = $('#comment_update_content_input').attr("data-type");

    if (data_type === "comment") {
        content = $('.st_comment_content[data-id=' + data_id + '][data-type=' + data_type + ']').text().trim();
    }
    else if (data_type === "reply") {
        content = $('.st_comment_reply_content[data-id=' + data_id + '][data-type=\'+data_type+\']').text().trim();
    }
    else {
        return;
    }

    if (data_type !== "comment" && data_type !== "reply") {
        return;
    }

    let data = {'data_id': data_id, 'data_content': data_content, 'data_type': data_type};

    console.log(data)

    $.ajax({
        url: comment_update_content_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {

        },
        success: function (response) {

            if (response.success === "success") {

                $('#comment_update_content_modal').modal("hide");

                if (data_type === "comment") {
                    $('.st_comment_content[data-id=' + data_id + '][data-type=' + data_type + ']').text(data_content);
                }
                else if (data_type === "reply") {
                    $('.st_comment_reply_content[data-id=' + data_id + '][data-type=' + data_type + ']').text(data_content);
                }

                const toast = swal.mixin({
                    toast: true,
                    position: 'bottom-right',
                    showConfirmButton: false,
                    timer: 3000
                });

                toast({
                    type: 'success',
                    title: 'Le commentaire a été modifié avec succès.'
                })
            }
            else {
                swal("Une erreur est survenu...", "Error", "error");
            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });
}

function comment_signal_call_modal(element) {
    data_id = $(element).attr("data-id");
    data_type = $(element).attr("data-type");
    $('#comment_signal_content_input').attr("data-id", data_id);
    $('#comment_signal_content_input').attr("data-type", data_type);
}

function comment_signal() {
    let data_type = $('#comment_signal_content_input').attr("data-type");
    let data_id = $('#comment_signal_content_input').attr("data-id");
    let data_content = $('#comment_signal_content_input').val();

    let data = {'data_id': data_id, 'data_content': data_content, 'data_type': data_type};

    if (data_type !== "comment" && data_type !== "reply")
        return;

    $.ajax({
        url: comment_signal_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {

        },
        success: function (response) {

            if (response.success === "success") {
                $('#comment_signal_modal').modal("hide");

                if (data_type === "comment") {
                    $('.st_comment[data-id=' + data_id + ']').remove();
                }
                else if (data_type === "reply") {
                    $('.st_comment_reply[data-id=' + data_id + ']').remove();
                }

                initialize_infinite_scrol();

                const toast = swal.mixin({
                    toast: true,
                    position: 'bottom-right',
                    showConfirmButton: false,
                    timer: 3000
                });

                toast({
                    type: 'success',
                    title: 'Le commentaire a été signalé avec succès.'
                })

            }
            else {
                swal("Une erreur est survenu...", "Error", "error");
            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });
}


function comment_delete(element) {

    let data_id = $(element).attr("data-id");
    let data_type = $(element).attr("data-type");

    if (data_type !== "comment" && data_type !== "reply") {
        return;
    }

    let data = {'data_id': data_id,};

    swal({
        title: 'Supprimer le commentaire',
        text: "Êtes-vous sûr(e) de vouloir supprimer définitivement ce commentaire?",
        type: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Supprimer',
        cancelButtonText: 'Annuler',
        reverseButtons: true,
    }).then((result) => {
        if (result.value === true) {
            $.ajax({
                url: comment_delete_url,
                type: 'GET',
                data: data,
                success: function (response) {
                    if (response.success == "success") {
                        if (data_type === "comment") {
                            $('.st_comment[data-id=' + data_id + ']').remove();
                        }
                        else if (data_type === "reply") {
                            $('.st_comment_reply[data-id=' + data_id + ']').remove();
                        }

                        swal(
                            'Operation effectuée',
                            'Le commentaire a été supprimé avec succès',
                            'success'
                        )
                        initialize_infinite_scrol();
                    }
                },
                error: function () {
                },
                complete: function () {
                },
                stop: function (e) {
                    swal("Un problème de connexion est survenu. Veuillez réessayer plus tard.", "Erreur Fatale", "error");
                }
            });
        } else {
            //$("#dropdown-"+statutID).fadeOut();
        }
    });
}

let st_scroll_f_time = true;

function initialize_infinite_scrol() {


    var infinite = new Waypoint.Infinite({
        element: $('.infinite-container')[0],
        onBeforePageLoad: function () {
            $('#loadingImageMoreComments').fadeIn(250);
        },
        onAfterPageLoad: function ($items) {
            $('#loadingImageMoreComments').fadeOut(250);
            $('.lgp, .slgp').each(function () {
                data_id = ($(this).attr('data-id'));
                if (loaded.indexOf(data_id) === -1) {
                    lightGallery(this, {
                        thumbnail: true
                    });
                    loaded.push(data_id);
                }
            })
        }
    });

    if (st_scroll_f_time) {
        $('.lgp, .slgp').each(function () {
            data_id = ($(this).attr('data-id'));
            if (loaded.indexOf(data_id) === -1) {
                lightGallery(this, {
                    thumbnail: true
                });
                loaded.push(data_id);
            }
        })
    };
}


function st_share_modal(element) {
    let id = $(element).attr("data-id");
    let st = $('.st_content_infos[data-id=' + id + ']').html();
    $('#st_share_button').attr("data-id", id);
    $('#modal_share_statut_preview').html(st);
    $('#modal_share_statut_preview').find('.st_menu[data-id=' + id + ']').remove();
}


function st_share(element) {
    let id = $(element).attr("data-id");
    let content = $('#share_statut_content_input').val();

    if (id === undefined)
        return;

    data = {'id': id, 'content': content}

    $.ajax({
        url: st_share_url,
        type: 'GET',
        data: data,

        beforeSend: function (xhr, settings) {

        },
        success: function (response) {

            if (response.success === "success") {
                $('#share_statut_modal').modal("hide");


                const toast = swal.mixin({
                    toast: true,
                    position: 'bottom-right',
                    showConfirmButton: false,
                    timer: 3000
                });

                toast({
                    type: 'success',
                    title: 'Le statut a été partagé avec succès.'
                })

            }
            else {
                swal("Une erreur est survenu...", "Error", "error");
            }
        },
        error: function () {
            swal("Une erreur est survenu...", "Error", "error");
        },
        complete: function () {
        },
        stop: function (e) {
            swal("Un problème de connexion est survenu...", "Fatal error", "error");
        }
    });

}


function displayStatut(bt) {
    $(bt).fadeOut(0);
    $('#statut').fadeIn(0);
    $('#statut').focus();
}


function hideStatut(txtbox) {
    if ($(txtbox).val().length === 0) {
        $(txtbox).fadeOut(0);
        $(".btstatutHIDESHOW").fadeIn();
    }
}


function open_menu(div) {

    if (!$(div).hasClass("open")) {
        $(div).siblings("[role='menu']").first().fadeIn(100);
        $(div).addClass("open");
    }
    else {
        $(div).siblings("[role='menu']").first().fadeOut(100);
        $(div).removeClass("open");
    }

}


function st_show_comment_publish_button(input, submit_button_id) {
    var submit_button = $("#" + submit_button_id);

    console.log(submit_button.innerHTML)

    if ($(input).val() === "") {
        submit_button.fadeOut();
    }
    else {
        submit_button.fadeIn();
    }
}


$('#statut').on('keyup', function () {
    display_link_preview(event, this, check_link_url = st_check_link_url);
});

$('#st_input_upload_images').on('change', function () {
    imagesPreview(this, $('#st_publier_images'));
});

$('#st_input_upload_video').on('change', function () {
    videoPreview(this, $('#st_publier_video'))
});

$('#st_input_upload_files').on('change', function () {
    filesPreview(this, $('#st_publier_fichiers'));
});