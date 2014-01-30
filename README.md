python-integration-test-webserver
=================================

A small little webserver library that can be used for integration testing all written in python.  

When the integration webserver is executed it will fire up a listener that allows you to register endpoints and callbacks to specific endpoints.  When the endpoints are hit from a client, the registered callback is executed so that you have full control of what you are testing.  

This is still a work in progress and still needs lots of time to sort out.

cloning
=======
When cloning this repo, make sure to rename (removing the dashes) otherwise the python interpreter will complain about not being able to find module paths.
