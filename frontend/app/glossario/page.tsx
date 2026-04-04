import { Metadata } from 'next';
import Link from 'next/link';
import LandingNavbar from '../components/landing/LandingNavbar';
import Footer from '../components/Footer';

export const metadata: Metadata = {
  title: 'Glossario de Licitacoes: 50 Termos Essenciais | SmartLic',
  description:
    'Glossario completo com 50 termos de licitacoes publicas explicados de forma pratica. Adjudicacao, pregao eletronico, PNCP, SRP e mais. Referencia essencial para empresas B2G.',
  alternates: {
    canonical: 'https://smartlic.tech/glossario',
  },
  openGraph: {
    title: 'Glossario de Licitacoes: 50 Termos Essenciais | SmartLic',
    description:
      'Referencia completa para profissionais de licitacoes. 50 termos explicados com definicoes claras e exemplos praticos.',
    type: 'website',
    url: 'https://smartlic.tech/glossario',
    siteName: 'SmartLic',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Glossario de Licitacoes: 50 Termos Essenciais | SmartLic',
    description:
      'Referencia completa para profissionais de licitacoes. 50 termos explicados com definicoes claras e exemplos praticos.',
  },
};

/* ---------------------------------------------------------------------------
 * Data
 * --------------------------------------------------------------------------- */

interface GlossaryTerm {
  term: string;
  slug: string;
  definition: string;
  example: string;
  guideHref: string;
  guideLabel: string;
}

