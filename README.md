# rpierwotny

Taken Approach:
-   management commands : [Task Commands](https://github.com/destro6984/rpierwotny/tree/master/users/management/commands)
 - [get_clients_duplicated_phone](https://github.com/destro6984/rpierwotny/blob/master/users/management/commands/get_clients_duplicated_phone.py)
```bash
 python manage.py get_clients_duplicated_phone
 ```

 - [get_user_conflicts_csv](https://github.com/destro6984/rpierwotny/blob/master/users/management/commands/get_user_conflicts_csv.py)
```bash
  python manage.py get_user_conflicts_csv users.SubscriberSMS
```
 - [migrate_data_to_users](https://github.com/destro6984/rpierwotny/blob/master/users/management/commands/migrate_data_to_users.py)
```bash
  python manage.py migrate_data_to_users users.Subscriber
```
 - [migrate_gdpr_consent](https://github.com/destro6984/rpierwotny/blob/master/users/management/commands/migrate_gdpr_consent.py)
```bash
  python manage.py migrate_gdpr_consent
```
# Assumptions:
- prepare small django app instead of bare script (no dockerization to save time not because I can't)
- dbsqlite assumed to be enough
- doesn't protect django envs as its just task (not because I don't know it)
- divide tasks into command for better readability
- don't create relations ,lack of it assumed as a part of a task
- small amount of tests to save time spend on task (I can write more if needed)
- logic approach: annotate conditions defined  in task and query data based on them to receive desired results,
last loop to prepare data for data migration
- additional get_test_data it's just a helper to have some data

If proposed solution is complete mismatch of what was desired still it was worth trying :)
