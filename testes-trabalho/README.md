# Testes trabalho

Scripts de teste usados para explorar aspectos do trabalho prático da disciplina. Esse projeto é gerenciado usando [Poetry](https://python-poetry.org/), certifique-se de ter a ferramenta instalada em seu sistema.

## Instalação

Para instalar as dependências do projeto, basta executar o seguinte comando no diretório do projeto: 

```sh
poetry install
```

## ZeroMQ pubsub

Implementação de uma sala de chat através de um broker usando mecanismo de pubsub. O arquivo `server.py` implementa um broker que repassa as mensagens recebidas para os subscribers do tópico pertencente a mensagem. O arquivo `client.py` implementa um client que se comunica com o broker e permite o envio e recebimento de mensagens para uma sala.

Executando o servidor:

```sh
poetry run python testes_trabalho/server.py 
```

Executando o client:

```sh
poetry run python testes_trabalho/client.py 
```

É interessante executar vários clients na mesma sala e alguns em salas diferentes para visualizar o roteamento das mensagens.

## OpenCV

A biblioteca OpenCV nos permite capturar e manipular vídeos e imagens. O arquivo `video.py` captura um vídeo da sua webcam e o salva em um arquivo `video.mp4`.

Para gravar o vídeo:

```sh
poetry run python testes_trabalho/video.py 
```
