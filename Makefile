migrate:
	docker-compose exec web python manage migrate

seed:
	docker-compose exec web python manage seed
	docker-compose exec web python manage import_warehouse

create_category:
	docker-compose exec web python manage create_category

create_cars:
	docker-compose exec web python manage create_car_models

create_modifications:
	docker-compose exec web python manage import_modifications

create_engines:
	docker-compose exec web python manage create_engines