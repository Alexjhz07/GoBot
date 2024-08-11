# Tables

This document contains all the tables currently in use along with any extra information regarding the data stored.
Tables that do not expect many rows, such as those that are per user or per day, are marked with [small] beside their title.

`VARCHAR(255)` is used throughout as, from what I've read, it has negligible performance differences compared to lesser values.
I do not want to deal with formating the whole database if Discord suddenly decides that usernames can be 200 characters long.

A commonly occurring key is the `user_id`. This key is always to be set to reference the foreign-key in `user_information`.

# User Creation

Certain tables must have an entry with certain fields set when a user is added to the system.
Please refer to the [List of Tables](list-of-tables) for more info on the entire structure

- `user_information` - `user_id`, `username` (This entry must be created first as it houses the `user_id` referenced by other tables)
- `user_experience` - `user_id`
- `bank_timer` - `user_id`

# List of Tables

## user_information [Small]

| Column name | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES |
| ----------- | ------------ | ----------- | ----------- | ----------------- | ---------- |
| user_id     | BIGINT       | PRIMARY KEY |             |                   |            |
| username    | VARCHAR(255) |             | NOT NULL    |                   |            |
| nickname    | VARCHAR(255) |             | NOT NULL    | ""                |            |
| avatar_url  | VARCHAR(255) |             | NOT NULL    | ""                |            |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |            |

```sql
CREATE TABLE public.user_information (
	user_id bigint NOT NULL,
	username varchar NOT NULL,
	nickname varchar DEFAULT '' NOT NULL,
	avatar_url varchar DEFAULT '' NOT NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT user_information_pk PRIMARY KEY (user_id)
);
```

## user_experience [Small]

| Column name | Type   | Properties  | CONSTRAINTS | DEFAULT | REFERENCES                |
| ----------- | ------ | ----------- | ----------- | ------- | ------------------------- |
| user_id     | BIGINT | PRIMARY KEY |             |         | user_information(user_id) |
| experience  | BIGINT |             | NOT NULL    | 0       |                           |

```sql
CREATE TABLE public.user_experience (
	user_id bigint NOT NULL,
	experience bigint DEFAULT 0 NOT NULL,
	CONSTRAINT user_experience_pk PRIMARY KEY (user_id),
	CONSTRAINT user_experience_user_information_fk FOREIGN KEY (user_id) REFERENCES public.user_information(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);
```

The cooldown can be reset on launch and stored in memory as it's fairly inconsequential.

## bank_timer [Small]

| Column name  | Type        | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ------------ | ----------- | ----------- | ----------- | ----------------- | ------------------------- |
| user_id      | BIGINT      | PRIMARY KEY |             |                   | user_information(user_id) |
| bank_daily   | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| bank_weekly  | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| bank_monthly | TIMESTAMPTZ |             | NOT NULL    | CURRENT_TIMESTAMP |                           |

```sql
CREATE TABLE public.bank_timer (
	user_id bigint NOT NULL,
	bank_daily timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
	bank_weekly timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
	bank_monthly timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
	CONSTRAINT user_timer_pk PRIMARY KEY (user_id),
	CONSTRAINT user_timer_user_information_fk FOREIGN KEY (user_id) REFERENCES public.user_information(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);
```

These are loaded once at the start of the bot and cached for quick use.
Rewrites to bank timers are infrequent and must be persisted. That is why this table exists.

## bank_transactions

| Column name        | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ------------------ | ------------ | ----------- | ----------- | ----------------- | ------------------------- |
| transaction_id     | SERIAL       | PRIMARY KEY |             |                   |                           |
| transaction_type   | VARCHAR(255) |             | NOT NULL    |                   |                           |
| transaction_amount | BIGINT       |             | NOT NULL    |                   |                           |
| user_id            | BIGINT       |             | NOT NULL    |                   | user_information(user_id) |
| created_at         | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |                           |
| group_uuid         | UUID         |             | NOT NULL    |                   |                           |

```sql
CREATE TABLE public.bank_transactions (
	transaction_id serial NOT NULL,
	transaction_type varchar NOT NULL,
	transaction_amount bigint NOT NULL,
	user_id bigint NOT NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NOT NULL,
	group_uuid uuid NOT NULL,
	CONSTRAINT bank_transactions_pk PRIMARY KEY (transaction_id),
	CONSTRAINT bank_transactions_user_information_fk FOREIGN KEY (user_id) REFERENCES public.user_information(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);
```

- `transaction_type`: A type of transaction for summary reports. Listed below are the current types in use:
  - `initial`: Used to deposit an initial amount from a data transfer
  - `daily`: Daily money collection
  - `weekly`: Weekly money collection
  - `monthly`: Monthly money collection
  - `transfer`: Money transferred in from or out to another user
  - `flip`: Money won or lost from a coin flip
  - `wordle`: Money won from winning a wordle game

The name `transaction` is only used in the sense of a bank transaction.
Transactions as in grouped requests in the psql sense are denoted in the `group_uuid` column.

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
| date_string | VARCHAR(255) |             | NOT NULL    |                   |            |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |            |

TODO

## wordle_games

| Column name | Type         | Properties  | CONSTRAINTS | DEFAULT           | REFERENCES                |
| ----------- | ------------ | ----------- | ----------- | ----------------- | ------------------------- |
| guess_id    | SERIAL       | PRIMARY KEY |             |                   |                           |
| user_id     | BIGINT       |             | NOT NULL    |                   | user_information(user_id) |
| guess_word  | VARCHAR(255) |             | NOT NULL    |                   |                           |
| date_string | VARCHAR(255) |             | NOT NULL    |                   |                           |
| created_at  | TIMESTAMPTZ  |             | NOT NULL    | CURRENT_TIMESTAMP |                           |

TODO
