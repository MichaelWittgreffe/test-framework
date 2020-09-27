from .base_request_runner import RequestRunner
from .example_request_runner import ExampleRequestRunner


def request_factory(protocol, auth_url, username, password):
    """
    factory for creating request runner classes. Custom auth hooks can be added by changing the protocol in the test
    e.g: 'http' becomes 'http_openstack' or similar - They MUST all contain the verb 'http' to be supported as HTTP
        requests
    """
    protocol = protocol.lower()

    if protocol == "http":
        return RequestRunner(auth_url=auth_url, username=username, password=password)
    elif protocol == "http_example":
        return ExampleRequestRunner(auth_url=auth_url, username=username, password=password)
    else:
        raise ValueError("Protocol " + protocol + " Not Supported")
