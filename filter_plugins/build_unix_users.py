#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright:
#   2022 Per H. <github.com/perfide>
# License:
#   BSD-2-Clause (BSD 2-Clause "Simplified" License)
#   https://spdx.org/licenses/BSD-2-Clause.html

"""Ansible filter merge variables into something consumable by
ansible.builtin.template"""

# 3rd-party
from ansible.errors import AnsibleOptionsError


def template_options(merged_options):
    """Template `comment` and `key_options` options"""
    for key in ('comment', 'key_options'):
        if key not in merged_options:
            continue
        try:
            merged_options[key] = merged_options[key].format(
                **merged_options.copy()
            )
        except IndexError as err:
            raise AnsibleOptionsError(
                f'unable to format `{key}`='
                f'`{merged_options[key]}` with `{merged_options}`'
            ) from err
    return merged_options


def build_unix_users(
    role_permissions: dict, roles: dict, users: dict, passwd: dict
) -> list:
    """Build dict with lists consumable by ansible.builtin.template

    Args:
        role_permissions (dict): roles-access to the current service
        roles (dict): available roles and their members
        users (dict): users and their ssh-keys
        passwd (dict): the systems passwd database

    Returns:
        list: dicts consumable by ansible.builtin.template
    """

    unix_users = {}
    for service_options in role_permissions:
        try:
            role_name = service_options.pop('role_name')
        except KeyError as err:
            raise AnsibleOptionsError(
                'role_name not in ssh_authorized_keys_access'
            ) from err
        role_options = roles[role_name]
        try:
            member_names = role_options.pop('users')
        except KeyError as err:
            raise AnsibleOptionsError(
                'users not in ssh_authorized_keys_roles'
            ) from err
        for member_name in member_names:
            user_options = users[member_name]
            merged_options = {}
            merged_options.update(user_options)
            merged_options.update(role_options)
            merged_options.update(service_options)
            merged_options['role_name'] = role_name
            merged_options['member_name'] = member_name
            login = merged_options.pop('login', 'root')

            if login not in passwd:
                raise AnsibleOptionsError(
                    f'the user `{login}` for `{member_name}` of `{role_name}` '
                    'does not exist on the target-host'
                )

            if login not in unix_users:
                unix_users[login] = {
                    'login': login,
                    'ssh_keys': [],
                }

                # only set home once
                unix_users[login]['home'] = passwd[login][4]

            merged_options = template_options(merged_options)
            unix_users[login]['ssh_keys'].append(merged_options)

    return unix_users.values()


class FilterModule:  # pylint: disable=too-few-public-methods
    """Hook module for Ansible filters"""
    def filters(self):
        """Hook function for Ansible filters"""
        return {'ssh_authorized_keys_build_unix_users': build_unix_users}


# [EOF]
