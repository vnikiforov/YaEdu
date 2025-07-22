Спринт 1 - Микросервисы и документирование решений
# Задание 1. Анализ и планирование

<aside>

**Заказчик**: компания "Теплый дом".
**Область деятельности**: организация управления отоплением в отдельном доме. 
**Текущее положение вещей**: реализовано предоставление пользователям управления отоплением помещений - получение актуальной и установка требуемой температуры.
В настоящий момент у компании 100 - web-клиентов и к системе подключено 100 контроллеров (термометр+реле) управления температурой. 
**Цель**: компания планирует развивать направление "умный дом". Выигран тендер на создание системы управления большого количества разных домов в различных георграфических регионах. Так же должна быть увеличена номенклатура предоставляемых сервисов управления домом, количество и их тип может варироваться в каждом объекте. В домах, которыми планируется управлять, ожидается наличие специальныъх блоки датчиков и реле. На текущий момент 50% домов уже оборудованы требуемыми блоками управления.

</aside>

### 1. Описание функциональности существующего решения

**Управление отоплением:**

- Пользователи могут:
	* зарегистрировать в системе контроллер температуры с указанием:
		* названия,   		
		* наименования помещения,
		* типа контроллера,
		* единицы измерения;
	* получить полный список зарегистрированных в системе контроллеров с их актуальным статусов на момент выполнения запроса;
	* получить информацию с датой регистрации в системе, актуальным статусом и значением темпереатуры для указанного уникальным иденификатором контроллера;
	* удалять, указанный при помощи уникального идентификатора, контроллер 
	* устанавливать требуемую температуру и текстовой статус контроллеру;
	* обновлять информацию о наименовании, типе, месте размещения, статусе, требуемой температуре, единице измерения, указанного уникальным идентификатором, контроллера.
- Система поддерживает обработку ошибочного указания некорректного идентифкатора контроллера и так же уведомление пользователя о некорретном формате входных данных. 
- В случае успешного выполнения команды, интерфейс системы таже уведомляет пользователя об этом. 

**Мониторинг температуры:**

-  Кроме получения информацмии о текущем состоянии непосредственно конкретного контроллера, система также реализует возможность чтения данных о состоянии всех контроллеров указанного помещения (по его наименованию), возвращается набор описателей, следующей структуры: 
	* наименование помещения,
	* текущее значения темпрературы контроллера,
	* единицы измерения контроллера,
	* текущего статуса контроллера,
	* время обновления информации об изменеиях контроллера,
	* строка с произольным описанием контроллера;
- Система обрабатывает некорректное указание помещения - возвращает ошибку, если наименование не указано, либо не зарегистрированно.
  

### 2. Анализ архитектуры монолитного приложения

Текущее решение представляет собой web-приложение, самостоятельно реализующее обработку HTTP-запросов.
Установка дополнительного Web-сервера или сервера приложений не требутся.
Сиcтема написана на языке Go и фактически является интерфейсом между произвольной системой отображения состояния (интерфейсом пользователя) системы отопления домом и непосредственно исполнителным механизмом управления отоплением - термометрами и регуляторами, с которым, в свою очередь коммуникация так же производится при помощи HTTP-запросов - REST API.
Так же система хранит в собственной базе данных (использована СУБЛ PostrgreSQL) информацию о зарегистрированных контроллерах управления отоплением, с возможностью получить последнее считанное с аппаратуры их состояние.
Хранение истории измерений не предусмотрено.
Внешние запросы обрабатываются последовательно, по правилу FIFO.
При старте, приложение жестко определят набор поддерживаемых URL запросов, каждому определяется обработчик, проверяющий коррекность формата, переданных в запрос данных.
Информация о текущем состоянии аппаратуры (температура и статус) получается по запросу от пользователя, никакой автоматизации не предусмотрено.

### 3. Определение доменов и границы контекстов

- ***Домен***: коммуникация с пользователем
	* Поддомен: "описание интерфейса"
	* Поддомен: "обработчики запросов"
- ***Домен***: модель данных
	* Поддомен: "менеджер структур данных"
	* Поддомен: "интерфейс с базой данных"
- ***Домен***: управление контроллером отопления
	* Поддомен: "настройка оборудование":
		* создние, 
		* удаление, 
		* корректировка параметров контролоеров отопления
	* Поддомен: "управление отоплением":
		* установка требуемой температуры, 
		* получение текущего значения температуры.

### **4. Проблемы монолитного решения**

