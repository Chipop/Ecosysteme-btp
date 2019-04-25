"""Hello Analytics Reporting API V4 bi tasarrof xD by chipop."""

from googleapiclient.discovery import build
import os
from oauth2client.service_account import ServiceAccountCredentials



##Datastructure, necessary for requesting API from views by chipop

class Metrics:
    """Request Report contient : Mesures ,  pour google analytics API. """
    def __init__(self):
        self.__json_metrics = []

    def add_metric_expression(self,metric):
        metric_dict = {}
        metric_dict['expression'] = metric
        self.__json_metrics.append(metric_dict)
        return self

    def get_metrics_json(self):
        return self.__json_metrics


class Dimensions:
    """Dimensions pour google analytics API. """
    def __init__(self):
        self.__json_dimensions = []

    def add_dimension_name(self,dimension):
        dimension_dict = {}
        dimension_dict['name'] = dimension
        self.__json_dimensions.append(dimension_dict)
        return self

    def get_metrics_json(self):
        return self.__json_dimensions

class Filters:
    """Filtres pour google analytics API. """
    def __init__(self):
        self.__json_filters = []

    def add_filter(self,dimensionName: str, operator: str, expressions: []):
        """Ajoute un filtre.

        Args:
          dimensionName: Nom de dimension : doit être dans la classe Dimensions ( exemple : ga:uniquePageViews)
          operator: exemple : "EXACT" , "PARTIAL" = contains , ENDS_WITH, BEGINS_WITH, NUMERIC_EQUALS,NUMERIC_GREATER_THAN,NUMERIC_LESS_THAN,IN_LIST
          expression: Comparer la dimensionName avec une liste d'expressions, exemple ['ga:pageViews'] EXACT ["/dashboard/"], || ga:pagePath IN_LIST ['/dashboard","e_commerce']

        Returns:
          Un filtre.
          """
        filter_dict = {}
        filter_dict['dimensionName'] = dimensionName
        filter_dict['operator'] = operator
        filter_dict['expressions'] = expressions
        self.__json_filters.append(filter_dict)
        return self

    def get_filters_json(self):
        print(self.__json_filters)
        return self.__json_filters

##Google Api

# The scope for the OAuth2 request.
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

# The location of the key file with the key data.

module_dir = os.path.dirname(__file__)  # get current directory
GOOGLE_KEY_FILEPATH = os.path.join(module_dir, 'google_analytics_private_key.json')

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = GOOGLE_KEY_FILEPATH
VIEW_ID = '181212196'


def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics, start_date, end_date, metrics, dimensions, filters=None):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object. + les arguments de la requête
    Returns:
      The Analytics Reporting API V4 response.
    """
    if filters:
        return analytics.reports().batchGet(
            body={
                'reportRequests': [
                    {
                        'viewId': VIEW_ID,
                        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                        'metrics': metrics,
                        'dimensions': dimensions,
                        "dimensionFilterClauses": [
                            {"filters": filters }
                        ]
                    },

                ],

            }
        ).execute()
    else:
        return analytics.reports().batchGet(
            body={
                'reportRequests': [
                    {
                        'viewId': VIEW_ID,
                        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                        'metrics': metrics,
                        'dimensions': dimensions,
                    },

                ],

            }
        ).execute()

""" #You don't need this :) 
def print_response(response):
    \"\"\"Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    \"\"\"
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ' ' + dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range: ' + str(i))
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print(metricHeader.get('name') + ': ' + value)
"""

# End google code

#chipop method
def get_result(response):
    """Parses and prints the Analytics Reporting API V4 response.

        Args:
          response: An Analytics Reporting API V4 response.
        """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dateRangeValues = row.get('metrics', [])

            for i, values in enumerate(dateRangeValues):
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    return value



#chipop method
def get_scalar_result_analytics(start_date, end_date, metrics: Metrics, dimensions: Dimensions, filters: Filters=None):
    """Fait appel au rapport et lui donne les arguments de la requête.

        Args:
              start_date : Format : "YYYY-MM-DD"
              end_date : Format : "YYYY-MM-DD"
              metrics : Metrics object
              dimensions : Dimensions object
              filters : Filters object

        Returns:
          Résultat : Un nombre scalaire. exemple : nombre de vues d'une page X
        """
    analytics = initialize_analyticsreporting()

    if filters:
        response = get_report(analytics, start_date=start_date, end_date=end_date, metrics=metrics.get_metrics_json(),
                              dimensions=dimensions.get_metrics_json(), filters=filters.get_filters_json())
    else:
        response = get_report(analytics, start_date=start_date, end_date=end_date, metrics=metrics.get_metrics_json(),
                              dimensions=dimensions.get_metrics_json(), filters=None)

    return get_result(response)

## Demo How to use : Metrics class, Dimensions class, Filters class , and get_scalar_result_analytics method in main bellow
#by chipop


def main():
    m = Metrics()
    m.add_metric_expression(metric="ga:uniquePageViews")
    d = Dimensions()
    d.add_dimension_name("ga:pagePath")

    f = Filters()
    f.add_filter("ga:pagePath","EXACT",["/e_commerce/"])

    f.get_filters_json()


    print(get_scalar_result_analytics(start_date="2018-08-30",end_date="2018-09-05",metrics=m,dimensions=d,filters=f))


if __name__ == '__main__':
    main()



