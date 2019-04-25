<!-- Initialize the plugin: -->
$(document).ready(function () {
    $('#multiselect-modules').multiselect({
        buttonWidth: '197px',
        dropRight: true,
        nonSelectedText: 'Tout (4)',
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


//Traffic Sources Table For QA
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
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:source',
            filters: 'ga:pagePath=@/e_commerce/',
            'max-results': 8,
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

});
////////////////////////////////////////////////////////////////////////

// Page plus vues Table Chart
gapi.analytics.ready(function () {

    /**
     * Authorize the user with an access token obtained server side.
     */
    gapi.analytics.auth.authorize({
        'serverAuth': {
            'access_token': '{{ ACCESS_TOKEN_FROM_GOOGLE_SERVICE_ACCOUNT }}'
        }
    });

    /**
     * Create a new DataChart instance with the given query parameters
     * and Google chart options. It will be rendered inside an element
     * with the id "chart-container".
     */
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:pageviews,ga:uniquePageviews,ga:avgTimeOnPage',
            dimensions: 'ga:pageTitle,ga:pagePath',
            'start-date': '30daysAgo',
            'end-date': 'today',
            sort: '-ga:pageviews',
            filters: 'ga:pagePath=@/e_commerce/',
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

});

//Pages où passe l'utilisateur le plus de temps

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
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:avgTimeOnPage',
            dimensions: 'ga:pagePath',
            filters: 'ga:pagePath=@/e_commerce/',
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

});

//Appareils des visiteurs

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
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:deviceCategory',
            filters: 'ga:pagePath=@/e_commerce/',
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

});


//Origine des vvisteurs

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
    var dataChart = new gapi.analytics.googleCharts.DataChart({
        query: {
            metrics: 'ga:users',
            dimensions: 'ga:city',
            filters: 'ga:pagePath=@/e_commerce/',
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

});


//Visites totales Line Chart Ecommerce

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
    var dataChart = new gapi.analytics.googleCharts.DataChart({
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

});


$('#reportrange_top').daterangepicker({
    format: 'DD/MM/YYYY',
    startDate: moment().subtract(29, 'days'),
    endDate: moment(),
    minDate: '01/01/2012',
    maxDate: '31/12/2099',
    dateLimit: {days: 29200},
    showDropdowns: true,
    showWeekNumbers: true,
    timePicker: false,
    timePickerIncrement: 1,
    timePicker12Hour: true,
    ranges: {
        "Aujourd'hui": [moment(), moment()],
        'Hier': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
        'Les 7 derniers jours': [moment().subtract(6, 'days'), moment()],
        'Les 30 derniers jours': [moment().subtract(29, 'days'), moment()],
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


start_date = "";
end_date = "";

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

            if (i !== arrayLength - 1) {
                // ; = AND, | , = OR
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

});

