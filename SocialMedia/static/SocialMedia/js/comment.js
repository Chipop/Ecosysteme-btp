function getMoreComments (bt)
    {
        statutid = bt.getAttribute('statutid');
        nextp = bt.getAttribute('page');
        commentsURL = "{% url 'SocialMedia:getMoreCommentsAcceuil' %}";
        $.ajax({
                    url: commentsURL,
                    type: 'GET',
                    data: {'page':nextp, 'statutid':statutid},
                    beforeSend: function (xhr, settings) {
                      $("#loadingImage").show();
                    },
                    success: function (data) {
                            $("#first_load_more_div" + statutid + ", #load_more_div" + statutid).remove();
                            $(".comments" + statutid).append(data);
                            console.log(data);
                    },
                    error: function () {
                    },
                    complete:function(){
                      $("#loadingImage").fadeOut(250);
                    },
                    stop: function (e) {
                        swal("Veuiller Verifier Votre Connexion Reseau Puis Ressayer", "Erreur Fatale", "error");
                    }
                });
    }