1. Существующая версия приложения не имеет никакого разграничения прав доступа - любой пользователь, знающий URL и описание API системы может свободно отключить все отопление в доме. 
2. На каждый, управялемый компанией, дом нужно разворачивать свой экземпляр приложения. Соответственно, требуется создание некой общей системы обновления экземпляров. По сути вся система управления отоплением является "макро-мироксервисом".
3. Отсутствует автоматический мониторинг состояния контроллеров отопления.
4. Не определены максимально и минимально допустимые диапазоны устанавливаемых значений температуры, что может привести к проблемам уже физического характера - пожары, оледенение, разморозка системы и пр.
5. В случае падения (перезапуска) приложения становится полностью недоступен весь функционал - управление отоплением и настройка оборудования.

### 5. Визуализация контекста системы — диаграмма С4

@startuml
title SmartHome Monolith (AS IS) Context Diagram

top to bottom direction

!includeurl diagrams/c4tpl/C4_Component.puml

System_Boundary(generic_commands, "Generic set of abilities") {
    Person(user, "User", "A tenant of the house")
    Person(admin, "Administrator", "System administrator, who can manage temperature controllers")
}

System(UserCommunicator, "Public User Inetrface", "API descriptor, format and rules of supported requsets and answers")

Rel(generic_commands,  UserCommunicator, "Request for current controller state")
Rel(generic_commands,  UserCommunicator, "Request for full house's controller list")
Rel(generic_commands,  UserCommunicator, "Update controller attributes")
Rel(generic_commands,  UserCommunicator, "Setup required temperature for the controller")
Rel(UserCommunicator, generic_commands, "Inform about controller's state")
Rel(UserCommunicator, generic_commands, "Returns controllers list")
Rel(admin, UserCommunicator, "Register new controller")
Rel(admin, UserCommunicator, "Delete the controller")

System_Ext(hw_api, "Controller Hardware Interface", "REST API")
System_Ext(data_storage, "DB storage for house's contollers", "PostgreSQL DB")

Rel(UserCommunicator, data_storage, "Store information about installed controllers")

Rel(UserCommunicator, hw_api, "Setup requried temperature by sensor ID")
Rel(hw_api, UserCommunicator, "Read current temperature from sensor by ID")

@enduml

# Задание 2. Проектирование микросервисной архитектуры

**Диаграмма контейнеров (Containers)**

@startuml
title SmartHome MS Containers Diagram

left to right direction

!includeurl diagrams/c4tpl/C4_Container.puml

Person(user, "SmartHomeUser", "Пользователь Умного дома")

Container(AuthSvc, "Authorization Service", "PHP/Yii", "Авторизация пользователя в системе, с использованием различных механизмов [OAuth/VK/Google/Yandex etc.]")
Container(UI_Svc, "UI Create&Handle ", "PHP/Yii/React/JS",  "Создание внешнего представления и обработка пользовательских действий")
Container(HW_Support_Svc, "Hardware Handling", "PHP/Python/C#", "Коммуникация с аппаратными интерфейсами оборудования Умного дома")
Container(DB_Svc, "DataBase Center", "SQL/JSON", "Хранение данных")
Container(API_Gate, "External API", "PHP/Python", "Интерфейс для внешних коммуникаций")
Container(CommCenter, "Commander Center", "PHP/Python", "Маршрутизатор и исполнитель запросов")

Rel(AuthSvc, DB_Svc, "Get user info - role & rights")
Rel(AuthSvc, DB_Svc, "Save loging event to log")
Rel(AuthSvc, UI_Svc, "Create login prompt for user's device")
Rel(AuthSvc, CommCenter, "Notify about succesful login")
Rel(user, CommCenter, "Users's request")
Rel(CommCenter, AuthSvc, "Ask for session authorization")
Rel(CommCenter, HW_Support_Svc, "Exec requested command")
Rel(HW_Support_Svc, DB_Svc, "Save action to log")
Rel(HW_Support_Svc, DB_Svc, "Get required refernce info")
Rel(API_Gate, CommCenter, "Request for execute operation")
Rel(CommCenter, UI_Svc, "Create UI for requesting device")
@endumlобавьте диаграмму.

**Диаграмма компонентов (Components)**

@startuml
title SmartHome System Component Diagram

top to bottom direction

!includeurl c4tpl/C4_Component.puml

Container(AuthSvc, "Authorization Service", "PHP/Yii") {
    Component(ExtAuthController, "ExtAuthController", "Handles authentication by external services")
    Component(InternalAuthController, "IntAuthController", "Handles authentication by self system")
    Component(UIbuiler, "AuthUIbuilder", "Create UI for auth for various platforms")
    Component(AccessManager, "AccessManager", "Controls access to requested resources")
}

