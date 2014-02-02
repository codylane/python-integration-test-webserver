import integration_webserver.integration_webserver as intweb
from integration_webserver.integration_webserver import MyHTTPServer
import os
import sys
import signal
from socket import gaierror
from nose.tools import raises, istest, nottest
from nose_parameterized import parameterized
from mock import patch

@nottest
def capture_stdout(callback, out=sys.stdout, *callback_args):
    from StringIO import StringIO
    saved_stdout = out
    try:
        out = StringIO()
        sys.stdout = out
        if callback_args:
            callback(callback_args)
        else:
            callback()
        output = out.getvalue().strip()
        return output
    finally:
        print('exception occured in capture_stdout')
        sys.stdout = saved_stdout

def is_module_present(name):
    v = intweb.__dict__.get(name)
    if v.__class__.__name__ == 'module': return True
    return False

def test_get_execution_path_should_not_return_current_working_dir():
    cur_path = os.getcwd()
    run_path = os.path.dirname(os.path.abspath(intweb.__file__))
    rval_path = intweb.get_execution_path()
    assert rval_path, 'Expected get_execution_path() to not return "%s"' %(rval_path)
    assert cur_path != run_path, 'Expected current directory %s should not be %s' %(cur_path, run_path)
    assert run_path == intweb.get_execution_path()

def test_LISTEN_global_variable_is_set_to_loopback():
    expected = '0.0.0.0'
    assert intweb.LISTEN == expected, 'Expected LISTEN global variable to be set to "%s", not "%s"' %(expected, intweb.LISTEN)

def test_PORT_global_variable_is_set_to_48000():
    expected = 48000
    assert isinstance(intweb.PORT, int), 'Expected PORT global variable to be an integer, not "%s"' %(type(intweb.PORT))
    assert intweb.PORT == expected, 'Expected PORT global variable to be set to "%s", not "%s"' %(expected, intweb.PORT)

def test_PIDFILE_global_variable_is_set_to_path_where_script_is_invoked_from_plus_webserver_dot_pid():
    run_dir = intweb.get_execution_path()
    expected = run_dir + '/webserver.pid'
    actual = intweb.PIDFILE
    assert run_dir, 'Expected get_execution_path() to not return "%s"' %(run_dir)
    assert actual == expected, 'Expected PIDFILE global variable to be set to "%s" not "%s"' %(expected, actual)

def test_STDOUT_LOG_global_variable_is_set_to_path_where_script_is_invoked_from_plus_stdout_dot_log():
    run_dir = intweb.get_execution_path()
    expected = run_dir + '/stdout.log'
    actual = intweb.STDOUT_LOG
    assert run_dir, 'Expected get_execution_path() to not return "%s"' %(run_dir)
    assert actual == expected, 'Expected STDOUT_LOG global variable to be set to "%s" not "%s"' %(expected, actual)

def test_STDERR_LOG_global_variable_is_set_to_path_where_script_is_invoked_from_plus_stderr_dot_log():
    run_dir = intweb.get_execution_path()
    expected = run_dir + '/stderr.log'
    actual = intweb.STDERR_LOG
    assert run_dir, 'Expected get_execution_path() to not return "%s"' %(run_dir)
    assert actual == expected, 'Expected STDERR_LOG global variable to be set to "%s" not "%s"' %(expected, actual)

@istest
class Endpoint:
    def test_when_printing_the_object_instance_should_return_special_formatted_string(self):
        endpoint = intweb.Endpoint('/foobar', 30)
        expected_val = 'Class=%s path=%s value=%s callback=%s' %('Endpoint', '/foobar', 30, None)
        actual = str(endpoint)
        assert actual == expected_val, 'Expected __str__ method to return "%s" not "%s"' %(expected_val, actual)

    @raises(TypeError)
    def test_constructor_requires_one_arguments(self):
        endpoint = intweb.Endpoint()

    def test_constructor_default_value_set_to_None_and_callback_value_set_to_None_when_passed_one_argument(self):
        endpoint = intweb.Endpoint('/foo')
        assert endpoint.value is None, 'Expected that when passing only one ' \
                'argument to Endpoint constructor, that argument "value" ' \
                'has a default value set to None. ' \
                'Instead value is set to "%s"' %(endpoint.value)
        assert endpoint.callback is None, 'Expected that when passing only ' \
                'argument to Endpoint constructor, that  argument "callback" ' \
                'has a default value set to None. ' \
                'Instead callback is set to "%s"' %(endpoint.callback)

