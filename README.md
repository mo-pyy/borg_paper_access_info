# Borg paper access info

## install
```bash
pip3 install .
```
Also install [melt](https://github.com/charmbracelet/melt)

## setup ssh
Generate ed25519 ssh key without password
```bash
ssh-keygen -t ed25519 -f ~/.ssh/borg_access_key -N ""
```
Grant access to your borg repo for this key in `append-only` mode.

## generate pdf with access information
```bash
python3 -m paper_backup.main ~/.ssh/borg_access_key YOUR_BORG_REPO_URL YOUR_BORG_REPO_SSH_FINGERPRINT
```

## print
Now print out the generated pdf and store it somewhere safe.