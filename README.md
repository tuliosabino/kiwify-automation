# Sobre o projeto
Essa aplicação tem como objetivo automatizar a criação e configuração (pagamento, checkout, área de membros) de cursos na Kiwify, usando o Playwright.

Muitos dados utilizados no código vieram de outros apps, então alguns trechos podem não fazer muito sentido no contexto dessa aplicação.

Algumas coisas ainda serão implementadas, principalmente a documentação, mas o app já está funcional e pode ser usado/adaptado.


# Como usar
Toda a configuração da aplicação é feita por dois arquivos [.env](.env_example), onde é configurado o ambiente onde a automação está rodando e [config.py](/src/config_example.py), onde são configuradas todas as informações sobre os cursos que serão cadastrados.

Além disso toda a estrutura do curso já deve estar pronta em uma objeto List, no meu caso tenho a função [get_structure](/src/pages/course.py#L24) que retorna essa estrutura. [Aqui](#estrutura-do-curso) você confere um exemplo dessa estrutura.

## .env

Você deve renomear o arquivo [.env_example](.env_example) para .env e configurar conforme seu ambiente.

Explicação das configurações de ambiente:
| Constante | Descrição |
| --------- | --------- |
| `CROME_EXE` | Caminho do executável do Google Chrome, deixar em branco para utilizar o default do Chrome.|
| `CHROME_USER_DATA_DIR` | Caminho para os dados de navegação (cookies, seção, etc..), deixar a string em branco para usar uma pasta temporária, isso vai requerir que você faça login a cada execução do script, o ideal já é configurar algum caminho para que esses dados fiquem salvos. |
| `EMAIL`|  E-mail de login de sua conta da Kiwify |
|`PASSWORD` | Senha de login de sua conta da Kiwify |
| `GET_STRUCTURE_PATH` | No meu caso essa constante representa o caminho do módulo que contém a função que fornece a estrutura do curso a ser cadastrado. Essa parte do código não posso compartilhar, mas deixarei um [exemplo](#estrutura-do-curso) mais abaixo da estrutura retornada por ela. Aqui você terá que adaptar o código. |
| `CREATION_META_PATH` | Caminho para o módulo do arquivo que contém os meta dados do curso a ser criado. Também deixarei um [exemplo](#meta-dados-do-curso) mais abaixo. Nesse caso você pode colocar esse arquivo dentro dessa aplicação, no meu caso esse arquivo está sendo reaproveitado. |

## config.py

Você deve renomear o arquivo [config_example.py](src/config_example.py) para config.py.

Nesse arquivo você deve setar todas as configurações e informações referentes ao cadastro e envio do(s) curso(s) para a Kiwify.

| Constante | Descrição |
| --------- | --------- |
| `ACCOUNT_NAME` | Nome da conta Kiwify onde o curso será criado. Funciona apenas se a conta que for logada for colaborador de alguma outra conta. Deixar uma strign vazia para não utilizar essa opção |
| `DOMAIN` | Domínio onde a página do produto(s) está hospedada. |
| `SUPPORT_EMAIL` | E-mail de suporte que aparece no checkout do produto. |
| `PRODUCER_DISPLAY_NAME` | Nome que é mostrado para os compradores do produto. |
| `PHONE_NUMBER` | Número de Whatsapp para aparecer como suporte dentro do curso, na primeira aula. Deixar a string vazia para não criar o link na aula. Deve estar no formato "00-00000-0000"( DDD, 5 Primeiros Dígitos e 4 Digitos restantes separados por `-`) |
| `PAYMENT_OPTION` | Define quais formas de pagamento serão aceitas. Deve ser uma string com uma das opções: "1" para Cartão de Crédito e Boleto; "2" para apenas Cartão de Crédito; "3" para todas as formas de pagamento; "4" para Cartão de Crédito e Pix. |
| `PAYMENT_TIMES` | Quantidade máxima de parcelas permiticas para o produto. No máximo 12. |
| `EXIT_POPUP_DISCOUNT` | Percentual que será oferecido no Exit Popup. Deve ser um int. Deixar 0 ou False para não utilizar o Exit Popup. |
| `CHECKOUT_PHONE_NUMBER` | Número de Whatsapp para aparecer no Checkout do produto, utiliza um plugin da plataforma que exibe um botão do whatsapp para o possível comprador entrar em contato. Deixar a string vazia para não utilizar esse botão. Deve estar no formato "00000000000" (DDD e número juntos, sem separação) |
| `ADDITIONAL_PLAN` | Nome do plano adicional a ser criado, utiliza o valor de "additional" dentro da variável COURSES. Deixar a string vazia para não criar planos adicionais |
| `COURSES` | Um dicionário onde as chaves são a course_tag e o valor é outro dicionário com os preços do curso. Essa course_tag será usada para identificar o curso durante toda a execução do script e também para buscar ma estrutura e nos meta dados as informações do curso. no arquivo [config_example.py](src/config_example.py#L48) tem um exemplo de como deve ser esse dicionário. |

## Estruturas de dados

Exemplos das estruturas de dados utilizados na execução do script.

### Estrutura do curso

Nesta implementação optei por reutilizar uma função de outra aplicação minha que retorna uma lista de dicionários com as informações sobre o conteúdo do curso (módulos, aulas, etc..), essa função foi definida [aqui](src/pages/course.py#L23) e é utilizada [aqui](src/pages/course.py#L34). Você precisará adaptar isso para a sua realidade.

Segue o exemplo da estrutura retornada pela função, com comentários sobre o que cada item significa e exemplo de valores:

```python
[ # Lista de dicionários, onde cada dicionário representa um módulo do curso
    { # Primeiro módulo
        # Nome do Módulo
        'modulo': 'Boas Vindas',
        # lista com as aulas desse módulo
        'aulas': [
            {
                # Nome da aula
                'nome': 'Boas Vindas',
                # Descrição da aula
                'desc_doppus': [
                        # O conteúdo da descrição pode ter texto
                        # ou link ou uma mistura dos dois
                        {
                            'tipo': 'Texto',
                            'conteudo': '''Exemplo de descrição em texto.'''
                        },
                        {
                            'tipo': 'Link',
                            'conteudo': 'https://seulink.com.br',
                            'texto_fixo': 'Texto que aparecerá para ser clicável', 
                        }
                    ],
                # Se o curso for um bônus a automação colocara
                # para a aulaser liberada somente após 8 dias
                'is_bonus': False,
                # Caminho do arquivo de vídeo da aula
                'video': r'D:\MeuCurso\Aulas\Boas Vindas\01 Boas Vindas.mp4',
                # Lista de arquivos adicionais da aula
                'files': [r'D:\MeuCurso\Files\pdf_extra.pdf']
            }
        ]
    },
    { # Segundo Módulo
        'modulo': 'Módulo 02',
        'aulas': [
            {
                'nome': 'Aula 01',
                'desc_doppus': [
                    {
                        'tipo': 'Link',
                        'conteudo': 'https://link3.com/',
                        'texto_fixo': 'Clique aqui para acessar o site!'
                    }
                ],
                'is_bonus': False,
                'video': r'D:\Aulas\Módulo 02\01 Aula 01.mp4',
                'files': []
            },
            {
                'nome': 'Aula 02',
                'desc_doppus': [
                    {
                        'tipo': 'Link',
                        'conteudo': 'https://link4.com/',
                        'texto_fixo': 'Site sobre a aula!'
                    }
                ],
                'is_bonus': False,
                'video': r'D:\MeuCurso\Aulas\Módulo 02\01 Aula 02.mp4',
                'files': [r'D:\MeuCurso\Files\pdf_extra2.pdf']
            }
        ]
    }
]
```

### Meta dados do Curso

Aqui fica as informações sobre a criação do produto em si, ou seja, o curso que será criado.

No meu caso esses dados ficam armazenados em uma variável, [creation_data](src/pages/course.py#L27), que é uma lista de dicionários, onde cada um representa os dados de um curso.

```python
{
    # Nome do seu curso
    'name': 'Curso de Exemplo',
    # Descrição breve do seu curso, com no máximo 500 caracteres
    'descrição': '''Este curso é uma exemplificação
Fique a vontade para modificar como achar melhor!''',
    # Nicho/Categoria do seu curso, A Kiwify tem os valores predefinidos,
    # você precisa conferir quais são na tela de criação de produto
    # e colocar o valor exatamente como está lá
    'category_kiwify': 'Apps & Software',
    # Caminho para as imagens do produto. Irei deixar abaixo uma lista
    # com os tamanhos necessários e onde é utilizado cada imagem
    'path_to_images': r'D:\MeuCurso\Imagens',
    # tags dos outros produtos que serão orderbump desse
    'orderbump': ['produto1', 'produto2'],
    # texto desse produto que será usado quando ele estiver de orderbump em outro
    'orderbump_text': 'Aumente suas habilidades com o nosso curso!!',
    # aqui é mais 1 produto que será utilizado como order bump, como disse
    # anteriormente esses dados são reaproveitados de outro app, então
    # nesse caso não faz muito sentido ter o upsell, poderia ser somente
    # o orderbump, ajuste como achar melhor!
    'upsell': ['produto3']
},
```


### Lista das imagens necessárias

As imagens também reaproveitei de outra aplicação. Isso siginifica que utilizei que não são do tamanho ideal para a Kiwify, e que o nome delas no meu script também vai ser diferente.

Você pode utilizar o nome que está no script ou alterar o código para ficar com os nomes corretos. Em todo caso deixarei abaixo todas as informações.

| Tamanho ideal da imagem | Onde é utilizada | Nome salvo no script |
| ----------------------- | ---------------- | -------------------- |
| 320x480 pixels | Capa de módulo | 800x500.png |
| 2000x590 pixels | Topo da área de membros no desktop | 1140x300.png |
| 400x400 pixels | Topo da área de membros no mobile | 600x600.png |
| N/A ¹ | Topo do checkout | 1140x300.png |
| 200x300 ² | Exit Popup | discount.png |

1. Nessa imagem você pode colocar o tamanho que achar ideal que ela se ajustara. só terá que mudar [aqui](src/pages/course.py#L661) no código por conta de ser o mesmo nome da imagem de topo da área de membros.

2. Essa imagem fica salva em [src/images](src/images).
