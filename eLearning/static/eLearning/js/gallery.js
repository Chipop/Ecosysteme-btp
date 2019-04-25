$('#modalYoutube').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var link = button.data('link');
    var count_x = parseInt(button.data("count_x"));
    var max = parseInt(button.data("max"));
    var classV = "";
    if(link.includes("youtube")) {
        link = link.split("?v=")[1];
        link = link.split("&")[0];
        link = "https://www.youtube.com/embed/" + link + "?rel=0&autoplay=1&modestbranding=1";
        classV = "dj-youtube";
        $("#modalYoutube .modal-header").css("height", "0px");
    }
    else {
        if (link.includes("vimeo")) {
            link = link.split("imeo.com/")[1];
            link = link.split("?")[0];
            link = "//player.vimeo.com/video/" + link + "?autoplay=1";
            classV = "dj-vimeo";
            $("#modalYoutube .modal-header").css("height", "100px");
        } else {
            $(this).modal('toggle');
        }
    }
    var row = '<iframe id="iframe_video" class="iframe_video" src="' + link + '" frameborder="0" allowfullscreen></iframe>\n';
    if(count_x > 1)
        row += '<button type="button" class="close previous_video" id="previous_video" data-pk="egZ35EG' + (count_x - 1) + 'ihaizaZF21faY73" style="position: absolute; color: #fff; opacity: 1; top: 270px; font-weight: 100; font-size: 40px; cursor: pointer; right: 940px;"><<</button>\n';
    if(count_x < max)
        row += '<button type="button" class="close next_video" id="next_video" data-pk="egZ35EG' + (count_x + 1) + 'ihaizaZF21faY73" style="position: absolute; color: #fff; opacity: 1; top: 270px; font-weight: 100; font-size: 40px; cursor: pointer; right: -80px;">>></button>';
    $("#div_iframe").html(row);
    $("#div_iframe").attr('class', classV);
});
$(".video-modal .close-modal").on("click", function() {
    $("video").each(function () { this.pause() });
    $("#iframe_video").attr("src", "");
    $(this).parent().parent().parent().modal('toggle');
});

$(document).on("click", ".next_video", function (e) {
    $("video").each(function () { this.pause() });
    $("#iframe_video").attr("src", "");
    $(this).parent().parent().parent().parent().modal('toggle');
    var pk = $(this).data('pk');
    var btn = $("#"+pk);
    btn.click();
});
$(document).on("click", ".previous_video", function (e) {
    $("video").each(function () { this.pause() });
    $("#iframe_video").attr("src", "");
    $(this).parent().parent().parent().parent().modal('toggle');
    var pk = $(this).data('pk');
    $("#"+pk).click();
});