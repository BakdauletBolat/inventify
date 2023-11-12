```bash
  docker-compose up -d --build 
```

```bash
  docker-compose exec web poetry run python manage.py migrate
```

```bash
  docker-compose exec web poetry run python manage.py create_seed
```