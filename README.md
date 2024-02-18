<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.icons8.com/ios-filled/100/FFFFFF/hockey-glove.png">
  <source media="(prefers-color-scheme: light)" srcset="https://img.icons8.com/ios-filled/100/hockey-glove.png">
  <img alt="glove icon" src="https://img.icons8.com/ios-filled/100/hockey-glove.png">
</picture>

# Gauntlet
A platform for organising social sports events and tracking one's results.

# Use case
I love playing table tennis, and I mainly play it in the office with my colleagues. I wanted to keep our scores with something a little more elaborate than a spreadsheet, and so I created a simple web app. With it you can:
- Register as a user an login in
- Input a score of freeplay matches played with other users
- See your previous matches and some basic stats (how many times you won/lost vs a certain player, what was the point distribution in sets)
- Organise a tournament and allow other players to sign up for it
- Start the tournamnent which automatically schedules matches between the participants
- The participants can enter scores for the planned matches, and see the progres (leaderboard, scoreboard)

# Tech stack
The app is written in Python with Django as the web framework. Frontend is created via Django Templates with Bootstrap and some JS sprinkled in. The app is Dockerized and uses Sendgrid to send out e-mail (e.g. to confirm user's e-mail account when signing up).

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

# To be done
- Support other popular office activities e.g. Foosball
- Support double (2x2) games and tournaments
- Make a nicer frontend (e.g. React)

# Name
To "throw down the gauntlet" means to invite someone to compete with you.

## Author
[Marcin Maciejewski](https://github.com/mmacieje/)

## Attribution
[Glove](https://icons8.com/icon/WIHhUgmcoIyB/hockey-glove) icon by [Icons8](https://icons8.com)
