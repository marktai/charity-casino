# Charity Casino
This website was used to throw a [Charity Casino Night Party](https://partiful.com/e/w905X3NsYD7f7FLNTqC1) on 8/10/2023

## Setup
Running `docker-compose build && docker-compose up` should do most of the setup

### Authenticate the Google sheet integration:
1. Hit `http://HOST/api/people`
2. Look at `docker-compose logs backend --tail 100`
3. Copy the authorization url (might look like `https://accounts.google.com/o/oauth2/auth/oauthchooseaccount?REDACTED`)
4. Log in with the right account (might be `markhsitai@gmail.com`)
5. Copy the URL that you're redirected to (might look like `http://localhost:40490/?REDACTED&scope=https://www.googleapis.com/auth/spreadsheets`)
6. "SSH" into the backend container: `docker-compose exec backend sh`
7. Hit the URL from 5: `curl 'http://localhost:40490/?REDACTED&scope=https://www.googleapis.com/auth/spreadsheets'`
8. Profit


### Running the static page
Because it is expensive to maintain a docker-compose fleet to just serve a static page, I've downloaded the page with Chrome, then served it statically. The current setup of `casino.marktai.com` is just serving the static directory from `./static/` in this repo.
