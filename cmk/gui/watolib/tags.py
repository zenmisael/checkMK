#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
"""Helper functions for dealing with host tags"""

import os
from pathlib2 import Path

import cmk.utils.paths
import cmk.utils.store as store

import cmk.gui.tags
import cmk.gui.config as config
from cmk.gui.watolib.simple_config_file import WatoSimpleConfigFile
from cmk.gui.watolib.utils import multisite_dir


class TagConfigFile(WatoSimpleConfigFile):
    """Handles loading the 1.6 tag definitions from tags.mk or
    the pre 1.6 tag configuration from hosttags.mk"""

    def __init__(self):
        file_path = Path(multisite_dir()) / "tags.mk"
        super(TagConfigFile, self).__init__(config_file_path=file_path, config_variable="wato_tags")

    def _load_file(self, lock=False):
        if not self._config_file_path.exists():
            return self._load_pre_16_config(lock=lock)
        return super(TagConfigFile, self)._load_file(lock=lock)

    def _load_pre_16_config(self, lock):
        file_path = Path(multisite_dir()) / "hosttags.mk"
        legacy_cfg = store.load_mk_file(
            str(file_path), {
                "wato_host_tags": [],
                "wato_aux_tags": []
            }, lock=lock)

        return cmk.gui.tags.transform_pre_16_tags(legacy_cfg["wato_host_tags"],
                                                  legacy_cfg["wato_aux_tags"])

    # TODO: Move the hosttag export to a hook
    def save(self, cfg):
        super(TagConfigFile, self).save(cfg)
        _export_hosttags_to_php(cfg)


# Creates a includable PHP file which provides some functions which
# can be used by the calling program, for example NagVis. It declares
# the following API:
#
# taggroup_title(group_id)
# Returns the title of a WATO tag group
#
# taggroup_choice(group_id, list_of_object_tags)
# Returns either
#   false: When taggroup does not exist in current config
#   null:  When no choice can be found for the given taggroup
#   array(tag, title): When a tag of the taggroup
#
# all_taggroup_choices(object_tags):
# Returns an array of elements which use the tag group id as key
# and have an assiciative array as value, where 'title' contains
# the tag group title and the value contains the value returned by
# taggroup_choice() for this tag group.
#
def _export_hosttags_to_php(cfg):
    php_api_dir = cmk.utils.paths.var_dir + "/wato/php-api/"
    path = php_api_dir + '/hosttags.php'
    store.mkdir(php_api_dir)

    tag_config = cmk.gui.tags.HosttagsConfiguration()
    tag_config.parse_config(cfg)
    tag_config += config.BuiltinHosttagsConfiguration()

    # need an extra lock file, since we move the auth.php.tmp file later
    # to auth.php. This move is needed for not having loaded incomplete
    # files into php.
    tempfile = path + '.tmp'
    lockfile = path + '.state'
    file(lockfile, 'a')
    store.aquire_lock(lockfile)

    # Transform WATO internal data structures into easier usable ones
    hosttags_dict = {}
    for tag_group in tag_config.tag_groups:
        tags = {}
        for grouped_tag in tag_group.tags:
            tags[grouped_tag.id] = (grouped_tag.title, grouped_tag.aux_tag_ids)

        hosttags_dict[tag_group.id] = (tag_group.topic, tag_group.title, tags)

    auxtags_dict = dict(tag_config.aux_tag_list.get_choices())

    # First write a temp file and then do a move to prevent syntax errors
    # when reading half written files during creating that new file
    file(tempfile, 'w').write('''<?php
// Created by WATO
global $mk_hosttags, $mk_auxtags;
$mk_hosttags = %s;
$mk_auxtags = %s;

function taggroup_title($group_id) {
    global $mk_hosttags;
    if (isset($mk_hosttags[$group_id]))
        return $mk_hosttags[$group_id][0];
    else
        return $taggroup;
}

function taggroup_choice($group_id, $object_tags) {
    global $mk_hosttags;
    if (!isset($mk_hosttags[$group_id]))
        return false;
    foreach ($object_tags AS $tag) {
        if (isset($mk_hosttags[$group_id][2][$tag])) {
            // Found a match of the objects tags with the taggroup
            // now return an array of the matched tag and its alias
            return array($tag, $mk_hosttags[$group_id][2][$tag][0]);
        }
    }
    // no match found. Test whether or not a "None" choice is allowed
    if (isset($mk_hosttags[$group_id][2][null]))
        return array(null, $mk_hosttags[$group_id][2][null][0]);
    else
        return null; // no match found
}

function all_taggroup_choices($object_tags) {
    global $mk_hosttags;
    $choices = array();
    foreach ($mk_hosttags AS $group_id => $group) {
        $choices[$group_id] = array(
            'topic' => $group[0],
            'title' => $group[1],
            'value' => taggroup_choice($group_id, $object_tags),
        );
    }
    return $choices;
}

?>
''' % (_format_php(hosttags_dict), _format_php(auxtags_dict)))
    # Now really replace the destination file
    os.rename(tempfile, path)
    store.release_lock(lockfile)
    os.unlink(lockfile)


def _format_php(data, lvl=1):
    s = ''
    if isinstance(data, (list, tuple)):
        s += 'array(\n'
        for item in data:
            s += '    ' * lvl + _format_php(item, lvl + 1) + ',\n'
        s += '    ' * (lvl - 1) + ')'
    elif isinstance(data, dict):
        s += 'array(\n'
        for key, val in data.iteritems():
            s += '    ' * lvl + _format_php(key, lvl + 1) + ' => ' + _format_php(val,
                                                                                 lvl + 1) + ',\n'
        s += '    ' * (lvl - 1) + ')'
    elif isinstance(data, str):
        s += '\'%s\'' % data.replace('\'', '\\\'')
    elif isinstance(data, unicode):
        s += '\'%s\'' % data.encode('utf-8').replace('\'', '\\\'')
    elif isinstance(data, bool):
        s += data and 'true' or 'false'
    elif data is None:
        s += 'null'
    else:
        s += str(data)

    return s