@istest
class MyHTTPServer():

    @raises(TypeError)
    def test_constructor_should_raise_TypeError_when_port_is_not_an_integer(self):
        srv = intweb.MyHTTPServer(port='48002')
        srv.server_close()

    @parameterized.expand([
        ('1.2,3,4', ),
        ('non-nslookup-hostname', )
    ])
    @raises(gaierror)
    def test_constructor_should_raise_gaierror_when_host_argument_can_not_be_resolved(self, invalid):
        srv = intweb.MyHTTPServer(host=invalid)
        srv.server_close()

    @parameterized.expand([
        ('', ),
        ('0.0.0.0', ),
    ])
    def test_constructor_listen_argument_should_not_raise_error_with_valid_values(self, listen):
        srv = intweb. MyHTTPServer(host=listen)
        srv.server_close()

    def test_constructor_uses_default_values_when_no_arguments_given(self):
        import socket
        hostname = socket.gethostname()
        fqdn = socket.gethostbyaddr(hostname)[0]
        srv = intweb.MyHTTPServer()
        srv.server_close()
        assert fqdn == srv.server_name, \
                'Expected that server_name be ' \
                'set to "%s" not "%s"' %(fqdn, srv.server_name)
        assert srv.server_port == intweb.PORT, \
                'Expected that port be set to "%s" not "%s"' \
                %(srv.server_port, intweb.PORT)

    def test_constructor_handler_argument_is_a_BaseHTTPRequestHandler_instance(self):
            srv = intweb.MyHTTPServer()
            actual_handler = srv.RequestHandlerClass.__name__
            srv.server_close()
            expected = 'MyHandler'
            assert actual_handler == expected, 'Expected handler to ' \
                    'return string "%s" not "%s"' %(expected, actual_handler)

    def test_constructor_sets_up_a_empty_dictionary_named_underscore_endpoints(self):
            srv = intweb.MyHTTPServer()
            actual = srv._endpoints
            srv.server_close()
            expected = {}
            assert actual == expected, 'Expected that _endpoints be an ' \
                    'empty dictionary, not "%s"' %(actual)

    def test_constructor_creates_a_SignalHandler_reference_named_underscore_sig_handler(self):
        srv = intweb.MyHTTPServer()
        actual = srv._sig_handler 
        srv.server_close()
        expected_class = intweb.SignalHandler
        assert actual, 'Expected that SignalHandler instance _sig_handler ' \
                'not be "%s"' %(actual)
        assert isinstance(actual, expected_class), 'Expected _sig_handler ' \
                'to be "%s" type not "%s"' %(expected_class, type(actual))

    def test_constructor_should_register_default_signals(self):
        srv = intweb.MyHTTPServer()
        srv.server_close()
        actual = srv._sig_handler.getActions()
        assert actual, 'Expected that the construtor would initialize some ' \
                'default signals to the _signal_handler ' \
                'instance, instead got "%s"' %(actual)

    def test_endpoint_returns_empty_dictionary_when_instance_is_first_created(self):
        srv = intweb.MyHTTPServer()
        srv.server_close()
        actual = srv.endpoints()
        expected = {}
        assert actual == expected, 'Expected that endpoints() to return "%s" ' \
                'when instance is first ' \
                'initialized, not "%s"' %(expected, actual)

    @parameterized.expand([
        ('/foobar', 30, None),
    ])
    def test_endpoint_returns_non_empty_dictionary_when_endpoints_are_registered(self, path, value, callback):
        srv = intweb.MyHTTPServer()
        srv.register_endpoint(path, value, callback)
        srv.server_close()
        actual = srv.endpoints()
        assert actual, 'Expected endpoints() to return a ' \
                'non-empty dictionary when an endpoint is ' \
                'registered, instead got "%s"' %(actual)
        assert isinstance(actual, dict), 'Expected that endpoints() to return ' \
                'a dictionary, when an endpoint is registered, ' \
                'got "%s" instead' %(type(actual))
        assert path in actual, 'Expected that endpoints() to contain the path ' \
                '"%s" as a key, when the endpoint "%s" is registered, instead ' \
                'endpoints contains "%s"' %(path, path, actual.keys())
        actual_endpoint = actual.get(path)
        assert actual_endpoint, 'Expected that endpoints()[%s] ' \
                'to not be "%s"' %(path, actual_endpoint)
        assert actual_endpoint.path == path, 'Expected registered endpoint ' \
                'path to be "%s" not "%s"' %(path, actual_endpoint.path)
        assert actual_endpoint.value == value, 'Expected registered endpoint ' \
                'value to be "%s" not "%s"' %(value, actual_endpoint.value)
        assert actual_endpoint.callback == callback, 'Expected registered ' \
                'endpoint callback to be "%s" not "%s"' \
                %(callback, actual_endpoint.callback)

    def test_register_default_sig_handlers_to_register_three_default_SignalHandler_instaces(self):
        # register_default_sig_handlers is called by the constructor so this method
        # should have already been called, but we will invoke it anyway just to be
        # safe.
        srv = intweb.MyHTTPServer()
        srv.register_default_sig_handlers()
        srv.server_close()
        expected_reg_count = 3
        actual_actions = srv._sig_handler.getActions()
        actual_reg_count = len(actual_actions)
        assert actual_reg_count == expected_reg_count, 'Expected that ' \
                'register_default_sig_handlers to contain ' \
                '"%s" entries not "%s"' %(expected_reg_count, actual_reg_count)
        # we explicitly set this, because we don't know if the order to which
        # registered signals will be added or changed.  We defined this here
        # to keep track of what signals are defined.
        should_find_actions = {
            str(signal.SIGTERM) : 0,
            str(signal.SIGINT)  : 0,
            str(signal.SIGUSR1) : 0
        }
        # loop through all the defualt registered signals and updated the 
        # reference counters for any that match. 
        for action in actual_actions:
            key = str(action.signum)
            value = should_find_actions.get(key)
            if value == 0:
                should_find_actions[key] = 1
        # If value != 1 then one of the default signals is not registered
        for key, value in should_find_actions.items():
            assert value == 1, 'Expected that signal "%s" be registered as ' \
                    'a default when register_default_sig_handlers() ' \
                    'is called' %(key)

    def test_list_endpoints_return_None(self):
        srv = intweb.MyHTTPServer()
        actual = srv.list_endpoints()
        srv.server_close()
        assert actual is None, 'Expected that list_endpoints() to return None, not "%s"' %(actual)

    def test_list_endpoints_displays_endpoints_to_stdout(self):
        srv = intweb.MyHTTPServer()
        srv.register_endpoint('/foobar', 30)
        srv.register_endpoint('/foobar_nation', 31)
        actual = capture_stdout(srv.list_endpoints)
        srv.server_close()
        assert actual.find("listing endpoint:") >= 0, 'Expected that stdout contain: "listening endpoint" but got "%s" instead' %(actual)

    @patch.object(intweb.MyHTTPServer, 'run', return_value=None)
    def test_run_is_called_once(self, mock_method):
        srv = intweb.MyHTTPServer()
        srv.run()
        srv.server_close()
        assert mock_method.call_count == 1, 'Expected that run() be ' \
                'called at leaset once, instead it was ' \
                'called "%s" times' %(mock_method.call_count)

    @patch.object(intweb.MyHTTPServer, 'run', return_value=None)
    @raises(Exception)
    def test_run_is_called_twice_and_raises_Exception(self, mock_method):
        srv = intweb.MyHTTPServer()
        srv.run()
        srv.server_close()
        mock_method.side_effect = Exception
        srv.run()
        srv.server_close()

    @raises(TypeError)
    def  test_register_endpoint_requires_one_argument_when_called_which_should_raise_TypeError(self):
        srv = intweb.MyHTTPServer()
        srv.server_close()
        srv.register_endpoint()

    def test_register_endpoint_should_not_register_endpoint_when_path_is_None(self):
        srv = intweb.MyHTTPServer()
        srv.server_close()
        srv.register_endpoint(None)
        actual_endpoints = srv.endpoints()
        assert not actual_endpoints, 'Expected when register_endpoint(path=%s) should not register this endpoint, instead "%s" endpoint(s) are registered' %(None, actual_endpoints)
        assert 'None' not in actual_endpoints, 'Expected that "%s" to not be in endpoints, but endpoints current has "%s"' %(None, actual_endpoints)

    def test_register_endpoint_default_argument_return_value_set_to_None(self):
        assert False

    def test_register_endpoint_default_argument_callback_set_to_None(self):
        assert False

    def test_register_endpoint_registers_Endpoint_objects(self):
        assert False