Container(UI_Svc, "UI Create&Handle", "PHP/Yii/React/JS") {
    Component(UIfabric, "UIfabric", "Gate for request for creating UI")
    Component(PlatformSupport, "PlatformSupport", "Make same actions for various platform - Web\Mobile\IoT")
    Component(GUIlibSupport, "GUIlibSupport", "Graphic primitive library")
    Component(UserActionsSupport, "UserActionsSupport", "User activity handling")
}

Container(CommCenter, "Commander Center", "PHP/Python") {
    Component(CommandRouter, "CommandRouter", "Route request to destination")
    Component(CommandParser, "CommandParser", "Parse & check command parameters")
    Component(ErrorHandling, "ErrorHandling", "Handle all incorrect actions and cases")
    Component(ActivityLog, "ActivityLog", "Do log all user and components activities")
}

Container(API_Gate, "External API", "PHP/Python") {
    Component(PublisherService, "PublisherService", "Run & handle external requests listener")
    Component(SecuriyLevel, "SecuriyLevel", "Organize safe data exchange")
}

Container(HW_Support_Svc, "Hardware Handling", "PHP/Yii/React/JS") {
    Component(HALsupport, "HWabstractionSupport", "Univesal hardware support system")
    Component(ClimatSupport, "ClimatDevicesSupport", "Supporting heater, air-conditiong")
    Component(SequritySupport, "SequrityDevicesSupport", "Supporting security devices")
    Component(CleaningSupport, "CleaningDevicesSupport", "Supporting cleaning devices")
    Component(MediaSupport, "MultimediaDevicesSupport", "Supporting multimedia devices")
}

Container(DB_Svc, "DataBase Center", "SQL/JSON") {
    Component(DataBaseUnifiedEngine, "DataBaseUnifiedEngine", "Universal DB interface")
    Component(PGsupport, "PGsupport", "PostgreSQL supporter")
    Component(JSONdataSupport, "JSONdataSupport", "Simply JSON data storage support")
    Component(XMLdataSupport, "XMLdataSupport", "Simply XML data storage support")
}

Rel(UIbuiler, UIfabric, "Ask for creating system login prompt")
Rel(UIfabric, UIbuiler, "Create system login prompt")
Rel(UIbuiler, ExtAuthController, "Do authorization by external system")
Rel(UIbuiler, InternalAuthController, "Do authorization by self")

Rel(UIbuiler, PlatformSupport, "Making platform depended manipulations")
Rel(UIbuiler, GUIlibSupport, "Create GUI elemens")
Rel(UserActionsSupport, GUIlibSupport, "Binding UI elemennts to user activities")

Rel(PublisherService, SecuriyLevel, "Check input data")
Rel(PublisherService, CommandParser, "Parse command format")
Rel(CommandParser, AccessManager, "Verify client's access")
Rel(CommandParser, CommandRouter, "Call command's handler")
Rel(CommandRouter, ActivityLog, "Log current action")
Rel(CommandRouter, ErrorHandling, "Handle execution problems")
Rel(CommandRouter, HALsupport, "Exec hardware actions")
Rel(CommandRouter, DataBaseUnifiedEngine, "Read\write required persistent data")

Rel(HALsupport, ClimatSupport, "Exec climate control commands")
Rel(HALsupport, SequritySupport, "Exec sequrity control commands")
Rel(HALsupport, CleaningSupport, "Exec cleaning control commands")
Rel(HALsupport, MediaSupport, "Exec multimedia control commands")
Rel(HALsupport, DataBaseUnifiedEngine, "Read\write required persistent data")

Rel(DataBaseUnifiedEngine, PGsupport, "Implements PostgreSQL storage")
Rel(DataBaseUnifiedEngine, JSONdataSupport, "Implements JSON\KV storage")
Rel(DataBaseUnifiedEngine, XMLdataSupport, "Implements XML\KV storage")

@enduml

**Диаграмма кода (Code)**

@startuml
title SmartHome MS "Commander Center" - component "CommandParser" code diagra

top to bottom direction

!includeurl c4tpl/C4_Component.puml

class Command{
    +string Name
    +string URL
    +ArrayList<> Attributes
    +string Format

    +bool IsCorrect()
    +void PrintMan()
}

class CommandReference {
    #ArrayList<> SupportingCommands
    +bool IsCommandSupported()
}

class CommandAttribute {
    +string Name
    +int ValueType
    +bool IsRequired()
}

class RequestAcceptor{
    +bool ReadInput()
    +bool CanExec()
    +void PoolCommand()
    -bool ParseRAW()
}

class Operation{
    +ArrayList<> CommandChain
    +ArrayList Data
}

