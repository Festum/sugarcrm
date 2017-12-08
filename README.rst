========
SugarCRM
========

Python client for SugarCRM API.

.. image:: http://img.shields.io/pypi/l/sugarcrm.svg
    :target: https://github.com/festum/sugarcrm/blob/master/LICENSE


Example Usage
-------------

.. code-block:: python

    import sugarcrm

    # Connect
    url = "http://your-sugarcrm-domain/service/v4/rest.php"
    session = sugarcrm.Session(url, username, password)

    # Create a new note
    note = sugarcrm.Note(name="Test Note")

    # Save note
    session.set_entry(note)

    # Add attachment to note
    session.set_note_attachment(note, "sugarcrm.py")

    # Query for all notes that have a name that begins with "Test"
    note_query = sugarcrm.Note(name="Test%")
    results = session.get_entry_list(note_query)

    # Query for all contacts with the first name "Mylee"
    contact_query = sugarcrm.Contact(first_name="Mylee")
    results = session.get_entry_list(contact_query)

    # Get the email address for the user assigned to an Opportunity
    op = session.get_entry("Opportunities", "82f72939-735e-53a2-0944-5418c4edae2a")
    user = session.get_entry("Users", op.assigned_user_id)
    print user.email1

    # Change the status of an Opportunity
    op = sugarcrm.Opportunity(id="82f72939-735e-53a2-0944-5418c4edae2a")
    op.sales_stage = "Approved"
    session.set_entry(op)

    # Extract all non-empty email fields from all Contacts in SugarCRM
    emails = set()
    contact_query = sugarcrm.Contact()  # No filters provider finds all objects
    contact_count = session.get_entries_count(contact_query, deleted=True)
    print "Extracting emails from %d Contacts" % contact_count
    # Grab 100 Contact objects at a time from SugarCRM
    for offset in range(0, count, 100):
        contacts = session.get_entry_list(contact_query, deleted=True,
                                        max_results=100, offset=offset)
        for contact in contacts:
            for field in dir(contact):
                if field.find("email") >= 0 and getattr(contact, field, "").find("@") >= 0:
                    emails.add(getattr(contact, field).lower())
    print "Found %d emails" % len(emails)


Install
-------

The latest stable version can always be installed or updated via pip:

.. code-block:: bash

    $ pip install git+https://github.com/festum/sugarcrm.git


Session Object
--------------

class sugarcrm.Session(url, username, password, app="Python", lang="en_us", verify=True)
    The main class used to connect to the SugarCRM API and make requests with.

.. code-block:: python

    url = "http://your-sugarcrm-domain/service/v4/rest.php"
    session = sugarcrm.Session(url, username, password)

The **verify** parameter is passed directly to the python-requests library that is used to make HTTP POST requests to the SugarCRM API. Read more about this parameter from the python-requests documentation: http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification


Available Methods
-----------------

get_available_modules(filter="default")
    Retrieves a list of available modules in the system.
    Possible filter values: "default", "mobile", "all"

.. code-block:: python

    modules = session.get_available_modules()
    for m in modules:
        print m.module_key

get_entry(module, object_id, links={}, track_view=False)
    Retrieves a single object based on object ID.

.. code-block:: python

    note = session.get_entry("Notes", "f0c78aab-e051-174a-12aa-5439a7146977")
    print note.name

    # Get a lead and specific fields from linked contacts in one query
    links = {'Contacts': ['id', 'first_name', 'last_name']}
    lead = session.get_entry("Leads", "d7dac88d-ce33-d98a-da8b-5418bba9e664",
                           links=links)
    for c in lead.contacts:
        print c.id, c.first_name, c.last_name

get_entries(module, object_ids, track_view=False)
    Retrieves a list of objects based on specified object IDs.

.. code-block:: python

    ids = [
        "f0c78aab-e051-174a-12aa-5439a7146977",
        "32f02fj2-4ggn-4nnf-fs33-f3fh3f93n333",
        "82f72939-735e-53a2-0944-5418c4edae2a",
    ]
    notes = session.get_entries("Notes", ids)
    for note in notes:
        print note.name

get_entries_count(query_object, deleted=False)
    Retrieves a count of beans based on query specifications.

.. code-block:: python

    # Get a count of all Contacts with a first name of "Fred"
    # and include Contacts that have been deleted
    contact_query = sugarcrm.Contact(first_name="Fred")
    contacts = session.get_entries_count(contact_query, deleted=True)
    for contact in contacts:
        print contact.first_name, contact.last_name

get_entry_list(query_object, fields=[], links={}, order_by="", max_results=0, offset=0, deleted=False, favorites=False)
    Retrieves a list of objects based on query specifications.

.. code-block:: python

    # Get a list of all Notes with a name that begins with "Test"
    note_query = sugarcrm.Note(name="Test%")
    notes = session.get_entry_list(note_query)
    for note in notes:
        print note.name

    # Get a list of all Opportunities created since Sept 1, 2014 and include
    # data about link contacts with each Opportunitity returned
    q = sugarcrm.Opportunity()
    q.query = "opportunities.date_entered > '2014-09-01'"
    links = {'Contacts': ['id', 'first_name', 'last_name']}
    results = session.get_entry_list(q, links=links)
    for o in results:
        for c in o.contacts:
            print o.id, c.id, c.first_name, c.last_name

login(username, password, app="Python", lang="en_us")
    Logs a user into the SugarCRM application.

set_document_revision(document, file)
    Creates a new document revision for a specific document record.

