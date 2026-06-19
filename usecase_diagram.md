---
title: UML Use Case діаграма
---
graph LR
    Actor(["👤 Користувач"])

    subgraph TC[Трекер звичок]
        direction TB
        UC1(Додати звичку)
        UC2(Відмітити виконання)
        UC3(Статус за тиждень)
        UC4(Відсоток виконання)
        UC5(Список звичок)
        UC6(Запустити автотест)
        UC7(Вийти)
    end

    Actor --- UC1
    Actor --- UC2
    Actor --- UC3
    Actor --- UC4
    Actor --- UC5
    Actor --- UC6
    Actor --- UC7
```

![UML Use Case діаграма](usecase_diagram.png)