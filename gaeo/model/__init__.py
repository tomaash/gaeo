# -*- coding: utf-8 -*-
#
# Copyright 2008 GAEO Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""GAEO model package
"""
import re

from google.appengine.ext import db

def pluralize(noun):
    if re.search('[sxz]$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)
    elif re.search('[^aeiou]y$', noun):
        return re.sub('y$', 'ies', noun)
    else:
        return noun + 's'

class BaseModel(db.Model):
    """BaseModel is the base class of data model."""

    @classmethod
    def has_and_belongs_to_many(cls, ref_cls):
        if ref_cls is None:
            raise Exception('No referenced class')
        
        f_name = pluralize(cls.__name__.lower())
        t_name = pluralize(ref_cls.__name__.lower())
        
        if t_name not in cls.__dict__:
            cls.__dict__[t_name] = db.ListProperty(db.Key)
        if f_name not in ref_cls.__dict__:
            ref_cls.__dict__[f_name] = property(lambda self: cls.gql('WHERE %s = :1' % t_name, self.key()))
    
    @classmethod
    def named_scope(cls, name, order_by=None, **conds):
        if name not in cls.__dict__:
            cond_str = "WHERE "
            for cond in conds.iterkeys():
                if len(cond_str) > 6:
                    cond_str += ' AND '
                cond_str += '%s %s' % (cond, conds[cond])
                
            if order_by:
                cond_str += ' ORDER BY %s' % order_by
            cls.__dict__[name] = property(lambda self: cls.gql(cond_str))
    
    def update_attribute(self, **kwds):
        """Update the specified properties"""
        need_change = False
        props = self.properties()
        for prop in props.values():
            if prop.name in kwds:
                if not need_change:
                    need_change = True
                prop.__set__(self, kwds[prop.name])
        
        if need_change:
            self.update()
        
    def save(self):
        self.put()
        
    def update(self):
        self.put()
        