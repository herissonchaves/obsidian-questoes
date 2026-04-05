import json
import os
import shutil

os.makedirs('Output', exist_ok=True)
os.makedirs('Output/imagens', exist_ok=True)

notes = {}

# map011
notes['map011'] = {
"banca": "[[UEFS]]", "ano": "", "tipo": "objetiva", "gab": "E",
"enunciado": """1. (UEFS) Ainda é difícil compreender a real dimensão do desastre nuclear de Fukushima, mas o alerta sobre novas ocorrências já foi dado.

(LENDMAN, 2011, p.14-16).

[...] "A energia nuclear não é eficiente, confiável, limpa e muito menos segura. Atualmente ela libera quantidades significativas de gases de efeito estufa e centenas de milhares de curies — unidade de radioatividade —, de gases e elementos radioativos fatais. Elas também são fábricas de bombas atômicas." [...]

A energia nuclear não deve ser aceita como uma forma alternativa de energia para atender à demanda da população humana porque""",
"alts": [
"a) Contribui para estabilizar a temperatura do Planeta pela liberação de gases.",
"b) Induz o desencadeamento de abalos sísmicos com o superaquecimento produzido no funcionamento dos reatores.",
"c) Inviabiliza, pelo seu alto custo, investimentos para a utilização de qualquer outra forma de energia.",
"d) Espolia, com sua utilização, reservas naturais em virtude de ser originada a partir das jazidas de ferro sedimentar.",
"e) Causa, circunstancialmente, mesmo submetida a controle rígido de vazamento, acidentes de efeitos devastadores para o Planeta."
]
}

# map012
notes['map012'] = {
"banca": "[[UNITAU]]", "ano": "", "tipo": "objetiva", "gab": "B",
"enunciado": """1. (UNITAU) A energia elétrica consumida no Brasil é proveniente de diversas fontes, cada uma delas envolvendo um processo próprio de geração de energia. Atualmente, as principais fontes geradoras de energia usadas no Brasil são as hidrelétricas, as usinas nucleares, os parques eólicos, a energia solar e as termelétricas. As sentenças a seguir versam sobre esses processos de geração de energia. Assinale a única que é TOTALMENTE CORRETA.""",
"alts": [
"a) Nas usinas nucleares, a energia é gerada a partir da energia dos ventos.",
"b) Nas usinas hidrelétricas, a energia é gerada a partir da energia de movimento da água dos rios.",
"c) Nas usinas termelétricas, a energia é gerada a partir da queima (combustão) de combustíveis animais.",
"d) Nos parques eólicos, a energia é gerada a partir da energia dos ciclones.",
"e) Nas usinas solares, a energia é gerada a partir da energia dos vulcões."
]
}

# map013
notes['map013'] = {
"banca": "[[URCA]]", "ano": 2017, "tipo": "objetiva", "gab": "C",
"enunciado": """1. (URCA - 2017) No ano de 2017 uma reportagem jornalística destacou que já foram instaladas mais de 500 torres de produção de energia elétrica, a partir da energia eólica (aerogeradores), com mais de 80 metros na Chapada do Araripe que engloba os estados do Piauí, Pernambuco e Ceará (beneficiando agricultores da região com o aluguel de terrenos e provocando alterações do ambiente local).

Em relação à produção da energia elétrica a partir da energia eólica no Brasil e particularmente no estado do Ceará aponte a alternativa incorreta.""",
"alts": [
"a) A production de energia elétrica a partir da energia dos ventos (eólica) é considerada uma energia renovável.",
"b) A energia elétrica produzida para o estado do Ceará é oriunda de diversas fontes, além da energia eólica, também de hidrelétricas, térmicas e fotovoltaica.",
"c) No Brasil a maior parte da energia elétrica, atualmente, é produzida por aerogeradores (energia eólica).",
"d) Em uma turbina eólica, o vento movimenta as pás que gira um rotor transmitindo a rotação ao gerador que transforma a energia mecânica em elétrica.",
"e) A energia eólica provoca impactos para o meio ambiente, por exemplo, ruídos para moradores próximos as torres, pode provocar mortes de aves que se chocam com as pás, etc."
]
}

notes['map014'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "D", "img": "map014.jpg", "old_img": "questoes_1.jpg",
"enunciado": """1. (ENEM) A energia térmica liberada em processos de fissão nuclear pode ser utilizada na geração de vapor para produzir energia mecânica que, por sua vez, será convertida em energia elétrica. Abaixo está representado um esquema básico de uma usina de energia nuclear.

A partir do esquema são feitas as seguintes afirmações:

I. a energia liberada na reação é usada para ferver a água que, como vapor a alta pressão, aciona a turbina.

II. a turbina, que adquire uma energia cinética de rotação, é acoplada mecanicamente ao gerador para produção de energia elétrica.

III. a água depois de passar pela turbina é pré-aquecida no condensador e bombeada de volta ao reator.

Dentre as afirmações acima, somente está(ão) correta(s):""",
"alts": ["a) I.", "b) II.", "c) III.", "d) I e II.", "e) II e III."]
}

