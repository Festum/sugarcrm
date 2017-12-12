#  SugarCRM
#  --------
#  Python client for SugarCRM API.
#
#  Authors:  Festum <festum@g.pl>
#  Website: https://github.com/Festum/sugarcrm
#  Forked: https://github.com/ryanss/sugarcrm
#  License: MIT (see LICENSE file)
#  Version: 0.1.4 (Dec 12, 2017)

__version__ = '0.1.4'

import base64
import hashlib
import json
import os
import sys
import requests


class Session(object):

    def __init__(self,
                 url,
                 username,
                 password,
                 app="Python",
                 lang="en_us",
                 verify=True):
        self.url = url
        self.username = username
        self.application = app
        self.language = lang
        self.verify = verify
        result = self.login(username, password)
        self.session_id = result['id']

    def _request(self, method, params):
        data = {
            'method': method,
            'input_type': "JSON",
            'response_type': "JSON",
            'rest_data': json.dumps(params),
        }
        r = requests.post(self.url, data=data, verify=self.verify)
        if r.status_code == 200:
            return json.loads(r.text.replace("&#039;", "'"))
        raise SugarError("SugarCRM API _request returned status code %d (%s)" %
                         (r.status_code, r.reason))

    def get_module_class(self, module_class='Leads'):
        """Return custom module with Class."""
        module_class = module_class.title() if module_class.islower(
        ) else module_class

        class module_class(SugarObject):
            module = module_class
            fields = {}

        return module_class

    def get_available_modules(self, filter="default", get_key=False):
        """Retrieves a list of available modules in the system."""
        data = [self.session_id, filter]
        modules = self._request('get_available_modules', data)['modules']
        ret = []
        if get_key:
            for module in modules:
                ret.append(module['module_key'])
        else:
            for module in modules:
                m = Module()
                for key, value in module.items():
                    setattr(m, key, value)
                ret.append(m)
        return ret

    def get_document_revision(self):
        raise SugarError("Method not implemented yet.")

    def get_entry(self, module, id, links=dict(), track_view=False):
        """Retrieves a single object based on object ID."""
        relationships = []
        for key, value in links.items():
            relationships.append({'name': key.lower(), 'value': value})
        data = [self.session_id, module, id, [], relationships, track_view]
        result = self._request('get_entry', data)
        obj = SugarObject(module=module)
        try:
            obj_data = result['entry_list'][0]['name_value_list']
        except:
            return obj
        for key in obj_data:
            if isinstance(key, dict):
                # No object found
                return None
            setattr(obj, key, obj_data[key]['value'])
        if result['relationship_list']:
            for m in result['relationship_list'][0]:
                setattr(obj, m['name'], [])
                for record in m['records']:
                    robj = SugarObject(module=m['name'])
                    for key in record:
                        setattr(robj, key, record[key]['value'])
                    getattr(obj, m['name']).append(robj)
        return obj

    def get_entries(self, module, ids, track_view=False, get_existed_ids=False):
        """Retrieves a list of objects based on specified object IDs."""
        if not isinstance(ids, list):
            ids = [
                ids,
            ]
        ids = list(set(ids))
        data = [self.session_id, module, ids, [], [], track_view]
        results = self._request('get_entries', data)['entry_list']
        ret = []
        if get_existed_ids:
            deleted = []
            try:
                for result in results:
                    if len(result['name_value_list']) > 2:
                        # Will got 'Access to this object is denied since it has been deleted or does not exist'
                        # if nv['name'] == 'deleted' and nv['value'] == '0':
                        ret.append(result['id'])
            except:
                pass
        else:
            try:
                for result in results:
                    obj = SugarObject(module=module)
                    for key in result['name_value_list']:
                        if isinstance(key, dict):
                            # No objects found
                            return []
                        setattr(obj, key,
                                result['name_value_list'][key]['value'])
                    ret.append(obj)
            except:
                pass
        return ret

    def get_entries_count(self, q, deleted=False):
        """Retrieves a count of beans based on query specifications."""
        data = [self.session_id, q.module, q.query, int(deleted)]
        return int(self._request('get_entries_count', data)['result_count'])

    def get_entry_list(self,
                       q,
                       fields=(),
                       links=dict(),
                       order_by="",
                       max_results=0,
                       offset=0,
                       deleted=False,
                       favorites=False):
        """Retrieves a list of objects based on query specifications."""
        relationships = []
        for key, value in links.items():
            relationships.append({'name': key.lower(), 'value': value})
        data = [
            self.session_id, q.module, q.query, order_by, offset, fields,
            relationships, max_results,
            int(deleted),
            int(favorites)
        ]
        results = self._request('get_entry_list', data)
        entry_list = results['entry_list']
        ret = []
        for i, result in enumerate(entry_list):
            obj = SugarObject(module=q.module)
            for key in result['name_value_list']:
                setattr(obj, key, result['name_value_list'][key]['value'])
            if results['relationship_list']:
                for m in results['relationship_list'][i]['link_list']:
                    setattr(obj, m['name'], [])
                    for record in m['records']:
                        robj = SugarObject(module=m['name'])
                        for k in record['link_value']:
                            setattr(robj, k, record['link_value'][k]['value'])
                        getattr(obj, m['name']).append(robj)
            ret.append(obj)
        return ret

    def get_language_definition(self):
        raise SugarError("Method not implemented yet.")

    def get_last_viewed(self):
        raise SugarError("Method not implemented yet.")

    def get_modified_relationships(self):
        raise SugarError("Method not implemented yet.")

    def get_module_fields(self, q, fields=(), get_structure=False):
        """Returns a list of fields as String List"""
        data = [self.session_id, q.module, fields]
        field_list = self._request('get_module_fields', data)
        if get_structure:
            field_data_structure_list = []
            for item in field_list:
                if item == "module_fields":
                    for i in field_list[item]:
                        field_data_structure_list.append(field_list[item][i])
            return field_data_structure_list
        else:
            if field_list['module_fields']:
                return [field for field in field_list['module_fields']]
            return []

    def get_module_fields_md5(self):
        raise SugarError("Method not implemented yet.")

    def get_module_layout(self):
        raise SugarError("Method not implemented yet.")

    def get_note_attachment(self):
        raise SugarError("Method not implemented yet.")

    def get_quotes_pdf(self):
        raise SugarError("Method not implemented yet.")

    def get_relationships(self, module_names, module_id, link_field_name, related_fields, related_module_link_name_to_fields_array):
        """Retrieves a specific relationship link for a specified record."""
        related_module_query = ' {}.name IS NOT NULL '.format(link_field_name)
        order_by = ' {}.name'.format(link_field_name)
        data = [
            self.session_id, module_names, module_id, link_field_name, related_module_query,
            related_fields, related_module_link_name_to_fields_array, 1, order_by, 0, limit
        ]
        return self._request('get_relationships', data)

    def get_report_entries(self):
        raise SugarError("Method not implemented yet.")

    def get_report_pdf(self):
        raise SugarError("Method not implemented yet.")

    def get_server_info(self):
        raise SugarError("Method not implemented yet.")

    def get_upcoming_activities(self):
        raise SugarError("Method not implemented yet.")

    def get_user_id(self):
        raise SugarError("Method not implemented yet.")

    def get_user_team_id(self):
        raise SugarError("Method not implemented yet.")

    def job_queue_cycle(self):
        raise SugarError("Method not implemented yet.")

    def job_queue_next(self):
        raise SugarError("Method not implemented yet.")

    def job_queue_run(self):
        raise SugarError("Method not implemented yet.")

    def login(self, username, password, app="Python", lang="en_us"):
        """Logs a user into the SugarCRM application."""
        data = [{
            'user_name': username,
            'password': hashlib.md5(password.encode('utf8')).hexdigest()
        }, app, [{
            'name': "language",
            'value': lang
        }]]
        return self._request('login', data)

    def logout(self):
        raise SugarError("Method not implemented yet.")

    def oauth_access(self):
        raise SugarError("Method not implemented yet.")

    def seamless_login(self):
        raise SugarError("Method not implemented yet.")

    def search_by_module(self):
        raise SugarError("Method not implemented yet.")

    def set_campaign_merge(self):
        raise SugarError("Method not implemented yet.")

    def set_document_revision(self, doc, f, revision=None):
        """Creates a new document revision for a specific document record."""
        if isinstance(f, str) or isinstance(f, unicode):
            f = open(f, 'rb')
            fields = {
                'id': doc.id,
                'filename': f.name.split(os.sep)[-1],
                'file': base64.b64encode(f.read()),
                'revision': revision or doc.revision,
            }
            data = [self.session_id, fields]
            return self._request('set_document_revision', data)

    def set_entries(self, obj_list):
        """Creates or updates a batch of objects."""
        if not isinstance(obj_list, list):
            obj_list = [
                obj_list,
            ]
        data = [
            self.session_id, obj_list[0].module,
            [obj.fields for obj in obj_list]
        ]
        result = self._request('set_entries', data)
        for i, obj_id in enumerate(result['ids']):
            obj_list[i].id = obj_id
        return obj_list

    def set_entries_smart(self, obj_list):
        ids = []
        obj_id_based = {}
        for obj in obj_list:
            ids.append(obj['id'])
        try:
            exist_ids = self.get_entries(
                obj_list[0].module, ids, get_existed_ids=True)
        except Exception as e:
            return {'msg': 'Failed to check records', 'reason': e}
        for obj in obj_list:
            if obj['id'] not in exist_ids:
                # This key is used to create a new item with specified id. See https://goo.gl/ExkCUj
                obj['new_with_id'] = True
            obj_id_based[obj['id']] = obj
        return self.set_entries(obj_list), obj_id_based

    def set_entry(self, obj):
        """Creates or updates a specific object."""
        data = [self.session_id, obj.module, obj.fields]
        result = self._request('set_entry', data)
        obj.id = result['id']
        return obj

    def set_note_attachment(self, note, f):
        """Creates an attachment and associates it to a specific note object."""
        if isinstance(f, str) or isinstance(f, unicode):
            f = open(f, 'rb')
        fields = {
            'id': note.id,
            'filename': f.name,
            'file': base64.b64encode(f.read())
        }
        data = [self.session_id, fields]
        return self._request('set_note_attachment', data)

    def set_relationship(self, parent, child, delete=False):
        """Sets relationship between two records."""
        delete = int(delete)
        related_ids = [
            child.id,
        ]
        name_value_list = [{
            'name':
            "%s_%s" % (parent.module.lower(), child.module.lower()),
            'value':
            'Other',
        }]
        data = [
            self.session_id, parent.module, parent.id,
            child.module.lower(), related_ids, name_value_list, delete
        ]
        return self._request('set_relationship', data)

    def set_relationships(self, module_collection):
        """Sets relationships between pair of records."""
        '''
        format:
        module_collection = [{
            'table': [
                'PARENT_MODULE_NAME',
                'RELATED_CHILD_MODULE_NAME'
            ],
            'map': {
                'PARENT_ITEM_ID': [
                    'RELATED_ID'
                ]
            }
            'delete': False
        }, ....]
        '''
        #The name of the modules from which to relate records.
        module_names = []
        #The IDs of the specified module beans.
        module_ids = []
        #The relationship names of the linked fields from which to relate records.
        field_names = []
        # The lists of record ids to relate
        related_ids = []
        # Sets the value for relationship based fields
        name_value_list = []
        # Whether or not to delete the relationships. 0:create, 1:delete
        delete_array = []
        for col in module_collection:
            try:
                module_names.append(col['table'][0])
                for pk, fks in col['map'].viewitems():
                    module_ids.append(pk)
                    related_ids.append(fks)
                field_names.append(col['table'][1])
                delete_array.append(int(col.get('delete', False)))
                name_value_list.append({
                    'name':
                    "%s_%s" % (col['table'][0].lower(),
                               col['table'][1].lower()),
                    'value':
                    'Other'
                })
            except:
                pass
        if len(module_names) < 1:
            return {'status': 204, 'msg': 'nothong to do'}
        if len(module_names) != len(module_ids) or len(module_names) != len(related_ids):
            return {'status': 400, 'msg': 'invalid input numbers'}
        data = [
            self.session_id, module_names, module_ids, field_names, related_ids,
            name_value_list, delete_array
        ]
        return self._request('set_relationships', data)

    def snip_import_emails(self):
        raise SugarError("Method not implemented yet.")

    def snip_update_contacts(self):
        raise SugarError("Method not implemented yet.")


