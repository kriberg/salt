# -*- coding: utf-8 -*-
'''
The key Thorium State is used to apply changes to the accepted/rejected/pending keys

.. versionadded:: Carbon
'''
# Import python libs
from __future__ import absolute_import
import time

# Import salt libs
import salt.key


def _get_key_api():
    '''
    Return the key api hook
    '''
    if 'keyapi' not in __context__:
        __context__['keyapi'] = salt.key.Key(__opts__)
    return __context__['keyapi']


def timeout(name, delete=0, reject=0):
    '''
    If any minion's status is older than the timeout value then apply the
    given action to the timed out key. This example will remove keys to
    minions that have not checked in for 300 seconds (5 minutes)

    code-block:: yaml

        clean_keys:
          key.timeout:
            - require:
              - status: stat_reg
            - delete: 300
    '''
    ret = {'name': name,
           'changes': {},
           'comment': '',
           'result': True}
    now = time.time()
    ktr = 'key_start_tracker'
    if ktr not in __context__:
        __context__[ktr] = {}
    remove = set()
    keyapi = _get_key_api()
    current = keyapi.list_status('acc')
    for id_ in current.get('minions', []):
        if id_ in __reg__['status']['val']:
            # minion is reporting, check timeout and mark for removal
            if (now - __reg__['status']['val'][id_]['recv_time']) > delete:
                remove.add(id_)
        else:
            # No report from minion recorded, mark for change if thorium has
            # been running for longer than the timeout
            if id_ not in __context__[ktr]:
                __context__[ktr][id_] = now
            else:
                if (now - __context__[ktr][id_]) > delete:
                    remove.add(id_)
    for id_ in remove:
        keyapi.delete_key(id_)
    return ret
