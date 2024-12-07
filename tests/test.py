import unittest
from requests import get, post


class TestApp(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://127.0.0.1:57424/api'

    def test_ping(self):
        url = self.base_url + '/ping'
        self.assertEqual(get(url).status_code, 200)

    def test_all_countries(self):
        url = self.base_url + '/countries'
        self.assertEqual(get(url).status_code, 200)

    def test_all_countries_by_region(self):
        url = self.base_url + '/countries?region=Europe&region=Africa'
        self.assertEqual(get(url).status_code, 200)

    def test_countries_by_alpa2(self):
        url = self.base_url + '/countries/RU'
        self.assertEqual(get(url).status_code, 200)

    def test_countries_by_not_existing_alpha2(self):
        url = self.base_url + '/countries/RUR'
        self.assertEqual(get(url).status_code, 404)

    def test_registration_0(self):
        """With no login"""
        url = self.base_url + '/auth/register'
        params = {
            'login': '',
            'email': 'yellowstone19801@you.ru',
            'password': '$aba4821FWfew01#.fewA$',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_1(self):
        """With no email"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon',
            'email': '',
            'password': '$aba4821FWfew01#.fewA$',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_2(self):
        """With no password"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': '',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_3(self):
        """With no country code"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'jdfhgjdfg',
            'countryCode': '',
            'isPublic': True,
            'phone': '+74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_4(self):
        """With not existing country code"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'jdfhgjdfg',
            'countryCode': 'RUR',
            'isPublic': True,
            'phone': '+74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_5(self):
        """With wrong phone"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'jdfhgjdfg',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '74951239922'

        }
        self.assertEqual(post(url, json=params).status_code, 400)


    def test_registration_6(self):
        """With too long image"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'jdfhgjdfg',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922',
            'image': 'a' * 300

        }
        self.assertEqual(post(url, json=params).status_code, 400)

    def test_registration_7(self):
        """With existing email"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'yellowstone1980@you.ru',
            'password': 'jdfhgjdfg',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922',

        }
        self.assertEqual(post(url, json=params).status_code, 409)


    def test_registration_8(self):
        """With existing login"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'yellowMonkey2',
            'email': 'mon1',
            'password': 'jdfhgjdfg',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922',

        }
        self.assertEqual(post(url, json=params).status_code, 409)


    def test_registration_9(self):
        """With too short password"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'jdfh',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922',

        }
        resp = post(url, json=params)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['reason'], 'length error')



    def test_registration_10(self):
        """With no latin syms in password"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': '123456789',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        resp = post(url, json=params)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['reason'], 'no latin symbols')



    def test_registration_11(self):
        """With no numbers in password"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'abcdefgksfjg',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        resp = post(url, json=params)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['reason'], 'no numbers')


    def test_registration_successful(self):
        """Success"""
        url = self.base_url + '/auth/register'
        params = {
            'login': 'mon1',
            'email': 'mon1',
            'password': 'abcdefgksfjg1',
            'countryCode': 'RU',
            'isPublic': True,
            'phone': '+74951239922'

        }
        resp = post(url, json=params)
        self.assertEqual(resp.status_code, 201)
