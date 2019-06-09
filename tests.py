# encoding: utf-8

# pylint: disable=line-too-long
# pylint: disable=anomalous-unicode-escape-in-string
# pylint: disable=no-self-argument

import unittest

import six
import httpretty

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError, ForbiddenError, NotAuthorizedError
from opencage.geocoder import floatify_latlng, _query_for_reverse_geocoding


class OpenCageGeocodeTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testUKPostcode(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"total_results":10,"licenses":[{"name":"CC-BY-SA","url":"http://creativecommons.org/licenses/by-sa/3.0/"},{"name":"ODbL","url":"http://opendatacommons.org/licenses/odbl/summary/"}],"status":{"message":"OK","code":200},"thanks":"For using an OpenCage Data API","rate":{"limit":"2500","remaining":2487,"reset":1402185600},"results":[{"annotations":{},"components":{"country_name":"United Kingdom","region":"Islington","locality":"Clerkenwell"},"formatted":"Clerkenwell, Islington, United Kingdom","geometry":{"lat":"51.5221558691","lng":"-0.100838524406"},"bounds":null},{"formatted":"82, Lokku Ltd, Clerkenwell Road, Clerkenwell, London Borough of Islington, London, EC1M 5RF, Greater London, England, United Kingdom, gb","components":{"county":"London","state_district":"Greater London","road":"Clerkenwell Road","country_code":"gb","house_number":"82","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","house":"Lokku Ltd","postcode":"EC1M 5RF"},"annotations":{},"bounds":{"northeast":{"lng":"-0.1023889","lat":"51.5226795"},"southwest":{"lat":"51.5225795","lng":"-0.1024889"}},"geometry":{"lat":"51.5226295","lng":"-0.1024389"}},{"components":{"county":"London","state_district":"Greater London","road":"Clerkenwell Road","country_code":"gb","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","postcode":"EC1M 6DS"},"annotations":{},"formatted":"Clerkenwell Road, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","geometry":{"lat":"51.5225346","lng":"-0.1027003"},"bounds":{"northeast":{"lat":"51.5225759","lng":"-0.1020597"},"southwest":{"lat":"51.5225211","lng":"-0.103223"}}},{"formatted":"Clerkenwell Road, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Craft Central","annotations":{},"components":{"postcode":"EC1M 6DS","arts_centre":"Craft Central","state":"England","suburb":"Clerkenwell","country":"United Kingdom","city":"London Borough of Islington","country_code":"gb","road":"Clerkenwell Road","state_district":"Greater London","county":"London"},"bounds":{"northeast":{"lat":"51.52246","lng":"-0.1027652"},"southwest":{"lng":"-0.1028652","lat":"51.52236"}},"geometry":{"lng":"-0.1028152","lat":"51.52241"}},{"components":{"county":"London","state_district":"Greater London","restaurant":"Noodle Express","road":"Albemarle Way","country_code":"gb","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","postcode":"EC1M 6DS"},"annotations":{},"formatted":"Noodle Express, Albemarle Way, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","geometry":{"lng":"-0.10255386845056","lat":"51.5228195"},"bounds":{"southwest":{"lng":"-0.102621","lat":"51.5227781"},"northeast":{"lat":"51.5228603","lng":"-0.1024869"}}},{"geometry":{"lat":"51.5229424","lng":"-0.102380530769224"},"bounds":{"northeast":{"lat":"51.5229759","lng":"-0.1023064"},"southwest":{"lng":"-0.1024639","lat":"51.5229046"}},"annotations":{},"components":{"county":"London","state_district":"Greater London","road":"Albemarle Way","country_code":"gb","cafe":"PAR","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","postcode":"EC1M 6DS"},"formatted":"PAR, Albemarle Way, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb"},{"formatted":"Workshop Coffee Co., 27, Clerkenwell Road, Clerkenwell, London Borough of Islington, London, EC1M 5RN, Greater London, England, United Kingdom, gb","components":{"county":"London","state_district":"Greater London","road":"Clerkenwell Road","country_code":"gb","house_number":"27","cafe":"Workshop Coffee Co.","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","postcode":"EC1M 5RN"},"annotations":{},"bounds":{"southwest":{"lng":"-0.1024422","lat":"51.5222246"},"northeast":{"lng":"-0.1022307","lat":"51.5224408"}},"geometry":{"lat":"51.52234585","lng":"-0.102338899572156"}},{"components":{"county":"London","state_district":"Greater London","road":"St. John Street","country_code":"gb","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","hairdresser":"Franco & Co","state":"England","postcode":"EC1M 6DS"},"annotations":{},"formatted":"St. John Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Franco & Co","geometry":{"lng":"-0.1024118","lat":"51.5231165"},"bounds":{"southwest":{"lng":"-0.1024618","lat":"51.5230665"},"northeast":{"lng":"-0.1023618","lat":"51.5231665"}}},{"bounds":{"northeast":{"lng":"-0.1023218","lat":"51.5231688"},"southwest":{"lat":"51.5229634","lng":"-0.1024934"}},"geometry":{"lng":"-0.102399365567707","lat":"51.5230257"},"formatted":"St. John Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, MacCarthy","annotations":{},"components":{"county":"London","state_district":"Greater London","road":"St. John Street","country_code":"gb","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","hairdresser":"MacCarthy","state":"England","postcode":"EC1M 6DS"}},{"geometry":{"lng":"-0.102730855172415","lat":"51.52267345"},"bounds":{"northeast":{"lng":"-0.1025498","lat":"51.5227315"},"southwest":{"lat":"51.5226068","lng":"-0.1028931"}},"annotations":{},"components":{"county":"London","state_district":"Greater London","road":"Albemarle Way","country_code":"gb","house_number":"84","country":"United Kingdom","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","house":"The Printworks","postcode":"EC1M 6DS"},"formatted":"84, The Printworks, Albemarle Way, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb"}],"timestamp":{"created_unix":1402133768,"created_http":"Sat, 07 Jun 2014 09:36:08 GMT"}}',
        )

        results = self.geocoder.geocode("EC1M 5RF")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results),
            msg="Bad result"
        )

    def testAustralia(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"licenses":[{"url":"http://creativecommons.org/licenses/by-sa/3.0/","name":"CC-BY-SA"},{"url":"http://opendatacommons.org/licenses/odbl/summary/","name":"ODbL"}],"status":{"message":"OK","code":200},"thanks":"For using an OpenCage Data API","results":[{"geometry":{"lng":"149.5886383","lat":"-32.5980702"},"components":{"country_code":"au","state":"New South Wales","country":"Australia","town":"Mudgee"},"formatted":"Mudgee, New South Wales, Australia, au","annotations":{},"bounds":{"southwest":{"lng":"149.5486383","lat":"-32.6380702"},"northeast":{"lng":"149.6286383","lat":"-32.5580702"}}},{"formatted":"Mudgee, Mid-Western Regional, New South Wales, Australia","components":{"state":"New South Wales","country":"Australia","county":"Mid-Western Regional","town":"Mudgee"},"bounds":{"southwest":{"lng":"149.573196411","lat":"-32.6093025208"},"northeast":{"lng":"149.602890015","lat":"-32.5818252563"}},"annotations":{},"geometry":{"lng":149.5871,"lat":-32.59426}}],"total_results":2,"rate":{"reset":1402185600,"limit":"2500","remaining":2489},"timestamp":{"created_http":"Sat, 07 Jun 2014 09:31:50 GMT","created_unix":1402133510}}',
        )

        results = self.geocoder.geocode("Mudgee, Australia")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - -32.5980702) < 0.05 and abs(result['geometry']['lng'] - 149.5886383) < 0.05) for result in results),
            msg="Bad result"
        )


    def testMustBeUnicodeString(self):
        # dud mock so this goes quick
        httpretty.register_uri(httpretty.GET, self.geocoder.url, body='{"results":{}}')

        # Should not give errors
        self.geocoder.geocode('xxx')    # ascii convertable
        self.geocoder.geocode(six.u('xxx'))   # unicode
        self.geocoder.geocode(six.u('xxá'))   # unicode

        # But if it isn't a unicode string, it should give error
        utf8_string = six.u("xxá").encode("utf-8")
        latin1_string = six.u("xxá").encode("latin1")

        self.assertRaises(InvalidInputError, self.geocoder.geocode, utf8_string)

        # check the exception
        try:
            self.geocoder.geocode(utf8_string)
        except InvalidInputError as ex:
            self.assertEqual(ex.bad_value, utf8_string)
            self.assertEqual(str(ex), "Input must be a unicode string, not {0!r}".format(utf8_string))

        self.assertRaises(InvalidInputError, self.geocoder.geocode, latin1_string)

        # check the exception
        try:
            self.geocoder.geocode(latin1_string)
        except InvalidInputError as ex:
            self.assertEqual(ex.bad_value, latin1_string)
            self.assertEqual(str(ex), "Input must be a unicode string, not {0!r}".format(latin1_string))


    def testMunster(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"licenses":[{"name":"CC-BY-SA","url":"http://creativecommons.org/licenses/by-sa/3.0/"},{"name":"ODbL","url":"http://opendatacommons.org/licenses/odbl/summary/"}],"thanks":"For using an OpenCage Data API","total_results":10,"status":{"message":"OK","code":200},"results":[{"formatted":"M\u00fcnster, M\u00fcnster, 48143,48144,48145,48146,48147,48148,48149,48150,48151,48152,48153,48154,48155,48156,48157,48158,48159,48160,48161,48162,48163,48164,48165,48166,48167, Regierungsbezirk M\u00fcnster, North Rhine-Westphalia, Germany, de","geometry":{"lat":"51.9625101","lng":"7.6251879"},"components":{"country_code":"de","postcode":"48143,48144,48145,48146,48147,48148,48149,48150,48151,48152,48153,48154,48155,48156,48157,48158,48159,48160,48161,48162,48163,48164,48165,48166,48167","state_district":"Regierungsbezirk M\u00fcnster","state":"North Rhine-Westphalia","city":"M\u00fcnster","county":"M\u00fcnster","country":"Germany"},"bounds":{"southwest":{"lng":"7.4651879","lat":"51.8025101"},"northeast":{"lng":"7.7851879","lat":"52.1225101"}},"annotations":{}},{"bounds":{"northeast":{"lat":"52.0600706","lng":"7.7743708"},"southwest":{"lat":"51.8402214","lng":"7.4738051"}},"annotations":{},"geometry":{"lat":"51.95027025","lng":"7.61334708872901"},"components":{"country_code":"de","state_district":"Regierungsbezirk M\u00fcnster","state":"North Rhine-Westphalia","county":"M\u00fcnster","country":"Germany"},"formatted":"M\u00fcnster, Regierungsbezirk M\u00fcnster, North Rhine-Westphalia, Germany, de"},{"formatted":"Munster, Ireland, ie","annotations":{},"bounds":{"southwest":{"lat":"51.4199027","lng":"-10.6891099"},"northeast":{"lng":"-6.9497829","lat":"53.1689062"}},"components":{"country_code":"ie","state_district":"Munster","country":"Ireland"},"geometry":{"lng":"-8.57089717629267","lat":"52.3076216"}},{"formatted":"Germany, de, M\u00fcnster","annotations":{},"bounds":{"southwest":{"lat":"51.8402214","lng":"7.4738051"},"northeast":{"lat":"52.0600706","lng":"7.7743708"}},"geometry":{"lat":"51.95027025","lng":"7.61334708872901"},"components":{"country_code":"de","address100":"M\u00fcnster","country":"Germany"}},{"formatted":"M\u00fcnster, M\u00fcnster, Stuttgart, Stuttgart, Regierungsbezirk Stuttgart, Baden-W\u00fcrttemberg, Germany, de","components":{"city":"Stuttgart","state":"Baden-W\u00fcrttemberg","city_district":"M\u00fcnster","country":"Germany","country_code":"de","state_district":"Regierungsbezirk Stuttgart","suburb":"M\u00fcnster","county":"Stuttgart"},"geometry":{"lat":"48.8212962","lng":"9.2200016"},"bounds":{"northeast":{"lng":"9.2400016","lat":"48.8412962"},"southwest":{"lng":"9.2000016","lat":"48.8012962"}},"annotations":{}},{"geometry":{"lng":"8.8671181","lat":"49.9229236"},"components":{"country_code":"de","state_district":"Regierungsbezirk Darmstadt","state":"Hesse","city":"M\u00fcnster","county":"Landkreis Darmstadt-Dieburg","country":"Germany"},"annotations":{},"bounds":{"northeast":{"lat":"49.9438725","lng":"8.9161067"},"southwest":{"lat":"49.9056973","lng":"8.7705856"}},"formatted":"M\u00fcnster, Landkreis Darmstadt-Dieburg, Regierungsbezirk Darmstadt, Hesse, Germany, de"},{"formatted":"M\u00fcnster, Stuttgart, Stuttgart, Regierungsbezirk Stuttgart, Baden-W\u00fcrttemberg, Germany, de","geometry":{"lat":"48.8272797","lng":"9.2024402537349"},"components":{"country_code":"de","state_district":"Regierungsbezirk Stuttgart","state":"Baden-W\u00fcrttemberg","city":"Stuttgart","city_district":"M\u00fcnster","county":"Stuttgart","country":"Germany"},"bounds":{"northeast":{"lat":"48.8384709","lng":"9.2273738"},"southwest":{"lng":"9.1883711","lat":"48.8152795"}},"annotations":{}},{"bounds":{"southwest":{"lng":"10.8788966","lat":"48.5896428"},"northeast":{"lat":"48.6515558","lng":"10.9314006"}},"annotations":{},"geometry":{"lng":"10.9008883","lat":"48.6242219"},"components":{"country_code":"de","state_district":"Swabia","state":"Free State of Bavaria","city":"M\u00fcnster","county":"Rain (Schwaben)","country":"Germany"},"formatted":"M\u00fcnster, Rain (Schwaben), Swabia, Free State of Bavaria, Germany, de"},{"formatted":"Munster, Lake County, Indiana, United States of America, us","bounds":{"northeast":{"lat":"41.5814003","lng":"-87.4802388"},"southwest":{"lng":"-87.5254509","lat":"41.522608"}},"annotations":{},"geometry":{"lat":"41.5644798","lng":"-87.5125412"},"components":{"country_code":"us","state":"Indiana","city":"Munster","county":"Lake County","country":"United States of America"}},{"bounds":{"northeast":{"lng":"12.5929086","lat":"48.9728073"},"southwest":{"lng":"12.5529086","lat":"48.9328073"}},"annotations":{},"geometry":{"lng":"12.5729086","lat":"48.9528073"},"components":{"country_code":"de","state_district":"Lower Bavaria","village":"M\u00fcnster","state":"Free State of Bavaria","county":"Landkreis Straubing-Bogen","country":"Germany"},"formatted":"M\u00fcnster, Landkreis Straubing-Bogen, Lower Bavaria, Free State of Bavaria, Germany, de"}],"timestamp":{"created_unix":1402135758,"created_http":"Sat, 07 Jun 2014 10:09:18 GMT"},"rate":{"remaining":2485,"reset":1402185600,"limit":"2500"}}',
        )

        results = self.geocoder.geocode(six.u("Münster"))
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 51.9625101) < 0.05 and abs(result['geometry']['lng'] - 7.6251879) < 0.05) for result in results),
            msg="Bad result"
        )

    def testDonostia(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"thanks":"For using an OpenCage Data API","status":{"message":"OK","code":200},"rate":{"remaining":2482,"limit":"2500","reset":1402185600},"total_results":7,"results":[{"geometry":{"lat":"43.3213324","lng":"-1.9856227"},"annotations":{},"components":{"postcode":"20001;20002;20003;20004;20005;20006;20007;20008;20009;20010;20011;20012;20013;20014;20015;20016;20017;20018","county":"Donostialdea/Donostia-San Sebasti\u00e1n","state":"Basque Country","country":"Spain","city":"San Sebasti\u00e1n","country_code":"es"},"formatted":"San Sebasti\u00e1n, Donostialdea/Donostia-San Sebasti\u00e1n, 20001;20002;20003;20004;20005;20006;20007;20008;20009;20010;20011;20012;20013;20014;20015;20016;20017;20018, Basque Country, Spain, es","bounds":{"southwest":{"lat":"43.2178373","lng":"-2.086808"},"northeast":{"lng":"-1.8878838","lat":"43.3381344"}}},{"formatted":"Donostia, Irun, Bidasoa Beherea / Bajo Bidasoa, Basque Country, Spain, es","components":{"county":"Bidasoa Beherea / Bajo Bidasoa","state":"Basque Country","country":"Spain","city":"Irun","country_code":"es","road":"Donostia"},"bounds":{"southwest":{"lat":"43.3422299","lng":"-1.8022744"},"northeast":{"lng":"-1.8013452","lat":"43.3449598"}},"geometry":{"lng":"-1.8019153","lat":"43.3432784"},"annotations":{}},{"annotations":{},"geometry":{"lng":"-1.8022744","lat":"43.3422299"},"formatted":"Donostia, Anaka, Irun, Bidasoa Beherea / Bajo Bidasoa, Basque Country, Spain, es","components":{"county":"Bidasoa Beherea / Bajo Bidasoa","state":"Basque Country","country":"Spain","city":"Irun","suburb":"Anaka","country_code":"es","road":"Donostia"},"bounds":{"southwest":{"lng":"-1.8022971","lat":"43.3421635"},"northeast":{"lng":"-1.8022744","lat":"43.3422299"}}},{"geometry":{"lng":"-2.69312049872164","lat":"42.868297"},"annotations":{},"bounds":{"southwest":{"lng":"-2.6933154","lat":"42.8681484"},"northeast":{"lat":"42.8684357","lng":"-2.6929252"}},"formatted":"Donostia kalea, Ibaiondo, Vitoria-Gasteiz, Vitoria-Gasteizko Eskualdea / Cuadrilla de Vitoria, Basque Country, Spain, es","components":{"county":"Vitoria-Gasteizko Eskualdea / Cuadrilla de Vitoria","state":"Basque Country","country":"Spain","city":"Vitoria-Gasteiz","suburb":"Ibaiondo","country_code":"es","road":"Donostia kalea"}},{"bounds":{"southwest":{"lng":"-2.6889534","lat":"42.8620967"},"northeast":{"lat":"42.8623764","lng":"-2.6885774"}},"formatted":"Donostia kalea, Lakua, Vitoria-Gasteiz, Vitoria-Gasteizko Eskualdea / Cuadrilla de Vitoria, Basque Country, Spain, es","components":{"county":"Vitoria-Gasteizko Eskualdea / Cuadrilla de Vitoria","state":"Basque Country","country":"Spain","city":"Vitoria-Gasteiz","suburb":"Lakua","country_code":"es","road":"Donostia kalea"},"geometry":{"lat":"42.8622515","lng":"-2.68876582144679"},"annotations":{}},{"annotations":{},"geometry":{"lat":"51.5146888","lng":"-0.1609307"},"components":{"restaurant":"Donostia","country":"United Kingdom","state_district":"Greater London","country_code":"gb","county":"London","state":"England","suburb":"Marylebone","city":"City of Westminster","road":"Great Cumberland Mews"},"formatted":"Donostia, Great Cumberland Mews, Marylebone, City of Westminster, London, Greater London, England, United Kingdom, gb","bounds":{"northeast":{"lng":"-0.1608807","lat":"51.5147388"},"southwest":{"lat":"51.5146388","lng":"-0.1609807"}}},{"geometry":{"lat":43.31283,"lng":-1.97499},"annotations":{},"bounds":{"northeast":{"lng":"-1.92020404339","lat":"43.3401603699"},"southwest":{"lat":"43.2644081116","lng":"-2.04920697212"}},"formatted":"San Sebastian, Gipuzkoa, Basque Country, Spain, Donostia / San Sebasti\u00e1n","components":{"county":"Gipuzkoa","state":"Basque Country","country":"Spain","town":"San Sebastian","local administrative area":"Donostia / San Sebasti\u00e1n"}}],"timestamp":{"created_unix":1402136556,"created_http":"Sat, 07 Jun 2014 10:22:36 GMT"},"licenses":[{"name":"CC-BY-SA","url":"http://creativecommons.org/licenses/by-sa/3.0/"},{"name":"ODbL","url":"http://opendatacommons.org/licenses/odbl/summary/"}]}',

        )

        results = self.geocoder.geocode("Donostia")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 43.300836) < 0.05 and abs(result['geometry']['lng'] - -1.9809529) < 0.05) for result in results),
            msg="Bad result"
        )

        # test that the results are in unicode
        self.assertEqual(results[0]['formatted'], six.u('San Sebasti\xe1n, Donostialdea/Donostia-San Sebasti\xe1n, 20001;20002;20003;20004;20005;20006;20007;20008;20009;20010;20011;20012;20013;20014;20015;20016;20017;20018, Basque Country, Spain, es'))