class SugarObject:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            if key == "module":
                try:
                    cls = value[:-1].replace('ie', 'y').title()
                    self.__class__ = getattr(sys.modules['sugarcrm'], cls)
                except:
                    pass

    @property
    def fields(self, json_obj={}):
        item_obj = json_obj if len(json_obj) else self.__dict__
        params = []
        for key, value in item_obj.items():
            if not value:
                continue
            params.append({'name': key, 'value': value})
        return params

    @property
    def query(self):
        q = ""
        for key, value in self.__dict__.items():
            if not value:
                continue
            if q:
                q += "AND "
            if value.find('%') >= 0:
                q += "%s.%s LIKE '%s' " \
                     % (self.module.lower(), key, str(value))
            else:
                q += "%s.%s='%s' " % (self.module.lower(), key, str(value))
        return q


class Call(SugarObject):
    module = "Calls"


class Campaign(SugarObject):
    module = "Campaigns"


class Contact(SugarObject):
    module = "Contacts"


class Document(SugarObject):
    module = "Documents"


class Email(SugarObject):
    module = "Emails"


class Lead(SugarObject):
    module = "Leads"


class Module(SugarObject):
    module = "Modules"


class Note(SugarObject):
    module = "Notes"


class Opportunity(SugarObject):
    module = "Opportunities"


class Product(SugarObject):
    module = "Products"


class Prospect(SugarObject):
    module = "Prospects"


class ProspectList(SugarObject):
    module = "ProspectLists"


class Quote(SugarObject):
    module = "Quotes"


class Report(SugarObject):
    module = "Reports"


class User(SugarObject):
    module = "Users"


class SugarError(Exception):
    pass
