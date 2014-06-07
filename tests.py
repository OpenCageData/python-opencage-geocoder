# encoding: utf-8
import unittest
import re
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import floatify_latlng

import httpretty

class OpenCageGeocodeTestCase(unittest.TestCase):
    def setUp(self):
        httpretty.enable()


        self.geocoder = OpenCageGeocode('abcde')

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def testBasic1(self):
        httpretty.register_uri(httpretty.GET,
            re.compile("http://prototype.opencagedata.com/geocode/v1/json"),
            body='{"results":[{"bounds":null,"formatted":"Clerkenwell, Islington, United Kingdom","annotations":{},"geometry":{"lng":"-0.100604408313","lat":"51.5198137539"},"components":{"region":"Islington","country_name":"United Kingdom","locality":"Clerkenwell"}},{"components":{"county":"London","country":"United Kingdom","suburb":"Clerkenwell","city":"London Borough of Islington","state":"England","state_district":"Greater London","postcode":"EC1M 6DS","country_code":"gb"},"geometry":{"lat":"51.5201774","lng":"-0.1025129"},"formatted":"Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","annotations":{},"bounds":{"northeast":{"lat":"51.5202274","lng":"-0.1024629"},"southwest":{"lat":"51.5201274","lng":"-0.1025629"}}},{"components":{"suburb":"Clerkenwell","city":"London Borough of Islington","county":"London","country":"United Kingdom","road":"St John Street","state_district":"Greater London","postcode":"EC1M 6DS","country_code":"gb","state":"England"},"geometry":{"lng":"-0.1016895","lat":"51.520447"},"annotations":{},"formatted":"St John Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","bounds":{"northeast":{"lat":"51.5209054","lng":"-0.101562"},"southwest":{"lat":"51.5198337","lng":"-0.1017732"}}},{"components":{"city":"London Borough of Islington","suburb":"Clerkenwell","country":"United Kingdom","footway":"Eagle Court","county":"London","state_district":"Greater London","country_code":"gb","postcode":"EC1M 6DS","state":"England"},"geometry":{"lat":"51.5203746","lng":"-0.1027904"},"formatted":"Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Eagle Court","annotations":{},"bounds":{"northeast":{"lng":"-0.1021824","lat":"51.5207147"},"southwest":{"lng":"-0.1031832","lat":"51.520334"}}},{"geometry":{"lng":"-0.10189816692463","lat":"51.52010815"},"components":{"country":"United Kingdom","county":"London","city":"London Borough of Islington","suburb":"Clerkenwell","bar":"Vinoteca","state":"England","country_code":"gb","postcode":"EC1M 6DS","road":"St John Street","state_district":"Greater London"},"bounds":{"southwest":{"lat":"51.5200688","lng":"-0.1019647"},"northeast":{"lng":"-0.1018282","lat":"51.5201475"}},"annotations":{},"formatted":"St John Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Vinoteca"},{"bounds":{"northeast":{"lng":"-0.1025795","lat":"51.5203565"},"southwest":{"lat":"51.5201568","lng":"-0.1028115"}},"annotations":{},"formatted":"Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Eagle Court, Itsu","geometry":{"lat":"51.52025105","lng":"-0.102689887248214"},"components":{"county":"London","country":"United Kingdom","footway":"Eagle Court","suburb":"Clerkenwell","city":"London Borough of Islington","state":"England","state_district":"Greater London","convenience":"Itsu","postcode":"EC1M 6DS","country_code":"gb"}},{"bounds":{"southwest":{"lat":"51.5200237","lng":"-0.1021637"},"northeast":{"lat":"51.5201325","lng":"-0.101997"}},"formatted":"La Cucina, Cowcross Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","annotations":{},"geometry":{"lat":"51.5201049","lng":"-0.102096400438596"},"components":{"county":"London","country":"United Kingdom","suburb":"Clerkenwell","city":"London Borough of Islington","state":"England","restaurant":"La Cucina","road":"Cowcross Street","state_district":"Greater London","postcode":"EC1M 6DS","country_code":"gb"}},{"components":{"county":"London","country":"United Kingdom","suburb":"Clerkenwell","city":"London Borough of Islington","house_number":"1","state":"England","restaurant":"Attilio","road":"Cowcross Street","state_district":"Greater London","postcode":"EC1M 6DS","country_code":"gb"},"geometry":{"lat":"51.5200198","lng":"-0.102031280449194"},"annotations":{},"formatted":"Attilio, 1, Cowcross Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","bounds":{"southwest":{"lng":"-0.1021076","lat":"51.5199807"},"northeast":{"lat":"51.5200641","lng":"-0.101955"}}},{"components":{"country":"United Kingdom","county":"London","fast_food":"Subway","city":"London Borough of Islington","suburb":"Clerkenwell","state":"England","country_code":"gb","postcode":"EC1M 6DS","road":"Cowcross Street","state_district":"Greater London"},"geometry":{"lat":"51.5201184","lng":"-0.102195063884225"},"annotations":{},"formatted":"Cowcross Street, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb, Subway","bounds":{"southwest":{"lng":"-0.1022353","lat":"51.5200776"},"northeast":{"lat":"51.5201834","lng":"-0.102152"}}},{"annotations":{},"formatted":"EAT., Greenhill Rents, Clerkenwell, London Borough of Islington, London, EC1M 6DS, Greater London, England, United Kingdom, gb","bounds":{"southwest":{"lng":"-0.1024206","lat":"51.5199315"},"northeast":{"lat":"51.5200315","lng":"-0.1023206"}},"components":{"country_code":"gb","postcode":"EC1M 6DS","road":"Greenhill Rents","state_district":"Greater London","state":"England","city":"London Borough of Islington","suburb":"Clerkenwell","country":"United Kingdom","county":"London","cafe":"EAT."},"geometry":{"lat":"51.5199815","lng":"-0.1023706"}}],"status":{"code":200,"message":"OK"},"thanks":"For using an OpenCage Data API","timestamp":{"created_unix":1402130114,"created_http":"Sat, 07 Jun 2014 08:35:14 GMT"},"we_are_hiring":"http://lokku.com/#jobs","total_results":10,"rate":{"limit":"2500","reset":1402185600,"remaining":2494},"licenses":[{"url":"http://creativecommons.org/licenses/by-sa/3.0/","name":"CC-BY-SA"},{"url":"http://opendatacommons.org/licenses/odbl/summary/","name":"ODbL"}]}'
        )
        #'

        results = self.geocoder.geocode("EC1M 6DS")
        self.assertTrue(
            any((abs(result['geometry']['lat'] - 51.5201666) < 0.05 and abs(result['geometry']['lng'] - -0.0985142) < 0.05) for result in results),
            msg="Bad result"
        )


#"Mudgee, Australia" => [ -32.5980702, 149.5886383 ],
#"EC1M 5RF"          => [  51.5201666,  -0.0985142 ],

## Encoding in request
#"Münster"           => [  51.9625101,   7.6251879 ],

## Encoding in response
#"Donostia"          => [   43.300836,  -1.9809529 ],

class FloatifyDictTestCase(unittest.TestCase):
    def _expected_output(input_value, expected_output):
        def test(self):
            self.assertEquals(floatify_latlng(input_value), expected_output)
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
