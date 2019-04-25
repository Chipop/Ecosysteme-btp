(function($) {
    "use strict"; // Start of use strict
    // Configure tooltips for collapsed side navigation
    $('.navbar-sidenav [data-toggle="tooltip"]').tooltip({
        template: '<div class="tooltip navbar-sidenav-tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
    });
    // Toggle the side navigation
    $("#sidenavToggler").click(function(e) {
        e.preventDefault();
        $("body").toggleClass("sidenav-toggled");
        $(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
        $(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
    });
    // Force the toggled class to be removed when a collapsible nav link is clicked
    $(".navbar-sidenav .nav-link-collapse").click(function(e) {
        e.preventDefault();
        $("body").removeClass("sidenav-toggled");
    });
  // Prevent the content wrapper from scrolling when the fixed side navigation hovered over
    $('body.fixed-nav .navbar-sidenav, body.fixed-nav .sidenav-toggler, body.fixed-nav .navbar-collapse').on('mousewheel DOMMouseScroll', function(e) {
        var e0 = e.originalEvent,
          delta = e0.wheelDelta || -e0.detail;
        this.scrollTop += (delta < 0 ? 1 : -1) * 30;
        e.preventDefault();
    });
  // Scroll to top button appear
    $(document).scroll(function() {
        var scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    // Configure tooltips globally
    $('[data-toggle="tooltip"]').tooltip()
    // Smooth scrolling using jQuery easing
    $(document).on('click', 'a.scroll-to-top', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
          scrollTop: ($($anchor.attr('href')).offset().top)
        }, 1000, 'easeInOutExpo');
        event.preventDefault();
    });
  
    // Inline popups
    $('.inline-popups').each(function () {
        $(this).magnificPopup({
            delegate: 'a',
            removalDelay: 500, //delay removal by X to allow out-animation
            callbacks: {
                beforeOpen: function () {
                    this.st.mainClass = this.st.el.attr('data-effect');
                }
            },
            midClick: true // allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source.
        });
    });

    // Bookmarks
    $('.wishlist_close').on('click', function (c) {
        $(this).parent().parent().parent().fadeOut('slow', function (c) {});
    });
	
    // Selectbox
    $(".selectbox").selectbox();
  
    // Pricing add
    function newMenuItem() {
		var newElem = $('tr.pricing-list-item').first().clone();
		newElem.find('input').val('');
		newElem.appendTo('table#pricing-list-container');
	}
	if ($("table#pricing-list-container").is('*')) {
        $('.add-pricing-list-item').on('click', function (e) {
            e.preventDefault();
            newMenuItem();
        });
        $(document).on("click", "#pricing-list-container .delete", function (e) {
            e.preventDefault();
            $(this).parent().parent().parent().remove();
        });
    }

    function newPrerequisite() {
		var newElem = $('tr.list-prerequisite-item').first().clone();
		newElem.find('input').val('');
		newElem.appendTo('table#list-prerequisite-container');
	}
	if ($("table#list-prerequisite-container").is('*')) {
        $('.add-list-prerequisite-item').on('click', function (e) {
            e.preventDefault();
            newPrerequisite();
        });
        $(document).on("click", "#list-prerequisite-container .delete", function (e) {
            e.preventDefault();
            $(this).parent().parent().parent().remove();
        });
        $(document).on("click", "#list-prerequisite-container .delete_existing", function (e) {
            e.preventDefault();
            var id = $(this).data('pk');
            var btn = $(this);
            var form = $('#formDeletePrerequisite'+id);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === "") {
                        btn.parent().parent().parent().remove();
                    }
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        });
	}

    $(document).on("click", ".mark_as_read", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var form = $('#formMarkAsRead' + id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    var my_div = $("#read_or_not" + id);
                    var my_link = $("#mark_as_read_link" + id);
                    var my_input = $("#mark_as_read_hidden" + id);
                    // unread = non lu
                    if(data.is_read === "unread") {
                        my_div.removeClass("unread");
                        my_div.addClass("read");
                        my_div.html("Lu");
                        my_link.html("Marquer comme non lu");
                        my_input.val("read");
                    }
                    else{
                        my_div.removeClass("read");
                        my_div.addClass("unread");
                        my_div.html("Non lu");
                        my_link.html("Marquer comme lu");
                        my_input.val("unread");
                    }
                    var span_base = $("#number_messages_base");
                    var num;
                    if(data.is_read === "unread")
                        num = parseInt(span_base.html()) - 1;
                    else
                        num = parseInt(span_base.html()) + 1;
                    span_base.html(num+"");
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });

    $(document).on("click", ".delete_part", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var btn = $(this);
        var form = $('#formDeletePart'+id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    btn.parent().parent().remove();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $(document).on("click", ".delete_quiz", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var btn = $(this);
        var form = $('#formDeleteQuiz'+id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    $("#div_quiz"+id).remove();
                    $("#add_question_button"+id).remove();
                    form.remove();
                    btn.parent().append('<a href="javascript:" style="position: absolute; top: 0; left: 123px; border: 1px solid;" class="btn_1 gray" data-toggle="modal" data-target="#modalQuiz" data-pk="' + btn.data("pk_part") + '" data-name="' + btn.data("name") + '"><i class="fa fa-fw fa-plus-circle"></i>Ajouter Quiz</a>');
                    btn.remove();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $(document).on("click", ".delete_question", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var btn = $(this);
        var form = $('#formDeleteQuestion'+id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    $("#div_question"+id).remove();
                    form.remove();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $(document).on("click", ".delete_choice", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var btn = $(this);
        var form = $('#formDeleteChoice'+id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    btn.parent().parent().parent().parent().parent().remove();
                    form.remove();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $(document).on("click", ".delete_chapter", function (e) {
        e.preventDefault();
        var id = $(this).data('pk');
        var btn = $(this);
        var form = $('#formDeleteChapter'+id);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    btn.parent().parent().parent().parent().parent().remove();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });

    $(document).on("click", ".clear_file", function (e) {
        $('#video_file').val('');
    });
    $(document).on("click", ".clear_modal_chapter", function (e) {
        $('#addChapter .form-control').val('');
    });
    $(document).on("click", ".clear_modal_part", function (e) {
        $('#addPart .form-control').val('');
    });
    $(document).on("click", ".clear_modal_quiz", function (e) {
        $('#addQuiz .form-control').val('');
        CKEDITOR.instances['id_description'].setData('');
    });
    $(document).on("click", ".clear_modal_question", function (e) {
        $('#addQuestion .form-control').val('');
        $('#is_multiple').prop("checked", false);
        CKEDITOR.instances['id_text'].setData('');
        CKEDITOR.instances['id_explanation'].setData('');
    });
    $(document).on("click", ".clear_modal_choice", function (e) {
        $('#addChoice .form-control').val('');
        $('#is_correct').prop("checked", false);
    });
    $(document).on("click", ".update_price", function (e) {
        var form = $('#formUpdatePrice');
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    swal({title: "Succès!", text: "Le prix a été modifié !", icon: "success"});
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $('#addChapter').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        var video_file = $('#video_file');
        var video_url = $('#video_url');
        if (video_file.val() === "" && video_url.val() === "")
            swal({title: "Erreur!", text: "Vous devez insérer l'url de la vidéo ou l'importer.", icon: "error"});
        else {
            if (video_file.val() !== "" && video_url.val() !== "")
                swal({title: "Erreur!", text: "Vous devez insérer l'url de la vidéo ou l'importer.", icon: "error"});
            else {
                var form_data = new FormData($(form)[0]);
                $.ajax({
                    url: form.attr("data-validate-url"),
                    data: form_data,
                    method: 'POST',
                    cache: false,
                    processData: false,
                    contentType: false,
                    beforeSend: function (xhr, settings) {
                        var csrftoken = getCookie('csrftoken');
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", csrftoken);
                        }
                        $("#progress_div").show();
                    },
                    xhr: function() {
                        var xhr = new window.XMLHttpRequest();
                        //Upload progress
                        xhr.upload.addEventListener("progress", function(evt){
                            if (evt.lengthComputable) {
                                var percentComplete = (evt.loaded / evt.total) * 100;
                                var progress_bar = $("#progress_bar");
                                progress_bar.html(parseFloat(percentComplete).toFixed(2) + " %");
                                progress_bar.css("width", percentComplete+"%");
                            }
                        }, false);
                        return xhr;
                    },
                    success: function (data) {
                        if (data.message_error === "") {
                            var row = '<tr class="video-list-item"><td>' +
                                '<form id="formDeleteChapter' + data.chapter_id + '" action="' + data.url + '" data-validate-url="' + data.url + '"><input type="hidden" value="' + data.chapter_id + '" name="chapter"><input type="hidden" value="' + data.course_id + '" name="course"></form>' +
                                '<div class="row"><div class="col-md-1"><div class="form-group"><input type="number" class="form-control" disabled="disabled" value="' + data.number + '"></div></div>\n' +
                                '<div class="col-md-4"><div class="form-group"><input type="text" class="form-control" disabled="disabled" value="' + data.name + '"></div></div>\n' +
                                '<div class="col-md-2"><div class="form-group"><input type="text" class="form-control" disabled="disabled" value="'+ data.duration + '"></div></div>\n' +
                                '<div class="col-md-4"><div class="form-group">';
                            if (data.video_url !== "")
                                row += '<a class="form-control" disabled="disabled" target="_blank" href="'+ data.video_url + '">' + data.video_url + '</a>\n';
                            if(data.video_file !== "")
                                row += '<a class="form-control" href="' + data.video_file +'">Télécharger</a>';
                            row += '</div></div><div class="col-md-1"><div class="form-group"><a class="delete_chapter" data-pk="' + data.chapter_id + '" href="javascript:"><i class="fa fa-fw fa-remove"></i></a>\n' +
                                    '</div></div></div></td></tr>';
                            $('#video-list-container'+data.part_id).append(row);
                            var progress_bar = $("#progress_bar");
                            progress_bar.css("width", "0%");
                            progress_bar.parent().hide();
                            $('#addChapter .form-control').val('');
                            $('#number_chapter').val(parseInt(data.number) + 1);
                            $('#modalChapter').modal('toggle');
                        }
                        else
                            swal({title: "Erreur!", text: data.message_error, icon: "error"});
                    }
                });
            }
        }
    });
    $('#addQuiz').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        CKEDITOR.instances['id_description'].updateElement();
        var form_data = new FormData($(form)[0]);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form_data,
            method: 'POST',
            cache: false,
            processData: false,
            contentType: false,
            success: function (data) {
                if (data.message_error === "") {
                    $('#addQuiz .form-control').val('');
                    CKEDITOR.instances['id_description'].setData('');
                    $('#modalQuiz').modal('toggle');
                    var button = $("#add_quiz_button"+data.part_id);
                    var row = '<div class="row" id="div_quiz' + data.quiz_id + '"></div>\n' +
                        '<a href="javascript:" class="btn_1 gray add-list-coupon-item" id="add_question_button' + data.quiz_id + '" data-toggle="modal" data-target="#modalQuestion" data-pk="' + data.quiz_id + '" data-name="' + data.quiz_title + '"><i class="fa fa-fw fa-plus-circle"></i>Ajouter Question</a>' +
                        '<form id="formDeleteQuiz' + data.quiz_id + '" action="' + data.url + '" data-validate-url="' + data.url + '">\n' +
                        '<input type="hidden" value="' + data.quiz_id + '" name="quiz">\n' +
                        '<input type="hidden" value="' + data.part_id + '" name="part">\n' +
                        '<input type="hidden" value="' + data.course_id + '" name="course">\n' +
                        '</form>\n' +
                        '<a href="javascript:" style="position: absolute; top: 0; left: 123px; border: 1px solid;" class="btn_1 danger delete_quiz" data-pk="' + data.quiz_id + '" data-pk_part="' + data.part_id + '" data-name="' + data.part_name + '"><i class="fa fa-fw fa-trash"></i>Supprimer Quiz</a>';
                    button.remove();
                    $("#div_parent_quiz"+data.part_id).append(row);
                    swal({title: "Succès!", text: "Votre quiz a été ajouté!", icon: "success"});
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $('#addQuestion').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        CKEDITOR.instances['id_text'].updateElement();
        CKEDITOR.instances['id_explanation'].updateElement();
        var text = CKEDITOR.instances['id_text'].getData();
        if(text !== "") {
            var form_data = new FormData($(form)[0]);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form_data,
                method: 'POST',
                cache: false,
                processData: false,
                contentType: false,
                beforeSend: function (xhr, settings) {
                    var csrftoken = getCookie('csrftoken');
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                success: function (data) {
                    if (data.message_error === "") {
                        $('#addQuestion .form-control').val('');
                        $('#is_multiple').prop("checked", false);
                        CKEDITOR.instances['id_text'].setData('');
                        CKEDITOR.instances['id_explanation'].setData('');
                        var row = '<div class="com-md-12" style="width:100%;" id="div_question' + data.question_id + '">\n' +
                            '<form id="formDeleteQuestion' + data.question_id + '" action="' + data.url + '" data-validate-url="' + data.url + '">\n' +
                            '<input type="hidden" value="' + data.question_id + '" name="question"><input type="hidden" value="' + data.course_id + '" name="course"></form>\n' +
                            '<h6>Question ' + data.question_number + ' : <a class="delete_question" data-pk="' + data.question_id + '" href="javascript:"><i style="padding-top: 14px"  class="fa fa-fw fa-remove"></i></a></h6>\n' +
                            text +
                            '<table style="width:100%;" id="table_question' + data.question_id + '"></table>\n' +
                            '<a href="javascript:" id="add_choice_btn' + data.question_id + '" class="btn_1 gray" data-toggle="modal" data-target="#modalChoice" data-pk="' + data.question_id + '" data-name="Question ' + data.question_number + '"><i class="fa fa-fw fa-plus-circle"></i>Ajouter Choix</a></div>';
                        $('#div_quiz'+data.exam_id).append(row);
                        $('#modalQuestion').modal('toggle');
                        $('#add_choice_btn' + data.question_id).click();

                    }
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        }
        else
            swal({title: "Erreur!", text: "Le texte est obligatoire!", icon: "error"});
    });
    $('#addChoice').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        var text = $("#value_choice").val();
        if(text !== "") {
            var form_data = new FormData($(form)[0]);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form_data,
                method: 'POST',
                cache: false,
                processData: false,
                contentType: false,
                success: function (data) {
                    if (data.message_error === "") {
                        var row = '<tr><td><form id="formDeleteChoice' + data.choice_id + '" action="' + data.url + '" data-validate-url="' + data.url + '"><input type="hidden" value="' + data.choice_id + '" name="choice">\n' +
                            '<input type="hidden" value="' + data.course_id + '" name="course"></form><div class="row">\n' +
                            '<div class="col-md-10"><div class="form-group"><input type="text" class="form-control" disabled="disabled" value="' + text + '">\n' +
                            '</div></div><div class="col-md-1"><div class="form-group" style="padding-top: 14px"><input type="checkbox" class="form-control" disabled="disabled"';
                        if(JSON.parse(data.is_correct) === true)
                            row += 'checked>';
                        else
                            row += '>';
                        row += '</div></div><div class="col-md-1"><div class="form-group"><a class="delete_choice" data-pk="' + data.choice_id + '" href="javascript:"><i style="padding-top:14px" class="fa fa-fw fa-remove"></i></a></div></div></div></td></tr>';
                        $("#table_question" + data.question_id).append(row);
                        $('#addChoice .form-control').val('');
                        $('#is_correct').prop("checked", false);
                    }
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        }
        else
            swal({title: "Erreur!", text: "La valeur est obligatoire!", icon: "error"});
    });

    $('.formUpdateUrlPart').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form.serialize(),
            dataType: 'json',
            success: function (data) {
                if(data.message_error === "") {
                    swal({title: "Succès!", text: "Le lien a été associé!", icon: "success"});
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });
    $('.formUpdateFilePart').submit(function(event) {
        var form = $(this);
        event.preventDefault();
        var form_data = new FormData($(form)[0]);
        $.ajax({
            url: form.attr("data-validate-url"),
            data: form_data,
            method: 'POST',
            cache: false,
            processData: false,
            contentType: false,
            beforeSend: function (xhr, settings) {
                var csrftoken = getCookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
                $("#progress_bar_file_part"+form.attr("data-part_id")).parent().show();
            },
            xhr: function() {
                var xhr = new window.XMLHttpRequest();
                //Upload progress
                xhr.upload.addEventListener("progress", function(evt){
                    if (evt.lengthComputable) {
                        var percentComplete = (evt.loaded / evt.total) * 100;
                        var progress_bar = $("#progress_bar_file_part"+form.attr("data-part_id"));
                        progress_bar.html(parseFloat(percentComplete).toFixed(2) + " %");
                        progress_bar.css("width", percentComplete+"%");
                    }
                }, false);
                return xhr;
            },
            success: function (data) {
                if (data.message_error === "") {
                    var row = '<a class="form-control" download href="' + data.url_file + '">Télécharger</a>';
                    $('#divDownloadAttachedFile'+data.part_id).html(row);
                    swal({title: "Succès!", text: "Le fichier a été importé", icon: "success"});
                    var progress_bar = $("#progress_bar_file_part"+form.attr("data-part_id"));
                    progress_bar.css("width", "0%");
                    progress_bar.parent().hide();
                }
                else
                    swal({title: "Erreur!", text: data.message_error, icon: "error"});
            }
        });
    });

    function newPostSkill() {
		var newElem = $('tr.list-postskill-item').first().clone();
		newElem.find('input').val('');
		newElem.appendTo('table#list-postskill-container');
	}
	if ($("table#list-postskill-container").is('*')) {
        $('.add-list-postskill-item').on('click', function (e) {
            e.preventDefault();
            newPostSkill();
        });
        $(document).on("click", "#list-postskill-container .delete", function (e) {
            e.preventDefault();
            $(this).parent().parent().parent().remove();
        });
        $(document).on("click", "#list-postskill-container .delete_existing", function (e) {
            e.preventDefault();
            var id = $(this).data('pk');
            var btn = $(this);
            var form = $('#formDeletePostskill'+id);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === "") {
                        btn.parent().parent().parent().remove();
                    }
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        });
	}

    function newCoupon() {
		var newElem = $('tr.list-coupon-item').first().clone();
		newElem.find('input').val('');
		newElem.appendTo('table#list-coupon-container');
	}
	if ($("table#list-coupon-container").is('*')) {
        $('.add-list-coupon-item').on('click', function (e) {
            e.preventDefault();
            newCoupon();
        });
        $(document).on("click", "#list-coupon-container .delete", function (e) {
            e.preventDefault();
            $(this).parent().parent().parent().remove();
        });
        $(document).on("click", "#list-coupon-container .delete_existing", function (e) {
            e.preventDefault();
            var id = $(this).data('pk');
            var btn = $(this);
            var form = $('#formDeleteCoupon'+id);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === "") {
                        btn.parent().parent().parent().remove();
                    }
                    else
                        swal({title: "Erreur!", text: data.message_error, icon: "error"});
                }
            });
        });
	}
})(jQuery); // End of use strict
