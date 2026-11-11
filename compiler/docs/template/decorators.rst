Decorators
==========

Decorators are able to register callback functions for handling updates in a much easier and cleaner way compared to
:doc:`Handlers <handlers>`; they do so by instantiating the correct handler and calling
:meth:`~pyrogram.Client.add_handler` automatically. All you need to do is adding the decorators on top of your
functions.

.. code-block:: python

    from pyrogram import Client

    app = Client("my_account")


    @app.on_message()
    def log(client, message):
        print(message)


    app.run()

-----

.. currentmodule:: pyrogram

Index
-----

.. hlist::
    :columns: 3

    {decorators_hlist}

-----

Details
-------

.. Decorators
{decorators_details}
