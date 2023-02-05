# Borg paper access info

## install
```bash
pip3 install .
```
Also install [melt](https://github.com/charmbracelet/melt) and [wkhtmltopdf](https://wkhtmltopdf.org/)
```bash
sudo apt install wkhtmltopdf
```

## setup ssh
Generate ed25519 ssh key without password
```bash
ssh-keygen -t ed25519 -f ~/.ssh/borg_access_key -N ""
```
Grant access to your borg repo for this key in `append-only` mode.

## generate pdf with access information
```bash
borg_paper_access_info ~/.ssh/borg_access_key YOUR_BORG_REPO_URL YOUR_BORG_REPO_SSH_FINGERPRINT YOUR_BORG_REPO_PASSWORD
```
See an example pdf with fake data here: [example.pdf](https://raw.githubusercontent.com/mo-pyy/borg_paper_access_info/main/examples/example.pdf)

## print
Now print out the generated pdf and store it somewhere safe.

## restoring
You need to have borg, melt and ssh installed.  
Restore the ssh key
```bash
melt restore ~/.ssh/borg_access_key --seed "MELT_SEED_PHRASE"
```
Check the ssh fingerprint of the borg repo
```bash
ssh -o VisualHostKey=yes -i ~/.ssh/borg_access_key borg_user@borg_hostname
```
Restore your files
```bash
export BORG_PASSPHRASE="BORG_PASSPHRASE"
export BORG_RSH="ssh -i ~/.ssh/borg_access_key"
export BORG_REPO="BORG_REPO_URL"
borg list
export BORG_ARCHIVE_NAME="ARCHIVE_TO_RESTORE"
borg extract $BORG_REPO::$BORG_ARCHIVE_NAME
```