notes['map015'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "E", "img": "map015.jpg", "old_img": "questoes_2.jpg",
"enunciado": """1. (ENEM) O setor de transporte, que concentra uma grande parcela da demanda de energia no país, continuamente busca alternativas de combustíveis.

Investigando alternativas ao óleo diesel, alguns especialistas apontam para o uso do óleo de girassol, menos poluente e de fonte renovável, ainda em fase experimental.

Foi constatado que um trator pode rodar, NAS MESMAS CONDIÇÕES, mais tempo com um litro de óleo de girassol, que com um litro de óleo diesel.

Essa constatação significaria, portanto, que usando óleo de girassol,""",
"alts": [
"a) o consumo por km seria maior do que com óleo diesel.",
"b) as velocidades atingidas seriam maiores do que com óleo diesel.",
"c) o combustível do tanque acabaria em menos tempo do que com óleo diesel.",
"d) a potência desenvolvida, pelo motor, em uma hora, seria menor do que com óleo diesel.",
"e) a energia liberada por um litro desse combustível seria maior do que por um de óleo diesel."
]
}

notes['map016'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "B", "img": "map016.jpg", "old_img": "questoes_3.jpg",
"enunciado": """1. (ENEM) A tabela a seguir apresenta alguns exemplos de processos, fenômenos ou objetos em que ocorrem transformações de energia. Nessa tabela, aparecem as direções de transformações de energia. Por exemplo, o termopar é um dispositivo onde energia térmica se transforma em energia elétrica.

Dentre os processos indicados na tabela, ocorre conservação de energia:""",
"alts": [
"a) em todos os processos.",
"b) somente nos processos que envolvem transformações de energia sem dissipação de calor.",
"c) somente nos processos que envolvem transformações de energia mecânica.",
"d) somente nos processos que não envolvem energia química.",
"e) somente nos processos que não envolvem nem energia química nem energia térmica."
]
}

notes['map017'] = {
"banca": "[[UFRGS]]", "ano": "", "tipo": "objetiva", "gab": "C", "img": "map017.jpg", "old_img": "questoes_4.jpg",
"enunciado": """1. (UFRGS) O uso de arco e flecha remonta a tempos anteriores à história escrita. Em um arco, a força da corda sobre a flecha é proporcional ao deslocamento $x$, ilustrado na figura abaixo, a qual representa o arco nas suas formas relaxada I e distendida II.

Uma força horizontal de $200 \\, \\text{N}$, aplicada na corda com uma flecha de massa $m = 40 \\, \\text{g}$, provoca um deslocamento $x = 0{,}5 \\, \\text{m}$. Supondo que toda a energia armazenada no arco seja transferida para a flecha, qual a velocidade que a flecha atingiria, em $\\text{m/s}$, ao abandonar a corda?""",
"alts": [
"a) $5 \\times 10^3$",
"b) $100$",
"c) $50$",
"d) $5$",
"e) $10^{1/2}$"
]
}

notes['map018'] = {
"banca": "[[UFRGS]]", "ano": "", "tipo": "objetiva", "gab": "E", "img": "map018.jpg", "old_img": "questoes_5.jpg",
"enunciado": """1. (UFRGS) O termo horsepower, abreviado hp, foi inventado por James Watt (1783), durante seu trabalho no desenvolvimento das máquinas a vapor. Ele convencionou que um cavalo, em média, eleva $3{,}30 \\times 10^4$ libras de carvão ($1 \\, \\text{libra} \\approx 0{,}454 \\, \\text{kg}$) à altura de um pé ($\\approx 0{,}305 \\, \\text{m}$) a cada minuto, definindo a potência correspondente como $1 \\, \\text{hp}$ (figura abaixo).

Posteriormente, James Watt teve seu nome associado à unidade de potência no Sistema Internacional de Unidades, no qual a potência é expressa em watts ($\\text{W}$). Com base nessa associação, $1 \\, \\text{hp}$ corresponde aproximadamente a""",
"alts": [
"a) $76{,}2 \\, \\text{W}$",
"b) $369 \\, \\text{W}$",
"c) $405 \\, \\text{W}$",
"d) $466 \\, \\text{W}$",
"e) $746 \\, \\text{W}$"
]
}