class FloatifyDictTestCase(unittest.TestCase):
    def _expected_output(input_value, expected_output):
        def test(self):
            self.assertEqual(floatify_latlng(input_value), expected_output)
        return test

    testString = _expected_output("123", "123")
    testEmptyDict = _expected_output({}, {})
    testEmptyList = _expected_output([], [])
    testDictWithFloats = _expected_output({'geom': {'lat': 12.01, 'lng': -0.9}}, {'geom': {'lat': 12.01, 'lng': -0.9}})
    testDictWithStringifiedFloats = _expected_output({'geom': {'lat': "12.01", 'lng': "-0.9"}}, {'geom': {'lat': 12.01, 'lng': -0.9}})
    testDictWithList = _expected_output(
        {'results': [{'geom': {'lat': "12.01", 'lng': "-0.9"}}, {'geometry': {'lat': '0.1', 'lng': '10'}}]},
        {'results': [{'geom': {'lat': 12.01, 'lng': -0.9}}, {'geometry': {'lat': 0.1, 'lng': 10}}]}
    )
    testListWithThings = _expected_output([{'foo': 'bar'}], [{'foo': 'bar'}])


class RateLimitErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testNoRateLimit(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"status":{"code":200,"message":"OK"},"thanks":"For using an OpenCage Data API","total_results":0,"licenses":[{"url":"http://creativecommons.org/licenses/by-sa/3.0/","name":"CC-BY-SA"},{"url":"http://opendatacommons.org/licenses/odbl/summary/","name":"ODbL"}],"rate":{"reset":1402185600,"limit":"2500","remaining":2479},"results":[],"timestamp":{"created_http":"Sat, 07 Jun 2014 10:38:45 GMT","created_unix":1402137525}}')

        # shouldn't raise an exception
        self.geocoder.geocode("whatever")


    def testRateLimitExceeded(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"status":{"code":402,"message":"OK"},"thanks":"For using an OpenCage Data API","total_results":0,"licenses":[{"url":"http://creativecommons.org/licenses/by-sa/3.0/","name":"CC-BY-SA"},{"url":"http://opendatacommons.org/licenses/odbl/summary/","name":"ODbL"}],"rate":{"reset":1402185600,"limit":"2500","remaining":0},"results":[],"timestamp":{"created_http":"Sat, 07 Jun 2014 10:38:45 GMT","created_unix":1402137525}}',
            status=402,
            adding_headers={'X-RateLimit-Limit': '2500', 'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1402185600'},
        )

        self.assertRaises(RateLimitExceededError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except RateLimitExceededError as ex:
            self.assertEqual(str(ex), 'Your rate limit has expired. It will reset to 2500 on 2014-06-08T00:00:00')
            self.assertEqual(ex.reset_to, 2500)


class NotAuthorizedErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('unauthorized-key')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testApiKeyForbidden(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"documentation":"https://opencagedata.com/api","licenses":[{"name":"see attribution guide","url":"https://opencagedata.com/credits"}],"results":[],"status":{"code":401,"message":"invalid API key"},"stay_informed":{"blog":"https://blog.opencagedata.com","twitter":"https://twitter.com/opencagedata"},"thanks":"For using an OpenCage Data API","timestamp":{"created_http":"Sun, 09 Jun 2019 19:58:46 GMT","created_unix":1560110326},"total_results":0}',
            status=401,
        )

        self.assertRaises(NotAuthorizedError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except NotAuthorizedError as ex:
            self.assertEqual(str(ex), 'Your API key is not authorized. You may have entered it incorrectly.')


class ForbiddenErrorTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()

        self.geocoder = OpenCageGeocode('2e10e5e828262eb243ec0b54681d699a')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testApiKeyBlocked(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"documentation":"https://opencagedata.com/api","licenses":[{"name":"see attribution guide","url":"https://opencagedata.com/credits"}],"results":[],"status":{"code":403,"message":"suspended"},"stay_informed":{"blog":"https://blog.opencagedata.com","twitter":"https://twitter.com/opencagedata"},"thanks":"For using an OpenCage Data API","timestamp":{"created_http":"Sun, 09 Jun 2019 20:01:22 GMT","created_unix":1560110482},"total_results":0}',
            status=403,
        )

        self.assertRaises(ForbiddenError, self.geocoder.geocode, "whatever")

        # check the exception
        try:
            self.geocoder.geocode("whatever")
        except ForbiddenError as ex:
            self.assertEqual(str(ex), 'Your API key has been blocked or suspended.')


