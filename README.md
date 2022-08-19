# gitUpdater
Utilize github to update client programs

## Setup

### Install
`pip install git+https://github.com/Trogiken/gitUpdater.git`

### Uninstall
`pip uninstall gitUpdater`

### Update
`pip install --upgrade gitUpdater`

## Code Examples
Generate a token [here](https://github.com/settings/tokens). Enable the 'repo' scope

### Public
```
from updater import Update

update = Update('user', 'my-public-repo')
if update.check('1.0.0'):  # Current version
    # update
    pass
```

### Private
```
from updater import Update

update = Update('user', 'my-private-repo', 'mypersonalaccesstoken')
if update.check('1.0.0'):  # Current version
    # update
    pass
```
