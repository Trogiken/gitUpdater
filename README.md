# gitUpdater
Utilize github tags to update client programs

## Setup

Generate a token [here](https://github.com/settings/tokens). Enable the 'repo' scope

### Install
`pip install git+https://github.com/Trogiken/gitUpdater.git`

### Uninstall
`pip uninstall gitUpdater`

### Update
`pip install --upgrade gitUpdater`

## Features
```
import updater

update = updater()  # 'current_version', 'username', 'repository', if the repo is private; 'token'

# Main Functions
update.check()
update.run(install_path, startup_path, force)  # 'force' is optional

# Subclass Functions
update.fetch(url)
update.get_tags()
update.get_versions()
update.download(path, tag)
```

## Example

```
import updater

update = updater(current_version='1.0-beta.1', username='Trogiken', 'DeMod-GTAV')

if update.check()['update']:
  print("Update is available. Installing Latest")
  update.run()
```