notes['map019'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "C", 
"enunciado": """1. (ENEM) A usina de Itaipu é uma das maiores hidrelétricas do mundo em geração de energia. Com $20$ unidades geradoras e $14.000 \\, \\text{MW}$ de potência total instalada, apresenta uma queda de $118{,}4 \\, \\text{m}$ e vazão nominal de $690 \\, \\text{m}^3/\\text{s}$ por unidade geradora. O cálculo da potência teórica leva em conta a altura da massa de água represada pela barragem, a gravidade local ($10 \\, \\text{m/s}^2$) e a densidade da água ($1.000 \\, \\text{kg/m}^3$). A diferença entre a potência teórica e a instalada é a potência não aproveitada.

Qual é a potência, em $\\text{MW}$, não aproveitada em cada unidade geradora de Itaipu?""",
"alts": [
"a) $0$",
"b) $1{,}18$",
"c) $116{,}96$",
"d) $816{,}96$",
"e) $13.183{,}04$"
]
}

notes['map020'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "D", "img": "map020.jpg", "old_img": "questoes_6.jpg",
"enunciado": """1. (ENEM) Observe a situação descrita na tirinha a seguir.

Assim que o menino lança a flecha, há transformação de um tipo de energia em outra. A transformação, nesse caso, é de energia""",
"alts": [
"a) potencial elástica em energia gravitacional.",
"b) gravitacional em energia potencial.",
"c) potencial elástica em energia cinética.",
"d) cinética em energia potencial elástica.",
"e) gravitacional em energia cinética."
]
}

notes['map021'] = {
"banca": "[[FATEC-SP]]", "ano": 2006, "tipo": "objetiva", "gab": "A", "img": "map021.jpg", "old_img": "questoes_7.jpg",
"enunciado": """1. (FATEC-SP) Considere o texto a seguir:

**PANORAMA ENERGÉTICO MUNDIAL**
Em termos mundiais, a oferta de energia no ano 2000 foi cerca de $9.963 \\times 10^6$ toneladas equivalentes de petróleo (tEP) e, em 2003, foi cerca de $10.573 \\times 10^6$ tEP, considerando uma taxa de crescimento média anual de $2\\%$.
A desagregação da oferta por fonte energética aponta para um cenário mundial no qual cerca de $87\\%$ de toda a energia provém de fontes não renováveis e somente $13\\%$ de fontes renováveis.
Portanto, o planeta é movido por fontes não renováveis de energia, e o fim desta era “não renovável” está próximo.

A palavra de ordem, para o século XXI, é a busca em larga escala, de fontes de energias renováveis.
(Curso de Gestão Ambiental – Autores: Arlindo Philippi Jr., Marcelo A. Romero, Gilda C Bruna – p.925 e 926 – USP – 2006 – Adaptado)

De acordo com as informações do texto, a oferta de energia que provém de fontes renováveis, em 2001, foi,
em toneladas equivalentes de petróleo, cerca de""",
"alts": [
"a) $1.300 \\times 10^6$.",
"b) $1.320 \\times 10^6$.",
"c) $1.340 \\times 10^6$.",
"d) $1.350 \\times 10^6$.",
"e) $1.370 \\times 10^6$."
]
}

notes['map022'] = {
"banca": "[[ENEM]]", "ano": "", "tipo": "objetiva", "gab": "E", 
"enunciado": """1. (ENEM) Muitas usinas hidroelétricas estão situadas em barragens. As características de algumas das grandes represas e usinas brasileiras estão apresentadas no quadro abaixo.

| Usina | Área alagada (Km²) | Potência (MW) | Sistema Hidrográfico |
|-------|--------------------|---------------|----------------------|
| Tucuruí | 2.430 | 4.240 | Rio Tocantins |
| Sobradinho | 4.214 | 1.050 | Rio São Francisco |
| Itaipu | 1.350 | 12.600 | Rio Paraná |
| Ilha Solteira | 1.077 | 3.230 | Rio Paraná |
| Furnas | 1.450 | 1.312 | Rio Grande |

A razão entre a área da região alagada por uma represa e a potência produzida pela usina nela instalada é uma das formas de estimar a relação entre o dano e o benefício trazidos por um projeto hidroelétrico.

A partir dos dados apresentados no quadro, o projeto que mais onerou o ambiente em termos de área alagada por potência foi""",
"alts": [
"a) Tucuruí.",
"b) Furnas.",
"c) Itaipu.",
"d) Ilha Solteira.",
"e) Sobradinho."
]
}