RequestAcceptor --+ CommandReference
CommandAttribute "1" -- "0..*" Command : includes
Command "1" -- "0..*" CommandReference : includes
Operation --+ Command


@enduml
# Задание 3. Разработка ER-диаграммы

@startuml

left to right direction

' Пользователи, группы, права
entity User {
    *id
    ---
    Name
}

entity Role {
    *id
    ---
    Name
}

entity Permission {
    *id
    ---
    Name
}

entity RoleMap {
    Role
    Permission
}

entity UserRightsMap {
    Role
    UserID
}

UserRightsMap::Role ||--o{ Role::ID
UserRightsMap::UserID ||--o{ User::ID

RoleMap::Role ||--o{ Role::ID
RoleMap::Permission ||--o{ Permission::ID

' Дома

entity ServicedHouse {
    *id
    ---
    Address
    HomeTitle
    Owner
}

entity HouseLocation {
    *id
    ---
    Name
    Type
}

entity Ref_HouseLocationType {
    *id
    ---
    Name
}

entity HouseStructures {
    House
    ---
    Location
    LocatinKind
}


entity HouseKeepers {
    User
    House
}

HouseLocation::Type ||--|| Ref_HouseLocationType::ID
HouseStructures::House ||--|| ServicedHouse::ID
HouseStructures::Location ||--o{ HouseLocation::ID
ServicedHouse::Owner ||--|| User::ID
HouseKeepers::User ||--o{ User::ID
HouseKeepers::House ||--o{ ServicedHouse::ID

' Устройства

entity ConrolledSystem {
    *id
    ---
    Name
    Type
}

entity ControlDevice {
    *id
    ---
    DisplayName
    HwModel
    UI_URL
    System
}

entity HouseDeviesMap {
    Device
    House
}

entity Ref_DeviceVendors {
    *id
    ---
    Name
    OfficalURL
}

entity Ref_DeviceModels {
    *id
    ---
    Name
    Vendor
    Type
}

Ref_DeviceModels::Vendor ||--o{ Ref_DeviceVendors::ID
ControlDevice::HwModel ||--o{ Ref_DeviceModels::ID
ControlDevice::System ||--|| ConrolledSystem::ID

HouseDeviesMap::Device ||--o{ ControlDevice::ID
HouseDeviesMap::House ||--o{ ServicedHouse::ID

@enduml

# Задание 4. Создание и документирование API

### 1. Тип API

Т.к. количество узлов (дом + его управляемые системы), согласно постановки задачи, хоть и достаточно велико, но не бесконечно и не планируется взрывной рост, а системы достаточно инерционны и часто не требуют мгновенной реакции, смысла вводить в систему дополнительнй компонерт регулировки трафика запросов нет. Достаточно использовать синхронный API с прямыми обращениями к конкретным устройствам.
Маршрутизатор запросов в дальнейшем может быть модернизирован путем добавления перед ним броккера сообщений и переводом API на асинхронный формат обмена.

### 2. Документация API

Здесь приложите ссылки на документацию API для микросервисов, которые вы спроектировали в первой части проектной работы. Для документирования используйте Swagger/OpenAPI или AsyncAPI.

# Задание 5. Работа с docker и docker-compose

Перейдите в apps.

Там находится приложение-монолит для работы с датчиками температуры. В README.md описано как запустить решение.

Вам нужно:

1) сделать простое приложение temperature-api на любом удобном для вас языке программирования, которое при запросе /temperature?location= будет отдавать рандомное значение температуры.

Locations - название комнаты, sensorId - идентификатор названия комнаты

```
	// If no location is provided, use a default based on sensor ID
	if location == "" {
		switch sensorID {
		case "1":
			location = "Living Room"
		case "2":
			location = "Bedroom"
		case "3":
			location = "Kitchen"
		default:
			location = "Unknown"
		}
	}

	// If no sensor ID is provided, generate one based on location
	if sensorID == "" {
		switch location {
		case "Living Room":
			sensorID = "1"
		case "Bedroom":
			sensorID = "2"
		case "Kitchen":
			sensorID = "3"
		default:
			sensorID = "0"
		}
	}
```

2) Приложение следует упаковать в Docker и добавить в docker-compose. Порт по умолчанию должен быть 8081

3) Кроме того для smart_home приложения требуется база данных - добавьте в docker-compose файл настройки для запуска postgres с указанием скрипта инициализации ./smart_home/init.sql

Для проверки можно использовать Postman коллекцию smarthome-api.postman_collection.json и вызвать:

- Create Sensor
- Get All Sensors

Должно при каждом вызове отображаться разное значение температуры

Ревьюер будет проверять точно так же.