const TERMS: GlossaryTerm[] = [
  // A
  {
    term: 'Adjudicacao',
    slug: 'adjudicacao',
    definition:
      'Ato formal pelo qual a autoridade competente atribui o objeto da licitacao ao licitante que apresentou a proposta mais vantajosa. Na Lei 14.133/2021, a adjudicacao ocorre apos a habilitacao e o julgamento dos recursos, consolidando o direito do vencedor a assinatura do contrato.',
    example:
      'Apos o pregao eletronico para aquisicao de 500 computadores, o pregoeiro adjudicou o objeto a empresa que ofertou R$ 2.800 por unidade, o menor preco valido apos a fase de lances.',
    guideHref: '/blog',
    guideLabel: 'Como funciona o processo licitatorio',
  },
  {
    term: 'Aditivo Contratual',
    slug: 'aditivo-contratual',
    definition:
      'Instrumento juridico utilizado para alterar clausulas de um contrato administrativo vigente, podendo modificar prazos, valores ou escopo. A Lei 14.133 limita acrescimos e supressoes a 25% do valor original (50% para reformas de edificios ou equipamentos).',
    example:
      'Um contrato de manutencao predial de R$ 1.200.000 recebeu aditivo de 20% (R$ 240.000) para incluir a reforma do sistema de ar-condicionado, dentro do limite legal.',
    guideHref: '/blog',
    guideLabel: 'Gestao de contratos publicos',
  },
  {
    term: 'Anulacao',
    slug: 'anulacao',
    definition:
      'Invalidacao de um processo licitatorio ou contrato administrativo por vicio de legalidade identificado pela propria administracao ou pelo Judiciario. A anulacao tem efeito retroativo (ex tunc), desfazendo todos os atos praticados desde a origem do vicio.',
    example:
      'O Tribunal de Contas determinou a anulacao de um pregao porque o edital exigia certificacao ISO especifica que restringia a competitividade sem justificativa tecnica.',
    guideHref: '/blog',
    guideLabel: 'Recursos e impugnacoes em licitacoes',
  },
  {
    term: 'Ata de Registro de Precos',
    slug: 'ata-de-registro-de-precos',
    definition:
      'Documento vinculativo que formaliza precos, fornecedores, orgaos participantes e condicoes para aquisicoes futuras dentro do Sistema de Registro de Precos (SRP). A ata tem validade de ate 1 ano (prorrogavel por mais 1 ano na Lei 14.133) e nao obriga o orgao a contratar.',
    example:
      'A Secretaria de Saude registrou precos de 30 tipos de medicamentos com 5 fornecedores. Durante 12 meses, qualquer hospital da rede pode emitir ordens de compra com os precos registrados sem nova licitacao.',
    guideHref: '/blog',
    guideLabel: 'Sistema de Registro de Precos na pratica',
  },
  {
    term: 'Atestado de Capacidade Tecnica',
    slug: 'atestado-de-capacidade-tecnica',
    definition:
      'Documento emitido por pessoa juridica de direito publico ou privado, comprovando que a empresa executou anteriormente servico ou obra similar ao objeto licitado. E o principal instrumento de qualificacao tecnica na fase de habilitacao.',
    example:
      'Para participar de licitacao de pavimentacao asfaltica de 15 km, a empresa apresentou atestado de prefeitura vizinha comprovando execucao de 12 km de pavimentacao concluida em 2024.',
    guideHref: '/blog',
    guideLabel: 'Habilitacao tecnica em licitacoes',
  },
  // B
  {
    term: 'Balanco Patrimonial',
    slug: 'balanco-patrimonial',
    definition:
      'Demonstracao contabil que apresenta a posicao financeira da empresa em determinada data, evidenciando ativos, passivos e patrimonio liquido. E exigido na habilitacao economico-financeira para comprovar indices como liquidez geral e endividamento.',
    example:
      'O edital exigia Indice de Liquidez Geral >= 1,0. A empresa apresentou balanco patrimonial de 2025 com ativo circulante de R$ 3.200.000 e passivo circulante de R$ 2.100.000, resultando em ILG de 1,52 — aprovada na habilitacao.',
    guideHref: '/blog',
    guideLabel: 'Habilitacao economico-financeira',
  },
  {
    term: 'BDI (Beneficios e Despesas Indiretas)',
    slug: 'bdi',
    definition:
      'Percentual aplicado sobre o custo direto de obras ou servicos que engloba despesas indiretas (administracao central, seguros, garantias), tributos e lucro. O BDI compoe o preco final da proposta e e objeto de analise detalhada pelos orgaos de controle.',
    example:
      'Em licitacao de obra publica, a empresa calculou custo direto de R$ 800.000 e aplicou BDI de 28,5%, resultando em preco final de R$ 1.028.000. O TCU considerou o percentual compativel com a referencia SINAPI.',
    guideHref: '/blog',
    guideLabel: 'Formacao de precos em obras publicas',
  },
  {
    term: 'BEC (Bolsa Eletronica de Compras)',
    slug: 'bec',
    definition:
      'Sistema eletronico de compras do governo do estado de Sao Paulo, utilizado para aquisicao de bens e servicos por orgaos estaduais e municipais paulistas. Funciona como plataforma de pregao eletronico e oferta de compra com catalogo de produtos padronizados.',
    example:
      'A Secretaria de Educacao de SP publicou oferta de compra na BEC para 10.000 cadeiras escolares. Fornecedores cadastrados no CAUFESP ofertaram precos diretamente na plataforma durante 3 dias.',
    guideHref: '/blog',
    guideLabel: 'Portais de compras estaduais',
  },
  // C
  {
    term: 'Cadastro de Fornecedores (SICAF)',
    slug: 'sicaf',
    definition:
      'O Sistema de Cadastramento Unificado de Fornecedores (SICAF) e o registro oficial do governo federal que centraliza dados cadastrais, habilitacao juridica, regularidade fiscal e qualificacao economica de empresas que fornecem ao poder publico. O cadastro simplifica a participacao em licitacoes federais.',
    example:
      'Antes de participar do pregao do Ministerio da Saude, a empresa atualizou seu SICAF com certidoes negativas federais, estaduais e municipais, balanco patrimonial e contrato social atualizado.',
    guideHref: '/blog',
    guideLabel: 'Como se cadastrar no SICAF',
  },
  {
    term: 'Certidao Negativa',
    slug: 'certidao-negativa',
    definition:
      'Documento oficial emitido por orgaos publicos que atesta a inexistencia de debitos ou pendencias do contribuinte. Na habilitacao, sao exigidas certidoes negativas de debitos federais (CND/PGFN), estaduais, municipais, FGTS e trabalhistas (CNDT).',
    example:
      'A empresa foi inabilitada porque a Certidao Negativa de Debitos Trabalhistas (CNDT) estava vencida ha 3 dias na data da sessao do pregao — ressaltando a importancia de monitorar vencimentos.',
    guideHref: '/blog',
    guideLabel: 'Documentos de habilitacao',
  },
  {
    term: 'Chamada Publica',
    slug: 'chamada-publica',
    definition:
      'Modalidade simplificada de selecao utilizada principalmente para aquisicao de alimentos da agricultura familiar no ambito do Programa Nacional de Alimentacao Escolar (PNAE). A Lei 11.947/2009 determina que no minimo 30% dos recursos do PNAE sejam destinados a compras via chamada publica.',
    example:
      'A prefeitura publicou chamada publica para aquisicao de 5 toneladas de hortalicas organicas de agricultores familiares locais para merenda escolar, com preco baseado no mercado atacadista regional.',
    guideHref: '/blog',
    guideLabel: 'Vendendo para programas de alimentacao escolar',
  },
  {
    term: 'ComprasNet',
    slug: 'comprasnet',
    definition:
      'Portal eletronico de compras do governo federal brasileiro, operado desde 2000, que concentra pregoes eletronicos, cotacoes e licitacoes federais. Esta sendo gradualmente substituido pelo PNCP (Portal Nacional de Contratacoes Publicas) conforme a Lei 14.133/2021.',
    example:
      'Ate 2025, o ComprasNet processou mais de R$ 50 bilhoes/ano em pregoes eletronicos federais. Empresas que ja operavam no ComprasNet precisam migrar seus cadastros para o PNCP ate o prazo de transicao.',
    guideHref: '/blog',
    guideLabel: 'Migracao ComprasNet para PNCP',
  },
  {
    term: 'Concorrencia',
    slug: 'concorrencia',
    definition:
      'Modalidade licitatoria destinada a contratacoes de maior vulto, com ampla publicidade e prazos mais longos. Na Lei 14.133/2021, a concorrencia e utilizada para obras, servicos de engenharia e compras acima dos limites do pregao, admitindo os criterios de julgamento menor preco, melhor tecnica ou tecnica e preco.',
    example:
      'O DNIT abriu concorrencia para construcao de ponte com valor estimado de R$ 45 milhoes. O prazo de publicacao do edital foi de 35 dias uteis, permitindo ampla participacao de construtoras de todo o pais.',
    guideHref: '/blog',
    guideLabel: 'Modalidades de licitacao',
  },
  {
    term: 'Consorcio',
    slug: 'consorcio',
    definition:
      'Agrupamento formal de duas ou mais empresas para participar conjuntamente de licitacao, somando capacidades tecnicas e financeiras. O consorcio nao cria nova pessoa juridica — cada consorciada mantem sua individualidade e responde solidariamente pelas obrigacoes.',
    example:
      'Tres empresas de TI formaram consorcio para disputar contrato de R$ 80 milhoes de modernizacao de datacenter: uma com expertise em infraestrutura, outra em seguranca e a terceira em cloud migration.',
    guideHref: '/blog',
    guideLabel: 'Consorcio em licitacoes',
  },
  {
    term: 'Contrato Administrativo',
    slug: 'contrato-administrativo',
    definition:
      'Acordo formal celebrado entre a administracao publica e o fornecedor vencedor da licitacao, estabelecendo direitos, obrigacoes, prazos e condicoes de execucao. Diferente dos contratos privados, o contrato administrativo possui clausulas exorbitantes que conferem prerrogativas especiais ao poder publico.',
    example:
      'Apos adjudicacao e homologacao de pregao para servicos de limpeza, o hospital publico assinou contrato administrativo de 12 meses com a empresa vencedora, no valor mensal de R$ 185.000, com clausulas de fiscalizacao e penalidades.',
    guideHref: '/blog',
    guideLabel: 'Execucao de contratos publicos',
  },
  // D
  {
    term: 'Dialogo Competitivo',
    slug: 'dialogo-competitivo',
    definition:
      'Modalidade licitatoria introduzida pela Lei 14.133/2021 para contratacoes de objetos inovadores ou tecnicamente complexos, onde a administracao dialoga com licitantes pre-selecionados para desenvolver solucoes antes da fase de propostas. E indicado quando o orgao nao consegue definir especificacoes tecnicas de forma precisa.',
    example:
      'O Ministerio da Ciencia abriu dialogo competitivo para sistema de inteligencia artificial de monitoramento ambiental. Tres empresas foram selecionadas para 60 dias de dialogos tecnicos antes de submeterem propostas finais.',
    guideHref: '/blog',
    guideLabel: 'Novas modalidades da Lei 14.133',
  },
  {
    term: 'Dispensa de Licitacao',
    slug: 'dispensa-de-licitacao',
    definition:
      'Hipotese de contratacao direta prevista em lei, onde a licitacao e dispensavel por razoes de valor (ate R$ 59.906,02 para compras em 2026), emergencia, situacao especifica ou outros casos do art. 75 da Lei 14.133. Difere da inexigibilidade porque a competicao seria possivel, mas a lei autoriza sua dispensa.',
    example:
      'A universidade contratou diretamente servico de conserto de ar-condicionado por R$ 42.000, enquadrado na dispensa por valor (limite de R$ 59.906,02 para servicos em 2026), com pesquisa de precos de 3 fornecedores.',
    guideHref: '/blog',
    guideLabel: 'Contratacao direta: dispensa e inexigibilidade',
  },
  {
    term: 'Dotacao Orcamentaria',
    slug: 'dotacao-orcamentaria',
    definition:
      'Previsao de recursos financeiros consignada no orcamento publico (LOA) destinada a cobrir determinada despesa. Nenhuma licitacao pode ser lancada sem dotacao orcamentaria que garanta os recursos necessarios para pagamento da contratacao.',
    example:
      'O edital de pregao para mobiliario escolar indicou a dotacao orcamentaria 12.361.0001.2035 — Programa de Equipamentos Escolares, com credito disponivel de R$ 2.300.000 no exercicio de 2026.',
    guideHref: '/blog',
    guideLabel: 'Orcamento publico e licitacoes',
  },
  // E
  {
    term: 'Edital',
    slug: 'edital',
    definition:
      'Instrumento convocatorio que estabelece todas as regras, exigencias, prazos e criterios de uma licitacao. E a "lei interna" do processo licitatorio — tudo o que nao esta no edital nao pode ser exigido, e tudo o que esta nele vincula tanto a administracao quanto os licitantes.',
    example:
      'O edital do Pregao Eletronico 045/2026 da Prefeitura de Curitiba especificava: objeto (500 notebooks), prazo de entrega (60 dias), criterio de julgamento (menor preco por lote), habilitacao exigida e modelo de proposta.',
    guideHref: '/blog',
    guideLabel: 'Como analisar editais de licitacao',
  },
  {
    term: 'Estudo Tecnico Preliminar (ETP)',
    slug: 'estudo-tecnico-preliminar',
    definition:
      'Documento obrigatorio na fase preparatoria da licitacao (Lei 14.133, art. 18) que demonstra a necessidade da contratacao, analisa solucoes disponiveis no mercado e define requisitos tecnicos. O ETP embasa o Termo de Referencia e e publicado no PNCP.',
    example:
      'Antes de licitar sistema de gestao hospitalar, o ETP comparou 4 solucoes de mercado (SaaS vs on-premise), analisou custos em 5 anos e concluiu que SaaS seria 35% mais economico, justificando a opcao tecnica do Termo de Referencia.',
    guideHref: '/blog',
    guideLabel: 'Fase preparatoria na Lei 14.133',
  },
  // F
  {
    term: 'Fiscalizacao',
    slug: 'fiscalizacao',
    definition:
      'Atividade exercida por servidor ou comissao designada pelo orgao contratante para acompanhar a execucao do contrato, verificar qualidade, prazos e conformidade com as clausulas pactuadas. A Lei 14.133 torna obrigatoria a designacao de fiscal para todo contrato.',
    example:
      'O fiscal do contrato de servicos de TI identificou que a equipe alocada estava com 2 profissionais a menos que o exigido. Notificou a empresa, que regularizou em 5 dias, evitando aplicacao de multa contratual de 2%.',
    guideHref: '/blog',
    guideLabel: 'Fiscalizacao de contratos publicos',
  },
  // G
  {
    term: 'Garantia Contratual',
    slug: 'garantia-contratual',
    definition:
      'Garantia exigida do contratado para assegurar a execucao do contrato, podendo ser caucao em dinheiro, seguro-garantia ou fianca bancaria. A Lei 14.133 permite exigir ate 5% do valor do contrato (ate 10% para obras de grande vulto).',
    example:
      'Para contrato de R$ 10 milhoes em obras de saneamento, a construtora apresentou seguro-garantia de R$ 500.000 (5%) emitido por seguradora autorizada pela SUSEP, com vigencia ate 90 dias apos o recebimento definitivo.',
    guideHref: '/blog',
    guideLabel: 'Garantias em contratos publicos',
  },
  {
    term: 'Garantia de Proposta',
    slug: 'garantia-de-proposta',
    definition:
      'Garantia exigida na fase de licitacao para assegurar a seriedade da proposta apresentada. A Lei 14.133 permite exigir garantia de ate 1% do valor estimado da contratacao, devolvida apos a adjudicacao.',
    example:
      'Em concorrencia para construcao de viaduto estimada em R$ 25 milhoes, o edital exigiu garantia de proposta de R$ 250.000 (1%). A empresa apresentou fianca bancaria, que foi devolvida 15 dias apos a homologacao.',
    guideHref: '/blog',
    guideLabel: 'Garantias em licitacoes',
  },
  // H
  {
    term: 'Habilitacao',
    slug: 'habilitacao',
    definition:
      'Fase do processo licitatorio em que se verifica a documentacao juridica, fiscal, trabalhista, tecnica e economico-financeira dos licitantes. Na Lei 14.133, a habilitacao ocorre apos o julgamento das propostas (inversao de fases), exceto quando o edital determina o contrario.',
    example:
      'Dos 12 participantes do pregao, 3 foram inabilitados: um por CNDT vencida, outro por falta de atestado tecnico compativel e o terceiro por indice de liquidez abaixo do minimo exigido de 1,0.',
    guideHref: '/blog',
    guideLabel: 'Habilitacao em licitacoes',
  },
  {
    term: 'Homologacao',
    slug: 'homologacao',
    definition:
      'Ato da autoridade superior que ratifica todo o procedimento licitatorio apos verificar sua legalidade e conveniencia. A homologacao e o ultimo ato antes da convocacao para assinatura do contrato e pode ser precedida de parecer juridico.',
    example:
      'O Secretario de Administracao homologou o pregao eletronico 30 dias apos a adjudicacao, confirmando que todas as etapas foram conduzidas conforme a lei e autorizando a assinatura do contrato com o vencedor.',
    guideHref: '/blog',
    guideLabel: 'Etapas do processo licitatorio',
  },
  // I
  {
    term: 'Impugnacao',
    slug: 'impugnacao',
    definition:
      'Instrumento juridico pelo qual qualquer cidadao ou licitante questiona termos do edital antes da realizacao da sessao publica. A impugnacao deve ser apresentada em ate 3 dias uteis antes da abertura (cidadao) ou ate 3 dias uteis (licitante) na Lei 14.133.',
    example:
      'Uma empresa de software impugnou edital que exigia "sistema desenvolvido em Java" sem justificativa tecnica, argumentando que a especificacao de linguagem restringia a concorrencia. A comissao acatou e alterou para "sistema web multiplataforma".',
    guideHref: '/blog',
    guideLabel: 'Impugnacao de editais',
  },
  {
    term: 'Inexigibilidade',
    slug: 'inexigibilidade',
    definition:
      'Contratacao direta quando ha inviabilidade de competicao, ou seja, quando o objeto so pode ser fornecido por um unico prestador ou quando a natureza do servico torna impossivel a comparacao objetiva. Difere da dispensa, onde a competicao seria possivel mas e dispensada por lei.',
    example:
      'A universidade contratou por inexigibilidade o unico representante autorizado no Brasil de equipamento de ressonancia magnetica Siemens MAGNETOM para manutencao corretiva, pois a fabricante nao credencia terceiros.',
    guideHref: '/blog',
    guideLabel: 'Contratacao direta: dispensa e inexigibilidade',
  },
  // L
  {
    term: 'Leilao',
    slug: 'leilao',
    definition:
      'Modalidade licitatoria utilizada para alienacao (venda) de bens moveis e imoveis da administracao publica ao maior lance. Na Lei 14.133, o leilao pode ser presencial ou eletronico e exige avaliacao previa dos bens.',
    example:
      'O Exercito realizou leilao eletronico de 50 veiculos descaracterizados com lance minimo de R$ 8.000 cada. Os veiculos foram arrematados com agio medio de 45% sobre a avaliacao.',
    guideHref: '/blog',
    guideLabel: 'Leilao de bens publicos',
  },
  {
    term: 'Licitacao Deserta',
    slug: 'licitacao-deserta',
    definition:
      'Situacao em que nenhum interessado comparece ao processo licitatorio. Quando a licitacao e deserta, a administracao pode repetir o processo ou realizar contratacao direta (dispensa) desde que mantenha as mesmas condicoes do edital original.',
    example:
      'O pregao para fornecimento de refeicoes em municipio do interior teve zero propostas. A prefeitura reabriu o certame com prazo estendido e, novamente deserto, contratou diretamente por dispensa (art. 75, III da Lei 14.133).',
    guideHref: '/blog',
    guideLabel: 'Licitacao deserta e fracassada',
  },
  {
    term: 'Licitacao Fracassada',
    slug: 'licitacao-fracassada',
    definition:
      'Situacao em que todos os licitantes sao inabilitados ou todas as propostas sao desclassificadas. Diferentemente da deserta (ninguem aparece), na fracassada houve participantes, mas nenhum atendeu aos requisitos. A Lei 14.133 permite fixar prazo para adequacao antes de repetir.',
    example:
      'Na concorrencia para construcao de escola, as 5 propostas foram desclassificadas por precos acima do orcamento estimado. A comissao fixou prazo de 8 dias para readequacao, conforme art. 75, III, da Lei 14.133.',
    guideHref: '/blog',
    guideLabel: 'Licitacao deserta e fracassada',
  },
  // M
  {
    term: 'Mapa de Riscos',
    slug: 'mapa-de-riscos',
    definition:
      'Documento elaborado na fase preparatoria da licitacao que identifica os principais riscos do processo de contratacao, suas probabilidades e impactos. A Lei 14.133 tornou obrigatoria sua elaboracao como parte do planejamento da contratacao.',
    example:
      'O mapa de riscos de contratacao de datacenter identificou 12 riscos, sendo o mais critico "indisponibilidade superior a 4h/mes" com probabilidade alta e impacto severo, levando a inclusao de SLA com multas progressivas no contrato.',
    guideHref: '/blog',
    guideLabel: 'Gestao de riscos em contratacoes',
  },
  {
    term: 'Matriz de Riscos',
    slug: 'matriz-de-riscos',
    definition:
      'Clausula contratual que distribui de forma objetiva as responsabilidades sobre eventos supervenientes entre contratante e contratado. Diferentemente do mapa de riscos (fase preparatoria), a matriz de riscos faz parte do contrato e vincula ambas as partes.',
    example:
      'Na matriz de riscos do contrato de obra rodoviaria, o risco de variacao do preco do asfalto acima de 10% ficou com a administracao (reequilibrio automatico), enquanto o risco de atraso por falta de mao-de-obra ficou com a construtora.',
    guideHref: '/blog',
    guideLabel: 'Gestao de riscos em contratacoes',
  },
  {
    term: 'ME/EPP',
    slug: 'me-epp',
    definition:
      'Microempresa (receita bruta anual ate R$ 360.000) e Empresa de Pequeno Porte (receita ate R$ 4.800.000) recebem tratamento diferenciado em licitacoes: direito de preferencia quando a proposta for ate 5% superior (pregao) ou 10% (demais modalidades) a melhor oferta, alem de prazo extra para regularizacao fiscal.',
    example:
      'No pregao para material de escritorio, a ME ofertou R$ 52.000 contra R$ 50.000 da empresa de grande porte. Como a diferenca foi inferior a 5%, a ME foi convocada para cobrir o lance e ofertou R$ 49.800, vencendo o certame.',
    guideHref: '/blog',
    guideLabel: 'Vantagens de ME/EPP em licitacoes',
  },
  {
    term: 'Medicao',
    slug: 'medicao',
    definition:
      'Procedimento periodico (geralmente mensal) de verificacao e quantificacao dos servicos ou obras efetivamente executados pelo contratado, servindo como base para emissao da nota fiscal e pagamento. A medicao e atestada pelo fiscal do contrato.',
    example:
      'Na 3a medicao mensal do contrato de limpeza hospitalar, o fiscal verificou que 95% da area foi atendida (2 alas em reforma ficaram sem servico) e autorizou pagamento proporcional de R$ 142.500 sobre os R$ 150.000 mensais.',
    guideHref: '/blog',
    guideLabel: 'Execucao de contratos de servicos',
  },
  // N
  {
    term: 'Nota de Empenho',
    slug: 'nota-de-empenho',
    definition:
      'Documento emitido pelo orgao publico que reserva dotacao orcamentaria para cobrir despesa especifica. O empenho e a primeira fase da execucao da despesa publica e precede a liquidacao e o pagamento. Em compras de pequeno valor, pode substituir o contrato formal.',
    example:
      'Apos homologacao do pregao de material de limpeza (R$ 38.000), o setor financeiro emitiu Nota de Empenho vinculada a dotacao 3.3.90.30 — Material de Consumo, autorizando o fornecedor a iniciar a entrega.',
    guideHref: '/blog',
    guideLabel: 'Ciclo da despesa publica',
  },
  // O
  {
    term: 'Ordem de Servico',
    slug: 'ordem-de-servico',
    definition:
      'Documento emitido pelo orgao contratante que autoriza formalmente o inicio da execucao do contrato ou de uma etapa especifica. Define data de inicio, escopo da demanda e prazo de conclusao, sendo obrigatoria em contratos de servicos continuados.',
    example:
      'A Ordem de Servico n. 001/2026 autorizou a empresa de TI a iniciar o desenvolvimento do modulo de RH do sistema, com prazo de 90 dias e equipe minima de 5 profissionais, conforme cronograma do contrato.',
    guideHref: '/blog',
    guideLabel: 'Gestao de contratos de servicos',
  },
  // P
  {
    term: 'Penalidade/Sancao',
    slug: 'penalidade-sancao',
    definition:
      'Punicao aplicada ao fornecedor por descumprimento contratual ou conduta irregular em licitacao. A Lei 14.133 preve 4 tipos: advertencia, multa (ate 30% do contrato), impedimento de licitar (ate 3 anos) e declaracao de inidoneidade (3 a 6 anos). Sancoes sao registradas no PNCP.',
    example:
      'Apos 3 notificacoes por atraso na entrega de medicamentos, o hospital aplicou multa de 10% do valor mensal (R$ 45.000) e impedimento de licitar por 2 anos, com registro no SICAF e PNCP.',
    guideHref: '/blog',
    guideLabel: 'Sancoes em contratos publicos',
  },
  {
    term: 'Plano de Contratacoes Anual (PCA)',
    slug: 'plano-de-contratacoes-anual',
    definition:
      'Instrumento de planejamento obrigatorio (Lei 14.133, art. 12, VII) em que cada orgao lista todas as contratacoes previstas para o exercicio seguinte. O PCA e publicado no PNCP e permite que fornecedores se preparem com antecedencia para as licitacoes do ano.',
    example:
      'O PCA 2026 do Ministerio da Educacao listou 847 itens de contratacao, totalizando R$ 2,3 bilhoes. Empresas de TI identificaram 23 contratacoes relevantes e iniciaram preparacao de atestados e certidoes 6 meses antes dos pregoes.',
    guideHref: '/blog',
    guideLabel: 'Planejamento de contratacoes',
  },
  {
    term: 'PNCP (Portal Nacional de Contratacoes Publicas)',
    slug: 'pncp',
    definition:
      'Portal eletronico oficial e obrigatorio, criado pela Lei 14.133/2021, que centraliza a divulgacao de todas as licitacoes, contratacoes diretas, atas de registro de precos e contratos dos tres niveis de governo (federal, estadual e municipal). E a principal fonte de dados para monitoramento de oportunidades.',
    example:
      'O SmartLic monitora diariamente o PNCP para identificar novas licitacoes publicadas em 27 UFs, classificando automaticamente por setor e avaliando viabilidade. Em media, sao publicadas 2.000+ contratacoes/dia no portal.',
    guideHref: '/blog',
    guideLabel: 'Como usar o PNCP',
  },
  {
    term: 'Preco de Referencia',
    slug: 'preco-de-referencia',
    definition:
      'Valor estimado pela administracao como parametro do preco justo para a contratacao. E obtido por pesquisa de mercado (minimo 3 cotacoes), consulta a bancos de precos (Painel de Precos, SINAPI, SICRO) ou contratacoes anteriores similares. O preco de referencia define o teto aceitavel.',
    example:
      'Para licitacao de notebooks, o orgao pesquisou: Painel de Precos (R$ 4.200), 3 cotacoes de mercado (media R$ 4.350) e ata de registro vigente (R$ 4.100). O preco de referencia foi fixado em R$ 4.217 (media ponderada).',
    guideHref: '/blog',
    guideLabel: 'Pesquisa de precos em licitacoes',
  },
  {
    term: 'Pregao Eletronico',
    slug: 'pregao-eletronico',
    definition:
      'Modalidade licitatoria realizada integralmente em plataforma digital, destinada a aquisicao de bens e servicos comuns pelo criterio de menor preco ou maior desconto. E a modalidade mais utilizada no Brasil, respondendo por mais de 80% das licitacoes federais. A fase de lances permite reducao competitiva dos precos em tempo real.',
    example:
      'No pregao eletronico para 1.000 licencas de antivirus, 8 empresas participaram da fase de lances que durou 15 minutos. O preco caiu de R$ 89/licenca para R$ 52/licenca — economia de 42% para a administracao.',
    guideHref: '/blog',
    guideLabel: 'Guia completo do pregao eletronico',
  },
  {
    term: 'Proposta Comercial',
    slug: 'proposta-comercial',
    definition:
      'Documento formal apresentado pelo licitante contendo precos, condicoes de pagamento, prazo de entrega e validade da oferta. Deve seguir rigorosamente o modelo exigido no edital. A proposta vincula o licitante, que nao pode alterala apos a abertura, exceto em negociacao com o pregoeiro.',
    example:
      'A proposta comercial para fornecimento de 200 impressoras incluiu: preco unitario R$ 1.890, prazo de entrega 30 dias, garantia 36 meses on-site, validade da proposta 90 dias, conforme modelo do Anexo II do edital.',
    guideHref: '/blog',
    guideLabel: 'Como elaborar propostas vencedoras',
  },
  {
    term: 'Proposta Tecnica',
    slug: 'proposta-tecnica',
    definition:
      'Documento que descreve a solucao tecnica, metodologia, equipe e plano de trabalho ofertados pelo licitante em licitacoes do tipo "tecnica e preco" ou "melhor tecnica". E avaliada por comissao tecnica segundo criterios objetivos definidos no edital.',
    example:
      'Na licitacao de consultoria ambiental (tecnica e preco, peso 60/40), a proposta tecnica incluiu: metodologia de diagnostico em 3 fases, equipe de 8 especialistas com curriculos, cronograma detalhado de 180 dias e 3 estudos de caso similares.',
    guideHref: '/blog',
    guideLabel: 'Licitacoes de tecnica e preco',
  },
  // R
  {
    term: 'Recebimento Definitivo',
    slug: 'recebimento-definitivo',
    definition:
      'Ato formal que confirma a aceitacao final do objeto contratado apos verificacao completa de qualidade, quantidade e conformidade com as especificacoes. Ocorre apos o recebimento provisorio e autoriza o pagamento integral remanescente. E realizado por comissao ou servidor designado.',
    example:
      'Apos 15 dias de testes do sistema de gestao implantado, a comissao de recebimento emitiu o Termo de Recebimento Definitivo, atestando que os 47 requisitos funcionais do Termo de Referencia foram atendidos integralmente.',
    guideHref: '/blog',
    guideLabel: 'Recebimento de objetos contratuais',
  },
  {
    term: 'Recebimento Provisorio',
    slug: 'recebimento-provisorio',
    definition:
      'Aceite inicial do objeto contratado, realizado pelo fiscal para fins de posterior verificacao detalhada de conformidade. Nao constitui aceite definitivo — e uma etapa intermediaria que permite a administracao conferir qualidade e quantidade antes do recebimento definitivo.',
    example:
      'O fiscal do contrato emitiu recebimento provisorio das 500 cadeiras escolares no ato da entrega, verificando apenas quantidade e integridade das embalagens. A conferencia detalhada (material, dimensoes, acabamento) foi realizada nos 15 dias seguintes.',
    guideHref: '/blog',
    guideLabel: 'Recebimento de objetos contratuais',
  },
  {
    term: 'Recurso',
    slug: 'recurso',
    definition:
      'Instrumento processual pelo qual o licitante pede revisao de decisao tomada durante a licitacao (habilitacao, julgamento, adjudicacao). Na Lei 14.133, o prazo para recurso e de 3 dias uteis apos a publicacao do ato, com efeito suspensivo automatico.',
    example:
      'A empresa classificada em 2o lugar interpôs recurso contra a habilitacao da vencedora, demonstrando que o atestado de capacidade tecnica apresentado nao atingia 50% do quantitativo exigido. O recurso foi provido e a recorrente foi declarada vencedora.',
    guideHref: '/blog',
    guideLabel: 'Recursos em licitacoes',
  },
  {
    term: 'Reequilibrio Economico-Financeiro',
    slug: 'reequilibrio-economico-financeiro',
    definition:
      'Mecanismo de restauracao das condicoes economicas originais do contrato quando eventos imprevisiveis e extraordinarios alteram significativamente os custos. Diferencia-se do reajuste (previsivel, por indice) por exigir comprovacao de fato superveniente e impacto financeiro concreto.',
    example:
      'Apos aumento de 40% no preco do aco em 3 meses devido a crise logistica global, a construtora solicitou reequilibrio do contrato de obra, apresentando notas fiscais comparativas que demonstravam impacto de R$ 1,2 milhao sobre o custo original.',
    guideHref: '/blog',
    guideLabel: 'Reequilibrio e reajuste contratual',
  },
  {
    term: 'Reajuste',
    slug: 'reajuste',
    definition:
      'Atualizacao periodica do valor contratual com base em indice de precos previamente definido no contrato (IPCA, IGPM, INPC ou indice setorial). O reajuste e aplicado anualmente, a partir da data da proposta, e nao depende de comprovacao de desequilibrio — e automatico conforme clausula contratual.',
    example:
      'O contrato de servicos de vigilancia previa reajuste anual pelo IPCA. Apos 12 meses, o indice acumulado foi de 4,87%, e o valor mensal foi reajustado de R$ 120.000 para R$ 125.844 automaticamente.',
    guideHref: '/blog',
    guideLabel: 'Reequilibrio e reajuste contratual',
  },
  {
    term: 'Revogacao',
    slug: 'revogacao',
    definition:
      'Anulacao da licitacao por razoes de interesse publico superveniente, devidamente justificadas pela autoridade competente. Diferente da anulacao (por ilegalidade), a revogacao decorre de conveniencia administrativa e tem efeito a partir da decisao (ex nunc).',
    example:
      'A prefeitura revogou a licitacao para construcao de quadra esportiva porque o terreno previsto foi desapropriado para passagem de via expressa estadual, inviabilizando o projeto original.',
    guideHref: '/blog',
    guideLabel: 'Anulacao e revogacao de licitacoes',
  },
  // S
  {
    term: 'Sistema de Registro de Precos (SRP)',
    slug: 'sistema-de-registro-de-precos',
    definition:
      'Conjunto de procedimentos para registro formal de precos com fornecedores, permitindo contratacoes futuras nas quantidades e prazos necessarios, sem obrigatoriedade de compra. E formalizado por Ata de Registro de Precos com validade de ate 1 ano. Ideal para compras frequentes com quantidades incertas.',
    example:
      'O governo estadual registrou precos de 200 itens de informatica via SRP. Durante 12 meses, 45 orgaos participantes emitiram 312 ordens de compra totalizando R$ 18 milhoes — sem precisar realizar nova licitacao para cada aquisicao.',
    guideHref: '/blog',
    guideLabel: 'SRP: vantagens e como participar',
  },
];

