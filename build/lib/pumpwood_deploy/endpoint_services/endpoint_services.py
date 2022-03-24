import os
from slugify import slugify

services = [
    {
        'service': 'pumpwood-frontend',
        'endpoint': [
            '/gui/',
        ]
    }, {
        'service': 'pumpwood-auth-app',
        'health-check': True,
        'admin': True,
        'endpoint': [
            '/rest/registration/',
            '/rest/user/',
            '/admin/registration/',
            '/static/registration/']
    }, {
        'service': 'crawler-facebook-ads-app',
        'health-check': True,
        'endpoint': [
            '/rest/facebookadspullerjob/',
            '/rest/facebookadspullerqueue/',
            '/rest/facebookadspusherjob/',
            '/rest/facebookadspusherqueue/',
            '/rest/facebookadscampaign/',
            '/rest/facebookadsadset/',
            '/rest/facebookadsad/',
            '/rest/facebookadscampaignreport/']
    }, {
        'service': 'crawler-twitter-ads-app',
        'health-check': True,
        'endpoint': [
            '/rest/twitteradspullerjob/',
            '/rest/twitteradspullerqueue/',
            '/rest/twitteradspusherjob/',
            '/rest/twitteradspusherqueue/',
            '/rest/twitteradsfundinginstrument/',
            '/rest/twitteradscampaign/',
            '/rest/twitteradslineitem/',
            '/rest/twitteradspromotedtweet/',
            '/rest/twitteradspromotedtweetdata/']
    }, {
        'service': 'crawler-twitter-open-app',
        'health-check': True,
        'endpoint': [
            '/rest/twitteropenpullerjob/',
            '/rest/twitteropenpullerqueue/',
            '/rest/twitteropenpusherjob/',
            '/rest/twitteropenpusherqueue/',
            '/rest/twitteropenapipageinfo/',
            '/rest/twitteropenapitweet/']
    }, {
        'service': 'crawler-google-trends-app',
        'health-check': True,
        'endpoint': [
            '/rest/googletrendspullerjob/',
            '/rest/googletrendspullerqueue/',
            '/rest/googletrendspusherjob/',
            '/rest/googletrendspusherqueue/',
            '/rest/googletrendscrawlerhistoricaldata/',
            '/rest/googletrendscrawlerrelatedtopics/',
            '/rest/googletrendscrawlerinterestbyregion/',
            '/rest/googletrendscrawlerrelatedquery/']
    }, {
        'service': 'crawler-google-ads-app',
        'health-check': True,
        'endpoint': [
            '/rest/googleadspullerjob/',
            '/rest/googleadspullerqueue/',
            '/rest/googleadspusherjob/',
            '/rest/googleadspusherqueue/',
            '/rest/googleadsaccount/',
            '/rest/googleadscampaign/',
            '/rest/googleadsadgroup/',
            '/rest/googleadsad/',
            '/rest/googleadsadperformancereport/']
    }, {
        'service': 'crawler-bigdata-corp-app',
        'health-check': True,
        'endpoint': [
            # Queue
            '/rest/bigdatacorppullerjob/',
            '/rest/bigdatacorppullerqueue/',
            '/rest/bigdatacorppusherjob/',
            '/rest/bigdatacorppusherqueue/',
            # Data
            '/rest/bigdatacorpdocfinder/',
            '/rest/bigdatacorpbasic/',
            '/rest/bigdatacorpprofessional/',
            '/rest/bigdatacorpdemographic/',
            '/rest/bigdatacorpaddress/',
            '/rest/bigdatacorpinterest/',
            '/rest/bigdatacorprelationship/',
            '/rest/bigdatacorpfinancial/',
            '/rest/bigdatacorpraw/']
    }, {
        'service': 'crawler-nbs-tetris-app',
        'health-check': True,
        'endpoint': [
            # Queue
            "/rest/nbstetrispullerjob/",
            "/rest/nbstetrispullerqueue/",
            "/rest/nbstetrispusherjob/",
            "/rest/nbstetrispusherqueue/",
            # Scheduler
            "/rest/nbstetrisschedulerjob/",
            "/rest/nbstetrisschedulerqueue/",
            # Data
            "/rest/nbstetriscampaign/",
            "/rest/nbstetriscampaignapiinfo/",
            "/rest/nbstetriscampaigngraphdata/",
            "/rest/nbstetriscampaignresults/", ]
    }, {
        'service': 'crawler-cryptocurrency-app',
        'health-check': True,
        'endpoint': [
            # Queue
            "/rest/cryptocurrencypullerjob/",
            "/rest/cryptocurrencypullerqueue/",
            "/rest/cryptocurrencypusherjob/",
            "/rest/cryptocurrencypusherqueue/",
            # Scheduler
            "/rest/cryptocurrencyschedulerjob/",
            "/rest/cryptocurrencyschedulerqueue/",
            # Data
            "/rest/cryptocurrencycandledata/"]
    }, {
        'service': 'pumpwood-datalake-app',
        'health-check': True,
        'endpoint': [
            # Data
            "/rest/descriptionattribute/",
            "/rest/attributehierarchy/",
            "/rest/categoricalattributedescription/",
            "/rest/descriptionmodelingunit/",
            "/rest/modelingunithierarchy/",
            "/rest/databasevariable/",
            "/rest/datainputdatabasevariable/",
            "/rest/toloaddatabasevariable/",
            # calendar
            "/rest/descriptioncalendar/",
            "/rest/calendarhierarchy/",
            "/rest/categoricalcalendardescription/",
            "/rest/calendardatabase/",
            "/rest/datainputcalendar/",
            "/rest/toloadcalendar/",
            # geography
            "/rest/descriptiongeoattribute/",
            "/rest/attributehierarchy/",
            "/rest/geoattributehierarchy/",
            "/rest/categoricalgeoattributedescription/",
            "/rest/descriptiongeoarea/",
            "/rest/geoareahierarchy/",
            "/rest/geodatabasevariable/",
            "/rest/datainputgeodatabasevariable/",
            "/rest/toloadgeodatabasevariable/",
            # dummy
            "/rest/descriptiondummy/",
            # ETL
            "/rest/datalakeetljob/",
            "/rest/datalakeetlqueue/", ]
    }, {
        'service': 'pumpwood-estimation-app',
        'health-check': True,
        'endpoint': [
            "/rest/autofilter/",
            "/rest/descriptionmodel/",
            "/rest/modelhierarchy/",
            "/rest/modelautofilterexception/",
            "/rest/modelfiltermodelingunit/",
            "/rest/modelfiltergeoarea/",
            "/rest/modelfiltercalendar/",
            "/rest/modelvarattribute/",
            "/rest/modelvargeoattribute/",
            "/rest/modelvarcalendar/",
            "/rest/modelvardummy/",
            "/rest/parametersneedbymodel/",
            "/rest/modelqueue/",
            "/rest/modelgroup/",
            "/rest/modelqueueresultsresiduals/",
            "/rest/modelqueueresultsparameter/",
            "/rest/modelqueueresultscomplex/"]
    }, {
        'service': 'pumpwood-transformation-app',
        'health-check': True,
        'endpoint': [
            # Auto Filter
            '/rest/datatransformation/',
        ]
    }, {
        'service': 'pumpwood-prediction-app',
        'health-check': True,
        'endpoint': [
            '/rest/predictionqueue/',
            '/rest/predictiondata/',
            '/rest/toloadpredictiondata/',
            '/rest/cleanpredictiondata/',
            '/rest/toloadcleanpredictiondata/',
            '/rest/scenarioblueprint',
            '/rest/scenariomodel',
            '/rest/scenarioattributeextensionrule',
            '/rest/scenariogeoattributeextensionrule',
            '/rest/scenariomodelprediction',
        ]
    },
    # Models
    {
        'service': 'estimation-modelrun--py-statsmodels-glm',
        'health-check': True,
        'model': 'py-statsmodels-glm',
        'endpoint': [
            # Auto Filter
            '/rest/estimation-model/py-statsmodels-glm/',
        ]
    },
]


class EndPointServices:
    """Create end-point services."""

    def __init__(self):
        """__init__."""
        self.base_path = os.getcwd() + '/endpoint_services/'

    def create_deployment_file(self):
        """create_deployment_file."""
        deployment_list = []
        for s in services:
            file_path = os.path.dirname(__file__)
            with open(os.path.join(file_path + '/resources_yml/{service}.yml'.format(
                    service=s['service'])), 'r') as file:
                service_text = file.read()
            deployment_list.append(
                {
                 'type': 'endpoint_services',
                 'name': slugify(s['service'], separator="_") +
                         '__endpoint_service',
                 'content': service_text, 'end_points': s['endpoint'],
                 'service': s['service'],
                 'health-check': s.get('health-check', False),
                 'admin': s.get('admin', False),
                 'model': s.get('model'),
                 'sleep': 0}
            )
        return deployment_list
