### 1. Склонировать репозиторий
```bash
git clone https://github.com/iamblessed-asd/doc-service.git
```
### 2. Перейти в репозиторий
```bash
cd doc-service
```
### 3. Собрать сервис
```bash
docker-compose up --build
```
### 4. Использовать сервис:


Сервис будет доступен по адресу http://localhost:8000.
Документация Swagger: http://localhost:8000/docs

Примеры запросов в PowerShell (В URL надо указывать $docId - ID документа)
#### 1. Получение JWT токена
```bash
$body = @{
    username = "alice"
    password = "any"
}

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/token" `
    -Method Post `
    -Body $body `
    -ContentType "application/x-www-form-urlencoded"

$token = $response.access_token
Write-Host "Token: $token"
```
#### 2. Создание документа
```bash
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$docBody = @{
    title = "Мой документ"
    content = @{
        name = "Тест"
        age = 30
        address = @{
            city = "Москва"
            street = "Тверская"
        }
    }
} | ConvertTo-Json -Depth 5

$doc = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/" `
    -Method Post `
    -Headers $headers `
    -Body $docBody

$docId = $doc.id
Write-Host "Document created with ID: $docId"
```
#### 3. Получить документ целиком
```bash
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$doc = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId" `
    -Headers $headers
$doc | ConvertTo-Json -Depth 5
```
#### 4. Получить часть документа по пути (В примере ищется город по path=address.city)
```bash
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId?path=address.city" `
    -Headers $headers
$response.content 
```
#### 5. Полное обновление документа (PUT)
```bash
$updateBody = @{
    title = "Новый заголовок"
    content = @{
        name = "Обновлённый тест"
        age = 31
    }
} | ConvertTo-Json -Depth 5

$updated = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId" `
    -Method Put `
    -Headers $headers `
    -Body $updateBody
$updated | ConvertTo-Json -Depth 5
```
#### 6. Частичное обновление
```bash
$patchBody = @{
    path = "address.city"
    value = "Санкт-Петербург"
} | ConvertTo-Json

$patched = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId/path" `
    -Method Patch `
    -Headers $headers `
    -Body $patchBody
$patched | ConvertTo-Json -Depth 5
```
#### 7. Удаление части документа по пути
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId/path?path=address" `
    -Method Delete `
    -Headers $headers
```
#### 8. Удаление документа целиком
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/$docId" `
    -Method Delete `
    -Headers $headers
```
#### 9. Сравнение двух документов
Нужно указать ID документов $id1 и $id2:

```bash
$compare = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/compare/$id1/$id2" `
    -Headers $headers
$compare | ConvertTo-Json -Depth 5
```
#### 10. Проверка здоровья сервиса
```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/"
```
