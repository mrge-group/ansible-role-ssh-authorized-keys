
Deploy role-based authorized_keys

Instead of assigning ssh-access-permissions per key/user
with this role you can assign keys/users to a role and then give
varying permissions to that role on different services/hosts.


# Variables

## Users (global)

`ssh_authorized_keys_users`
is a nested dictionary with users and their assigned roles.

Example:
```
ssh_authorized_keys_users:
  john1:
    key: "ssh-ed25519 AAAAC471147114711471147114711471147114711O"
    name: "John Hendik Dow"
```


## Roles (global)

`ssh_authorized_keys_roles`
is a global variable to assign users/keys to roles.
Its main purpose is to assign users from `ssh_authorized_keys_users` to roles.

Example:
```
ssh_authorized_keys_roles:
  shop-backend-developer: {}
  bi-po:
    key_options: "no-X11-forwarding"
    login: "po"
    users:
    - john1
```


## Access (per service or host)

`ssh_authorized_keys_access`
is a variable to define which role has access to the current host / service.
You should set it per service or group of services.

Example:
```
ssh_authorized_keys_access:
- role_name: shop-backend-developer:
  key_options: 'no-port-forwarding,no-X11-forwarding,from="10.0.1.1"'
- role_name: bi-po
```


# Developer note

With `ansible.posix.authorized_key` supporting
multiple keys in `key` and the `exclusive=true` parameter,
it would be possible to use it instead of `ansible.builtin.template`,
but we would lose the ability to add `ansible_managed` and other comments.