class ReverseGeocodingTestCase(unittest.TestCase):
    def _expected_output(input_latlng, expected_output):
        def test(self):
            lat, lng = input_latlng
            self.assertEqual(_query_for_reverse_geocoding(lat, lng), expected_output)
        return test

    testSimple1 = _expected_output((10, 10), "10,10")
    testSimple2 = _expected_output((10.0, 10.0), "10.0,10.0")
    testSimple3 = _expected_output((0.000002, -120), "0.000002,-120")
    testSimple4 = _expected_output((2.000002, -120), "2.000002,-120")
    testSimple5 = _expected_output((2.000002, -120.000002), "2.000002,-120.000002")
    testSimple6 = _expected_output((2.000002, -1.0000002), "2.000002,-1.0000002")
    testSimple7 = _expected_output((2.000002, 0.0000001), "2.000002,0.0000001")

    testSimple8 = _expected_output(("2.000002", "-120"), "2.000002,-120")


class UnknownProblemTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()
        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test500Status(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='',
            status=500,
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")

    def testNonJson(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='',
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")

    def testNoResultsKey(self):
        httpretty.register_uri(
            httpretty.GET,
            self.geocoder.url,
            body='{"spam": "eggs"}',
        )

        self.assertRaises(UnknownError, self.geocoder.geocode, "whatever")