/* ---------------------------------------------------------------------------
 * Helpers
 * --------------------------------------------------------------------------- */

/** Extract unique first letters (uppercase) from sorted terms. */
function getAlphabetLetters(terms: GlossaryTerm[]): string[] {
  const set = new Set<string>();
  for (const t of terms) {
    set.add(t.term.charAt(0).toUpperCase());
  }
  return Array.from(set).sort();
}

/** Group terms by their first letter. */
function groupByLetter(terms: GlossaryTerm[]): Record<string, GlossaryTerm[]> {
  const groups: Record<string, GlossaryTerm[]> = {};
  for (const t of terms) {
    const letter = t.term.charAt(0).toUpperCase();
    if (!groups[letter]) groups[letter] = [];
    groups[letter].push(t);
  }
  return groups;
}

/* ---------------------------------------------------------------------------
 * Component
 * --------------------------------------------------------------------------- */

export default function GlossarioPage() {
  const letters = getAlphabetLetters(TERMS);
  const grouped = groupByLetter(TERMS);

  /* JSON-LD: BreadcrumbList */
  const breadcrumbLd = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: 'https://smartlic.tech',
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Glossario',
        item: 'https://smartlic.tech/glossario',
      },
    ],
  };

  /* JSON-LD: DefinedTerm array */
  const definedTermsLd = TERMS.map((t) => ({
    '@type': 'DefinedTerm',
    name: t.term,
    description: t.definition,
    inDefinedTermSet: {
      '@type': 'DefinedTermSet',
      name: 'Glossario de Licitacoes SmartLic',
    },
  }));

  const definedTermSetLd = {
    '@context': 'https://schema.org',
    '@type': 'DefinedTermSet',
    name: 'Glossario de Licitacoes SmartLic',
    description:
      'Glossario com 50 termos essenciais sobre licitacoes publicas no Brasil.',
    url: 'https://smartlic.tech/glossario',
    hasDefinedTerm: definedTermsLd,
  };

  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      <LandingNavbar />

      {/* JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(definedTermSetLd) }}
      />

      <main className="flex-1">
        {/* ── Hero ── */}
        <div className="bg-surface-1 border-b border-[var(--border)]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20 text-center">
            <h1
              className="text-3xl sm:text-4xl lg:text-5xl font-bold text-ink tracking-tight mb-4"
              style={{ fontFamily: "Georgia, 'Times New Roman', serif" }}
            >
              Glossario de Licitacoes
            </h1>
            <p className="text-base sm:text-lg text-ink-secondary max-w-2xl mx-auto leading-relaxed">
              50 termos essenciais explicados de forma pratica para quem participa de licitacoes publicas no Brasil
            </p>
          </div>
        </div>

        {/* ── Alphabetical Navigation ── */}
        <div className="sticky top-0 z-20 bg-canvas/95 backdrop-blur-sm border-b border-[var(--border)]">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav
              aria-label="Navegacao alfabetica"
              className="flex flex-wrap gap-1 py-3 justify-center"
            >
              {letters.map((letter) => (
                <a
                  key={letter}
                  href={`#letra-${letter}`}
                  className="inline-flex items-center justify-center w-9 h-9 rounded-md text-sm font-semibold text-ink-secondary hover:text-brand-blue hover:bg-surface-1 transition-colors"
                >
                  {letter}
                </a>
              ))}
            </nav>
          </div>
        </div>

        {/* ── Terms ── */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          {letters.map((letter) => (
            <section key={letter} id={`letra-${letter}`} className="mb-12">
              <h2 className="text-2xl font-bold text-brand-blue border-b-2 border-brand-blue/20 pb-2 mb-6">
                {letter}
              </h2>

              <div className="space-y-8">
                {grouped[letter].map((t) => (
                  <article
                    key={t.slug}
                    id={t.slug}
                    className="scroll-mt-24"
                  >
                    <h3 className="text-lg font-bold text-ink mb-1">
                      {t.term}
                    </h3>
                    <p className="text-ink-secondary leading-relaxed mb-3">
                      {t.definition}
                    </p>

                    {/* Example box */}
                    <div className="text-sm bg-surface-1 border border-[var(--border)] rounded-lg p-3 mb-2">
                      <span className="font-semibold text-ink">Exemplo: </span>
                      <span className="text-ink-secondary">{t.example}</span>
                    </div>

                    <Link
                      href={t.guideHref}
                      className="text-brand-blue hover:underline text-sm"
                    >
                      {t.guideLabel} &rarr;
                    </Link>
                  </article>
                ))}
              </div>
            </section>
          ))}

          {/* ── CTA ── */}
          <section className="mt-16 mb-8 rounded-2xl bg-brand-blue p-8 sm:p-10 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
              Encontre licitacoes do seu setor automaticamente
            </h2>
            <p className="text-white/85 max-w-xl mx-auto mb-6">
              O SmartLic monitora PNCP, PCP e ComprasGov diariamente, classifica por setor com IA e avalia viabilidade para voce focar nas melhores oportunidades.
            </p>
            <Link
              href="/signup?source=glossario-cta"
              className="inline-flex items-center gap-2 bg-white text-brand-blue px-8 py-4 rounded-lg font-semibold hover:bg-white/90 transition-colors focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-blue"
            >
              Testar gratis por 14 dias
            </Link>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
