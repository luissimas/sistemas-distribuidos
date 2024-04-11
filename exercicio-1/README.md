# Exercício 1

Implementação de um client e um server utilizando o [padrão de request/response](https://zeromq.org/socket-api/#request-reply-pattern).

A ideia é conseguirmos medir a capacidade de serviço do sistema com base nas latências médias.

## Executando

Para fins de testes, podemos executar os arquivos diretamente sem gerar um binário compilado com o comando `go run`. Executando o server:

``` sh
go run server.go
```

Executando o client:

``` sh
go run client.go
```
