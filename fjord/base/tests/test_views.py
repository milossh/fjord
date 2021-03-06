from django.test.utils import override_settings

from nose.tools import eq_

from fjord.base import views
from fjord.base.tests import LocalizingClient, reverse
from fjord.base.views import IntentionalException
from fjord.search.tests import ElasticTestCase


# Note: This needs to be an ElasticTestCase because the view does ES
# stuff.
class MonitorViewTest(ElasticTestCase):
    client_class = LocalizingClient

    def test_monitor_view(self):
        """Tests for the monitor view."""
        # TODO: When we add a mocking framework, we can mock this
        # properly.
        test_memcached = views.test_memcached
        try:
            with self.settings(
                # Note: tower dies if we don't set SETTINGS_MODULE.
                SETTINGS_MODULE='fjord.settings',
                CACHES={
                    'default': {
                        'BACKEND': 'caching.backends.memcached.CacheClass',
                        'LOCATION': ['localhost:11211', 'localhost2:11211']
                        }
                    }):

                # Mock the test_memcached function so it always returns
                # True.
                views.test_memcached = lambda host, port: True

                # TODO: Replace when we get a mock library.
                def mock_rabbitmq():
                    class MockRabbitMQ(object):
                        def connect(self):
                            return True
                    return lambda *a, **kw: MockRabbitMQ()
                views.establish_connection = mock_rabbitmq()

                # Request /services/monitor and make sure it returns
                # HTTP 200 and that there aren't errors on the page.
                resp = self.client.get(reverse('services-monitor'))
                errors = [line for line in resp.content.splitlines()
                          if 'ERROR' in line]

                eq_(resp.status_code, 200, '%s != %s (%s)' % (
                        resp.status_code, 200, repr(errors)))

        finally:
            views.test_memcached = test_memcached


class ErrorTesting(ElasticTestCase):
    client_class = LocalizingClient

    def test_404(self):
        request = self.client.get('/a/path/that/should/never/exist')
        eq_(request.status_code, 404)
        self.assertTemplateUsed(request, '404.html')

    @override_settings(SHOW_STAGE_NOTICE=True, SETTINGS_MODULE='fjord.settings')
    def test_500(self):
        with self.assertRaises(IntentionalException) as cm:
            self.client.get('/services/throw-error')

        eq_(type(cm.exception), IntentionalException)
