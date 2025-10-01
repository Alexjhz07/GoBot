# Services

Currently, we just have 3 core services running.  
In the future, we might merge, split, or add more!

| Service  | Port | Description                                                                                                                                                                                                       |
| -------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| database | 3815 | Handles all operations relating to databases. This critical service should always be running.                                                                                                                     |
| banking  | 3817 | Handles all operations relating to banking from the user's perspective.<br />The scope does not cover monetary rewards from mini-games, etc.<br />Note that games may still update the banking table for rewards. |
| wordle   | 3915 | Handles all operations relating to the wordle game                                                                                                                                                                |