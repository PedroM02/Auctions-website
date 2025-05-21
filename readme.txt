frontend
api(é onde estão definidas as rotas e retorna o valor que vem do crud)
crud(tem a lógica da aplicação, é onde estão as funções que retornam o que é pedido pelo user usando a informação que está na base de dados)
models(cria o modelo da base de dados(tabelas) usando classes de python)
db.connection(conecta à base dedados)
schemas(é onde estão as interfaces dos objetos que vão ser retornados pela api)

api->crud->models->db.connection