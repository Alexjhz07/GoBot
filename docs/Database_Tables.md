# Tables

This document contains all the tables currently in use along with any extra information regarding the data stored.  
Tables that do not expect many rows, such as those that are per user or per day, are marked with [small] beside their title.  

`VARCHAR(255)` is used throughout as, from what I've read, it has negligible performance differences compared to lesser values.  
I do not want to deal with formating the whole database if Discord suddenly decides that usernames can be 200 characters long.  

These tables require a row to be inserted for each joining user:
- `user_information`
- `user_experience`
- `user_timer`

## user_information [Small]

| Column name | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES |
| ----------- | ------------ | ----------- | ----------- | ----------------- | ---------- |
| user_id     | BIGINT       | PRIMARY KEY |             |                   |            |
| username    | VARCHAR(255) |             | NOT NULL    |                   |            |
| nickname    | VARCHAR(255) |             | NOT NULL    | ""                |            |
| avatar_url  | VARCHAR(255) |             | NOT NULL    | ""                |            |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |            |

## user_experience [Small]

| Column name | Type   | Properties  | CONSTRAINTS | DEFAULT | REFERENCES                |
| ----------- | ------ | ----------- | ----------- | ------- | ------------------------- |
| user_id     | BIGINT | PRIMARY KEY |             |         | user_information(user_id) |
| experience  | BIGINT |             | NOT NULL    | 0       |                           |

This will be operated upon with a write quite frequently and it does not interfere with any other operations.  
It may be worth dispatching a thread for each experience entry.  

## user_timer [Small]

| Column name         | Type        | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ------------------- | ----------- | ----------- | ----------- | ----------------- | ------------------------- |
| user_id             | BIGINT      | PRIMARY KEY |             |                   | user_information(user_id) |
| experience_cooidown | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| bank_daily          | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| bank_weekly         | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| bank_monthly        | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |

These are loaded once at the start of the bot and the experience cooldown will be cached for quick use.  
However, writes will occur frequently. This will likely run on the same thread as user_experiences.  
Rewrites to bank timers are infrequent enough that this should not matter.  

## bank_transactions

| Column name        | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ------------------ | ------------ | ----------- | ----------- | ----------------- | ------------------------- |
| transaction_id     | SERIAL       | PRIMARY KEY |             |                   |                           |
| transaction_type   | VARCHAR(255) | PRIMARY KEY |             |                   |                           |
| user_id            | BIGINT       |             | NOT NULL    |                   | user_information(user_id) |
| transaction_amount | BIGINT       |             | NOT NULL    |                   |                           |
| created_at         | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |                           |

- `transaction_type`: A type of transaction for summary reports. Listed below are the current types in use:
  - `initial`: Used to deposit an initial amount from a data transfer
  - `daily`: Daily money collection
  - `weekly`: Weekly money collection
  - `monthly`: Monthly money collection
  - `flip`: Money won or lost from a coin flip
  - `wordle`: Money won from winning a wordle game

Note that the bank transactions are currently used for everything money related to make things easy.  
In the future, it may be wise to have a separate table for summarized account info.  
This will allow us to retrieve balances and aggregate info without needed to calculate it each time.  

## stock_transactions

TODO

## wordle_history [Small]

| Column name | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES |
| ----------- | ------------ | ----------- | ----------- | ----------------- | ---------- |
| game_id     | SERIAL       | PRIMARY KEY |             |                   |            |
| word        | VARCHAR(255) |             | NOT NULL    |                   |            |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |            |

## wordle_games

| Column name | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ----------- | ------------ | ----------- | ----------- | ----------------- | ------------------------- |
| guess_id    | SERIAL       | PRIMARY KEY |             |                   |                           |
| user_id     | BIGINT       |             | NOT NULL    |                   | user_information(user_id) |
| guess_word  | VARCHAR(255) |             | NOT NULL    |                   |                           |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
