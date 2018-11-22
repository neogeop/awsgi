# -*- coding: utf-8 -*-
from io import StringIO
import sys
import unittest
try:
    # Python 3
    from urllib.parse import urlencode

    # Convert bytes to str, if required
    def convert_str(s):
        return s.decode('utf-8') if isinstance(s, bytes) else s
except:
    # Python 2
    from urllib import urlencode

    # No conversion required
    def convert_str(s):
        return s
import awsgi


class TestAwsgi(unittest.TestCase):
    def compareStringIOContents(self, a, b, msg=None):
        a_loc = a.tell()
        b_loc = b.tell()
        a.seek(0)
        b.seek(0)
        if a.read() != b.read():
            raise self.failureException(msg)
        a.seek(a_loc)
        b.seek(b_loc)

    def test_environ(self):
        event = {
            'httpMethod': 'TEST',
            'path': '/test',
            'queryStringParameters': {
                'test': '✓',
            },
            'multiValueQueryStringParameters': {
                'test': ['✓'],
            },
            'body': u'test',
            'headers': {
                'X-test-suite': 'testing',
                'Content-type': 'text/plain',
                'Host': 'test',
                'X-forwarded-for': 'first, second',
                'X-forwarded-proto': 'https',
                'X-forwarded-port': '12345',
            },
        }
        expected = {
            'REQUEST_METHOD': event['httpMethod'],
            'SCRIPT_NAME': '',
            'PATH_INFO': event['path'],
            'QUERY_STRING': urlencode(event['multiValueQueryStringParameters'], doseq=True),
            'CONTENT_LENGTH': str(len(event['body'])),
            'HTTP': 'on',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.input': StringIO(event['body']),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'CONTENT_TYPE': event['headers']['Content-type'],
            'HTTP_CONTENT_TYPE': event['headers']['Content-type'],
            'SERVER_NAME': event['headers']['Host'],
            'HTTP_HOST': event['headers']['Host'],
            'REMOTE_ADDR': event['headers']['X-forwarded-for'].split(', ')[0],
            'HTTP_X_FORWARDED_FOR': event['headers']['X-forwarded-for'],
            'wsgi.url_scheme': event['headers']['X-forwarded-proto'],
            'HTTP_X_FORWARDED_PROTO': event['headers']['X-forwarded-proto'],
            'SERVER_PORT': event['headers']['X-forwarded-port'],
            'HTTP_X_FORWARDED_PORT': event['headers']['X-forwarded-port'],
            'HTTP_X_TEST_SUITE': event['headers']['X-test-suite'],
        }
        result = awsgi.environ(event, object())
        self.addTypeEqualityFunc(StringIO, self.compareStringIOContents)
        for k, v in result.items():
            self.assertEqual(v, expected[k])
