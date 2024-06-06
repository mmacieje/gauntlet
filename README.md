<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/ios-filled/100/FFFFFF/hockey-glove.png">
  <source media="(prefers-color-scheme: light)" srcset="https://img.icons8.com/ios-filled/100/hockey-glove.png">
  <img alt="glove icon" src="https://img.icons8.com/ios-filled/100/hockey-glove.png">
</picture>

# Gauntlet
I love playing table tennis, and I mainly play it in the office with my colleagues. I wanted to keep our scores with something a little more elaborate than a spreadsheet, and so I created a simple web app. With it you can:
- Register as a user an login in
- Input match scores and see a history of played matches
- Organise a tournament:
  - Player can sign up for an upcomming tournament
  - Once the tournament starts, matches are planned for each player
  - Players can then input scores for the planned matches
  - There is a leaderboard an a scoreboard available for an ongoing tournament
  - All-on-all tournaments supported as of now, elimination tournaments to be done

# Tech stack
The app is written in Python with Django as the web framework. Frontend is created via Django Templates with Bootstrap and some JS sprinkled in. The app is Dockerized and uses Sendgrid to send out e-mail (e.g. to confirm user's e-mail account when signing up).

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

# Demo
See the project in action at [demo.gauntlet.pl](https://demo.gauntlet.pl/)

## Author
[Marcin Maciejewski](https://github.com/mmacieje/)

## Attribution
[Glove](https://icons8.com/icon/WIHhUgmcoIyB/hockey-glove) icon by [Icons8](https://icons8.com)
