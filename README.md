# API для работы с порталом Мосэнергосбыт
###### Установка 
`pip install mosenergosbyt`
###### Доступные функции: 
* Авторизация на портле 
* Получение базовой информации клиента с портала, которая нужна для последующих вызовов
* Получение списка переданных ранее показаний
* Получение списка оплат
* Передача показаний за текущий месяц

###### Режим CLI:
```
> mosenergosbyt -h
usage: mosenergosbyt [-h] [-i] -l LOGIN -p PASSWORD [-u] [-m METER] [-d DAY] [-n NIGHT] [-e EVENING]

Укажите параметры ввода

optional arguments:
  -h, --help            show this help message and exit
  -i, --info            Получение информации
  -l LOGIN, --login LOGIN
                        логин
  -p PASSWORD, --password PASSWORD
                        пароль
  -u, --upload          Передача показаний
  -m METER, --meter METER
                        Номер счетчика для передачи (обязательно для upload)
  -d DAY, --day DAY     дневные показания
  -n NIGHT, --night NIGHT
                        ночные показания
  -e EVENING, --evening EVENING
                        вечерние показания
```

Загрузка данных с портала
```
> mosenergosbyt -i -l **** -p *****
```
Получение данных в виде json либо сообщение об ошибке (при этом выполнение приложения завершается с статусом 1)

Загрукза данных на портал
```
> mosenergosbyt -u -l ***** -p **** -m *****-***-** -d * -n *
```
