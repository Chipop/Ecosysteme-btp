<!-- Initialize the plugin: -->
$(document).ready(function () {
    $('#multiselect-modules').multiselect({
        buttonWidth: '197px',
        dropRight: true,
        nonSelectedText: 'Tout (6)',
        selectAllText: 'Selectionner tout',
        includeSelectAllOption: true,
        allSelectedText: "Tout",
        //enableFiltering: true,
    });
});


$('#icon-filtrer-ga').on('click', function (e) {

    $('.search-filters').slideToggle();
});


(function (w, d, s, g, js, fs) {
    g = w.gapi || (w.gapi = {});
    g.analytics = {
        q: [], ready: function (f) {
            this.q.push(f);
        }
    };
    js = d.createElement(s);
    fs = d.getElementsByTagName(s)[0];
    js.src = 'https://apis.google.com/js/platform.js';
    fs.parentNode.insertBefore(js, fs);
    js.onload = function () {
        g.load('analytics');
    };
}(window, document, 'script'));


gapi.analytics.ready(function () {

    /**
     * Authorize the user with an access token obtained server side.
     */
    gapi.analytics.auth.authorize({
        'serverAuth': {
            'access_token': google_token
        }
    });

    /**
     * Create a new DataChart instance with the given query parameters
     * and Google chart options. It will be rendered inside an element
     * with the id "chart-container".
     */
        /////////// VILLES DES VISITEURS ////////////////
    var dataChart = new gapi.analytics.googleCharts.DataChart({
            query: {
                metrics: 'ga:users',
                dimensions: 'ga:city',
                filters: 'ga:pagePath=@/',
                'start-date': '30daysAgo',
                'end-date': 'today',
            },
            chart: {
                container: 'origine-chart-container',
                type: 'PIE',
                options: {
                    width: '100%'
                }
            }
        });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    //Visites Totales  LINE
    dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:pageviews,ga:uniquePageViews',
            dimensions: 'ga:date',
            'start-date': '30daysAgo',
            'end-date': 'today',
            filters: 'ga:pagePath=@/',
        },
        chart: {
            container: 'visites-totales-chart-container',
            type: 'LINE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ///////////// APPAREILS DES VISITEURS /////////////:
    dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:deviceCategory',
            filters: 'ga:pagePath=@/',
            'start-date': '30daysAgo',
            'end-date': 'today',
        },
        chart: {
            container: 'appareils-chart-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    //////////// TEMPS  PASSEE EN  SECONDE  PAR PAGE  //////////

    dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:avgTimeOnPage',
            dimensions: 'ga:pagePath',
            filters: 'ga:pagePath=@/',
            'max-results': 10,
            'sort': '-ga:avgTimeOnPage',
            'start-date': '30daysAgo',
            'end-date': 'today',
        },
        chart: {
            container: 'pages-plus-temps-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ////////// PAGES PLUS VUES TABLE ////////////

    dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:pageviews,ga:uniquePageviews,ga:avgTimeOnPage',
            dimensions: 'ga:pageTitle,ga:pagePath',
            'start-date': '30daysAgo',
            'end-date': 'today',
            sort: '-ga:pageviews',
            filters: 'ga:pagePath=@/',
            'max-results': 10,
        },
        chart: {
            container: 'pages-plus-visites-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    /////////// TRAFFIC SOURCES ///////////////
    dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:source',
            filters: 'ga:pagePath=@/',
            'max-results': 8,
            'start-date': '30daysAgo',
            'end-date': 'today',
        },
        chart: {
            container: 'traffic-source-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ///////////////// NEW VS RETURNING VISITORS : Comportement des visiteurs ///////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:userType',
            filters: 'ga:pagePath=@/',
            'start-date': '30daysAgo',
            'end-date': 'today',
        },
        chart: {
            container: 'new-returning-visitors-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();

    ///////////////// Top Channels ( Direct, social, organic) ///////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:channelGrouping',
            filters: 'ga:pagePath=@/',
            'start-date': '30daysAgo',
            'end-date': 'today',
            'max-results': 5,
        },
        chart: {
            container: 'visitors-channels-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();

});

start_date = "";
end_date = "";

