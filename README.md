# pyclarindspace

Python package using clarin-dspace API.

## Installation

```
 pip install -U git+https://github.com/ufal/pyclarindspace.git@master
```


## Quick setup
Provide `.env` file with admin email, password and repo_url (everything before `/rest`):
```
export EMAIL=
export PASSWORD=
export REPO_URL=
export DEBUG=True
```

Now run `./run.examples.sh` to source the environment and import items from the test dir