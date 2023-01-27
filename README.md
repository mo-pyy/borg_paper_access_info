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