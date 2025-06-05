## Клонирование проекта

Клонируйте репозиторий на вашу локальную машину:

```sh
git clone https://github.com/Egor213/foodgram-st.git
````

После выполнения этой команды появится директория `foodgram-st`, содержащая весь проект.

---

## Запуск проекта

Перейдите в директорию `infra`:

```sh
cd foodgram-st/infra
```

Создайте файл `.env` на основе примера:

```sh
cp .env.example .env
```

Пример содержимого `.env`:

```env
DJANGO_SECRET_KEY=secret-kEy
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost
CORS_ALLOWED_HOSTS=http://localhost:3000
NGINX_PORT=80
DB_ENGINE=postgresql 
DB_NAME=test
DB_PASSWORD=test
DB_USER=test
DB_HOST=db
DB_PORT=5432
```

Запустите контейнеры:

```sh
docker compose up -d --build
```

Вы должны увидеть запуск всех необходимых сервисов. Проверить их можно с помощью команды:

```sh
docker ps
```
![image](https://github.com/user-attachments/assets/94c2b7b0-ea88-4eb1-b2af-5ef18feee4b0)



---

## Доступ к приложению

Приложение будет доступно по адресу:

**[http://localhost](http://localhost)**

---

## Демо-аккаунты

### Администратор

* **Email**: `admin@example.com`
* **Пароль**: `adminpass`

### Обычные пользователи

| Email                                           | Пароль    |
| ----------------------------------------------- | --------- |
| [tolick@gmail.com](mailto:tolick@gmail.com)     | superpass |
| [vitalick@gmail.com](mailto:vitalick@gmail.com) | superpass |
| [nikitos@gmail.com](mailto:nikitos@gmail.com)   | superpass |

---

##  Сценарий работы


* Пользователь может **войти** на сайт.

  
  ![image](https://github.com/user-attachments/assets/980bc4e4-8ba9-4cdf-80a8-70b424e084b6)

* Пользователь может **зарегистрироваться**.

  
  ![image](https://github.com/user-attachments/assets/7b97430a-f393-4dac-8f1f-72788c94866a)

* Залогиненный пользователь может **сменить пароль**.

  
  ![image](https://github.com/user-attachments/assets/121808c4-13a6-49ce-acdc-d4f83c72ce09)

* Залогиненный пользователь может **установить или удалить аватарку**.

 
  ![image](https://github.com/user-attachments/assets/060e19ee-1f79-4256-b0ec-5906567bbfdf)




* Главная страница содержит **список всех рецептов**, отсортированных по дате.

  
  ![image](https://github.com/user-attachments/assets/b6122b7a-0ade-40e8-b117-60dd858cf574)

* Пользователь может **создавать рецепты**.

  
  ![image](https://github.com/user-attachments/assets/9560f27b-6226-47c0-b8fb-fc8c09becf79)

* Можно **просматривать подробности** рецептов.

  
  ![image](https://github.com/user-attachments/assets/14a64120-5b6c-44f5-ac79-fc8e5f2464ae)

* Пользователь может **подписываться на других** и просматривать свои подписки.

  
  ![image](https://github.com/user-attachments/assets/c11ec212-16f8-49fb-87b2-791be28ba6a9)

* Можно добавлять рецепты в **избранное**.

  
  ![image](https://github.com/user-attachments/assets/8a5dffc1-b476-4da2-9e2e-75fc1fa80915)

* Можно добавлять рецепты в **список покупок** и **скачивать его в PDF**.

  
  ![image](https://github.com/user-attachments/assets/cfbb9f22-ab7d-4a7d-bc9d-abad2c1cee88)

  
  ![image](https://github.com/user-attachments/assets/dfeae0fc-a5ff-46ef-8885-277e60d1d9f7)



---

##  Остановка проекта

Чтобы остановить и удалить все контейнеры и тома, выполните:

```sh
docker compose down -v
```

---

## Стек технологий

* Python / Django / Django REST Framework
* PostgreSQL
* Docker / Docker Compose
* Gunicorn / Nginx
* FPDF (для формирования PDF файла)
* React (для фронтенда)
