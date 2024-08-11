# Services

Core services start at port 3815 with the database.

| Service    | Port | Description                                                                                                                                                                                                              |
| ---------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| database   | 3815 | Handles all operations relating to databases. This critical service should always be running.                                                                                                                            |
| experience | 3816 | Handles all operations relating to experience gain from normal messaging.<br />The scope does not cover experience rewards from mini-games, etc.<br />Note that games may still update the experience table for rewards. |
| banking    | 3817 | Handles all operations relating to banking from the user's perspective.<br />The scope does not cover monetary rewards from mini-games, etc.<br />Note that games may still update the banking table for rewards.        |
| wordle     | 3915 | Handles all operations relating to the wordle game                                                                                                                                                                       |