notes['map023'] = {
"banca": "", "ano": "", "tipo": "objetiva", "gab": "D", 
"enunciado": """1. O debate em torno do uso da energia nuclear para produção de eletricidade permanece atual. Em um encontro internacional para a discussão desse tema, foram colocados os seguintes argumentos:

I. Uma grande vantagem das usinas nucleares é o fato de não contribuírem para o aumento do efeito estufa, uma vez que o urânio, utilizado como “combustível”, não é queimado, mas sofre fissão.

II. Ainda que sejam raros os acidentes com usinas nucleares, seus efeitos podem ser tão graves que essa alternativa de geração de eletricidade não nos permite ficar tranquilos.

A respeito desses argumentos, pode-se afirmar que""",
"alts": [
"a) o primeiro é válido e o segundo não é, já que nunca ocorreram acidentes com usinas nucleares.",
"b) o segundo é válido e o primeiro não é, pois de fato há queima de combustível na geração nuclear de eletricidade.",
"c) o segundo é válido e o primeiro é irrelevante, pois nenhuma forma de gerar eletricidade produz gases do efeito estufa.",
"d) ambos são válidos para se compararem vantagens e riscos na opção por essa forma de geração de energia.",
"e) ambos são irrelevantes, pois a opção pela energia nuclear está se tornando uma necessidade inquestionável."
]
}

notes['map024'] = {
"banca": "", "ano": "", "tipo": "objetiva", "gab": "C", 
"enunciado": """1. O petróleo é uma das principais fontes de energia não renováveis e é utilizado em diversos setores. Considerando seu impacto ambiental, assinale a alternativa que apresenta uma consequência significativa do uso excessivo de petróleo.""",
"alts": [
"a) Aumento das áreas de deserto em regiões tropicais.",
"b) Diminuição da qualidade do ar em áreas urbanas.",
"c) Aumento das emissões de gases do efeito estufa.",
"d) Alterações na fauna e flora marinha.",
"e) Poluição das águas em regiões costeiras."
]
}

notes['map025'] = {
"banca": "[[FUVEST]]", "ano": 2018, "tipo": "objetiva", "gab": "C", 
"enunciado": """1. (FUVEST - 2018) Após a assinatura do Protocolo de Quioto em 1997, estabeleceu-se a criação de um mercado mundial de créditos de carbono, relacionado à necessidade de redução das emissões de gases do efeito estufa. Sobre esse assunto, é correto afirmar que""",
"alts": [
"a) os acordos internacionais resultam da busca de soluções comuns para os problemas ambientais, o que leva à superação de conflitos políticos e interesses divergentes.",
"b) o Protocolo de Quioto foi o primeiro acordo internacional resultante da Conferência de Estocolmo, na qual se debateram estratégias de desenvolvimento sustentável.",
"c) a venda de créditos de carbono tem estimulado os países altamente poluidores no desenvolvimento de tecnologia limpa e na alteração do padrão de produção-consumo.",
"d) esse mercado permite que países com altas taxas de emissões de carbono possam comprar cotas de países que produzem menos CO2.",
"e) as metas de redução da emissão de gases do efeito estufa são comuns a todos os países, uma vez que prevalece o princípio de que a responsabilidade é coletiva."
]
}

def write_md(id_local, note):
    banca = note.get('banca', '')
    ano = note.get('ano', '')
    tipo = note.get('tipo', 'objetiva')
    gab = note.get('gab', '')
    enun = note['enunciado']
    alts = note.get('alts', [])
    img_filename = note.get('img')
    old_img_filename = note.get('old_img')

    if old_img_filename and os.path.exists(f"Output/imagens/{old_img_filename}"):
        shutil.copy(f"Output/imagens/{old_img_filename}", f"Output/imagens/{img_filename}")

    md = f"""---
id: {id_local}
disciplina: Map_Natureza
topico:
  - "[[Energia]]"
conteudo:
  - "[[Fontes de Energia]]"
assunto:
  - "[[Matriz Energetica]]"
banca: "{banca}"
ano: {ano if ano else '""'}
tipo: {tipo}
dificuldade: "[[media]]"
gabarito: {gab if gab else '""'}
resolucao_link: ""
selecionada: false
---

{enun}
"""
    if img_filename:
        md += f"\n![[01 - Sources/imagens/{img_filename}]]\n"
    
    if alts:
        md += "\n" + "\n\n".join(alts) + "\n"
    elif tipo == 'discursiva':
        md += "\n\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\n"
        md += "\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\n"
        md += "\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\_\\n"

    with open(f'{id_local}.md', 'w', encoding='utf-8') as f:
        f.write(md)

for k, v in notes.items():
    write_md(k, v)

print("Gerados map011 a map025.")
