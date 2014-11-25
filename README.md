testmagic
=========

Embedded system automation test framework

Run example
-----------

#. Move into the example and do a `syncdb`::

    $ python manage.py syncdb #be sure to create an admin user


#. Move up one directory and run the example::

    $ twistd -ny server.py #open localhost:8000 in browser

#. If you decide to build an application with this server and deploy it, you can start the server as a daemon with::

    $ twistd -y server.py #remember to change the port in server.py to choose an open port in your server.
