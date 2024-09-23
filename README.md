# GoBot

Continuing the legacy of our little Bond Bot

## File system

| Item      | Description                                | Type           | Notes                                                                                                         |
| --------- | ------------------------------------------ | -------------- | ------------------------------------------------------------------------------------------------------------- |
| bot/      | Files relating to the bot itself           | Python         |                                                                                                               |
| cluster/  | PSQL directory, create to run own instance | PSQL           | Not provided in repo, should create and run on port 5434 (Slightly different from default to avoid collision) |
| docs/     | Documents for understanding the system     | Markdown       | Database table info in docs                                                                                   |
| services/ | Contains all our lovely microservices      | Go, Typescript | More info available in the README of this folder                                                              |
