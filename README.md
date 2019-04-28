# ansible-role-atom

[![Build Status](https://travis-ci.org/hidoo/ansible-role-atom.svg?branch=master)](https://travis-ci.org/hidoo/ansible-role-atom)

> Ansible role that setup Atom.

## Installation

```sh
$ ansible-galaxy install git+https://github.com/hidoo/ansible-role-atom
```

## Usage

```yml
roles:
  - ansible-role-atom

vars:
  atom:

    # skip install visual studio code or not (default: no)
    skip_install: yes

    # list of packages to install (default state: latest)
    packages:
      - { name: editorconfig }
      - { name: file-icons, state: absent }
```

## Test

install Atom before testting.

```
$ brew install Atom
```

then run following commands.

```sh
$ pipenv run test:lint
$ pipenv run test:unit
```

## License

MIT
