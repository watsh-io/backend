
# Introduction
Watsh is the first secrets manager powered by JSON Schema.
Manage your secrets through API or via a user-friendly interface.
JSON Schema makes your secrets error free for non-tech user.


# Important
This project is no longer maintained. This repo is a POC/MVP and should not be used in production.
If you wish to take over the project for commercial use, I can be reached by mp

# How to run
## Set up env variables
You'll need:
- to generate secrets (see example.env)
- a mongodb server (you can run one free on https://cloud.mongodb.com/)
- an SMTP email address for login with magic link (you can create one free on gmail: https://myaccount.google.com/apppasswords)
- ngrok for running the project in local


## Install backend dependancies
Requires python3.11
Run 'pipenv install . python3.11'

## Run
Start with 'python main.py'

## Access the front end
The front end application uses Bubble.io
You can access yours at https://watsh-box.bubbleapps.io/version-test?host={ngrok-or-domain}


# Links
Landing page: https://watsh-io.webflow.io/
Doc: https://watsh.readme.io/reference/intro/authentication
Front-end: https://watsh-box.bubbleapps.io/version-test
Notion: https://watsh.notion.site/e54162d8f60047038d531d648c48c2f7?v=cc09de48158e4b07a6eaa86c2307dd78


# Roadmap
## Backend
- CLI
- python SDK
- rollback commit 
- rollback specific item/secret
- websocket monitor item ID
- webhook per secret or per configuration
- restore secret from default branch
- promote secret to default branch
- promote item to default branch
- compare secret between branches and environments
- secret features (min/max number, REGEX string, ...)
- secret referencing
- comments/tags
- nested json reference
- secret generation
- secret rotation
- share secret
- override with personal value

## Frontend
- popup revert
- popup unsaved changes
- + ("" if DOMAIN != "https://api.watsh.io" else "&host={DOMAIN}")