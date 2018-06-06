# mq-component-py
Python component for MoniQue.

## Сборка и установка

Необходимы библиотеки `pyzmq` и `msgpack`. Их можно установить с помощью пакетного менеджера `pip3`:

```bash
pip3 install pyzmq msgpack
```

Непосредственно библиотеку с компонентом можно установить с помощью следующих команд:

```bash
git clone https://github.com/biocad/mq-component-py.git
cd mq-component-py
python3 setup.py install
```

Для удаления библиотеки необходимо выполнить
```bash
pip3 uninstall mq-component-py
```

## Использование в сторонних библиотеках

После установки для импорта будут доступны три модуля:
1. `mq.protocol`: типы `Message`, `MonitoringResult`, функции для работы с тегом, запаковки/распаковки в `MessagePack`.
2. `mq.component`: класс `Component` с не реализованным методом `run()`. Для написания своего компонента необходимо создать наследника `Component` и реализовать метод `run()`. 
   Для общения с `MoniQue` доступны входящие коммуникационные каналы от центрального места и контроллера, а также исходящий канал в центральное место. [Пример](examples/radio-listener.py)
3. `mq.config`: класс `Config`, который может загружать параметры из конфигурационного файла. Содержит адреса контроллера и центрального места, указание, куда писать лог и т.д.

## Создание нового компонента

Порядок создания нового компонента описан [тут](doc/Develop.md)

## Запуск примеров

Для запуска всех примеров необходим запущенный scheduler – "одно место". Мы считаем, что "одно место" у вас уже запущено на локальной машине (подробнее читай в документации [mq](https://github.com/biocad/mq)).

Для взаимодействия с примерами можно воспользоваться [jobcontrol](https://github.com/biocad/mq-jobcontrol).

### Пример "радио"

Является примером асинхронного общения двух компонентов: [один](examples/radio-speaker.py) умеет формировать и рассылать сообщения, а [другой](examples/radio-listener.py) их получать и обрабатывать.
После запуска scheduler в корневой директории библиотеки можно выполнить

```bash
python3 examples/radio-listener.py --config-file examples/config.json
```

Если передать этому компоненту сообщение, он должен распечатать его `data`. Также в мониторинг будет включено пользовательское сообщение о приёме с `id` отправителя.
В качестве источника сообщений можно запустить вещатель.

Вещатель передаёт каждые две секунды сообщение с текстом `Hello! It's me.`

```bash
python3 examples/radio-speaker.py --config-file examples/config.json
```

### Пример "[Калькулятор](examples/calculator.py)"

Является примером компонента, который умеет принять соответствующее сообщение с конфигурацией, обработать его и отправить результат обратно.
Раньше такой компонент назывался "рабочим".
Представляет собой примитивный калькулятор: он принимает два операнда и действие над ними (`+` или `*`), а возвращает результат. Запуск производится командой 

```bash
python3 examples/calculator.py --config-file examples/config.json
```

Для отправки ему сообщения можно в отдельном окне запустить [jobcontrol](https://github.com/biocad/mq-jobcontrol) и использовать [calculator.json](examples/calculator.json).

### Пример "[Банк](examples/bank.py)"

Является примером того, как один компонент при выполнении задачи может использовать другой компонент.

Банк принимает месячный доход и срок в месяцах, а возвращает суммарный доход – см. [bank.json](examples/bank.json). Он использует компонент `calculator` для вычисления результата.
Для запуска понадобятся три окна с открытой текущей директорией.

Запуск калькулятора
```bash
python3 examples/calculator.py --config-file examples/config.json
```

Запуск непосредственно банка
```bash
python3 examples/bank.py --config-file examples/config.json
```

Для взаимодействия с помощью `jobcontrol` можно использовать `bank-data.json` при постановке задачи.

### Пример "Часики"

Пример того, как можно объединять несколько одинаковых компонентов в кластер при помощи [контроллера](https://github.com/biocad/mq-controller). 

Помимо scheduler-а потребуется собрать и запустить контроллер, об этом можно подробнее прочитать в его описании.

Нужно будет запустить несколько экземпляров [часов](examples/clock-reply.py)
```bash
python3 examples/clock-reply.py -f examples/config.json
python3 examples/clock-reply.py -f examples/config.json
...
```

и один экземпляр [опрашивающего компонента](examples/clock-ask.py)
```bash
python3 examples/clock-ask.py -f examples/config.json
```

Каждую секунду опрашивающий компонент посылает сообщение со строкой `What time is it?` в поле data. Контроллер ищет не занятый коспонент-часы и направляет задачу ему, тот в свою очередь отправляет ответ с текущим временем в [Epoch time](https://en.wikipedia.org/wiki/Unix_time).

## Порядок реализации компонента

Как вы уже наверняка знаете, для полноценной работы компонента в его обёртке необходимо реализовать различную функциональность.
Ниже приведены указания на места в библиотеке с соответствующей реализацией.

  * Протокол – описание формата общения с MQ.
    * [Типы](mq/protocol/types.py). Содержит описание сообщения. 
    * [Функции](mq/protocol/functions.py). Содержит функции для работы с сообщениями: создание, конвертация в/из MessagePack и т.д. 
    * [Тэг](mq/protocol/tag.py). Содержит функции для работы с тэгом: создание, обращение к полям.
    * [Ошибки](mq/protocol/error.py). Содержит класс ошибки и коды ошибок.
  * Компонент – общение с MQ.
    * [Компонент](mq/component/component.py). Содержит класс Компонент, позволяющий слушать и отправлять сообщения, а также выполнять некоторую полезную работу.
    * [Технический канал](mq/component/technical.py). Содержит функцию обработки технических сообщений.
    * [Коммуникационный канал](mq/component/communication.py). Содержит функцию обработки коммуникационных сообщений.
    * [Мониторинг](mq/component/monitoring.py). Содержит логику компонента мониторинга. 
  * Config – загрузка параметров MQ.
    * [Загрузка параметров](mq/config.py). Умеет загружать параметры согласно [описанию](https://github.com/biocad/mq/blob/master/doc/ConfigJson.md).