.. code-block:: python

    doc = sugarcrm.Document(document_name="Test Doc", revision=1)
    session.set_entry(doc)
    session.set_document_revision(doc, "/path/to/test.pdf")


set_entry(sugar_object)
    Creates or updates a specific object.

.. code-block:: python

    note = sugarcrm.Note()
    note.name = "Test Note"
    note.assigned_user_id = "82f72939-735e-53a2-0944-5418c4edae2a"
    session.set_entry(note)
    print note.id


set_entries()
    Creates or updates specific objects.

.. code-block:: python

    note = sugarcrm.Note()
    note.name = "Test Note"
    note.assigned_user_id = "82f72939-735e-53a2-0944-5418c4edae2a"
    session.set_entries([note, ])
    print note[0].id


set_note_attachment(note, attachment)
    Creates an attachmentand associates it to a specific note object.

.. code-block:: python

    with open("test1.pdf") as pdf_file:
        session.set_note_attachment(note1, pdf_file)
    session.set_note_attachment(note2, "test2.pdf")
    print note1.filename, note2.filename

set_relationship(parent, child, delete=False)
    Sets the relationships between two records.

.. code-block:: python

    doc = sugarcrm.Document(document_name="Test Doc", revision=1)
    session.set_entry(doc)
    session.set_document_revision(doc, "/path/to/test.pdf")
    opportunity = session.get_entry("Opportunities", "5b671886-cfe4-36f5-fa9d-5418a24e4aca")
    session.set_relationship(opportunity, doc)

set_relationships(module_collection)
    Sets relationships between pair of records.

.. code-block:: python

    doc1 = sugarcrm.Document(document_name="Test Doc", revision=1)
    session.set_entry(doc1)
    session.set_document_revision(doc1, "/path/to/test.pdf")
    doc2 = sugarcrm.Document(document_name="Test Doc", revision=1)
    session.set_entry(doc2)
    session.set_document_revision(doc2, "/path/to/test.pdf")
    module_collection = [{
        'table': [
            'Opportunities',
            'documents'
        ],
        'map': {
            '5b671886-cfe4-36f5-fa9d-5418a24e4aca':[
                doc1.id, 
                doc2.id
            ]
        }
        'delete': True
    }]
    session.set_relationship(module_collection)


Unavailable Methods
-------------------

.. _issue: https://github.com/festum/sugarcrm/issues

The following lesser-used SugarCRM API methods have not been included in this
library yet. Please open an issue_ if you require any of these methods and I
would be more than happy to implement them!

get_document_revision()
    Method not implemented yet.

get_language_definition()
    Method not implemented yet.

get_last_viewed()
    Method not implemented yet.

get_modified_relationships()
    Method not implemented yet.

get_module_fields()
    Method not implemented yet.

get_module_fields_md5()
    Method not implemented yet.

get_module_layout()
    Method not implemented yet.

get_note_attachment()
    Method not implemented yet.

get_quotes_pdf()
    Method not implemented yet.

get_relationships()
    Method not implemented yet.

get_report_entries()
    Method not implemented yet.

get_report_pdf()
    Method not implemented yet.

get_server_info()
    Method not implemented yet.

get_upcoming_activities()
    Method not implemented yet.

get_user_id()
    Method not implemented yet.

get_user_team_id()
    Method not implemented yet.

job_queue_cycle()
    Method not implemented yet.

job_queue_next()
    Method not implemented yet.

job_queue_run()
    Method not implemented yet.

logout()
    Method not implemented yet.

oauth_access()
    Method not implemented yet.

seamless_login()
    Method not implemented yet.

search_by_module()
    Method not implemented yet.

set_campaign_merge()
    Method not implemented yet.

snip_import_emails()
    Method not implemented yet.

snip_update_contacts()
    Method not implemented yet.


SugarCRM Objects
----------------

.. code-block:: python

    >>> call = sugarcrm.Call()
    >>> print call.module
    "Calls"

    >>> campaign = sugarcrm.Campaign()
    >>> print campaign.module
    "Campaigns"

    >>> contact = sugarcrm.Contact()
    >>> print contact.module
    "Contacts"

    >>> document = sugarcrm.Document()
    >>> print document.module
    "Documents"

    >>> email = sugarcrm.Email()
    >>> print email.module
    "Emails"

    >>> lead = sugarcrm.Lead()
    >>> print lead.module
    "Leads"

    >>> module = sugarcrm.Module()
    >>> print module.module
    "Modules"

    >>> note = sugarcrm.Note()
    >>> print note.module
    "Notes"

    >>> opportunity = sugarcrm.Opportunity()
    >>> print opportunity.module
    "Opportunities"

    >>> product = sugarcrm.Product()
    >>> print product.module
    "Products"

    >>> prospect = sugarcrm.Prospect()
    >>> print prospect.module
    "Prospects"

    >>> prospect_list = sugarcrm.ProspectList()
    >>> print prospect_list.module
    "ProspectLists"

    >>> quote = sugarcrm.Quote()
    >>> print quote.module
    "Quotes"

    >>> report = sugarcrm.Report()
    >>> print report.module
    "Reports"

    >>> user = sugarcrm.User()
    >>> print user.module
    "Users"


Contributions
-------------

.. _issues: https://github.com/festum/sugarcrm/issues
.. __: https://github.com/festum/sugarcrm/pulls

Issues_ and `Pull Requests`__ are always welcome.


License
-------

.. __: https://github.com/festum/sugarcrm/raw/master/LICENSE

Code and documentation are available according to the MIT License
(see LICENSE__).