$(document).ready(function () {

    var start = moment().subtract(30, 'days');
    var end = moment();

    start_date =  start.format('YYYY-MM-DD');
    end_date = end.format('YYYY-MM-DD');

    $('#reportrange_top span').html("du " + start.format('DD/MM/YYYY') + ' au ' + end.format('DD/MM/YYYY'));

    $('#reportrange_top').daterangepicker({
        format: 'DD/MM/YYYY',
        startDate: moment().subtract(31, 'days'),
        endDate: moment(),
        minDate: '01/01/2012',
        maxDate: '31/12/2099',
        dateLimit: {days: 29200},
        showDropdowns: true,
        timePicker: false,
        ranges: {
            "Aujourd'hui": [moment(), moment()],
            'Hier': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
            'Les 7 derniers jours': [moment().subtract(6, 'days'), moment()],
            'Les 30 derniers jours': [moment().subtract(31, 'days'), moment()],
            'Ce mois': [moment().startOf('month'), moment().endOf('month')],
            'Le mois dernier': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        opens: 'left',
        drops: 'down',
        buttonClasses: ['btn', 'btn-sm'],
        applyClass: 'btn-primary',
        cancelClass: 'btn-default',
        separator: ' to ',
        locale: {
            applyLabel: 'Filtrer',
            cancelLabel: 'Annuler',
            fromLabel: 'Du',
            toLabel: 'Au',
            customRangeLabel: 'Filtre personnalisé',
            daysOfWeek: ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'],
            monthNames: ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
            firstDay: 1
        },
    }, function (start, end, label) {
        //console.log(start.toISOString(), end.toISOString(), label);
        $('#reportrange_top span').html("du " + start.format('DD/MM/YYYY') + ' au ' + end.format('DD/MM/YYYY'));

    });




});



$('#reportrange_top').on('apply.daterangepicker', function (ev, picker) {

    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');

});


function construct_filters(multiselect_values) {
    multiselect_values += ""
    var filters_array = multiselect_values.split(',');

    var arrayLength = filters_array.length;

    var filters = "";


    if (arrayLength === 4 | arrayLength === 0) {
        filters = "ga:pagePath=@/";
    }
    else if (arrayLength === 1) {
        filters = "ga:pagePath=@/" + filters_array[0] + "/";
    }
    else {
        for (var i = 0; i <= arrayLength - 1; i++) {
            filters += "ga:pagePathLevel1=@/" + filters_array[i] + "/";

            // S'i l'array n'est pas encore  fini on ajoute : OR et on   reboucle
            if (i !== arrayLength - 1) {
                // ; = AND, et , = OR

                filters += ","
            }

        }

    }

    if (filters === "" || filters === "ga:pagePath=@//") {
        filters = "ga:pagePath=@/";
    }


    return filters;
}


$("#btn-filtrer-ga").on("click", function () {


    var modules = $('#multiselect-modules').val();

    var filters = construct_filters(modules);

    ///////////////// Visites Total Line Chart ////////////////////
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:pageviews,ga:uniquePageViews',
            dimensions: 'ga:date',
            'start-date': start_date,
            'end-date': end_date,
            filters: filters,
        },
        chart: {
            container: 'visites-totales-chart-container',
            type: 'LINE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    dataChart.set({query: {ids: "ga:181212196"}}).execute();

    ////////////////// Pages les plus visités Table Chart ////////////////////////
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:pageviews,ga:uniquePageviews,ga:avgTimeOnPage',
            dimensions: 'ga:pageTitle,ga:pagePath',
            'start-date': start_date,
            'end-date': end_date,
            sort: '-ga:pageviews',
            filters: filters,
            'max-results': 10,
        },
        chart: {
            container: 'pages-plus-visites-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ///////////////// Users Devices ///////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:deviceCategory',
            filters: filters,
            'start-date': start_date,
            'end-date': end_date,
        },
        chart: {
            container: 'appareils-chart-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    /////////// Pages ou il a passéé le plus de temps ////////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:avgTimeOnPage',
            dimensions: 'ga:pagePath',
            filters: filters,
            'start-date': start_date,
            'end-date': end_date,
            'max-results': 10,
            'sort': '-ga:avgTimeOnPage'
        },
        chart: {
            container: 'pages-plus-temps-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ////////// Traffic Sources ////////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:source',
            filters: filters,
            'max-results': 8,
            'start-date': start_date,
            'end-date': end_date,
        },
        chart: {
            container: 'traffic-source-chart-container',
            type: 'TABLE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ///////////// Origine des visiteurs /////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:city',
            filters: filters,
            'start-date': start_date,
            'end-date': end_date,
        },
        chart: {
            container: 'origine-chart-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();


    ///////////////// NEW VS RETURNING VISITORS : Comportement des visiteurs ///////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:userType',
            filters: filters,
            'start-date': start_date,
            'end-date': end_date,
        },
        chart: {
            container: 'new-returning-visitors-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();

    ///////////////// Top Channels ( Direct, social, organic) ///////////////

    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:channelGrouping',
            filters: filters,
            'start-date': start_date,
            'end-date': end_date,
            'max-results': 5,
        },
        chart: {
            container: 'visitors-channels-container',
            type: 'PIE',
            options: {
                width: '100%'
            }
        }
    });

    /**
     * Render the dataChart on the page.
     */

    // Ga:xxxx = L'id de la propriété Google analytics
    dataChart.set({query: {ids: "ga:181212196"}}).execute();

});

