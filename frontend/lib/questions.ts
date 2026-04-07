/**
 * Shared Q&A registry for SmartLic public procurement FAQ pages (S10).
 *
 * Used by:
 * - /perguntas (hub page)
 * - /perguntas/[slug] (individual question pages)
 *
 * 53 questions across 6 categories covering Brazilian public procurement
 * under Lei 14.133/2021 with references to PNCP data where applicable.
 */

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export type QuestionCategory =
  | 'modalidades'
  | 'prazos-cronogramas'
  | 'documentacao-habilitacao'
  | 'precos-propostas'
  | 'setores-especificos'
  | 'tecnologia-sistemas';

export interface Question {
  slug: string;
  title: string;
  category: QuestionCategory;
  answer: string;
  legalBasis?: string;
  relatedTerms: string[];
  relatedSectors: string[];
  relatedArticles: string[];
  metaDescription: string;
}

/* ------------------------------------------------------------------ */
/*  Category metadata                                                  */
/* ------------------------------------------------------------------ */

export const CATEGORY_META: Record<
  QuestionCategory,
  { label: string; description: string }
> = {
  modalidades: {
    label: 'Modalidades de Licitacao',
    description:
      'Pregao, concorrencia, dispensa, inexigibilidade e outras modalidades da Lei 14.133/2021.',
  },
  'prazos-cronogramas': {
    label: 'Prazos e Cronogramas',
    description:
      'Prazos legais para impugnacao, recurso, publicacao, vigencia e pagamento em licitacoes.',
  },
  'documentacao-habilitacao': {
    label: 'Documentacao e Habilitacao',
    description:
      'Documentos exigidos, SICAF, certidoes, atestados e qualificacao tecnica.',
  },
  'precos-propostas': {
    label: 'Precos e Propostas',
    description:
      'Calculo de precos, BDI, inexequibilidade, reequilibrio e registro de precos.',
  },
  'setores-especificos': {
    label: 'Setores Especificos',
    description:
      'Requisitos especiais por setor: TI, saude, engenharia, alimentos, facilities.',
  },
  'tecnologia-sistemas': {
    label: 'Tecnologia e Sistemas',
    description:
      'PNCP, ComprasNet, certificado digital, assinatura eletronica e IA em licitacoes.',
  },
};

/* ------------------------------------------------------------------ */
/*  Questions                                                          */
/* ------------------------------------------------------------------ */

export const QUESTIONS: Question[] = [
  /* ================================================================ */
  /*  MODALIDADES (10)                                                 */
  /* ================================================================ */
  {
    slug: 'o-que-e-pregao-eletronico',
    title: 'O que e pregao eletronico e como funciona?',
    category: 'modalidades',
    answer:
      'O pregao eletronico e a modalidade de licitacao mais utilizada no Brasil para aquisicao de bens e servicos comuns. Funciona inteiramente pela internet, em plataformas como o ComprasNet (ComprasGov) ou sistemas estaduais/municipais homologados.\n\n' +
      'Na Lei 14.133/2021, o pregao esta previsto nos artigos 6, inciso XLI, e 29, sendo obrigatoriamente na forma eletronica (art. 17, paragrafo 2). O processo segue estas etapas principais:\n\n' +
      '1. **Publicacao do edital** no PNCP e em jornal de grande circulacao, com prazo minimo de 8 dias uteis para bens/servicos comuns.\n' +
      '2. **Fase de propostas** em que os licitantes registram seus precos iniciais no sistema eletronico.\n' +
      '3. **Fase de lances** com disputa em tempo real, onde os participantes reduzem progressivamente seus precos. O modo de disputa pode ser aberto (lances publicos em tempo real), fechado (proposta unica) ou aberto-fechado (combinacao).\n' +
      '4. **Julgamento** pelo menor preco ou maior desconto, criterios obrigatorios para o pregao.\n' +
      '5. **Habilitacao** apenas do licitante classificado em primeiro lugar (inversao de fases em relacao a concorrencia tradicional).\n' +
      '6. **Adjudicacao e homologacao** pela autoridade competente.\n\n' +
      'O pregao eletronico oferece vantagens significativas: maior competitividade (participantes de todo o pais), transparencia (lances registrados eletronicamente), economia (redecoes medias de 20-30% sobre o preco estimado) e celeridade (processos concluidos em dias, nao meses).\n\n' +
      'Para participar, a empresa precisa de certificado digital valido (tipo A1 ou A3), cadastro no sistema eletronico correspondente (SICAF para o federal) e documentos de habilitacao atualizados. E fundamental acompanhar o chat do sistema durante a sessao, pois o pregoeiro pode solicitar esclarecimentos em tempo real.',
    legalBasis: 'Lei 14.133/2021, arts. 6 (XLI), 17 (par. 2), 29',
    relatedTerms: ['pregao-eletronico', 'lance', 'pregoeiro'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Entenda o que e pregao eletronico, como funciona na Lei 14.133/2021, etapas do processo, e como participar de licitacoes online.',
  },
  {
    slug: 'diferenca-pregao-concorrencia',
    title: 'Qual a diferenca entre pregao e concorrencia na Lei 14.133?',
    category: 'modalidades',
    answer:
      'Pregao e concorrencia sao as duas principais modalidades de licitacao na Lei 14.133/2021 e possuem diferencas fundamentais quanto ao objeto, criterio de julgamento, prazos e procedimento.\n\n' +
      '**Pregao** (art. 29): exclusivo para aquisicao de bens e servicos comuns, cujos padroes de desempenho e qualidade possam ser objetivamente definidos pelo edital. O criterio de julgamento e obrigatoriamente menor preco ou maior desconto. O prazo minimo de publicacao e de 8 dias uteis. A fase de habilitacao ocorre apos o julgamento (inversao de fases), tornando o processo mais agil.\n\n' +
      '**Concorrencia** (art. 29, II): utilizada para obras, servicos especiais, compras de grande vulto e qualquer objeto que nao se enquadre como bem ou servico comum. Admite criterios de julgamento variados: menor preco, melhor tecnica, tecnica e preco, maior retorno economico ou maior lance. O prazo minimo de publicacao e mais longo — 25 dias uteis para tecnica e preco, 15 dias uteis para demais casos.\n\n' +
      '**Principais diferencas praticas:**\n\n' +
      '| Aspecto | Pregao | Concorrencia |\n' +
      '|---------|--------|--------------|\n' +
      '| Objeto | Bens/servicos comuns | Obras, servicos especiais, qualquer objeto |\n' +
      '| Criterio | Menor preco/maior desconto | Varios criterios |\n' +
      '| Prazo edital | 8 dias uteis | 15-25 dias uteis |\n' +
      '| Fase habilitacao | Apos julgamento | Antes ou apos (escolha do gestor) |\n' +
      '| Forma | Obrigatoriamente eletronica | Preferencialmente eletronica |\n\n' +
      'Na pratica, o pregao corresponde a cerca de 80% das licitacoes federais por volume, dada sua agilidade. A concorrencia e predominante em obras de engenharia e contratacoes complexas que exigem avaliacao tecnica qualitativa. A Lei 14.133 permite que o gestor escolha a inversao de fases tambem na concorrencia, aproximando os procedimentos.',
    legalBasis: 'Lei 14.133/2021, arts. 28, 29, 33, 34',
    relatedTerms: ['pregao-eletronico', 'concorrencia', 'modalidade'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Compare pregao e concorrencia na Lei 14.133/2021: objeto, criterios de julgamento, prazos e quando usar cada modalidade.',
  },
  {
    slug: 'quando-usar-dispensa-licitacao',
    title: 'Quando e possivel usar dispensa de licitacao?',
    category: 'modalidades',
    answer:
      'A dispensa de licitacao e a contratacao direta permitida por lei em situacoes especificas onde o processo licitatorio e inexigivel na pratica ou inconveniente ao interesse publico. A Lei 14.133/2021 traz as hipoteses de dispensa no artigo 75.\n\n' +
      '**Principais hipoteses de dispensa (art. 75):**\n\n' +
      '1. **Por valor (incisos I e II):** Obras e servicos de engenharia ate R$ 119.812,20 (atualizado por decreto); demais compras e servicos ate R$ 59.906,10. Esses limites sao atualizados anualmente pelo IPCA.\n' +
      '2. **Emergencia ou calamidade (inciso VIII):** Contratacao direta para atender situacao emergencial que possa causar prejuizo ou comprometer a continuidade de servicos publicos. Vigencia maxima de 1 ano, improrrogavel.\n' +
      '3. **Licitacao deserta ou fracassada (incisos III e IV):** Quando nenhum interessado comparece ou todas as propostas sao desclassificadas, desde que mantidas as condicoes do edital.\n' +
      '4. **Compras entre orgaos (inciso IX):** Aquisicao de bens por orgao integrante da administracao junto a outro ente publico.\n' +
      '5. **Generos pereciveis (inciso IV, alinea d):** Compra de alimentos frescos durante o tempo necessario para realizacao de processo licitatorio.\n' +
      '6. **Pesquisa e inovacao (inciso V):** Contratacao de instituicao brasileira dedicada a pesquisa, ensino ou desenvolvimento tecnologico.\n\n' +
      '**Procedimento obrigatorio:** Mesmo na dispensa, a Lei 14.133 exige procedimento simplificado: pesquisa de precos com no minimo 3 cotacoes, justificativa da situacao, parecer juridico, publicacao no PNCP e comprovacao de que o contratado atende aos requisitos de habilitacao. O processo deve ser transparente e auditavel.\n\n' +
      '**Atencao:** A Lei 14.133 criou a "dispensa eletronica" (art. 75, paragrafo 3), processo simplificado conduzido em plataforma digital que amplia a competitividade mesmo nas contratacoes diretas.',
    legalBasis: 'Lei 14.133/2021, art. 75',
    relatedTerms: ['dispensa', 'licitacao', 'edital'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Saiba quando a dispensa de licitacao e permitida pela Lei 14.133/2021: limites de valor, emergencia, licitacao deserta e mais.',
  },
  {
    slug: 'o-que-e-inexigibilidade',
    title: 'O que e inexigibilidade de licitacao e quais os requisitos?',
    category: 'modalidades',
    answer:
      'A inexigibilidade de licitacao ocorre quando a competicao e inviavel, ou seja, quando nao e possivel realizar um processo licitatorio porque so existe um fornecedor capaz de atender a demanda, ou porque o objeto possui caracteristicas tao singulares que tornam a comparacao entre propostas impossivel.\n\n' +
      'A Lei 14.133/2021 disciplina a inexigibilidade no artigo 74, estabelecendo tres hipoteses principais:\n\n' +
      '1. **Fornecedor exclusivo (inciso I):** Aquisicao de materiais, equipamentos ou generos que so possam ser fornecidos por produtor, empresa ou representante comercial exclusivo. A exclusividade deve ser comprovada por atestado de exclusividade emitido pelo orgao competente (como Juntas Comerciais ou sindicatos patronais).\n\n' +
      '2. **Servicos tecnicos especializados (inciso III):** Contratacao de profissionais ou empresas de notoria especializacao para servicos listados no art. 74, inciso III (pareceres, auditorias, consultorias, patrocinio juridico, treinamentos, restauracao de obras de arte, entre outros). A notoria especializacao deve ser comprovada por publicacoes, experiencia e reconhecimento no mercado.\n\n' +
      '3. **Profissional do setor artistico (inciso II):** Contratacao de artista consagrado pela critica especializada ou pela opiniao publica.\n\n' +
      '**Requisitos obrigatorios para inexigibilidade:**\n' +
      '- Justificativa fundamentada da inviabilidade de competicao\n' +
      '- Razao da escolha do contratado\n' +
      '- Justificativa do preco (pesquisa de mercado ou comprovacao de compatibilidade)\n' +
      '- Parecer juridico aprovando a contratacao\n' +
      '- Publicacao no PNCP em ate 10 dias uteis\n\n' +
      'A diferenca fundamental em relacao a dispensa e que na inexigibilidade a competicao e IMPOSSIVEL (nao ha alternativa), enquanto na dispensa a competicao e possivel mas a lei AUTORIZA a contratacao direta por conveniencia. A inexigibilidade e uma constatacao factual; a dispensa e uma opcao legal.',
    legalBasis: 'Lei 14.133/2021, art. 74',
    relatedTerms: ['inexigibilidade', 'licitacao', 'proposta'],
    relatedSectors: ['consultoria'],
    relatedArticles: [],
    metaDescription:
      'Entenda o que e inexigibilidade de licitacao na Lei 14.133/2021: hipoteses, requisitos legais e diferenca para dispensa.',
  },
  {
    slug: 'dialogo-competitivo-quando-usar',
    title: 'O que e dialogo competitivo e quando usar?',
    category: 'modalidades',
    answer:
      'O dialogo competitivo e uma modalidade de licitacao introduzida pela Lei 14.133/2021 (art. 32) para contratacoes complexas em que a administracao nao consegue definir com precisao a solucao tecnica ou as condicoes comerciais mais adequadas. E inspirado no modelo europeu (Competitive Dialogue) e representa uma inovacao significativa no ordenamento juridico brasileiro.\n\n' +
      '**Quando usar o dialogo competitivo:**\n\n' +
      '1. **Inovacao tecnologica ou tecnica:** Quando o orgao publico precisa de solucao inovadora e nao consegue especificar antecipadamente todos os requisitos tecnicos.\n' +
      '2. **Impossibilidade de definir meios de execucao:** Quando ha multiplas abordagens possiveis e o gestor nao tem certeza de qual e a mais adequada.\n' +
      '3. **Necessidade de adaptacao de solucoes disponiveis:** Quando as solucoes de mercado precisam ser customizadas.\n\n' +
      '**Como funciona o processo:**\n\n' +
      '1. **Pre-selecao:** O orgao publica edital com os requisitos minimos e criterios de pre-selecao. Empresas interessadas se candidatam e sao pre-qualificadas.\n' +
      '2. **Fase de dialogo:** O orgao dialoga individualmente com cada participante pre-selecionado (minimo 3) para explorar solucoes tecnicas e comerciais. As discussoes sao confidenciais — nenhuma informacao de um participante e compartilhada com os demais sem autorizacao.\n' +
      '3. **Fase competitiva:** Apos encerrar o dialogo, o orgao elabora os criterios definitivos e convida os participantes a apresentarem propostas finais.\n' +
      '4. **Julgamento e contratacao:** As propostas sao avaliadas pelos criterios definidos.\n\n' +
      '**Requisitos importantes:** Minimo de 3 participantes pre-selecionados; comissao de contratacao com pelo menos 3 membros; sigilo das informacoes compartilhadas durante o dialogo; e publicacao no PNCP com prazo minimo de 25 dias uteis.\n\n' +
      'Na pratica, o dialogo competitivo e indicado para projetos de TI complexos, PPPs e concessoes inovadoras.',
    legalBasis: 'Lei 14.133/2021, art. 32',
    relatedTerms: ['modalidade', 'edital', 'licitacao'],
    relatedSectors: ['informatica'],
    relatedArticles: [],
    metaDescription:
      'Saiba o que e dialogo competitivo na Lei 14.133/2021, quando usar, etapas do processo e requisitos para participar.',
  },
  {
    slug: 'leilao-eletronico-como-funciona',
    title: 'Como funciona o leilao eletronico na Lei 14.133?',
    category: 'modalidades',
    answer:
      'O leilao e a modalidade de licitacao utilizada para alienacao (venda) de bens imoveis ou moveis inservibles pela administracao publica. Na Lei 14.133/2021, o leilao esta previsto no artigo 31 e pode ser realizado na forma eletronica ou presencial.\n\n' +
      '**Quando o leilao e utilizado:**\n\n' +
      '1. **Bens moveis inservibles:** Veiculos, equipamentos, mobiliario e materiais em desuso que nao atendem mais ao servico publico.\n' +
      '2. **Bens imoveis:** Predios, terrenos e outros imoveis cuja alienacao seja autorizada por lei.\n' +
      '3. **Bens apreendidos ou penhorados:** Produtos apreendidos por orgaos fiscalizadores ou penhorados em execucoes fiscais.\n' +
      '4. **Produtos legalmente apreendidos ou abandonados:** Mercadorias apreendidas pela Receita Federal, por exemplo.\n\n' +
      '**Como funciona o leilao eletronico:**\n\n' +
      '1. **Publicacao:** O edital e publicado no PNCP com prazo minimo de 15 dias uteis, descrevendo os bens, o valor minimo de arrematacao (avaliacao previa obrigatoria) e as condicoes de pagamento.\n' +
      '2. **Visitacao:** Periodo para que os interessados inspecionem os bens pessoalmente.\n' +
      '3. **Sessao de lances:** Os participantes oferecem lances crescentes em plataforma eletronica. O criterio de julgamento e obrigatoriamente o maior lance.\n' +
      '4. **Arrematacao:** O bem e adjudicado ao autor do maior lance que atinja ou supere o valor minimo.\n' +
      '5. **Pagamento e retirada:** O arrematante efetua o pagamento nas condicoes do edital e retira o bem.\n\n' +
      '**Particularidades importantes:**\n' +
      '- O leiloeiro pode ser servidor designado ou leiloeiro oficial (art. 31, paragrafo 1).\n' +
      '- Bens imoveis exigem avaliacao previa e autorizacao legislativa.\n' +
      '- O leilao e aberto a qualquer interessado — nao exige cadastro previo no SICAF.\n' +
      '- A comissao do leiloeiro oficial e fixada no edital (em geral 5% sobre o valor da arrematacao).\n\n' +
      'O leilao eletronico tem crescido significativamente, com plataformas como o Licitacoes-e (Banco do Brasil) e o proprio ComprasGov disponibilizando modulos de leilao.',
    legalBasis: 'Lei 14.133/2021, art. 31',
    relatedTerms: ['modalidade', 'licitacao', 'edital'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Entenda como funciona o leilao eletronico na Lei 14.133/2021: quando e usado, etapas do processo e como participar.',
  },
  {
    slug: 'concorrencia-eletronica-passo-a-passo',
    title: 'Como participar de uma concorrencia eletronica?',
    category: 'modalidades',
    answer:
      'A concorrencia eletronica e a modalidade utilizada para contratacoes de maior complexidade — obras de engenharia, servicos especiais, concessoes e compras de grande vulto. Na Lei 14.133/2021, a concorrencia e disciplinada nos artigos 29 a 30 e deve ser preferencialmente na forma eletronica.\n\n' +
      '**Passo a passo para participar:**\n\n' +
      '**1. Identificacao da oportunidade:**\n' +
      'Monitore publicacoes no PNCP (Portal Nacional de Contratacoes Publicas), diarios oficiais e portais de compras estaduais/municipais. Use ferramentas como o SmartLic para receber alertas automatizados por setor e regiao.\n\n' +
      '**2. Analise do edital:**\n' +
      'Leia atentamente todas as clausulas, especialmente: objeto, criterio de julgamento (menor preco, tecnica e preco, melhor tecnica), requisitos de habilitacao, prazo de execucao e condicoes de pagamento. O prazo para impugnacao e de ate 3 dias uteis antes da abertura.\n\n' +
      '**3. Preparacao da documentacao:**\n' +
      'Reuna os documentos de habilitacao: juridica, fiscal/trabalhista, economico-financeira e tecnica. Mantenha o SICAF atualizado se for licitacao federal. Prepare atestados de capacidade tecnica conforme exigido.\n\n' +
      '**4. Elaboracao da proposta:**\n' +
      'Formule a proposta tecnica (se aplicavel) e a proposta de precos conforme modelo do edital. Em concorrencias de tecnica e preco, a proposta tecnica e avaliada separadamente e tem peso na nota final.\n\n' +
      '**5. Envio no sistema eletronico:**\n' +
      'Acesse a plataforma indicada no edital (ComprasGov, BEC-SP, Licitacoes-e, etc.) com seu certificado digital. Envie propostas e documentos dentro do prazo.\n\n' +
      '**6. Acompanhamento da sessao:**\n' +
      'Na data marcada, acompanhe a abertura das propostas, a fase de lances (se modo aberto) e a habilitacao. Esteja preparado para responder diligencias em ate 2 horas.\n\n' +
      '**7. Recursos e contrato:**\n' +
      'Se classificado em primeiro lugar, aguarde a habilitacao e o prazo recursal. Apos a homologacao, assine o contrato no prazo estipulado (em geral 5 dias corridos).',
    legalBasis: 'Lei 14.133/2021, arts. 29, 30, 33, 34',
    relatedTerms: ['concorrencia', 'habilitacao', 'proposta'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Guia passo a passo para participar de concorrencia eletronica: do edital a assinatura do contrato na Lei 14.133/2021.',
  },
  {
    slug: 'diferenca-dispensa-inexigibilidade',
    title: 'Qual a diferenca entre dispensa e inexigibilidade?',
    category: 'modalidades',
    answer:
      'Dispensa e inexigibilidade sao formas de contratacao direta previstas na Lei 14.133/2021, mas possuem fundamentos juridicos completamente diferentes. Entender essa distincao e essencial para fornecedores que desejam atuar no mercado publico.\n\n' +
      '**Inexigibilidade (art. 74):**\n' +
      'Ocorre quando a competicao e INVIAVEL — ou seja, nao e possivel comparar propostas porque so existe um fornecedor ou porque o objeto e singular. A inexigibilidade e uma constatacao de fato. As hipoteses mais comuns sao:\n' +
      '- Fornecedor exclusivo (comprovado por atestado)\n' +
      '- Servicos tecnicos especializados de notoria especializacao\n' +
      '- Contratacao de artista consagrado\n\n' +
      '**Dispensa (art. 75):**\n' +
      'Ocorre quando a competicao e POSSIVEL, mas a lei AUTORIZA a contratacao direta por razoes de conveniencia publica. A dispensa e uma opcao legal. As hipoteses incluem:\n' +
      '- Valor abaixo dos limites legais (R$ 59.906,10 para compras; R$ 119.812,20 para obras)\n' +
      '- Situacao de emergencia ou calamidade\n' +
      '- Licitacao deserta ou fracassada\n' +
      '- Compra de generos pereciveis\n\n' +
      '**Comparacao direta:**\n\n' +
      '| Aspecto | Inexigibilidade | Dispensa |\n' +
      '|---------|----------------|----------|\n' +
      '| Competicao | Inviavel (impossivel) | Possivel (mas dispensada) |\n' +
      '| Natureza | Constatacao factual | Autorizacao legal |\n' +
      '| Hipoteses | Rol exemplificativo (caput art. 74) | Rol taxativo (art. 75) |\n' +
      '| Justificativa | Comprovar singularidade/exclusividade | Enquadrar em hipotese legal |\n\n' +
      '**Para o fornecedor:** Se voce e o unico que atende determinada demanda, oriente o orgao publico sobre a possibilidade de inexigibilidade — apresentando atestados de exclusividade ou comprovando notoria especializacao. Se o valor e pequeno, a dispensa por valor pode ser o caminho mais rapido. Em ambos os casos, a publicacao no PNCP e obrigatoria e a pesquisa de precos deve demonstrar compatibilidade com o mercado.',
    legalBasis: 'Lei 14.133/2021, arts. 74 e 75',
    relatedTerms: ['dispensa', 'inexigibilidade', 'licitacao'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Entenda a diferenca entre dispensa e inexigibilidade de licitacao na Lei 14.133/2021: fundamentos, hipoteses e quando usar.',
  },
  {
    slug: 'pregao-presencial-ainda-existe',
    title: 'O pregao presencial ainda existe na nova lei de licitacoes?',
    category: 'modalidades',
    answer:
      'A Lei 14.133/2021 estabelece que o pregao deve ser realizado PREFERENCIALMENTE na forma eletronica (art. 17, paragrafo 2). Isso significa que o pregao presencial nao foi expressamente extinto, mas sua utilizacao passou a ser excepcional e exige justificativa fundamentada.\n\n' +
      '**O que mudou na pratica:**\n\n' +
      'Durante a vigencia da Lei 10.520/2002 (antiga lei do pregao), o pregao presencial era amplamente utilizado, especialmente em municipios menores que nao tinham infraestrutura tecnologica. Com a Lei 14.133/2021, houve uma forte orientacao para a digitalizacao completa das compras publicas.\n\n' +
      '**Quando o pregao presencial pode ser usado:**\n' +
      '- Comprovada inviabilidade tecnica do meio eletronico (problemas de conectividade, por exemplo)\n' +
      '- Justificativa formal no processo administrativo\n' +
      '- Aprovacao da autoridade superior\n\n' +
      'Na pratica, a tendencia e de extincao progressiva do pregao presencial. O Decreto Federal 10.024/2019, ainda vigente para regulamentacao do pregao no ambito federal, ja tornava o eletronico obrigatorio. Municipios que antes realizavam pregoes presenciais estao migrando para plataformas eletronicas como BLL, Compras BR, Portal de Compras Publicas e outros sistemas homologados.\n\n' +
      '**Impacto para fornecedores:**\n\n' +
      'A virtualizacao do pregao amplia significativamente o mercado para fornecedores, que podem participar de licitacoes em qualquer municipio do pais sem deslocamento fisico. Por outro lado, exige:\n' +
      '- Certificado digital ativo (tipo A1 ou A3 da ICP-Brasil)\n' +
      '- Familiaridade com as diferentes plataformas eletronicas\n' +
      '- Conexao estavel de internet durante as sessoes\n' +
      '- Atencao aos prazos e notificacoes do sistema\n\n' +
      'Para empresas que atuam em licitacoes, o investimento em infraestrutura digital e treinamento de equipe para operacao em plataformas eletronicas e agora indispensavel. O pregao presencial pode existir pontualmente, mas nao deve ser considerado como estrategia de atuacao.',
    legalBasis: 'Lei 14.133/2021, art. 17, par. 2',
    relatedTerms: ['pregao-eletronico', 'pregao-presencial', 'pregoeiro'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Descubra se o pregao presencial ainda existe na Lei 14.133/2021 e quais as excecoes para sua utilizacao.',
  },
  {
    slug: 'manifestacao-interesse-pmi',
    title: 'O que e Procedimento de Manifestacao de Interesse (PMI)?',
    category: 'modalidades',
    answer:
      'O Procedimento de Manifestacao de Interesse (PMI) e um instrumento previsto na Lei 14.133/2021 (art. 81) que permite a administracao publica solicitar ao setor privado a elaboracao de estudos, projetos, levantamentos e investigacoes necessarios para a estruturacao de contratacoes complexas — especialmente concessoes, parcerias publico-privadas (PPPs) e grandes obras de infraestrutura.\n\n' +
      '**Como funciona o PMI:**\n\n' +
      '1. **Publicacao do chamamento:** O orgao publico publica edital convocando empresas, pessoas fisicas ou juridicas interessadas em apresentar projetos, estudos ou investigacoes para determinado empreendimento.\n' +
      '2. **Apresentacao de propostas:** Os interessados elaboram e submetem seus estudos de viabilidade tecnica, economico-financeira, juridica e ambiental.\n' +
      '3. **Avaliacao:** O orgao avalia os estudos recebidos, podendo selecionar um ou combinar elementos de diferentes propostas.\n' +
      '4. **Ressarcimento:** Os autores dos estudos aproveitados tem direito ao ressarcimento dos custos, que sera pago pelo futuro contratado (vencedor da licitacao) — nao pelo orgao publico.\n\n' +
      '**Pontos criticos do PMI:**\n\n' +
      '- O PMI NAO garante a contratacao do proponente. O autor dos estudos pode participar da licitacao subsequente, mas nao tem preferencia.\n' +
      '- Os estudos passam a ser propriedade da administracao.\n' +
      '- Multiplos interessados podem apresentar propostas concorrentes.\n' +
      '- A confidencialidade dos estudos e mantida ate a publicacao da licitacao.\n\n' +
      '**Quando o PMI e estrategico para empresas:**\n\n' +
      'Participar de um PMI permite a empresa influenciar as especificacoes tecnicas do futuro edital (dentro dos limites legais), demonstrar conhecimento tecnico ao orgao publico, obter informacoes privilegiadas sobre o empreendimento (que serao depois publicadas) e posicionar-se antecipadamente no mercado. E uma ferramenta estrategica especialmente para empresas de engenharia, consultoria e tecnologia que atuam em grandes projetos de infraestrutura.',
    legalBasis: 'Lei 14.133/2021, art. 81',
    relatedTerms: ['licitacao', 'edital', 'termo-referencia'],
    relatedSectors: ['engenharia', 'consultoria'],
    relatedArticles: [],
    metaDescription:
      'Saiba o que e o PMI (Procedimento de Manifestacao de Interesse), como funciona e quando participar na Lei 14.133/2021.',
  },

  /* ================================================================ */
  /*  PRAZOS E CRONOGRAMAS (8)                                         */
  /* ================================================================ */
  {
    slug: 'prazo-impugnacao-edital',
    title: 'Qual o prazo para impugnar um edital de licitacao?',
    category: 'prazos-cronogramas',
    answer:
      'A impugnacao do edital e o instrumento pelo qual qualquer cidadao ou licitante pode questionar clausulas ilegais, restritivas ou descabidas de um edital de licitacao. Na Lei 14.133/2021, o prazo para impugnacao esta definido no artigo 164.\n\n' +
      '**Prazos de impugnacao:**\n\n' +
      '- **Qualquer cidadao:** Ate 3 (tres) dias uteis ANTES da data de abertura das propostas.\n' +
      '- **Licitante:** Ate 3 (tres) dias uteis ANTES da data de abertura das propostas.\n\n' +
      'A Lei 14.133 unificou o prazo em 3 dias uteis para ambos os casos, diferente da legislacao anterior que diferenciava os prazos. A impugnacao deve ser feita preferencialmente por meio eletronico, diretamente na plataforma onde a licitacao esta sendo conduzida.\n\n' +
      '**Procedimento de impugnacao:**\n\n' +
      '1. **Apresentacao:** Protocolar a impugnacao pela plataforma eletronica (ComprasGov, portal estadual/municipal) ou fisicamente no orgao.\n' +
      '2. **Resposta:** A administracao tem o dever de responder em ate 3 dias uteis, contados do recebimento.\n' +
      '3. **Efeito:** A impugnacao NAO suspende automaticamente o processo licitatorio. O orgao pode decidir suspender ou nao, conforme a relevancia da materia.\n' +
      '4. **Recurso:** Se a impugnacao for indeferida, o impugnante pode recorrer ao Tribunal de Contas ou ao Judiciario.\n\n' +
      '**Fundamentos validos para impugnacao:**\n' +
      '- Exigencias de habilitacao excessivas ou restritivas\n' +
      '- Especificacoes tecnicas direcionadas a marca ou fornecedor\n' +
      '- Prazos de execucao inexequiveis\n' +
      '- Criterios de julgamento inadequados ao objeto\n' +
      '- Ausencia de pesquisa de precos adequada\n' +
      '- Violacao de normas da Lei 14.133/2021\n\n' +
      '**Dica pratica:** Leia o edital imediatamente apos a publicacao. Nao deixe para analisar nos ultimos dias — a fundamentacao tecnica e juridica exige tempo de preparacao. Impugnacoes bem fundamentadas com citacao de jurisprudencia do TCU tem maior probabilidade de acolhimento.',
    legalBasis: 'Lei 14.133/2021, art. 164',
    relatedTerms: ['impugnacao', 'edital', 'recurso'],
    relatedSectors: [],
    relatedArticles: ['impugnacao-edital-quando-como-contestar'],
    metaDescription:
      'Saiba o prazo para impugnar edital de licitacao na Lei 14.133/2021: 3 dias uteis antes da abertura, para qualquer cidadao.',
  },
  {
    slug: 'prazo-recurso-licitacao',
    title: 'Qual o prazo para recurso em licitacao?',
    category: 'prazos-cronogramas',
    answer:
      'O recurso administrativo e o meio pelo qual o licitante contesta decisoes tomadas durante o processo licitatorio. Na Lei 14.133/2021, os prazos recursais estao previstos nos artigos 165 a 168.\n\n' +
      '**Prazos de recurso na Lei 14.133/2021:**\n\n' +
      '- **Intencao de recurso:** Deve ser manifestada IMEDIATAMENTE apos a declaracao do vencedor, na propria sessao publica (presencial ou eletronica).\n' +
      '- **Razoes do recurso:** 3 (tres) dias uteis contados a partir da manifestacao de intencao.\n' +
      '- **Contrarrazoes:** Os demais licitantes tem 3 (tres) dias uteis para apresentar contrarrazoes, contados do termino do prazo do recorrente.\n\n' +
      '**Decisoes passiveis de recurso (art. 165):**\n' +
      '1. Julgamento das propostas\n' +
      '2. Habilitacao ou inabilitacao de licitante\n' +
      '3. Anulacao ou revogacao da licitacao\n' +
      '4. Extincao do contrato\n' +
      '5. Aplicacao de sancoes\n\n' +
      '**Procedimento recursal:**\n\n' +
      '1. O licitante manifesta intencao de recurso imediatamente na sessao, com breve exposicao de motivos.\n' +
      '2. O pregoeiro/comissao avalia a admissibilidade da intencao.\n' +
      '3. Se admitido, o recorrente tem 3 dias uteis para apresentar as razoes escritas fundamentadas.\n' +
      '4. Os demais licitantes sao notificados e tem 3 dias uteis para contrarrazoes.\n' +
      '5. O pregoeiro/comissao analisa e decide — se mantiver a decisao, encaminha a autoridade superior.\n' +
      '6. A autoridade superior decide em ate 10 dias uteis.\n\n' +
      '**Efeito suspensivo:** O recurso contra o julgamento de propostas e habilitacao tem efeito suspensivo automatico — o processo fica paralisado ate a decisao. Recursos contra anulacao e sancoes tambem possuem efeito suspensivo.\n\n' +
      '**Dica pratica:** A manifestacao de intencao de recurso e OBRIGATORIA para preservar o direito. Se o licitante nao se manifestar imediatamente na sessao, perde o prazo — nao existe segunda chance. Esteja sempre presente (ou com representante) na sessao de abertura.',
    legalBasis: 'Lei 14.133/2021, arts. 165 a 168',
    relatedTerms: ['recurso', 'adjudicacao', 'homologacao'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Entenda os prazos para recurso em licitacao na Lei 14.133: intencao imediata, 3 dias para razoes e 3 para contrarrazoes.',
  },
  {
    slug: 'prazo-publicacao-edital',
    title: 'Qual o prazo minimo de publicacao de edital na Lei 14.133?',
    category: 'prazos-cronogramas',
    answer:
      'A Lei 14.133/2021 estabelece prazos minimos entre a publicacao do edital e a data de abertura das propostas, variando conforme a modalidade e o criterio de julgamento. Esses prazos estao definidos no artigo 55.\n\n' +
      '**Prazos minimos de publicacao:**\n\n' +
      '| Situacao | Prazo Minimo |\n' +
      '|----------|-------------|\n' +
      '| Concorrencia — tecnica e preco | 25 dias uteis |\n' +
      '| Concorrencia — menor preco/maior desconto | 15 dias uteis |\n' +
      '| Pregao — bens e servicos comuns | 8 dias uteis |\n' +
      '| Leilao | 15 dias uteis |\n' +
      '| Dialogo competitivo | 25 dias uteis |\n' +
      '| Concurso | 35 dias uteis |\n\n' +
      '**Regras de publicacao (art. 54):**\n\n' +
      '1. **PNCP obrigatorio:** Todos os editais devem ser publicados no Portal Nacional de Contratacoes Publicas, independente da esfera (federal, estadual, municipal).\n' +
      '2. **Diario Oficial:** Publicacao em diario oficial da unidade federativa.\n' +
      '3. **Jornal de grande circulacao:** Obrigatorio para licitacoes acima de determinados valores.\n' +
      '4. **Site do orgao:** O edital completo deve estar disponivel no site institucional.\n\n' +
      '**Contagem do prazo:**\n' +
      '- Conta-se a partir do primeiro dia util seguinte a publicacao.\n' +
      '- Exclui-se o dia da publicacao e inclui-se o dia do vencimento.\n' +
      '- Somente dias uteis (excluem-se sabados, domingos e feriados).\n\n' +
      '**Alteracao de edital e republicacao:**\n' +
      'Se o edital for alterado apos a publicacao e a alteracao afetar a formulacao das propostas, o prazo de publicacao deve ser reaberto integralmente. Alteracoes menores que nao impactam a proposta nao exigem reabertura de prazo, mas devem ser comunicadas a todos os interessados.\n\n' +
      '**Dica para fornecedores:** Configure alertas no PNCP e em plataformas como o SmartLic para receber notificacoes assim que editais de seu setor forem publicados. Isso maximiza o tempo disponivel para analise e preparacao da proposta.',
    legalBasis: 'Lei 14.133/2021, arts. 54, 55',
    relatedTerms: ['edital', 'licitacao', 'pncp'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Confira os prazos minimos de publicacao de edital na Lei 14.133/2021: 8 dias (pregao), 15-25 dias (concorrencia) e mais.',
  },
  {
    slug: 'vigencia-contrato-administrativo',
    title: 'Qual a vigencia maxima de um contrato administrativo?',
    category: 'prazos-cronogramas',
    answer:
      'A Lei 14.133/2021 trouxe mudancas significativas nos prazos de vigencia de contratos administrativos, ampliando consideravelmente os limites anteriores. Os prazos estao definidos nos artigos 105 a 114.\n\n' +
      '**Vigencia por tipo de contrato:**\n\n' +
      '1. **Servicos e fornecimentos continuados (art. 106):** Vigencia inicial ate 5 anos, prorrogavel por ate 10 anos no total. Servicos com dedicacao exclusiva de mao de obra podem chegar a 10 anos.\n\n' +
      '2. **Obras e servicos de engenharia (art. 111):** A vigencia deve contemplar o prazo necessario para conclusao do objeto, acrescido de prazo para liquidacao e pagamento.\n\n' +
      '3. **Aluguel de equipamentos e utilizacao de programas de informatica (art. 106, par. 2):** Vigencia ate 5 anos, podendo ser prorrogada por ate 10 anos.\n\n' +
      '4. **Contratos de receita (art. 110):** Concessoes de uso de espaco publico e similares podem ter vigencia de ate 10 anos.\n\n' +
      '5. **Concessoes de servico publico (Lei 8.987/95):** Prazos variam conforme a complexidade — tipicamente 20 a 35 anos para concessoes de infraestrutura.\n\n' +
      '**Prorrogacao contratual:**\n\n' +
      'A prorrogacao exige:\n' +
      '- Previsao no edital e no contrato original\n' +
      '- Justificativa por escrito do gestor\n' +
      '- Demonstracao de vantajosidade da prorrogacao versus nova licitacao\n' +
      '- Anuencia do contratado\n' +
      '- Parecer juridico favoravel\n\n' +
      '**Extincao antecipada:**\n' +
      'O contrato pode ser extinto antecipadamente por inadimplemento, interesse publico superveniente, caso fortuito ou forca maior. O contratado tem direito a indenizacao pelos prejuizos comprovados.\n\n' +
      '**Dica para fornecedores:** Ao elaborar a proposta, considere o periodo total possivel de contratacao (incluindo prorrogacoes) para calcular o retorno do investimento. Contratos de servicos continuados com potencial de 10 anos representam receita previsivel de longo prazo — precifique considerando ganhos de escala ao longo do tempo.',
    legalBasis: 'Lei 14.133/2021, arts. 105 a 114',
    relatedTerms: ['contrato-administrativo', 'licitacao', 'edital'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Saiba a vigencia maxima de contratos administrativos na Lei 14.133: ate 5 anos iniciais, prorrogavel a 10 anos ou mais.',
  },
  {
    slug: 'prazo-assinatura-contrato',
    title: 'Qual o prazo para assinatura do contrato apos adjudicacao?',
    category: 'prazos-cronogramas',
    answer:
      'Apos a adjudicacao e homologacao do processo licitatorio, o licitante vencedor e convocado para assinar o contrato dentro do prazo estabelecido no edital. A Lei 14.133/2021 trata desse tema no artigo 90.\n\n' +
      '**Regras de prazo:**\n\n' +
      '1. **Prazo do edital:** O edital deve fixar o prazo para assinatura do contrato, que geralmente varia entre 5 e 30 dias corridos, conforme a complexidade do objeto.\n' +
      '2. **Prazo legal supletivo:** Se o edital nao fixar prazo, aplica-se o prazo de 10 dias corridos a partir da convocacao.\n' +
      '3. **Prorrogacao:** O prazo pode ser prorrogado uma vez, por igual periodo, quando solicitado justificadamente pelo convocado e aceito pela administracao.\n\n' +
      '**Consequencias da nao assinatura:**\n\n' +
      'Se o vencedor nao assinar o contrato no prazo:\n' +
      '- Perde o direito a contratacao.\n' +
      '- Pode ser penalizado com impedimento de licitar (art. 156, III) por prazo de ate 3 anos.\n' +
      '- A administracao convoca o segundo classificado, nas mesmas condicoes do primeiro.\n' +
      '- Se o segundo tambem recusar, convoca o terceiro, e assim sucessivamente.\n\n' +
      '**Documentos exigidos na assinatura:**\n' +
      '- Documentos de habilitacao atualizados (certidoes negativas com validade vigente)\n' +
      '- Comprovante de garantia contratual (se exigida no edital)\n' +
      '- Comprovante de ART/RRT (para obras e servicos de engenharia)\n' +
      '- Dados bancarios para pagamento\n\n' +
      '**Assinatura eletronica:**\n' +
      'A Lei 14.133 permite a assinatura eletronica de contratos (art. 91), o que acelera significativamente o processo. Muitos orgaos ja utilizam plataformas como SEI (Sistema Eletronico de Informacoes) ou gov.br para assinatura digital.\n\n' +
      '**Dica pratica:** Mantenha todas as certidoes negativas atualizadas ANTES do resultado da licitacao. Certidoes vencidas na data da convocacao podem impedir a assinatura e levar a desclassificacao.',
    legalBasis: 'Lei 14.133/2021, arts. 90, 91',
    relatedTerms: ['adjudicacao', 'contrato-administrativo', 'habilitacao'],
    relatedSectors: [],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Saiba o prazo para assinar contrato apos adjudicacao na Lei 14.133: entre 5 e 30 dias conforme edital, prorrogavel uma vez.',
  },
  {
    slug: 'renovacao-contrato-servicos-continuados',
    title:
      'Como funciona a renovacao de contratos de servicos continuados?',
    category: 'prazos-cronogramas',
    answer:
      'Contratos de servicos continuados sao aqueles cuja interrupcao compromete a continuidade das atividades da administracao — como limpeza, vigilancia, manutencao, TI e alimentacao. A Lei 14.133/2021 disciplina a prorrogacao desses contratos no artigo 107.\n\n' +
      '**Regras de prorrogacao:**\n\n' +
      '1. **Vigencia inicial:** Ate 5 anos (art. 106).\n' +
      '2. **Prorrogacao maxima:** O contrato pode ser prorrogado sucessivamente, desde que:\n' +
      '   - O prazo total nao exceda 10 anos (art. 107)\n' +
      '   - A prorrogacao esteja prevista no edital\n' +
      '   - O contratado concorde\n' +
      '   - O gestor justifique a vantajosidade\n' +
      '   - O parecer juridico seja favoravel\n\n' +
      '3. **Servicos com dedicacao exclusiva de mao de obra:** Podem atingir 10 anos de vigencia total. A administracao deve verificar se os custos continuam vantajosos comparados a nova licitacao.\n\n' +
      '**Procedimento de prorrogacao:**\n\n' +
      '1. **Pesquisa de precos:** Antes da prorrogacao, o gestor deve comparar os precos contratados com os praticados no mercado.\n' +
      '2. **Parecer do gestor:** Justificativa tecnica e financeira da vantajosidade.\n' +
      '3. **Anuencia do contratado:** O fornecedor deve concordar expressamente.\n' +
      '4. **Reajuste/repactuacao:** A prorrogacao e o momento adequado para aplicar reajuste pelo indice contratual ou repactuacao por convencao coletiva.\n' +
      '5. **Termo aditivo:** Formalizacao por aditivo contratual, publicado no PNCP.\n\n' +
      '**Reajuste versus repactuacao:**\n' +
      '- **Reajuste:** Correcao automatica por indice (IPCA, INPC, IGP-M). Anual, a partir da data do orcamento.\n' +
      '- **Repactuacao:** Revisao detalhada dos custos com base em convencao coletiva de trabalho. Exclusiva para servicos com dedicacao de mao de obra.\n\n' +
      '**Dica estrategica:** Para fornecedores, contratos de servicos continuados sao os mais valiosos no mercado publico — receita recorrente por ate 10 anos. Invista na qualidade da execucao e no relacionamento com o gestor do contrato, pois a decisao de prorrogar depende diretamente da avaliacao de desempenho.',
    legalBasis: 'Lei 14.133/2021, arts. 106, 107',
    relatedTerms: [
      'contrato-administrativo',
      'reajuste',
      'reequilibrio-economico-financeiro',
    ],
    relatedSectors: ['facilities', 'seguranca'],
    relatedArticles: [],
    metaDescription:
      'Entenda como funciona a prorrogacao de contratos de servicos continuados: vigencia ate 10 anos, reajuste e repactuacao.',
  },
  {
    slug: 'prazo-pagamento-contrato-publico',
    title: 'Qual o prazo de pagamento em contratos publicos?',
    category: 'prazos-cronogramas',
    answer:
      'O prazo de pagamento em contratos publicos e uma das maiores preocupacoes de fornecedores que atuam com o governo. A Lei 14.133/2021 estabelece regras mais claras sobre prazos e penalidades por atraso.\n\n' +
      '**Prazo legal de pagamento (art. 141):**\n\n' +
      'A administracao publica deve efetuar o pagamento em ate 30 (trinta) dias corridos contados do recebimento definitivo do objeto e da apresentacao correta da nota fiscal/fatura. Esse e o prazo maximo — o edital pode fixar prazo menor.\n\n' +
      '**Fluxo de pagamento:**\n\n' +
      '1. **Entrega/execucao:** O fornecedor entrega o bem ou executa o servico.\n' +
      '2. **Recebimento provisorio:** O gestor recebe e verifica preliminarmente (prazo do edital, geralmente 15 dias).\n' +
      '3. **Recebimento definitivo:** Apos conferencia completa, emite o termo de recebimento definitivo.\n' +
      '4. **Emissao da nota fiscal:** O fornecedor emite NF conforme instrucoes do orgao.\n' +
      '5. **Ateste:** O gestor do contrato atesta a nota fiscal, confirmando a execucao.\n' +
      '6. **Liquidacao e pagamento:** O setor financeiro processa o pagamento em ate 30 dias.\n\n' +
      '**Atraso no pagamento:**\n\n' +
      'A Lei 14.133 garante ao contratado o direito a atualizacao monetaria do valor devido em caso de atraso (art. 141, par. unico). Alem disso:\n' +
      '- Atraso superior a 2 meses autoriza o contratado a suspender a execucao (art. 137, par. 2, IV).\n' +
      '- O contratado pode optar pela extincao do contrato se o atraso for reiterado.\n' +
      '- Juros de mora sao devidos pelo poder publico (em geral 1% ao mes).\n\n' +
      '**Antecipacao de pagamento:**\n' +
      'A Lei 14.133 permite antecipacao de pagamento mediante garantia (art. 145), especialmente para obras e fornecimentos que exijam investimento inicial do contratado.\n\n' +
      '**Realidade pratica:** Apesar do prazo legal de 30 dias, atrasos sao frequentes, especialmente em municipios menores. Considere esse risco no seu fluxo de caixa e precifique adequadamente.',
    legalBasis: 'Lei 14.133/2021, arts. 141, 145',
    relatedTerms: ['contrato-administrativo', 'licitacao', 'edital'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Saiba o prazo de pagamento em contratos publicos na Lei 14.133: ate 30 dias do recebimento definitivo. Veja direitos do fornecedor.',
  },
  {
    slug: 'cronograma-pregao-eletronico',
    title: 'Quanto tempo demora um pregao eletronico do inicio ao fim?',
    category: 'prazos-cronogramas',
    answer:
      'O tempo total de um pregao eletronico varia conforme a complexidade do objeto, o numero de participantes e eventuais recursos. Em media, o processo completo leva entre 30 e 90 dias da publicacao do edital a assinatura do contrato.\n\n' +
      '**Cronograma tipico de um pregao eletronico:**\n\n' +
      '| Fase | Duracao Tipica |\n' +
      '|------|---------------|\n' +
      '| Publicacao do edital | D+0 |\n' +
      '| Prazo de impugnacao | 3 a 8 dias uteis |\n' +
      '| Prazo minimo para propostas | 8 dias uteis |\n' +
      '| Sessao publica (abertura + lances) | 1 dia (2-6 horas) |\n' +
      '| Habilitacao do vencedor | 1-5 dias uteis |\n' +
      '| Manifestacao de intencao de recurso | Imediata (sessao) |\n' +
      '| Prazo para razoes de recurso | 3 dias uteis |\n' +
      '| Prazo para contrarrazoes | 3 dias uteis |\n' +
      '| Decisao do recurso | 5-10 dias uteis |\n' +
      '| Adjudicacao + homologacao | 1-5 dias uteis |\n' +
      '| Convocacao para contrato | 5-10 dias corridos |\n\n' +
      '**Cenarios de tempo total:**\n\n' +
      '- **Sem recursos:** 25-35 dias corridos (melhor cenario)\n' +
      '- **Com 1 recurso:** 40-60 dias corridos\n' +
      '- **Com diligencias + recursos:** 60-90 dias corridos\n' +
      '- **Com impugnacao acatada (republicacao):** 50-80 dias corridos\n\n' +
      '**Fatores que aceleram o processo:**\n' +
      '- Termo de referencia bem elaborado (menos pedidos de esclarecimento)\n' +
      '- Poucos itens no certame\n' +
      '- Licitantes com documentacao atualizada no SICAF\n' +
      '- Ausencia de recursos\n\n' +
      '**Fatores que atrasam:**\n' +
      '- Impugnacoes acatadas (republicacao integral)\n' +
      '- Multiplos recursos em cadeia\n' +
      '- Diligencias para esclarecimentos\n' +
      '- Licitantes com certidoes vencidas (nova convocacao necessaria)\n\n' +
      '**Dica para fornecedores:** Planeje seu calendario de licitacoes considerando 60 dias como media segura do edital ao contrato. Mantenha estoque/equipe prontos para iniciar a execucao rapidamente apos a assinatura — atrasos na mobilizacao podem gerar sancoes contratuais.',
    legalBasis: 'Lei 14.133/2021, arts. 55, 164, 165',
    relatedTerms: ['pregao-eletronico', 'edital', 'adjudicacao'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Veja quanto tempo demora um pregao eletronico: de 30 a 90 dias. Cronograma completo de cada fase do processo.',
  },

  /* ================================================================ */
  /*  DOCUMENTACAO E HABILITACAO (10)                                  */
  /* ================================================================ */
  {
    slug: 'documentos-habilitacao-licitacao',
    title: 'Quais documentos sao exigidos na habilitacao de licitacao?',
    category: 'documentacao-habilitacao',
    answer:
      'A habilitacao e a fase do processo licitatorio em que a administracao verifica se o licitante possui condicoes juridicas, fiscais, tecnicas e financeiras para executar o contrato. A Lei 14.133/2021 define os documentos exigiveis nos artigos 62 a 70.\n\n' +
      '**Categorias de documentos de habilitacao:**\n\n' +
      '**1. Habilitacao juridica (art. 66):**\n' +
      '- Ato constitutivo (contrato social ou estatuto) atualizado\n' +
      '- Documento de identidade do representante legal\n' +
      '- Procuracao (se representante nao for socio)\n\n' +
      '**2. Regularidade fiscal e trabalhista (art. 68):**\n' +
      '- CND Federal (conjunta PGFN/RFB)\n' +
      '- CND Estadual (ICMS)\n' +
      '- CND Municipal (ISS)\n' +
      '- CRF do FGTS\n' +
      '- CNDT (Certidao Negativa de Debitos Trabalhistas)\n' +
      '- Prova de inscricao no CNPJ\n\n' +
      '**3. Qualificacao economico-financeira (art. 69):**\n' +
      '- Balanco patrimonial do ultimo exercicio\n' +
      '- Certidao negativa de falencia/recuperacao judicial\n' +
      '- Indices financeiros (liquidez geral, liquidez corrente, solvencia geral — minimo 1,0 salvo justificativa)\n' +
      '- Capital social minimo ou patrimonio liquido (ate 10% do valor estimado)\n\n' +
      '**4. Qualificacao tecnica (art. 67):**\n' +
      '- Registro no conselho profissional (CREA, CRA, CRN, etc.)\n' +
      '- Atestados de capacidade tecnica\n' +
      '- Indicacao de equipe tecnica (para servicos especializados)\n\n' +
      '**Regras importantes:**\n' +
      '- O edital NAO pode exigir documentos alem dos previstos na Lei 14.133 (art. 62, par. 1).\n' +
      '- Micro e pequenas empresas podem regularizar a documentacao fiscal ate a assinatura do contrato (art. 43, par. 1).\n' +
      '- O SICAF substitui a apresentacao de documentos nele cadastrados.\n' +
      '- Certidoes obtidas por internet podem ser verificadas diretamente pelo pregoeiro.\n\n' +
      '**Dica pratica:** Crie um checklist permanente de todos os documentos e verifique validades mensalmente. Certidoes vencem a cada 180 dias e a falta de uma unica pode causar inabilitacao.',
    legalBasis: 'Lei 14.133/2021, arts. 62 a 70',
    relatedTerms: ['habilitacao', 'certidao-negativa', 'sicaf'],
    relatedSectors: [],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Veja todos os documentos exigidos na habilitacao de licitacao: juridica, fiscal, tecnica e financeira conforme Lei 14.133.',
  },
  {
    slug: 'sicaf-o-que-e-como-cadastrar',
    title: 'O que e SICAF e como se cadastrar?',
    category: 'documentacao-habilitacao',
    answer:
      'O SICAF (Sistema de Cadastramento Unificado de Fornecedores) e o cadastro oficial do Governo Federal para empresas que desejam participar de licitacoes federais. Mantido pelo Ministerio da Gestao e da Inovacao em Servicos Publicos, o SICAF centraliza e valida a documentacao dos fornecedores.\n\n' +
      '**O que o SICAF oferece:**\n' +
      '- Cadastro unificado para todas as licitacoes federais\n' +
      '- Validacao automatica de certidoes (via integracao com orgaos emissores)\n' +
      '- Substituicao da apresentacao fisica de documentos na habilitacao\n' +
      '- Niveis de credenciamento progressivos\n\n' +
      '**Como se cadastrar no SICAF:**\n\n' +
      '1. **Acesse o portal:** Entre em comprasnet.gov.br (ou comprasgov.br) com login gov.br.\n' +
      '2. **Solicite o cadastro:** Selecione "Cadastrar Fornecedor" e preencha os dados basicos (CNPJ, razao social, endereco, atividade economica).\n' +
      '3. **Selecione niveis de cadastro:**\n' +
      '   - Nivel I: Credenciamento (dados basicos)\n' +
      '   - Nivel II: Habilitacao juridica (contrato social)\n' +
      '   - Nivel III: Regularidade fiscal (certidoes federais, estaduais, municipais)\n' +
      '   - Nivel IV: Qualificacao tecnica (registro profissional)\n' +
      '   - Nivel V: Qualificacao economico-financeira (balanco patrimonial)\n' +
      '   - Nivel VI: Completo (todos os niveis)\n' +
      '4. **Envie documentos digitalizados:** Faca upload dos documentos correspondentes a cada nivel.\n' +
      '5. **Validacao:** O sistema valida certidoes automaticamente. Documentos que exigem analise manual sao avaliados em ate 3 dias uteis.\n\n' +
      '**Manutencao do SICAF:**\n' +
      '- Certidoes vencem a cada 180 dias — renove antes do vencimento.\n' +
      '- O balanco patrimonial deve ser atualizado anualmente (ate 30 de abril).\n' +
      '- Alteracoes contratuais devem ser refletidas imediatamente.\n\n' +
      '**O SICAF e obrigatorio?**\n' +
      'Para licitacoes federais, o SICAF e o sistema padrao e seu uso e fortemente recomendado. Para licitacoes estaduais e municipais, cada ente pode ter seu proprio cadastro (como CAUFESP em SP ou CRC nos municipios), mas o SICAF e amplamente aceito como referencia.',
    legalBasis: 'Lei 14.133/2021, art. 87',
    relatedTerms: ['sicaf', 'habilitacao', 'certidao-negativa'],
    relatedSectors: [],
    relatedArticles: ['sicaf-como-cadastrar-manter-ativo-2026'],
    metaDescription:
      'Entenda o que e SICAF, como se cadastrar passo a passo, niveis de credenciamento e dicas para manter o cadastro ativo.',
  },
  {
    slug: 'atestado-capacidade-tecnica',
    title: 'O que e atestado de capacidade tecnica e quem emite?',
    category: 'documentacao-habilitacao',
    answer:
      'O atestado de capacidade tecnica (ACT) e o documento que comprova que uma empresa ja executou com sucito servicos ou fornecimentos similares ao objeto da licitacao. E emitido por clientes anteriores — orgaos publicos ou empresas privadas — e constitui a principal prova de experiencia tecnica exigida nos processos licitatorios.\n\n' +
      '**Quem emite o atestado:**\n' +
      '- Orgaos publicos que contrataram o fornecedor\n' +
      '- Empresas privadas que receberam servicos ou produtos\n' +
      '- Qualquer pessoa juridica de direito publico ou privado\n\n' +
      '**O que o atestado deve conter:**\n' +
      '1. Identificacao do emitente (razao social, CNPJ, endereco)\n' +
      '2. Descricao detalhada do servico ou fornecimento realizado\n' +
      '3. Quantidades executadas (parcelas de maior relevancia)\n' +
      '4. Periodo de execucao (datas de inicio e termino)\n' +
      '5. Avaliacao de qualidade (desempenho satisfatorio)\n' +
      '6. Assinatura do responsavel pelo emitente\n\n' +
      '**Regras da Lei 14.133/2021 (art. 67):**\n\n' +
      '- A administracao pode exigir atestados que comprovem a execucao de **parcelas de maior relevancia tecnica** e de **valor significativo** do objeto.\n' +
      '- E vedado exigir quantitativos minimos ou prazos maximos de experiencia (sumula 263 TCU), salvo em casos tecnicamente justificados.\n' +
      '- Os atestados devem ser referentes a servicos de natureza e complexidade similares ao objeto — nao identicos.\n' +
      '- O orgao licitante pode realizar diligencia para confirmar as informacoes do atestado.\n\n' +
      '**Acervo tecnico (CREA/CAU):**\n' +
      'Para servicos de engenharia e arquitetura, alem do atestado da empresa, exige-se a Certidao de Acervo Tecnico (CAT) emitida pelo CREA ou CAU, que comprova a experiencia dos profissionais indicados como responsaveis tecnicos.\n\n' +
      '**Dica pratica:** Solicite atestados de TODOS os seus clientes ao final de cada contrato, mesmo os privados. Mantenha um portfolio organizado por tipo de servico e valor. Quanto maior seu acervo de atestados, mais licitacoes voce atendera.',
    legalBasis: 'Lei 14.133/2021, art. 67',
    relatedTerms: ['habilitacao', 'licitacao', 'parecer-tecnico'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Saiba o que e atestado de capacidade tecnica, quem emite, o que deve conter e como usar em licitacoes (Lei 14.133).',
  },
  {
    slug: 'certidoes-negativas-obrigatorias',
    title: 'Quais certidoes negativas sao obrigatorias em licitacoes?',
    category: 'documentacao-habilitacao',
    answer:
      'As certidoes negativas de debito sao documentos que comprovam a regularidade fiscal e trabalhista da empresa perante os orgaos governamentais. Na Lei 14.133/2021, as certidoes exigiveis estao listadas no artigo 68.\n\n' +
      '**Certidoes obrigatorias:**\n\n' +
      '1. **CND Federal (Conjunta PGFN/RFB):**\n' +
      '   - Certidao Conjunta de Debitos Relativos a Tributos Federais e a Divida Ativa da Uniao\n' +
      '   - Emissao: site da Receita Federal (www.gov.br/receitafederal)\n' +
      '   - Validade: 180 dias\n\n' +
      '2. **CRF do FGTS:**\n' +
      '   - Certificado de Regularidade do FGTS\n' +
      '   - Emissao: site da Caixa Economica Federal (www.caixa.gov.br)\n' +
      '   - Validade: 30 dias\n\n' +
      '3. **CNDT (Trabalhista):**\n' +
      '   - Certidao Negativa de Debitos Trabalhistas\n' +
      '   - Emissao: site do TST (www.tst.jus.br)\n' +
      '   - Validade: 180 dias\n\n' +
      '4. **CND Estadual (ICMS):**\n' +
      '   - Certidao de Regularidade Fiscal Estadual\n' +
      '   - Emissao: site da Secretaria de Fazenda do estado\n' +
      '   - Validade: varia por estado (60-180 dias)\n\n' +
      '5. **CND Municipal (ISS):**\n' +
      '   - Certidao de Regularidade Fiscal Municipal\n' +
      '   - Emissao: site da Prefeitura ou Secretaria de Financas\n' +
      '   - Validade: varia por municipio (60-180 dias)\n\n' +
      '6. **Certidao Negativa de Falencia/Recuperacao Judicial:**\n' +
      '   - Emissao: distribuidor judicial da comarca da sede da empresa\n' +
      '   - Validade: 90 dias (em geral)\n\n' +
      '**Certidao positiva com efeitos de negativa:**\n' +
      'Se a empresa tiver debitos com exigibilidade suspensa (parcelamento, liminar judicial, etc.), a certidao emitida sera "positiva com efeitos de negativa" — tem o mesmo valor da certidao negativa para fins de habilitacao.\n\n' +
      '**Beneficio para ME/EPP:**\n' +
      'Micro e pequenas empresas podem participar da licitacao mesmo com certidoes fiscais irregulares, desde que regularizem a situacao em ate 5 dias uteis apos a declaracao de vencedor (art. 43, par. 1 da LC 123/2006).\n\n' +
      '**Dica:** Configure alertas de vencimento para cada certidao. A falta de uma unica certidao valida no momento da habilitacao resulta em inabilitacao automatica.',
    legalBasis: 'Lei 14.133/2021, art. 68',
    relatedTerms: ['certidao-negativa', 'habilitacao', 'sicaf'],
    relatedSectors: [],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Lista completa de certidoes negativas obrigatorias em licitacoes: CND Federal, CRF FGTS, CNDT, estadual e municipal.',
  },
  {
    slug: 'qualificacao-tecnica-lei-14133',
    title: 'O que mudou na qualificacao tecnica com a Lei 14.133?',
    category: 'documentacao-habilitacao',
    answer:
      'A Lei 14.133/2021 trouxe mudancas significativas na qualificacao tecnica exigida em licitacoes, buscando equilibrar a necessidade de comprovar capacidade com o principio da competitividade. As regras estao no artigo 67.\n\n' +
      '**Principais mudancas:**\n\n' +
      '**1. Profissional de referencia (art. 67, I e II):**\n' +
      'A lei distingue entre qualificacao tecnico-profissional (do responsavel tecnico) e tecnico-operacional (da empresa). Para obras e servicos de engenharia, pode ser exigida a comprovacao de que a empresa possui profissional com experiencia em parcelas de maior relevancia tecnica.\n\n' +
      '**2. Limite de exigencia de quantitativos (art. 67, par. 1):**\n' +
      'A administracao nao pode exigir atestados com quantidades identicas ao objeto — deve aceitar atestados que demonstrem capacidade tecnica proporcional. A jurisprudencia do TCU admite ate 50% do quantitativo como referencia razoavel.\n\n' +
      '**3. Experiencia com especificidade (art. 67, par. 3):**\n' +
      'A lei permite exigir experiencia especifica em parcelas de maior relevancia tecnica e valor significativo, devidamente justificadas no estudo tecnico preliminar.\n\n' +
      '**4. Indicacao da equipe tecnica (art. 67, par. 6):**\n' +
      'A equipe tecnica indicada na habilitacao deve ser mantida durante a execucao. A substituicao so e permitida com anuencia da administracao e por profissional de experiencia equivalente ou superior.\n\n' +
      '**5. Visita tecnica facultativa (art. 63, par. 2):**\n' +
      'A visita tecnica ao local da obra/servico nao pode ser exigida como condicio obrigatoria — deve ser substituida por declaracao de conhecimento das condicoes locais.\n\n' +
      '**6. Soma de atestados (art. 67, par. 2):**\n' +
      'Quando o edital exigir comprovacao de capacidade para parcelas de diferentes naturezas, permite-se a apresentacao de atestados distintos (somatorios) para cada parcela, ampliando a participacao.\n\n' +
      '**Impacto pratico:**\n' +
      'Essas mudancas beneficiam principalmente empresas de medio porte, que agora tem mais facilidade para comprovar capacidade tecnica em licitacoes maiores. A proibicao de exigencias excessivas amplia a competitividade e reduz o direcionamento.',
    legalBasis: 'Lei 14.133/2021, art. 67',
    relatedTerms: ['habilitacao', 'parecer-tecnico', 'licitacao'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Veja as mudancas na qualificacao tecnica da Lei 14.133: novos limites para atestados, soma de experiencias e mais.',
  },
  {
    slug: 'me-epp-beneficios-licitacao',
    title: 'Quais beneficios ME e EPP tem em licitacoes?',
    category: 'documentacao-habilitacao',
    answer:
      'Microempresas (ME) e Empresas de Pequeno Porte (EPP) possuem tratamento diferenciado e favorecido em licitacoes publicas, garantido pela Lei Complementar 123/2006 e reafirmado pela Lei 14.133/2021 (arts. 4 e 48).\n\n' +
      '**Principais beneficios:**\n\n' +
      '**1. Empate ficto / lance diferenciado (art. 44, LC 123):**\n' +
      'Se a proposta da ME/EPP for ate 5% superior a melhor proposta (10% na concorrencia), ela tem direito a oferecer um lance final inferior, empatando ou superando o primeiro colocado. No pregao eletronico, o sistema convoca automaticamente.\n\n' +
      '**2. Regularizacao fiscal tardia (art. 43, par. 1, LC 123):**\n' +
      'ME/EPP com certidoes fiscais irregulares pode participar da licitacao e, se vencedora, tem ate 5 dias uteis para regularizar a situacao. Esse beneficio nao se aplica a qualificacao tecnica ou economico-financeira.\n\n' +
      '**3. Licitacoes exclusivas (art. 48, I, LC 123):**\n' +
      'Contratacoes de ate R$ 80.000,00 podem ser destinadas exclusivamente a ME/EPP. Muitos orgaos usam esse limite regularmente.\n\n' +
      '**4. Subcontratacao obrigatoria (art. 48, II, LC 123):**\n' +
      'O edital pode exigir que o vencedor subcontrate ME/EPP para ate 30% do objeto.\n\n' +
      '**5. Cota reservada (art. 48, III, LC 123):**\n' +
      'Em licitacoes de bens divisiveis, ate 25% do quantitativo pode ser reservado para ME/EPP.\n\n' +
      '**6. Credenciamento simplificado no SICAF:**\n' +
      'Processo de cadastro facilitado com menos documentos.\n\n' +
      '**Como comprovar o enquadramento:**\n' +
      '- ME: Faturamento bruto anual ate R$ 360.000,00\n' +
      '- EPP: Faturamento bruto anual entre R$ 360.000,01 e R$ 4.800.000,00\n' +
      '- Declaracao no sistema eletronico no momento do cadastro da proposta\n' +
      '- Certidao da Junta Comercial ou declaracao do contador\n\n' +
      '**Atencao:** A declaracao falsa de enquadramento como ME/EPP constitui fraude, sujeitando a empresa a sancoes administrativas e penais. Alem disso, o beneficio do empate ficto nao se aplica quando ME/EPP ultrapassa o limite de faturamento no exercicio anterior.',
    legalBasis:
      'LC 123/2006, arts. 43-49; Lei 14.133/2021, arts. 4, 48',
    relatedTerms: ['licitacao', 'habilitacao', 'pregao-eletronico'],
    relatedSectors: [],
    relatedArticles: ['mei-microempresa-vantagens-licitacoes'],
    metaDescription:
      'Conheca os beneficios de ME e EPP em licitacoes: empate ficto, regularizacao fiscal, cotas exclusivas e licitacoes ate R$80 mil.',
  },
  {
    slug: 'consorcio-licitacao-como-funciona',
    title: 'Como funciona consorcio em licitacoes publicas?',
    category: 'documentacao-habilitacao',
    answer:
      'O consorcio e a uniao temporaria de duas ou mais empresas para participar de licitacoes e executar contratos publicos que, individualmente, nenhuma delas teria capacidade tecnica ou financeira suficiente. A Lei 14.133/2021 disciplina os consorcios no artigo 15.\n\n' +
      '**Quando formar consorcio:**\n' +
      '- Obras de grande porte que exigem especializacoes complementares\n' +
      '- Contratos com exigencias de qualificacao tecnica e financeira elevadas\n' +
      '- Quando a soma de atestados de diferentes empresas e necessaria\n' +
      '- Projetos que combinam engenharia civil, eletrica, mecanica, etc.\n\n' +
      '**Regras legais (art. 15):**\n\n' +
      '1. **Compromisso de constituicao:** Apresentar compromisso publico ou particular de constituicao do consorcio, assinado pelos consorciados.\n' +
      '2. **Lider do consorcio:** Indicar uma empresa lider, responsavel pela representacao perante a administracao.\n' +
      '3. **Responsabilidade solidaria:** Todos os consorciados sao solidariamente responsaveis pelas obrigacoes do consorcio.\n' +
      '4. **Habilitacao individual:** Cada consorciado apresenta seus proprios documentos de habilitacao.\n' +
      '5. **Soma de capacidades:** A qualificacao tecnica e economico-financeira pode ser somada entre os consorciados.\n\n' +
      '**Acrescimo na qualificacao (art. 15, par. 1):**\n' +
      'O edital pode exigir acrescimo de ate 30% nos requisitos de qualificacao economico-financeira para consorcios, como forma de garantir capacidade adequada.\n\n' +
      '**Vedacao de participacao simultanea (art. 15, par. 4):**\n' +
      'A empresa consorciada nao pode participar da mesma licitacao individualmente ou em outro consorcio.\n\n' +
      '**Consorcio de ME/EPP:**\n' +
      'Nas licitacoes exclusivas para ME/EPP, admite-se a participacao de consorcio formado exclusivamente por essas empresas, mantendo os beneficios da LC 123/2006.\n\n' +
      '**Dica pratica:** Antes de formar consorcio, defina claramente em contrato particular: a participacao percentual de cada empresa, a divisao de responsabilidades, o regime de faturamento e a gestao de riscos. O acordo de consorcio deve ser solido para evitar conflitos durante a execucao.',
    legalBasis: 'Lei 14.133/2021, art. 15',
    relatedTerms: ['licitacao', 'habilitacao', 'proposta'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: [],
    metaDescription:
      'Entenda como funciona consorcio em licitacoes: quando formar, regras da Lei 14.133, responsabilidade solidaria e habilitacao.',
  },
  {
    slug: 'subcontratacao-permitida-licitacao',
    title: 'Quando a subcontratacao e permitida em licitacoes?',
    category: 'documentacao-habilitacao',
    answer:
      'A subcontratacao e a transferencia parcial da execucao do contrato a terceiros, mantendo o contratado original como responsavel perante a administracao. A Lei 14.133/2021 regula o tema no artigo 122.\n\n' +
      '**Regras gerais de subcontratacao:**\n\n' +
      '1. **Previsao no edital:** A subcontratacao so e permitida se expressamente prevista no edital e no contrato. Sem previsao, e vedada.\n' +
      '2. **Limites:** O edital define o percentual maximo subcontratavel e as parcelas que podem ser subcontratadas.\n' +
      '3. **Nucleo do objeto:** A parcela principal do objeto (nucleo) nao pode ser subcontratada — esta e reservada ao contratado.\n' +
      '4. **Autorizacao previa:** O contratado deve solicitar autorizacao a administracao antes de subcontratar.\n' +
      '5. **Qualificacao do subcontratado:** O subcontratado deve atender aos requisitos de qualificacao tecnica exigidos para a parcela subcontratada.\n\n' +
      '**O que nao pode ser subcontratado:**\n' +
      '- A totalidade do objeto\n' +
      '- Parcelas para as quais se exigiu qualificacao tecnica especifica na habilitacao\n' +
      '- Parcelas que justificaram a contratacao do fornecedor especifico\n\n' +
      '**Responsabilidade:**\n' +
      'Mesmo com subcontratacao, o contratado original permanece integralmente responsavel perante a administracao. Problemas causados pelo subcontratado sao atribuidos ao contratado principal.\n\n' +
      '**Subcontratacao obrigatoria de ME/EPP:**\n' +
      'Conforme a LC 123/2006 (art. 48, II), o edital pode exigir que o vencedor subcontrate ME/EPP para ate 30% do objeto, como mecanismo de fomento a participacao de pequenas empresas.\n\n' +
      '**Dica para fornecedores:** Se voce planeja subcontratar parte da execucao, declare isso na proposta e identifique o subcontratado. Escolha parceiros de confianca — voce responde por eles. Mantenha controle rigoroso sobre qualidade e prazos da parcela subcontratada.',
    legalBasis: 'Lei 14.133/2021, art. 122',
    relatedTerms: ['contrato-administrativo', 'licitacao', 'habilitacao'],
    relatedSectors: ['engenharia', 'facilities'],
    relatedArticles: [],
    metaDescription:
      'Saiba quando a subcontratacao e permitida em licitacoes na Lei 14.133: limites, regras, autorizacao e responsabilidades.',
  },
  {
    slug: 'garantia-proposta-licitacao',
    title: 'O que e garantia de proposta e quando e exigida?',
    category: 'documentacao-habilitacao',
    answer:
      'A garantia de proposta e uma caução exigida dos licitantes para assegurar que o vencedor cumprira sua obrigacao de assinar o contrato. Trata-se de uma inovacao da Lei 14.133/2021, prevista no artigo 58.\n\n' +
      '**O que e a garantia de proposta:**\n\n' +
      'E um valor que o licitante deposita ou apresenta como caucao ao participar da licitacao. Se o vencedor desistir de assinar o contrato sem justificativa, a administracao executa a garantia. Se o licitante nao vencer ou se o processo for normal, a garantia e devolvida integralmente.\n\n' +
      '**Quando e exigida:**\n' +
      '- Em licitacoes de obras, servicos e fornecimentos de GRANDE VULTO (art. 58, paragrafo unico)\n' +
      '- Quando o valor estimado da contratacao justificar a exigencia\n' +
      '- A criterio da administracao, desde que prevista no edital\n' +
      '- NAO pode ser exigida em pregao para bens e servicos comuns de baixo valor\n\n' +
      '**Limites:**\n' +
      '- Ate 1% do valor estimado da contratacao (art. 58)\n\n' +
      '**Modalidades de garantia aceitas:**\n' +
      '1. **Caucao em dinheiro:** Deposito em conta bancaria indicada pelo orgao\n' +
      '2. **Seguro-garantia:** Apolice emitida por seguradora autorizada pela SUSEP\n' +
      '3. **Fianca bancaria:** Carta de fianca emitida por instituicao financeira\n' +
      '4. **Titulo da divida publica:** Titulos federais escriturais\n\n' +
      '**Diferenca entre garantia de proposta e garantia contratual:**\n\n' +
      '| Aspecto | Garantia de Proposta | Garantia Contratual |\n' +
      '|---------|---------------------|--------------------|\n' +
      '| Fase | Licitacao | Contrato |\n' +
      '| Limite | Ate 1% | Ate 5% (30% para grande vulto) |\n' +
      '| Finalidade | Assegurar assinatura | Assegurar execucao |\n' +
      '| Devolucao | Apos adjudicacao | Apos execucao completa |\n\n' +
      '**Dica pratica:** Ao participar de licitacoes de grande vulto, ja tenha pre-aprovacao de seguro-garantia com sua seguradora. O custo da apolice e geralmente entre 0,5% e 2% do valor segurado — inclua esse custo na formacao do preco da proposta.',
    legalBasis: 'Lei 14.133/2021, art. 58',
    relatedTerms: ['proposta', 'licitacao', 'contrato-administrativo'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: [],
    metaDescription:
      'Entenda o que e garantia de proposta na Lei 14.133: ate 1% do valor estimado, quando e exigida e modalidades aceitas.',
  },
  {
    slug: 'cadastro-pncp-fornecedor',
    title: 'Como se cadastrar no PNCP como fornecedor?',
    category: 'documentacao-habilitacao',
    answer:
      'O PNCP (Portal Nacional de Contratacoes Publicas) e a plataforma oficial do Governo Federal para divulgacao e centralizacao de informacoes sobre licitacoes e contratos publicos de todas as esferas (federal, estadual e municipal). Foi instituido pela Lei 14.133/2021 (art. 174).\n\n' +
      '**Importante esclarecer:** O PNCP e primariamente um portal de PUBLICIDADE e TRANSPARENCIA, nao um sistema transacional de licitacoes como o ComprasGov. Ou seja, as licitacoes sao publicadas no PNCP, mas a participacao efetiva (envio de propostas, lances, documentos) ocorre na plataforma especifica indicada no edital.\n\n' +
      '**Como acessar o PNCP como fornecedor:**\n\n' +
      '1. **Acesse o portal:** Navegue ate pncp.gov.br\n' +
      '2. **Login gov.br:** Faca login com sua conta gov.br (nivel prata ou ouro)\n' +
      '3. **Vincule seu CNPJ:** Associe o CNPJ da empresa a sua conta pessoal\n' +
      '4. **Consulte licitacoes:** Use os filtros de busca para encontrar oportunidades por:\n' +
      '   - Palavra-chave no objeto\n' +
      '   - UF e municipio\n' +
      '   - Modalidade de licitacao\n' +
      '   - Faixa de valor estimado\n' +
      '   - Data de publicacao\n' +
      '   - Orgao contratante\n\n' +
      '**Para participar de licitacoes, voce precisa se cadastrar nos sistemas transacionais:**\n' +
      '- **ComprasGov (federal):** comprasgov.br — exige certificado digital e SICAF\n' +
      '- **BEC-SP (Sao Paulo):** bec.sp.gov.br — cadastro proprio\n' +
      '- **Licitacoes-e (Banco do Brasil):** licitacoes-e.com.br — cadastro e certificado digital\n' +
      '- **Portal de Compras Publicas:** portaldecompraspublicas.com.br — cadastro gratuito\n' +
      '- **BLL Compras:** bllcompras.com — cadastro e certificado digital\n\n' +
      '**Beneficios de acompanhar o PNCP:**\n' +
      '- Visao centralizada de todas as licitacoes do pais\n' +
      '- Acesso a atas, contratos e aditivos publicados\n' +
      '- Consulta a historico de precos practicados\n' +
      '- Transparencia total do processo licitatorio\n\n' +
      '**Dica:** Use o SmartLic para monitorar o PNCP automaticamente com alertas por setor, regiao e valor — muito mais eficiente do que consultas manuais diarias.',
    legalBasis: 'Lei 14.133/2021, art. 174',
    relatedTerms: ['pncp', 'sicaf', 'licitacao'],
    relatedSectors: [],
    relatedArticles: ['sicaf-como-cadastrar-manter-ativo-2026'],
    metaDescription:
      'Aprenda a acessar o PNCP como fornecedor, consultar licitacoes e se cadastrar nos sistemas de compras publicas.',
  },

  /* ================================================================ */
  /*  PRECOS E PROPOSTAS (9)                                           */
  /* ================================================================ */
  {
    slug: 'como-calcular-preco-proposta-licitacao',
    title: 'Como calcular o preco de uma proposta de licitacao?',
    category: 'precos-propostas',
    answer:
      'O calculo correto do preco de uma proposta de licitacao e o fator determinante entre vencer o certame com lucro ou ser desclassificado por inexequibilidade. A formacao de precos deve ser tecnica, documentada e competitiva.\n\n' +
      '**Estrutura basica de formacao de precos:**\n\n' +
      '1. **Custos diretos:** Materiais, insumos, mao de obra direta, equipamentos, transporte.\n' +
      '2. **Custos indiretos:** Supervisao, administracao de obra/servico, alimentacao, EPI.\n' +
      '3. **Despesas administrativas:** Aluguel, contabilidade, departamento pessoal, seguros.\n' +
      '4. **Encargos sociais e trabalhistas:** INSS, FGTS, 13o, ferias, rescisao (entre 60% e 90% do salario, conforme o regime).\n' +
      '5. **BDI (Bonificacoes e Despesas Indiretas):** Para obras e servicos de engenharia.\n' +
      '6. **Tributos:** ISS, PIS, COFINS, IRPJ, CSLL (variam conforme regime tributario).\n' +
      '7. **Lucro:** Margem de retorno sobre o investimento.\n\n' +
      '**Fontes para pesquisa de precos:**\n' +
      '- **Painel de precos do governo** (paineldeprecos.planejamento.gov.br)\n' +
      '- **PNCP:** Contratos e atas de registro de precos similares\n' +
      '- **SINAPI/SICRO:** Tabelas referenciais para obras (Caixa/DNIT)\n' +
      '- **Cotacoes de fornecedores:** Minimo 3 cotacoes\n' +
      '- **Contratos anteriores:** Seus proprios contratos como referencia\n\n' +
      '**Passo a passo:**\n\n' +
      '1. Leia o edital e o termo de referencia integralmente\n' +
      '2. Identifique todos os custos envolvidos na execucao\n' +
      '3. Pesquise precos de mercado e referencias publicas\n' +
      '4. Monte a planilha de custos item a item\n' +
      '5. Aplique encargos sociais e tributos corretos\n' +
      '6. Adicione margem de lucro realista\n' +
      '7. Verifique se o preco final esta acima do limite de inexequibilidade\n' +
      '8. Compare com o valor estimado do edital (quando divulgado)\n\n' +
      '**Regra de ouro:** O preco deve ser competitivo o suficiente para vencer, mas alto o bastante para garantir execucao com qualidade e lucro. Vencer com preco inexequivel e pior do que perder.',
    legalBasis: 'Lei 14.133/2021, arts. 23, 59',
    relatedTerms: ['proposta', 'licitacao', 'bdi'],
    relatedSectors: [],
    relatedArticles: ['como-calcular-preco-proposta-licitacao'],
    metaDescription:
      'Aprenda a calcular o preco de proposta para licitacao: custos diretos, encargos, BDI, tributos e margem de lucro.',
  },
  {
    slug: 'preco-inexequivel-licitacao',
    title: 'O que e preco inexequivel e como evitar desclassificacao?',
    category: 'precos-propostas',
    answer:
      'Preco inexequivel e aquele manifestamente insuficiente para cobrir os custos de execucao do contrato. A administracao deve desclassificar propostas com precos inexequiveis para proteger o interesse publico, evitando contratacoes que resultem em inadimplemento.\n\n' +
      '**Criterios de inexequibilidade na Lei 14.133/2021:**\n\n' +
      '**Para obras e servicos de engenharia (art. 59, par. 4):**\n' +
      'Considera-se inexequivel a proposta cujo valor global seja inferior a 75% do orcamento estimado pela administracao. Para itens individuais, o limite e 75% do custo unitario.\n\n' +
      '**Para bens e servicos em geral (art. 59, par. 3):**\n' +
      'Considera-se potencialmente inexequivel a proposta com desconto superior a 50% em relacao ao valor estimado. Nesse caso, o licitante deve comprovar a viabilidade dos precos.\n\n' +
      '**Regra complementar (art. 59, par. 2):**\n' +
      'A proposta nao sera desclassificada automaticamente — o licitante tera a oportunidade de demonstrar a compatibilidade do preco com os custos, apresentando planilha detalhada e comprovantes.\n\n' +
      '**Como evitar a desclassificacao por inexequibilidade:**\n\n' +
      '1. **Planilha detalhada:** Tenha uma planilha de composicao de precos completa, com custos unitarios de materiais, mao de obra, encargos e tributos.\n' +
      '2. **Cotacoes de fornecedores:** Apresente cotacoes que comprovem os precos de insumos.\n' +
      '3. **Contratos anteriores:** Demonstre que ja executou servicos similares com precos equivalentes.\n' +
      '4. **Economia de escala:** Justifique precos baixos com ganhos de escala, produtividade superior ou inovacao tecnologica.\n' +
      '5. **Regime tributario:** Empresas do Simples Nacional podem ter carga tributaria menor, justificando precos mais baixos.\n\n' +
      '**Atencao com "jogo de planilha":**\n' +
      'A pratica de colocar precos irrisoriamente baixos em itens de menor quantidade e precos altos em itens de maior quantidade (para manipular a classificacao) e vedada e pode resultar em sancoes.\n\n' +
      '**Dica:** Sempre calcule o custo real ANTES de definir o preco de lance. Se durante a fase de lances voce se aproximar do limite de inexequibilidade, pare de dar lances — melhor perder a licitacao do que vencer com preco inviavel.',
    legalBasis: 'Lei 14.133/2021, art. 59',
    relatedTerms: ['proposta', 'lance', 'licitacao'],
    relatedSectors: [],
    relatedArticles: [
      'erros-desclassificam-propostas-licitacao',
      'como-calcular-preco-proposta-licitacao',
    ],
    metaDescription:
      'Entenda o que e preco inexequivel em licitacao, os limites da Lei 14.133 e como evitar desclassificacao da proposta.',
  },
  {
    slug: 'bdi-composicao-licitacao',
    title: 'Como compor o BDI para licitacoes de obras e servicos?',
    category: 'precos-propostas',
    answer:
      'O BDI (Bonificacoes e Despesas Indiretas) e o percentual aplicado sobre os custos diretos de uma obra ou servico para cobrir as despesas indiretas, tributos e lucro. E um componente essencial na formacao de precos para licitacoes de engenharia.\n\n' +
      '**Composicao do BDI:**\n\n' +
      '| Componente | Faixa Tipica |\n' +
      '|------------|-------------|\n' +
      '| Administracao central | 3% a 6% |\n' +
      '| Seguros e garantias | 0,5% a 1,5% |\n' +
      '| Riscos e imprevistos | 0,5% a 1,5% |\n' +
      '| Despesas financeiras | 0,5% a 1,5% |\n' +
      '| Lucro | 5% a 10% |\n' +
      '| Tributos (ISS, PIS, COFINS, IRPJ, CSLL) | 6% a 10% |\n' +
      '| **BDI Total Tipico** | **20% a 30%** |\n\n' +
      '**Formula do BDI:**\n\n' +
      'BDI = [(1+AC)(1+S)(1+R)(1+DF)(1+L) / (1-T)] - 1\n\n' +
      'Onde: AC=administracao central, S=seguros, R=riscos, DF=despesas financeiras, L=lucro, T=tributos.\n\n' +
      '**Referencias do TCU (Acordao 2622/2013):**\n' +
      '- Obras: BDI entre 20,34% e 28,43% (referencia)\n' +
      '- Fornecimento de materiais e equipamentos: BDI entre 11,10% e 18,30%\n' +
      '- Servicos especializados: BDI entre 22% e 30%\n\n' +
      '**BDI diferenciado:**\n' +
      'A Lei 14.133 permite a utilizacao de BDIs diferenciados para parcelas distintas da obra. Por exemplo:\n' +
      '- BDI cheio para servicos (25%)\n' +
      '- BDI reduzido para materiais e equipamentos (15%)\n' +
      '- BDI especifico para instalacoes e montagens (20%)\n\n' +
      '**Erros comuns:**\n' +
      '- Incluir encargos sociais no BDI (devem estar nos custos de mao de obra)\n' +
      '- Usar BDI de obras para servicos continuados (sao diferentes)\n' +
      '- Nao considerar o regime tributario correto (Simples, Lucro Presumido, Lucro Real)\n' +
      '- Aplicar BDI sobre materiais fornecidos pelo orgao\n\n' +
      '**Dica:** Use a tabela SINAPI da Caixa como referencia para custos unitarios e o Acordao TCU 2622/2013 como parametro para faixas de BDI. BDI fora da faixa de referencia exige justificativa detalhada.',
    legalBasis: 'Lei 14.133/2021, art. 23, par. 1; Acordao TCU 2622/2013',
    relatedTerms: ['bdi', 'proposta', 'licitacao'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: ['como-calcular-preco-proposta-licitacao'],
    metaDescription:
      'Aprenda a compor o BDI para licitacoes de obras: formula, faixas de referencia do TCU e erros comuns a evitar.',
  },
  {
    slug: 'margem-preferencia-produto-nacional',
    title: 'O que e margem de preferencia para produtos nacionais?',
    category: 'precos-propostas',
    answer:
      'A margem de preferencia e um mecanismo previsto na Lei 14.133/2021 (art. 26) que permite ao poder publico pagar um preco ate determinado percentual superior por produtos e servicos nacionais em relacao a concorrentes estrangeiros, como forma de fomentar a industria nacional.\n\n' +
      '**Como funciona:**\n\n' +
      'Quando o edital preve margem de preferencia, os produtos manufaturados ou servicos nacionais podem ser classificados em primeiro lugar mesmo que sejam ate X% mais caros que o concorrente estrangeiro. Esse percentual e definido por decreto do Poder Executivo.\n\n' +
      '**Limites legais (art. 26):**\n' +
      '- Margem normal: ate 10% sobre o preco do produto estrangeiro\n' +
      '- Margem adicional para produtos com tecnologia nacional: ate 20% cumulativamente\n' +
      '- Deve ser baseada em estudos que demonstrem geracao de emprego e renda, inovacao tecnologica e desenvolvimento produtivo\n\n' +
      '**Setores com margem de preferencia regulamentada:**\n' +
      '- Equipamentos de TI e comunicacoes (Decreto 7.903/2013)\n' +
      '- Farmacos e medicamentos (Decreto 7.713/2012)\n' +
      '- Equipamentos medico-hospitalares\n' +
      '- Veiculos e automoveis\n' +
      '- Confeccoes e calcados\n\n' +
      '**Como comprovar origem nacional:**\n' +
      '- Processo Produtivo Basico (PPB) para eletronicos e informatica\n' +
      '- Certificado de Registro do INPI para inovacao\n' +
      '- Processo produtivo com etapas significativas realizadas no Brasil\n\n' +
      '**Regras da Lei 14.133:**\n' +
      '- A margem de preferencia so se aplica quando prevista em decreto regulamentador especifico\n' +
      '- Nao se aplica quando nao houver producao nacional suficiente para atender a demanda\n' +
      '- O orgao deve justificar a aplicacao no processo administrativo\n\n' +
      '**Impacto para fornecedores nacionais:**\n' +
      'A margem de preferencia pode ser decisiva em licitacoes com participacao de empresas estrangeiras. Se voce fabrica ou fornece produtos com tecnologia nacional, solicite ao orgao licitante a inclusao da margem de preferencia quando aplicavel — e um direito previsto em lei.',
    legalBasis: 'Lei 14.133/2021, art. 26',
    relatedTerms: ['licitacao', 'proposta', 'edital'],
    relatedSectors: ['informatica', 'equipamentos-medicos'],
    relatedArticles: [],
    metaDescription:
      'Saiba o que e margem de preferencia para produtos nacionais em licitacoes: ate 10-20% conforme Lei 14.133/2021.',
  },
  {
    slug: 'reequilibrio-economico-financeiro',
    title:
      'Como solicitar reequilibrio economico-financeiro de contrato?',
    category: 'precos-propostas',
    answer:
      'O reequilibrio economico-financeiro e o instrumento que permite a revisao dos precos contratuais quando eventos extraordinarios, imprevisiveis e alheios a vontade das partes alteram significativamente os custos de execucao. Diferentemente do reajuste (previsivel e automatico), o reequilibrio e excepcional.\n\n' +
      '**Fundamento legal:**\n' +
      'A Lei 14.133/2021 garante a manutencao do equilibrio economico-financeiro do contrato no artigo 124, inciso II, alinea "d", e artigo 134. A Constituicao Federal tambem protege esse direito (art. 37, XXI).\n\n' +
      '**Quando solicitar reequilibrio:**\n' +
      '- Aumento extraordinario de custos de insumos (acima da inflacao normal)\n' +
      '- Alteracao de carga tributaria que impacte o contrato\n' +
      '- Eventos de forca maior (pandemias, guerras, desastres naturais)\n' +
      '- Mudancas legislativas que aumentem custos de execucao\n' +
      '- Variacao cambial abrupta (para insumos importados)\n\n' +
      '**Como solicitar — passo a passo:**\n\n' +
      '1. **Identificar o evento:** Documente o fato extraordinario que causou o desequilibrio.\n' +
      '2. **Demonstrar nexo causal:** Prove que o evento impactou diretamente os custos do contrato.\n' +
      '3. **Quantificar o impacto:** Apresente planilha comparativa de custos antes/depois do evento.\n' +
      '4. **Reunir evidencias:** Notas fiscais, cotacoes, tabelas de precos, noticias, decretos.\n' +
      '5. **Protocolar requerimento:** Enderece ao gestor do contrato com toda a documentacao.\n' +
      '6. **Negociar:** O orgao analisa e negocia o percentual de reequilibrio.\n' +
      '7. **Termo aditivo:** Se aprovado, formaliza-se por aditivo contratual.\n\n' +
      '**Diferenca entre reajuste, repactuacao e reequilibrio:**\n\n' +
      '| Mecanismo | Previsibilidade | Base | Periodicidade |\n' +
      '|-----------|----------------|------|---------------|\n' +
      '| Reajuste | Previsivel | Indice (IPCA, IGP-M) | Anual |\n' +
      '| Repactuacao | Previsivel | Convencao coletiva | Anual |\n' +
      '| Reequilibrio | Imprevisivel | Evento extraordinario | Quando necessario |\n\n' +
      '**Dica:** Nao espere o contrato se tornar inviavel para solicitar reequilibrio. Protocole o pedido assim que identificar o desequilibrio, com documentacao robusta.',
    legalBasis: 'Lei 14.133/2021, arts. 124 (II, d), 134',
    relatedTerms: [
      'reequilibrio-economico-financeiro',
      'reajuste',
      'contrato-administrativo',
    ],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Aprenda a solicitar reequilibrio economico-financeiro de contrato publico: quando, como e documentacao necessaria.',
  },
  {
    slug: 'planilha-custos-formacao-precos',
    title: 'Como preencher a planilha de custos e formacao de precos?',
    category: 'precos-propostas',
    answer:
      'A planilha de custos e formacao de precos e o documento que detalha todos os componentes do preco proposto em licitacoes de servicos, especialmente aqueles com dedicacao exclusiva de mao de obra (limpeza, vigilancia, portaria, etc.). Sua correta elaboracao e obrigatoria e determinante para a classificacao.\n\n' +
      '**Estrutura padrao da planilha (IN SEGES/ME 65/2021):**\n\n' +
      '**Modulo 1 — Composicao da remuneracao:**\n' +
      '- Salario-base (conforme convencao coletiva)\n' +
      '- Adicional de periculosidade/insalubridade\n' +
      '- Adicional noturno (se aplicavel)\n' +
      '- Outros adicionais previstos em CCT\n\n' +
      '**Modulo 2 — Encargos e beneficios:**\n' +
      '- Submudulo 2.1: 13o salario, ferias + 1/3\n' +
      '- Submudulo 2.2: Encargos previdenciarios (INSS, SAT/RAT, Terceiros)\n' +
      '- Submudulo 2.3: FGTS\n' +
      '- Submudulo 2.4: Vale-transporte, vale-alimentacao, assistencia medica\n\n' +
      '**Modulo 3 — Provisoes para rescisao:**\n' +
      '- Aviso previo indenizado/trabalhado\n' +
      '- Multa do FGTS (40%)\n' +
      '- Incidencia do FGTS sobre aviso previo\n\n' +
      '**Modulo 4 — Custos indiretos, tributos e lucro:**\n' +
      '- Custos indiretos: administracao, supervisao, uniformes, EPI, treinamento\n' +
      '- Tributos: ISS, PIS, COFINS, IRPJ, CSLL\n' +
      '- Lucro: percentual sobre o custo total\n\n' +
      '**Erros frequentes que levam a desclassificacao:**\n' +
      '1. Salario abaixo do piso da convencao coletiva\n' +
      '2. Encargos sociais calculados incorretamente\n' +
      '3. Beneficios da CCT omitidos (cesta basica, seguro de vida)\n' +
      '4. Tributos inconsistentes com o regime tributario declarado\n' +
      '5. Custos indiretos irrealistas (muito baixos)\n\n' +
      '**Dica essencial:** Obtenha a Convencao Coletiva de Trabalho (CCT) vigente da categoria profissional na regiao de execucao do servico. O salario-base e todos os beneficios obrigatorios estao la. Use a CCT correta — usar a de outra regiao ou categoria e causa de inabilitacao.',
    legalBasis: 'Lei 14.133/2021, art. 63; IN SEGES/ME 65/2021',
    relatedTerms: ['proposta', 'bdi', 'licitacao'],
    relatedSectors: ['facilities', 'seguranca'],
    relatedArticles: ['como-calcular-preco-proposta-licitacao'],
    metaDescription:
      'Guia completo para preencher a planilha de custos e formacao de precos em licitacoes: modulos, encargos e erros a evitar.',
  },
  {
    slug: 'lance-minimo-pregao-eletronico',
    title: 'Qual o valor de lance minimo no pregao eletronico?',
    category: 'precos-propostas',
    answer:
      'No pregao eletronico, o lance e a oferta de preco feita pelos licitantes durante a fase de disputa em tempo real. O valor minimo de diferenca entre lances (decremento minimo) e definido pelo pregoeiro no edital e varia conforme o objeto e o valor estimado.\n\n' +
      '**Regras sobre lances na Lei 14.133/2021:**\n\n' +
      '**Modos de disputa (art. 56):**\n\n' +
      '1. **Modo aberto:** Lances publicos e sucessivos em tempo real. E o mais comum no pregao.\n' +
      '   - Intervalo entre lances: definido no edital (ex: R$ 0,01, R$ 1,00, R$ 100,00)\n' +
      '   - Tempo de disputa: aleatorio apos periodo minimo (2 a 30 minutos, conforme o sistema)\n' +
      '   - Lances crescentes (leilao) ou decrescentes (pregao)\n\n' +
      '2. **Modo fechado:** Proposta unica, sem fase de lances. Usado quando nao e adequada a disputa em tempo real.\n\n' +
      '3. **Modo aberto-fechado:** Fase aberta de lances seguida de lance final fechado dos 3 primeiros colocados.\n\n' +
      '**Decremento minimo:**\n\n' +
      'O edital fixa o valor ou percentual minimo de diferenca entre os lances. Exemplos tipicos:\n' +
      '- Bens de baixo valor: R$ 0,01 a R$ 0,50\n' +
      '- Servicos: R$ 1,00 a R$ 50,00\n' +
      '- Obras: R$ 100,00 a R$ 1.000,00\n' +
      '- Percentual: 0,1% a 1% do valor do lance anterior\n\n' +
      '**Regras praticas:**\n' +
      '- O lance deve ser inferior ao seu lance anterior (voce nao pode aumentar)\n' +
      '- O lance deve respeitar o decremento minimo do edital\n' +
      '- Lances iguais ou superiores ao anterior sao rejeitados pelo sistema automaticamente\n' +
      '- Voce pode dar lances a qualquer momento durante a fase aberta\n' +
      '- O lance e irretratavel — uma vez enviado, nao pode ser cancelado\n\n' +
      '**Estrategia de lances:**\n' +
      '- Conheca seu preco minimo viavel ANTES da sessao\n' +
      '- Comece com lances moderados, nao revele seu melhor preco de imediato\n' +
      '- Acompanhe os lances dos concorrentes em tempo real\n' +
      '- Nos segundos finais do tempo aleatorio, esteja preparado para o lance decisivo\n' +
      '- Nunca va abaixo do seu custo — a vitoria a qualquer preco nao e vitoria',
    legalBasis: 'Lei 14.133/2021, art. 56',
    relatedTerms: ['lance', 'pregao-eletronico', 'pregoeiro'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Entenda como funcionam os lances no pregao eletronico: decremento minimo, modos de disputa e estrategias para vencer.',
  },
  {
    slug: 'ata-registro-precos-como-funciona',
    title: 'Como funciona a Ata de Registro de Precos (SRP)?',
    category: 'precos-propostas',
    answer:
      'O Sistema de Registro de Precos (SRP) e um procedimento especial de licitacao em que a administracao registra os precos de fornecedores para futuras aquisicoes, sem compromisso imediato de compra. A Ata de Registro de Precos (ARP) e o documento que formaliza esse registro.\n\n' +
      '**Quando usar o SRP (art. 82, Lei 14.133):**\n' +
      '- Aquisicoes frequentes do mesmo objeto\n' +
      '- Contratacao por mais de um orgao (compra compartilhada)\n' +
      '- Quando nao e possivel definir o quantitativo exato antecipadamente\n' +
      '- Bens com entrega parcelada\n\n' +
      '**Como funciona na pratica:**\n\n' +
      '1. **Licitacao:** O orgao gerenciador realiza pregao ou concorrencia para registrar precos.\n' +
      '2. **Ata de Registro:** Os fornecedores classificados assinam a ARP com precos, quantitativos e condicoes.\n' +
      '3. **Vigencia da ata:** Ate 1 ano, prorrogavel por mais 1 ano (total 2 anos — art. 84).\n' +
      '4. **Emissao de pedidos:** Quando necessitar, o orgao emite ordens de fornecimento contra a ata.\n' +
      '5. **Adesao (carona):** Outros orgaos podem aderir a ata, nas condicoes registradas.\n\n' +
      '**Vantagens para fornecedores:**\n' +
      '- Garantia de preço registrado por ate 2 anos\n' +
      '- Possibilidade de fornecimento para multiplos orgaos (via adesao)\n' +
      '- Fluxo de pedidos recorrente sem nova licitacao\n' +
      '- Volume potencial significativo\n\n' +
      '**Obrigacoes do fornecedor registrado:**\n' +
      '- Manter o preco registrado durante a vigencia\n' +
      '- Atender os pedidos dentro do prazo estipulado\n' +
      '- Manter as condicoes de habilitacao\n' +
      '- O fornecedor NAO e obrigado a fornecer alem do quantitativo registrado\n\n' +
      '**Adesao a ata (carona):**\n' +
      'A Lei 14.133 limitou a adesao: orgaos nao participantes podem aderir ate o limite de 50% dos quantitativos registrados, e cada adesao individual esta limitada a 50% do total (art. 86). O fornecedor pode aceitar ou recusar a adesao.\n\n' +
      '**Dica estrategica:** Participar de registros de precos de orgaos gerenciadores grandes (como ministerios e secretarias estaduais) pode gerar volume significativo de vendas via adesoes.',
    legalBasis: 'Lei 14.133/2021, arts. 82 a 86',
    relatedTerms: ['registro-precos', 'ata-registro-precos', 'pregao-eletronico'],
    relatedSectors: [],
    relatedArticles: ['ata-registro-precos-estrategia-licitacao'],
    metaDescription:
      'Entenda como funciona o Sistema de Registro de Precos (SRP) e a Ata de Registro: vigencia, adesao e estrategias.',
  },
  {
    slug: 'indice-reajuste-contrato-publico',
    title: 'Qual indice usar para reajuste de contrato publico?',
    category: 'precos-propostas',
    answer:
      'O reajuste contratual e a correcao periodica dos precos do contrato para compensar a inflacao e manter o poder de compra do valor pactuado. A Lei 14.133/2021 trata do reajuste no artigo 92, paragrafo 3, e artigos 134-135.\n\n' +
      '**Indices mais utilizados em contratos publicos:**\n\n' +
      '| Indice | Orgao | Uso Principal |\n' +
      '|--------|-------|---------------|\n' +
      '| IPCA | IBGE | Indice oficial de inflacao; contratos de bens e servicos em geral |\n' +
      '| INPC | IBGE | Contratos com componente de mao de obra; base para salario minimo |\n' +
      '| IGP-M | FGV | Contratos de aluguel, fornecimentos de longo prazo |\n' +
      '| SINAPI | Caixa | Obras e servicos de engenharia (custo unitario) |\n' +
      '| SICRO | DNIT | Obras rodoviarias |\n' +
      '| IPC-Fipe | FIPE | Contratos municipais (Sao Paulo) |\n\n' +
      '**Regras de reajuste na Lei 14.133:**\n\n' +
      '1. **Periodicidade:** O reajuste so pode ocorrer apos 12 meses da data do orcamento estimativo da contratacao (nao da assinatura do contrato).\n' +
      '2. **Previsao contratual:** O indice de reajuste deve estar previsto no edital e no contrato.\n' +
      '3. **Automaticidade:** O reajuste e um direito do contratado — nao depende de pedido formal se estiver previsto contratualmente.\n' +
      '4. **Retroatividade:** Se o pedido for tardio, retroage a data-base.\n\n' +
      '**Reajuste versus repactuacao:**\n' +
      '- **Reajuste por indice:** Aplicacao automatica de indice sobre o valor total. Para bens e servicos em geral.\n' +
      '- **Repactuacao:** Revisao detalhada da planilha com base em convencao coletiva. Para servicos com dedicacao de mao de obra.\n\n' +
      '**Qual indice escolher?**\n' +
      '- Para bens e servicos gerais: IPCA (mais conservador) ou IGP-M (mais volatil)\n' +
      '- Para obras: SINAPI ou SICRO (setoriais, mais precisos)\n' +
      '- Para servicos com mao de obra: INPC + repactuacao por CCT\n' +
      '- Para TI: IPCA ou indice setorial de TI (quando disponivel)\n\n' +
      '**Dica:** Ao formular proposta, verifique qual indice o edital preve para reajuste. Indices como o IGP-M tendem a variar mais que o IPCA, o que pode ser vantajoso ou desvantajoso dependendo do cenario economico.',
    legalBasis: 'Lei 14.133/2021, arts. 92 (par. 3), 134, 135',
    relatedTerms: ['reajuste', 'contrato-administrativo', 'reequilibrio-economico-financeiro'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Saiba qual indice usar para reajuste de contrato publico: IPCA, IGP-M, SINAPI e regras da Lei 14.133/2021.',
  },

  /* ================================================================ */
  /*  SETORES ESPECIFICOS (7)                                          */
  /* ================================================================ */
  {
    slug: 'licitacao-ti-requisitos-especificos',
    title: 'Quais requisitos especificos existem em licitacoes de TI?',
    category: 'setores-especificos',
    answer:
      'As licitacoes de Tecnologia da Informacao e Comunicacao (TIC) possuem normas especificas que vao alem da Lei 14.133/2021, incluindo a IN SGD/ME 94/2022 (Instrucao Normativa de Contratacoes de TIC) e o Modelo de Contratacao de Solucoes de TIC.\n\n' +
      '**Normas especificas para TI:**\n\n' +
      '1. **IN SGD/ME 94/2022:** Regulamenta contratacoes de TIC no Executivo Federal.\n' +
      '2. **Modelo de Contratacao (MCTIC):** Fases de planejamento, selecao e gestao.\n' +
      '3. **Lei 14.133, art. 20:** Exigencia de estudo tecnico preliminar (ETP) detalhado.\n\n' +
      '**Etapas obrigatorias no planejamento de TI:**\n\n' +
      '1. **DOD (Documento de Oficializacao de Demanda):** Formalizacao da necessidade.\n' +
      '2. **ETP (Estudo Tecnico Preliminar):** Analise de viabilidade, alternativas de mercado, custos.\n' +
      '3. **Analise de riscos:** Mapeamento de riscos tecnicos, financeiros e operacionais.\n' +
      '4. **Termo de referencia:** Especificacao detalhada da solucao, niveis de servico (SLA), metricas.\n\n' +
      '**Requisitos tecnicos comuns:**\n' +
      '- Certificacoes (ISO 27001, ISO 20000, CMMI, ITIL)\n' +
      '- Equipe tecnica com certificacoes especificas (AWS, Azure, CISSP, PMP)\n' +
      '- Atestados de capacidade tecnica em projetos similares\n' +
      '- Plano de transicao para troca de fornecedor\n' +
      '- Politica de seguranca da informacao\n' +
      '- Plano de backup e recuperacao de desastres\n\n' +
      '**SLA (Service Level Agreement):**\n' +
      'Licitacoes de TI frequentemente incluem metricas de SLA:\n' +
      '- Disponibilidade: 99,5% a 99,99%\n' +
      '- Tempo de resposta a incidentes: 15min a 4h\n' +
      '- Tempo de resolucao: 2h a 48h\n' +
      '- Aplicacao de glosas por descumprimento\n\n' +
      '**Particularidades de contratacao SaaS:**\n' +
      '- Backup e portabilidade de dados sao obrigatorios\n' +
      '- Dados em territorio nacional (LGPD compliance)\n' +
      '- Plano de saida (exit plan) com exportacao de dados\n' +
      '- Propriedade intelectual dos dados e do contratante\n\n' +
      '**Dica para empresas de TI:** Invista em certificacoes (ISO 27001, CMMI) e mantenha equipe certificada. Esses sao os diferenciais mais exigidos em licitacoes federais de TI.',
    legalBasis: 'Lei 14.133/2021, art. 20; IN SGD/ME 94/2022',
    relatedTerms: ['termo-referencia', 'habilitacao', 'licitacao'],
    relatedSectors: ['informatica'],
    relatedArticles: [],
    metaDescription:
      'Conheca os requisitos especificos de licitacoes de TI: IN SGD 94/2022, SLAs, certificacoes e contratacao de SaaS.',
  },
  {
    slug: 'licitacao-saude-anvisa-requisitos',
    title: 'Quais exigencias da ANVISA se aplicam a licitacoes de saude?',
    category: 'setores-especificos',
    answer:
      'Licitacoes de produtos e servicos de saude possuem exigencias regulatorias adicionais da ANVISA (Agencia Nacional de Vigilancia Sanitaria) que devem ser atendidas tanto pelo edital quanto pelos licitantes. Essas exigencias visam garantir a seguranca e eficacia dos produtos utilizados no SUS e em servicos de saude publicos.\n\n' +
      '**Exigencias de registro e autorizacao:**\n\n' +
      '1. **Registro na ANVISA:** Medicamentos, equipamentos medicos, materiais hospitalares e produtos para saude devem ter registro valido na ANVISA (ou notificacao, conforme a classe de risco).\n' +
      '2. **AFE (Autorizacao de Funcionamento):** A empresa deve possuir AFE expedida pela ANVISA para fabricar, importar ou distribuir produtos sujeitos a vigilancia sanitaria.\n' +
      '3. **Licenca sanitaria:** Emitida pela vigilancia sanitaria estadual/municipal do local de fabricacao ou armazenamento.\n' +
      '4. **CBPF (Certificado de Boas Praticas de Fabricacao):** Obrigatorio para fabricantes de medicamentos, produtos biologicos e alguns dispositivos medicos.\n\n' +
      '**Classificacao de risco de dispositivos medicos:**\n' +
      '- Classe I (baixo risco): notificacao (ex: luvas, seringas)\n' +
      '- Classe II (medio risco): registro (ex: equipamentos de monitoramento)\n' +
      '- Classe III e IV (alto risco): registro com analise mais rigorosa (ex: implantes, equipamentos de suporte a vida)\n\n' +
      '**Exigencias em editais de saude:**\n' +
      '- Registro ANVISA vigente (numero e validade)\n' +
      '- AFE do fabricante e do distribuidor\n' +
      '- Laudo de analise ou certificado de qualidade\n' +
      '- Rastreabilidade completa do produto\n' +
      '- Prazo de validade minimo (geralmente 75% da validade total na entrega)\n' +
      '- Amostras para avaliacao tecnica\n\n' +
      '**Compras emergenciais de saude:**\n' +
      'Em situacoes de emergencia sanitaria, a ANVISA pode conceder registro temporario ou autorizacao de uso emergencial (como ocorreu com vacinas da COVID-19), flexibilizando requisitos sem comprometer a seguranca.\n\n' +
      '**Dica para fornecedores de saude:** Mantenha todos os registros ANVISA atualizados com antecedencia — o processo de renovacao pode levar meses. Verifique se o distribuidor autorizado tambem possui AFE e licenca sanitaria vigentes.',
    legalBasis:
      'Lei 14.133/2021; Lei 6.360/1976; RDC ANVISA 185/2001',
    relatedTerms: ['habilitacao', 'licitacao', 'edital'],
    relatedSectors: ['saude', 'equipamentos-medicos'],
    relatedArticles: [],
    metaDescription:
      'Saiba quais exigencias da ANVISA se aplicam a licitacoes de saude: registro, AFE, CBPF e requisitos por classe de risco.',
  },
  {
    slug: 'licitacao-obras-engenharia-qualificacao',
    title: 'Qual qualificacao tecnica e exigida em obras de engenharia?',
    category: 'setores-especificos',
    answer:
      'Licitacoes de obras e servicos de engenharia possuem os requisitos mais rigorosos de qualificacao tecnica, dada a complexidade, os riscos envolvidos e os valores tipicamente elevados. A Lei 14.133/2021 detalha essas exigencias nos artigos 67 e 68.\n\n' +
      '**Qualificacao tecnico-profissional (art. 67, I):**\n\n' +
      '1. **Registro no CREA/CAU:** A empresa deve ter registro no Conselho Regional de Engenharia e Agronomia ou no Conselho de Arquitetura e Urbanismo.\n' +
      '2. **Responsavel tecnico:** Indicacao de profissional(is) com:\n' +
      '   - Registro ativo no CREA/CAU\n' +
      '   - CAT (Certidao de Acervo Tecnico) comprovando experiencia em parcelas de maior relevancia tecnica\n' +
      '   - Vinculo com a empresa (contrato de trabalho, contrato social ou contrato de prestacao de servicos)\n\n' +
      '**Qualificacao tecnico-operacional (art. 67, II):**\n\n' +
      '1. **Atestados da empresa:** Comprovacao de que a empresa executou obras/servicos de natureza e complexidade similares ao objeto.\n' +
      '2. **Parcelas de maior relevancia:** O edital deve definir quais parcelas sao de maior relevancia tecnica e valor significativo.\n' +
      '3. **Quantitativos:** Nao pode exigir quantidades identicas ao objeto — a jurisprudencia do TCU admite ate 50% como parametro.\n\n' +
      '**Documentos especificos de engenharia:**\n' +
      '- ART/RRT (Anotacao de Responsabilidade Tecnica / Registro de Responsabilidade Tecnica)\n' +
      '- CAT (Certidao de Acervo Tecnico)\n' +
      '- Registro no CREA/CAU (empresa e profissionais)\n' +
      '- Atestados com acervo registrado\n' +
      '- Declaracao de disponibilidade de equipamentos\n\n' +
      '**Exigencias complementares comuns:**\n' +
      '- ISO 9001 (sistema de gestao de qualidade)\n' +
      '- PBQP-H (Programa Brasileiro de Qualidade e Produtividade do Habitat) — nivel A\n' +
      '- Certificacao ambiental (ISO 14001)\n' +
      '- Programa de seguranca (PCMSO, PPRA)\n\n' +
      '**Limites das exigencias (jurisprudencia TCU):**\n' +
      '- Vedado exigir numero minimo de obras executadas (Sumula 263)\n' +
      '- Vedado exigir atestados de obra identica (deve aceitar similar)\n' +
      '- Vedado exigir tempo minimo de experiencia da empresa\n' +
      '- Permitido exigir experiencia em parcelas de maior relevancia com quantitativos razoaveis',
    legalBasis: 'Lei 14.133/2021, arts. 67, 68; Sumula TCU 263',
    relatedTerms: ['habilitacao', 'parecer-tecnico', 'licitacao'],
    relatedSectors: ['engenharia', 'construcao'],
    relatedArticles: ['checklist-habilitacao-licitacao-2026'],
    metaDescription:
      'Veja a qualificacao tecnica exigida em obras de engenharia: CREA/CAU, CAT, atestados e limites do TCU.',
  },
  {
    slug: 'licitacao-alimentos-merenda-regras',
    title:
      'Quais regras especiais existem para licitacoes de merenda escolar?',
    category: 'setores-especificos',
    answer:
      'As licitacoes de alimentacao escolar (merenda) possuem legislacao especifica que vai alem da Lei 14.133/2021. O Programa Nacional de Alimentacao Escolar (PNAE), gerido pelo FNDE, estabelece regras proprias para aquisicao de alimentos para escolas publicas.\n\n' +
      '**Legislacao especifica:**\n' +
      '- Lei 11.947/2009 (PNAE)\n' +
      '- Resolucao FNDE 06/2020 (regulamentacao do PNAE)\n' +
      '- Lei 14.133/2021 (licitacoes em geral)\n\n' +
      '**Regra dos 30% para agricultura familiar (art. 14, Lei 11.947):**\n\n' +
      'No minimo 30% dos recursos do FNDE destinados a merenda escolar devem ser utilizados na compra de alimentos diretamente da agricultura familiar e do empreendedor familiar rural. Essa compra utiliza a **Chamada Publica** (dispensa de licitacao), nao pregao.\n\n' +
      '**Requisitos nutricionais:**\n' +
      '- Cardapio elaborado por nutricionista (RT do PNAE)\n' +
      '- Respeito a habitos alimentares regionais\n' +
      '- Proibicao de bebidas com baixo teor nutricional\n' +
      '- Oferta de frutas e hortalicas (minimo 3x por semana)\n' +
      '- Limite de acucar, sodio e gordura saturada\n\n' +
      '**Exigencias sanitarias:**\n' +
      '- Alvara sanitario vigente do fornecedor\n' +
      '- Licenca de funcionamento da vigilancia sanitaria\n' +
      '- Controle de qualidade com laudos laboratoriais\n' +
      '- Rastreabilidade dos produtos (lote, validade, procedencia)\n' +
      '- Rotulagem conforme normas da ANVISA\n' +
      '- Transporte adequado (cadeia fria para pereciveis)\n\n' +
      '**Particularidades das licitacoes de alimentos:**\n\n' +
      '1. **Amostras obrigatorias:** O edital pode exigir amostras para degustacao e analise.\n' +
      '2. **Marca:** Permitido indicar marcas como referencia de qualidade.\n' +
      '3. **Entrega parcelada:** Obrigatoria para pereciveis (semanal ou quinzenal).\n' +
      '4. **SRP (Registro de Precos):** Muito utilizado pela variacao sazonal de precos.\n' +
      '5. **Organicos:** Preferencia para alimentos organicos e agroecologicos.\n\n' +
      '**Dica para fornecedores:** O mercado de merenda escolar e enorme e recorrente. Se voce atua com alimentos, mantenha alvara sanitario atualizado, invista em logistica de entrega e considere se cadastrar como fornecedor da agricultura familiar (DAP/CAF) para acessar os 30% reservados.',
    legalBasis:
      'Lei 11.947/2009, art. 14; Resolucao FNDE 06/2020; Lei 14.133/2021',
    relatedTerms: ['licitacao', 'dispensa', 'registro-precos'],
    relatedSectors: ['alimentos', 'educacao'],
    relatedArticles: [],
    metaDescription:
      'Conheca as regras especiais de licitacao de merenda escolar: 30% agricultura familiar, PNAE, requisitos sanitarios.',
  },
  {
    slug: 'licitacao-software-saas-contratacao',
    title: 'Como funciona a contratacao de software SaaS pelo governo?',
    category: 'setores-especificos',
    answer:
      'A contratacao de software como servico (SaaS — Software as a Service) pelo governo brasileiro segue regras especificas da IN SGD/ME 94/2022 e da Lei 14.133/2021, alem de orientacoes do Tribunal de Contas da Uniao.\n\n' +
      '**Enquadramento legal:**\n' +
      'SaaS e classificado como servico (nao licenciamento de software), o que permite contratacao por pregao eletronico na modalidade de menor preco por item ou global. A assinatura mensal/anual e tratada como servico continuado.\n\n' +
      '**Requisitos obrigatorios em contratacao SaaS:**\n\n' +
      '1. **Seguranca da informacao:**\n' +
      '   - Dados armazenados em territorio nacional (LGPD, art. 33)\n' +
      '   - Criptografia em transito e em repouso\n' +
      '   - Autenticacao multifator\n' +
      '   - Logs de auditoria acessiveis\n' +
      '   - Conformidade com a Politica de Seguranca do orgao\n\n' +
      '2. **Portabilidade e interoperabilidade:**\n' +
      '   - Exportacao de dados em formato aberto (CSV, JSON, XML)\n' +
      '   - API documentada para integracao\n' +
      '   - Plano de transicao para troca de fornecedor (exit plan)\n' +
      '   - Prazo de 90 dias apos encerramento para exportacao\n\n' +
      '3. **Niveis de servico (SLA):**\n' +
      '   - Disponibilidade minima: 99,5% a 99,9%\n' +
      '   - Tempo de resposta a incidentes\n' +
      '   - RPO e RTO definidos (backup e recuperacao)\n' +
      '   - Penalidades (glosas) por descumprimento\n\n' +
      '4. **LGPD compliance:**\n' +
      '   - Contrato de processamento de dados (DPA)\n' +
      '   - Encarregado de dados (DPO) indicado\n' +
      '   - Registro de operacoes de tratamento\n\n' +
      '**Modelo de precificacao aceito:**\n' +
      '- Por usuario/mes (mais comum)\n' +
      '- Por volume de transacoes\n' +
      '- Por modulo funcional\n' +
      '- Tarifa fixa mensal\n\n' +
      '**Vigencia contratual:**\n' +
      'Contratos de SaaS sao classificados como servicos continuados — vigencia de ate 5 anos, prorrogavel a 10 anos (art. 106).\n\n' +
      '**Dica para empresas de SaaS:** Prepare uma documentacao tecnica robusta (arquitetura, seguranca, SLA, politica de backup, LGPD) que possa ser anexada a qualquer proposta. Muitos editais exigem esses documentos na habilitacao tecnica.',
    legalBasis: 'Lei 14.133/2021, art. 106; IN SGD/ME 94/2022; LGPD',
    relatedTerms: ['termo-referencia', 'licitacao', 'pregao-eletronico'],
    relatedSectors: ['informatica'],
    relatedArticles: [],
    metaDescription:
      'Entenda como funciona a contratacao de SaaS pelo governo: LGPD, SLA, portabilidade de dados e requisitos da IN SGD 94.',
  },
  {
    slug: 'licitacao-vigilancia-requisitos-pf',
    title:
      'Quais requisitos da Policia Federal se aplicam a vigilancia?',
    category: 'setores-especificos',
    answer:
      'A prestacao de servicos de vigilancia patrimonial e seguranca privada para orgaos publicos e regulamentada pela Lei 7.102/1983, pelo Decreto 89.056/1983 e por portarias da Policia Federal. Esses requisitos sao adicionais aos da Lei 14.133/2021.\n\n' +
      '**Autorizacao da Policia Federal:**\n\n' +
      '1. **Autorizacao de funcionamento:** A empresa deve possuir autorizacao de funcionamento expedida pela Delegacia de Controle de Seguranca Privada (DELESP) ou Comissao de Vistoria da PF, valida para o estado de execucao do servico.\n' +
      '2. **Revisao de autorizacao:** A autorizacao deve ser revisada anualmente.\n' +
      '3. **Certificado de Seguranca:** Documento que atesta a regularidade da empresa junto a PF.\n\n' +
      '**Requisitos para a empresa:**\n' +
      '- Capital social integralizado minimo (definido pela PF conforme a regiao)\n' +
      '- Instalacoes fisicas adequadas (escritorio, deposito de armamento)\n' +
      '- Seguro de vida em grupo para vigilantes\n' +
      '- Contrato de seguro de responsabilidade civil\n' +
      '- Plano de seguranca aprovado\n\n' +
      '**Requisitos para os vigilantes:**\n' +
      '- Curso de formacao de vigilante (reciclagem a cada 2 anos)\n' +
      '- Certificado de aptidao psicologica\n' +
      '- Certidao negativa de antecedentes criminais\n' +
      '- Carteira Nacional de Vigilante (CNV) valida\n' +
      '- Aptidao fisica comprovada\n\n' +
      '**Exigencias em editais de vigilancia:**\n' +
      '- Autorizacao da PF para vigilancia patrimonial (obrigatoria)\n' +
      '- Certificado de Seguranca vigente\n' +
      '- Atestados de capacidade tecnica em postos de vigilancia\n' +
      '- Planilha de custos conforme CCT da categoria\n' +
      '- Uniforme e equipamentos conforme Portaria DG/PF\n' +
      '- Se armada: certificado de registro de armas, apolice de seguro, plano de transporte\n\n' +
      '**Vigilancia armada versus desarmada:**\n' +
      '- Armada: requisitos adicionais de controle de armamento, cofre, plano de tiro\n' +
      '- Desarmada: requisitos simplificados, sem controle de armas\n' +
      '- Eletronica: CFTV, alarmes, monitoramento 24h — requisitos tecnologicos adicionais\n\n' +
      '**Dica:** A regularizacao junto a PF pode levar meses. Se voce esta iniciando no segmento de seguranca privada, comece o processo de autorizacao com bastante antecedencia.',
    legalBasis: 'Lei 7.102/1983; Decreto 89.056/1983; Portarias DG/PF',
    relatedTerms: ['habilitacao', 'licitacao', 'edital'],
    relatedSectors: ['seguranca'],
    relatedArticles: [],
    metaDescription:
      'Conheca os requisitos da Policia Federal para licitacoes de vigilancia: autorizacao, CNV, seguro e controle de armamento.',
  },
  {
    slug: 'licitacao-facilities-planilha-custos',
    title:
      'Como montar a planilha de custos em licitacoes de facilities?',
    category: 'setores-especificos',
    answer:
      'Licitacoes de facilities (gestao de facilidades) abrangem servicos como limpeza, manutencao predial, portaria, jardinagem, controle de pragas e servicos administrativos. Por envolverem dedicacao exclusiva de mao de obra, exigem planilha de custos detalhada conforme a IN SEGES/ME 65/2021.\n\n' +
      '**Estrutura da planilha de custos para facilities:**\n\n' +
      '**1. Remuneracao (baseada na CCT):**\n' +
      '- Salario-base da categoria (zelador, porteiro, auxiliar de limpeza)\n' +
      '- Adicional de insalubridade (limpeza: 20% ou 40% do salario minimo)\n' +
      '- Adicional noturno (portaria 24h: 20% para 22h-05h)\n' +
      '- Hora extra habitual (se prevista na CCT)\n\n' +
      '**2. Encargos sociais e trabalhistas:**\n' +
      '- Grupo A: INSS (20%), SAT/RAT (1-3%), Terceiros (5,8%), FGTS (8%) = ~37%\n' +
      '- Grupo B: 13o salario (8,33%), ferias + 1/3 (11,11%) = ~20%\n' +
      '- Grupo C: Aviso previo, multa FGTS = ~5-7%\n' +
      '- Grupo D: Incidencia cumulativa dos grupos\n' +
      '- **Total encargos: 65% a 85%** do salario (varia por CCT e regime)\n\n' +
      '**3. Beneficios (conforme CCT):**\n' +
      '- Vale-transporte (6% do salario descontado do empregado)\n' +
      '- Vale-alimentacao/refeicao (valor da CCT)\n' +
      '- Assistencia medica (se previsto na CCT)\n' +
      '- Seguro de vida (obrigatorio pela CCT em muitas categorias)\n' +
      '- Cesta basica (se previsto)\n\n' +
      '**4. Insumos e custos operacionais:**\n' +
      '- Uniformes e EPI (quantidade anual por funcionario)\n' +
      '- Materiais de limpeza (litros/unidades por m2)\n' +
      '- Equipamentos (aspiradores, lavadoras, etc.)\n' +
      '- Treinamento e reciclagem\n\n' +
      '**5. Custos indiretos, lucro e tributos:**\n' +
      '- Administracao/supervisao: 3% a 5%\n' +
      '- Lucro: 5% a 10%\n' +
      '- Tributos: ISS (2-5%), PIS (0,65-1,65%), COFINS (3-7,6%), IRPJ, CSLL\n\n' +
      '**Erros fatais em planilhas de facilities:**\n' +
      '- Usar CCT da categoria errada ou de outro estado\n' +
      '- Esquecer adicional de insalubridade para limpeza\n' +
      '- Nao considerar intrajornada para jornada 12x36\n' +
      '- Subestimar custo de substituicao (ferias, faltas, licencas)\n' +
      '- Nao prever custo de supervisao/encarregado\n\n' +
      '**Dica:** A CCT da categoria na regiao de execucao e a BIBLIA da sua planilha. Consulte o sindicato patronal e laboral para obter a convencao vigente com todas as clausulas economicas.',
    legalBasis: 'Lei 14.133/2021, art. 63; IN SEGES/ME 65/2021',
    relatedTerms: ['proposta', 'bdi', 'licitacao'],
    relatedSectors: ['facilities', 'servicos-gerais'],
    relatedArticles: ['como-calcular-preco-proposta-licitacao'],
    metaDescription:
      'Guia completo para montar planilha de custos em licitacoes de facilities: remuneracao, encargos, CCT e erros a evitar.',
  },

  /* ================================================================ */
  /*  TECNOLOGIA E SISTEMAS (9)                                        */
  /* ================================================================ */
  {
    slug: 'pncp-o-que-e-como-usar',
    title: 'O que e o PNCP e como consultar licitacoes?',
    category: 'tecnologia-sistemas',
    answer:
      'O PNCP (Portal Nacional de Contratacoes Publicas) e a plataforma digital oficial do Governo Federal criada pela Lei 14.133/2021 para centralizar a divulgacao de todas as licitacoes, contratacoes diretas, atas de registro de precos e contratos publicos do pais — nas esferas federal, estadual e municipal.\n\n' +
      '**O que o PNCP oferece:**\n' +
      '- Publicacao obrigatoria de editais de todas as esferas\n' +
      '- Acesso a atas, contratos e aditivos\n' +
      '- Consulta de precos praticados em contratacoes\n' +
      '- Dados abertos para pesquisa e analise\n' +
      '- API publica para integracao com sistemas\n\n' +
      '**Como consultar licitacoes no PNCP:**\n\n' +
      '1. **Acesse pncp.gov.br** — o portal e publico, nao exige login para consulta.\n' +
      '2. **Use a busca avancada** com filtros:\n' +
      '   - Palavra-chave no objeto da contratacao\n' +
      '   - UF e municipio do orgao contratante\n' +
      '   - Modalidade (pregao, concorrencia, dispensa)\n' +
      '   - Esfera (federal, estadual, municipal)\n' +
      '   - Data de publicacao\n' +
      '   - Faixa de valor estimado\n' +
      '3. **Analise os resultados:** Cada licitacao exibe o resumo do objeto, orgao contratante, valor estimado, data de abertura e situacao.\n' +
      '4. **Acesse o edital completo:** Clique na licitacao para ver o edital, anexos e documentos.\n\n' +
      '**API do PNCP:**\n' +
      'O PNCP disponibiliza uma API REST publica (pncp.gov.br/api) para consulta automatizada de contratacoes. Isso permite que ferramentas como o SmartLic agreguem e classifiquem licitacoes automaticamente, facilitando a descoberta de oportunidades por setor e regiao.\n\n' +
      '**Limitacoes atuais do PNCP:**\n' +
      '- Nem todos os municipios publicam no PNCP ainda (adesao progressiva)\n' +
      '- A busca textual e basica (sem sinonimos ou classificacao inteligente)\n' +
      '- Dados historicos anteriores a 2023 sao incompletos\n' +
      '- O sistema de filtros pode ser lento em horarios de pico\n\n' +
      '**Dica:** Para maximizar a cobertura, combine o PNCP com plataformas complementares como o Portal de Compras Publicas, BLL, Licitacoes-e e portais estaduais. Ou use o SmartLic, que consolida todas essas fontes em uma busca unica com classificacao por setor.',
    legalBasis: 'Lei 14.133/2021, arts. 174, 175, 176',
    relatedTerms: ['pncp', 'licitacao', 'edital'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Saiba o que e o PNCP, como consultar licitacoes, usar filtros de busca e acessar editais de todas as esferas do governo.',
  },
  {
    slug: 'comprasnet-como-participar',
    title: 'Como participar de licitacoes no ComprasNet/ComprasGov?',
    category: 'tecnologia-sistemas',
    answer:
      'O ComprasGov (antigo ComprasNet) e o sistema eletronico de compras do Governo Federal, operado pelo Ministerio da Gestao e da Inovacao. E a principal plataforma para participacao em licitacoes federais — pregoes, concorrencias e dispensas eletronicas.\n\n' +
      '**Como se cadastrar e participar:**\n\n' +
      '**1. Cadastro no gov.br:**\n' +
      '- Crie uma conta gov.br (https://acesso.gov.br) com nivel prata ou ouro\n' +
      '- Vincule o CPF do representante legal ao CNPJ da empresa\n\n' +
      '**2. Cadastro no SICAF:**\n' +
      '- Acesse comprasgov.br e selecione "Fornecedor"\n' +
      '- Complete o cadastro SICAF com documentos de habilitacao\n' +
      '- Obtenha credenciamento nos niveis necessarios (I a VI)\n\n' +
      '**3. Certificado digital:**\n' +
      '- Adquira certificado digital ICP-Brasil tipo A1 (arquivo) ou A3 (token/cartao)\n' +
      '- Associe o certificado ao CNPJ da empresa no sistema\n\n' +
      '**4. Participando de uma licitacao:**\n\n' +
      'a) **Busca de editais:** Use o modulo "Editais" para encontrar licitacoes por palavra-chave, UASG, data ou tipo.\n' +
      'b) **Leitura do edital:** Baixe e leia o edital completo, incluindo termo de referencia e planilhas.\n' +
      'c) **Cadastro de proposta:** Na data indicada, acesse o modulo do certame e cadastre sua proposta com precos e declaracoes.\n' +
      'd) **Sessao publica:** No dia e horario marcados, acompanhe a sessao eletronica para a fase de lances.\n' +
      'e) **Lances:** Oferte lances decrescentes em tempo real durante a fase de disputa.\n' +
      'f) **Habilitacao:** Se classificado em primeiro lugar, o pregoeiro verifica seus documentos no SICAF.\n' +
      'g) **Adjudicacao:** Sendo habilitado e apos prazo recursal, o objeto e adjudicado.\n\n' +
      '**Dicas importantes:**\n' +
      '- Teste seu certificado digital ANTES da sessao — problemas tecnicos no dia podem impedir a participacao.\n' +
      '- Fique atento ao chat do sistema — o pregoeiro pode solicitar documentos ou esclarecimentos durante a sessao com prazos curtos (2-4 horas).\n' +
      '- Mantenha o SICAF atualizado — certidoes vencidas impedem a habilitacao.\n' +
      '- Acompanhe o resultado pelo sistema — recursos e convocacoes sao notificados eletronicamente.',
    legalBasis: 'Lei 14.133/2021; Decreto 10.024/2019',
    relatedTerms: ['pregao-eletronico', 'sicaf', 'pncp'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Guia completo para participar de licitacoes no ComprasGov: cadastro, SICAF, certificado digital e passo a passo.',
  },
  {
    slug: 'certificado-digital-licitacao',
    title: 'Qual certificado digital e necessario para licitacoes?',
    category: 'tecnologia-sistemas',
    answer:
      'O certificado digital e indispensavel para participar de licitacoes eletronicas no Brasil. Ele autentica a identidade do licitante no sistema e garante a validade juridica das propostas, lances e documentos enviados.\n\n' +
      '**Tipo de certificado necessario:**\n\n' +
      'Para licitacoes, voce precisa de um certificado digital e-CNPJ (pessoa juridica) ou e-CPF (representante legal) da cadeia ICP-Brasil (Infraestrutura de Chaves Publicas Brasileira).\n\n' +
      '**Formatos disponiveis:**\n\n' +
      '| Tipo | Armazenamento | Validade | Preco Medio |\n' +
      '|------|--------------|----------|-------------|\n' +
      '| A1 | Arquivo no computador | 1 ano | R$ 150-300 |\n' +
      '| A3 (token USB) | Token criptografico | 1-3 anos | R$ 200-500 |\n' +
      '| A3 (cartao) | Smart card + leitora | 1-3 anos | R$ 250-550 |\n' +
      '| A3 (nuvem) | Servidor remoto | 1-5 anos | R$ 200-450 |\n\n' +
      '**Recomendacao para licitantes:**\n' +
      '- **A1:** Mais pratico para uso diario, pode ser instalado em multiplos computadores (com copia segura). Ideal para empresas que participam de muitas licitacoes.\n' +
      '- **A3 token/cartao:** Mais seguro (chave privada nao sai do dispositivo), mas exige o token/cartao fisicamente presente. Ideal para quem prioriza seguranca.\n' +
      '- **A3 nuvem:** Combina seguranca e praticidade — acesso de qualquer dispositivo com autenticacao.\n\n' +
      '**Autoridades Certificadoras (AC) reconhecidas:**\n' +
      '- Serasa Experian, Certisign, Valid Certificadora, Safeweb, AC Soluti, entre outras credenciadas pelo ITI.\n\n' +
      '**Como obter:**\n' +
      '1. Escolha uma AC credenciada pelo ITI (iti.gov.br)\n' +
      '2. Solicite o certificado online\n' +
      '3. Agende validacao presencial (ou por videoconferencia, para A1/A3 nuvem)\n' +
      '4. Apresente documentos da empresa e do representante legal\n' +
      '5. Receba o certificado (download para A1, entrega do token/cartao para A3)\n\n' +
      '**Plataformas que exigem certificado digital:**\n' +
      '- ComprasGov (obrigatorio)\n' +
      '- BEC-SP (obrigatorio)\n' +
      '- Licitacoes-e (obrigatorio)\n' +
      '- Portal de Compras Publicas (aceita login sem certificado para consulta)\n\n' +
      '**Dica:** Tenha sempre um certificado reserva (ou backup do A1 em local seguro). Se seu certificado expirar ou apresentar problemas no dia de uma sessao, voce perde a oportunidade.',
    legalBasis: 'MP 2.200-2/2001 (ICP-Brasil); Lei 14.133/2021',
    relatedTerms: ['pregao-eletronico', 'sicaf', 'licitacao'],
    relatedSectors: [],
    relatedArticles: ['pregao-eletronico-guia-passo-a-passo'],
    metaDescription:
      'Saiba qual certificado digital usar em licitacoes: tipos A1 e A3, onde comprar, precos e como instalar.',
  },
  {
    slug: 'assinatura-eletronica-contratos-publicos',
    title:
      'Como funciona a assinatura eletronica em contratos publicos?',
    category: 'tecnologia-sistemas',
    answer:
      'A assinatura eletronica em contratos publicos foi ampliada pela Lei 14.063/2020 e reafirmada pela Lei 14.133/2021, que permite a formalizacao de contratos administrativos por meio eletronico, eliminando a necessidade de documentos fisicos.\n\n' +
      '**Niveis de assinatura eletronica (Lei 14.063/2020):**\n\n' +
      '1. **Assinatura simples:** Identifica o signatario de forma basica (ex: login/senha em sistema). Aceita para atos de menor complexidade.\n\n' +
      '2. **Assinatura avancada:** Utiliza certificados nao emitidos pela ICP-Brasil, mas com mecanismos de autenticacao robustos (ex: gov.br nivel prata/ouro). Aceita para:\n' +
      '   - Interacoes com entes publicos\n' +
      '   - Atos de gestao interna\n' +
      '   - Documentos entre orgaos publicos\n\n' +
      '3. **Assinatura qualificada:** Utiliza certificado ICP-Brasil. Obrigatoria para:\n' +
      '   - Contratos administrativos\n' +
      '   - Atos de transferencia de bens imoveis\n' +
      '   - Documentos em que a lei exija reconhecimento de firma\n\n' +
      '**Sistemas utilizados para assinatura:**\n\n' +
      '| Sistema | Ambito | Tipo |\n' +
      '|---------|--------|------|\n' +
      '| SEI (Sistema Eletronico de Informacoes) | Federal/Estadual/Municipal | Avancada/Qualificada |\n' +
      '| gov.br (assinatura digital) | Federal | Avancada |\n' +
      '| Portal de Compras (contrato digital) | Plataformas de compras | Qualificada |\n' +
      '| DocuSign / Adobe Sign | Aceitos se ICP-Brasil | Qualificada |\n\n' +
      '**Fluxo tipico de assinatura eletronica de contrato:**\n\n' +
      '1. O orgao elabora a minuta do contrato no sistema (SEI, e-Licitacao, etc.)\n' +
      '2. O contratado recebe notificacao eletronica para assinar\n' +
      '3. O contratado acessa o sistema com certificado digital ou conta gov.br\n' +
      '4. Revisa o documento e aplica a assinatura eletronica\n' +
      '5. O ordenador de despesa do orgao contrassina\n' +
      '6. O contrato e publicado automaticamente no PNCP\n\n' +
      '**Validade juridica:**\n' +
      'Documentos assinados eletronicamente com certificado ICP-Brasil tem a mesma validade juridica de documentos assinados em cartorio (MP 2.200-2/2001). A integridade e autenticidade sao verificaveis a qualquer momento.\n\n' +
      '**Dica pratica:** Configure a assinatura eletronica no seu certificado digital antes da primeira contratacao. Familiarize-se com o sistema SEI ou a plataforma do orgao — a assinatura pode ter prazo curtissimo (24-48h) apos notificacao.',
    legalBasis:
      'Lei 14.063/2020; Lei 14.133/2021, art. 91; MP 2.200-2/2001',
    relatedTerms: ['contrato-administrativo', 'licitacao', 'pncp'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Entenda como funciona a assinatura eletronica em contratos publicos: niveis, sistemas, validade juridica e passo a passo.',
  },
  {
    slug: 'governo-digital-impacto-licitacoes',
    title: 'Como a estrategia de Governo Digital impacta licitacoes?',
    category: 'tecnologia-sistemas',
    answer:
      'A Estrategia Nacional de Governo Digital (EGD), instituida pelo Decreto 10.332/2020 e atualizada periodicamente, esta transformando profundamente o processo de compras publicas no Brasil. O objetivo e tornar as contratacoes mais transparentes, eficientes e acessiveis por meio da tecnologia.\n\n' +
      '**Principais impactos nas licitacoes:**\n\n' +
      '**1. Digitalizacao completa dos processos:**\n' +
      '- Todos os atos (publicacao, proposta, lance, habilitacao, recurso, contrato) realizados eletronicamente\n' +
      '- Eliminacao de documentos fisicos (art. 12, Lei 14.133)\n' +
      '- Assinatura eletronica em todos os documentos\n\n' +
      '**2. PNCP como plataforma central:**\n' +
      '- Centralizacao de todas as licitacoes do pais em um unico portal\n' +
      '- Dados abertos para consulta publica e analise\n' +
      '- Integracao com sistemas estaduais e municipais\n\n' +
      '**3. Identidade digital unificada (gov.br):**\n' +
      '- Login unico para todos os sistemas de compras publicas\n' +
      '- Autenticacao por biometria e reconhecimento facial\n' +
      '- Nivel prata/ouro para operacoes mais complexas\n\n' +
      '**4. Interoperabilidade de dados:**\n' +
      '- Validacao automatica de certidoes (CND, CRF, CNDT)\n' +
      '- Consulta em tempo real a bases governamentais\n' +
      '- Reducao de documentos exigidos na habilitacao\n\n' +
      '**5. Inteligencia de dados:**\n' +
      '- Painel de Precos com historico de contratacoes\n' +
      '- Analise de precos praticados em compras similares\n' +
      '- Deteccao de anomalias e irregularidades via IA\n\n' +
      '**Impacto para fornecedores:**\n\n' +
      '- **Maior acessibilidade:** Empresas de qualquer regiao participam de licitacoes em todo o pais sem deslocamento.\n' +
      '- **Transparencia ampliada:** Decisoes, atas e contratos acessiveis publicamente.\n' +
      '- **Agilidade:** Processos mais rapidos com menos burocracia documental.\n' +
      '- **Dados para inteligencia:** Acesso a dados historicos para analise de mercado e precificacao.\n\n' +
      '**Desafios da transicao digital:**\n' +
      '- Municipios pequenos com infraestrutura tecnologica limitada\n' +
      '- Necessidade de capacitacao de servidores e fornecedores\n' +
      '- Integracao entre multiplos sistemas (federal, estadual, municipal)\n' +
      '- Seguranca cibernetica e protecao de dados\n\n' +
      '**Para fornecedores, a mensagem e clara:** investir em capacitacao digital nao e opcional — e uma exigencia do mercado de compras publicas.',
    legalBasis: 'Decreto 10.332/2020; Lei 14.133/2021, art. 12',
    relatedTerms: ['pncp', 'licitacao', 'sicaf'],
    relatedSectors: ['informatica'],
    relatedArticles: [],
    metaDescription:
      'Veja como a Estrategia de Governo Digital transforma licitacoes: PNCP, login unico, dados abertos e processos 100% digitais.',
  },
  {
    slug: 'bec-sp-bolsa-eletronica-compras',
    title: 'O que e a BEC/SP Bolsa Eletronica de Compras?',
    category: 'tecnologia-sistemas',
    answer:
      'A BEC/SP (Bolsa Eletronica de Compras do Estado de Sao Paulo) e o sistema eletronico de compras utilizado pelo Governo do Estado de Sao Paulo para realizar pregoes eletronicos, dispensas eletronicas e cotacoes eletronicas. E um dos maiores portais de compras publicas do pais em volume de transacoes.\n\n' +
      '**O que a BEC/SP oferece:**\n' +
      '- Pregoes eletronicos estaduais\n' +
      '- Oferta de compra (dispensa eletronica)\n' +
      '- Cotacao eletronica\n' +
      '- Catalogo de materiais e servicos (Banco BEC)\n' +
      '- Atas de registro de precos estaduais\n\n' +
      '**Como participar:**\n\n' +
      '1. **Cadastro no CAUFESP:** O Cadastro Unificado de Fornecedores do Estado de Sao Paulo e pre-requisito para participar. Acesse www.bec.sp.gov.br e selecione "Cadastro de Fornecedores".\n' +
      '2. **Documentos necessarios:** CNPJ, contrato social, procuracao (se aplicavel), certidoes de regularidade.\n' +
      '3. **Certificado digital:** Obrigatorio para participar de pregoes (ICP-Brasil).\n' +
      '4. **Senha BEC:** Apos o cadastro CAUFESP, solicite senha de acesso ao sistema de pregoes.\n\n' +
      '**Particularidades da BEC/SP:**\n\n' +
      '- **Catalogo de materiais:** A BEC mantem um catalogo padronizado de itens (codigos BEC) que facilita a cotacao e comparacao de precos.\n' +
      '- **Oferta de compra:** Sistema de dispensa eletronica em que o fornecedor cadastrado oferece preco para demandas do estado — funciona como "balcao virtual".\n' +
      '- **Volume expressivo:** Sao Paulo e o maior comprador publico estadual do Brasil, com milhares de unidades gestoras (secretarias, autarquias, prefeituras conveniadas).\n' +
      '- **Convenio com municipios:** Municipios paulistas podem utilizar a BEC mediante convenio, ampliando o alcance.\n\n' +
      '**Diferenca entre BEC/SP e ComprasGov:**\n\n' +
      '| Aspecto | BEC/SP | ComprasGov |\n' +
      '|---------|--------|------------|\n' +
      '| Ambito | Estado de SP + municipios conveniados | Federal |\n' +
      '| Cadastro | CAUFESP | SICAF |\n' +
      '| Catalogo | Banco BEC (codigos proprios) | CATMAT/CATSER |\n' +
      '| Pregao | Sistema proprio | ComprasGov |\n\n' +
      '**Dica para fornecedores:** Se voce atua em Sao Paulo, o cadastro na BEC e praticamente obrigatorio. O estado de SP realiza milhares de pregoes por mes e o registro de precos estadual pode gerar pedidos de centenas de unidades gestoras.',
    legalBasis: 'Decreto Estadual SP 49.722/2005; Lei 14.133/2021',
    relatedTerms: ['pregao-eletronico', 'licitacao', 'sicaf'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Entenda o que e a BEC/SP, como se cadastrar no CAUFESP e participar de licitacoes do Estado de Sao Paulo.',
  },
  {
    slug: 'licitacao-sustentavel-criterios-verdes',
    title: 'O que e licitacao sustentavel e quais criterios sao exigidos?',
    category: 'tecnologia-sistemas',
    answer:
      'A licitacao sustentavel (ou compra publica verde) e a incorporacao de criterios ambientais, sociais e economicos no processo de contratacao publica, buscando reduzir impactos negativos e promover o desenvolvimento sustentavel. A Lei 14.133/2021 tornou a sustentabilidade um principio obrigatorio (art. 5 e art. 11, IV).\n\n' +
      '**Fundamentos legais:**\n' +
      '- Lei 14.133/2021, art. 11, IV (desenvolvimento nacional sustentavel como objetivo)\n' +
      '- Decreto 7.746/2012 (criterios e praticas de sustentabilidade)\n' +
      '- IN SLTI/MP 01/2010 (criterios sustentaveis em compras federais)\n\n' +
      '**Criterios ambientais comuns em editais:**\n\n' +
      '1. **Eficiencia energetica:** Selo PROCEL/INMETRO classe A para equipamentos eletricos.\n' +
      '2. **Materiais reciclados:** Preferencia por produtos com conteudo reciclado.\n' +
      '3. **Gestao de residuos:** Plano de gerenciamento de residuos solidos (PGRS).\n' +
      '4. **Substancias toxicas:** Restricao a materiais com substancias nocivas (RoHS).\n' +
      '5. **Embalagens:** Preferencia por embalagens reciclaveis ou biodegradaveis.\n' +
      '6. **Agua:** Equipamentos com selo de economia de agua (torneiras, descargas).\n' +
      '7. **Certificacoes ambientais:** ISO 14001, FSC (madeira), selo organico.\n\n' +
      '**Criterios sociais:**\n' +
      '- Insercao de trabalhadores com deficiencia\n' +
      '- Aprendizagem e formacao profissional\n' +
      '- Igualdade de genero\n' +
      '- Respeito a legislacao trabalhista e previdenciaria\n\n' +
      '**Como a sustentabilidade afeta a proposta:**\n\n' +
      'O edital pode:\n' +
      '- Exigir certificacoes ambientais como requisito de habilitacao\n' +
      '- Usar criterio de julgamento "tecnica e preco" com pontuacao para sustentabilidade\n' +
      '- Aplicar margem de preferencia para produtos sustentaveis\n' +
      '- Exigir logistica reversa apos o consumo\n' +
      '- Prever ciclo de vida do produto (TCO — Total Cost of Ownership)\n\n' +
      '**Setores mais impactados:**\n' +
      '- Construcao civil (edificacoes verdes, PBQP-H)\n' +
      '- TI (descarte de eletronicos, eficiencia energetica de data centers)\n' +
      '- Alimentacao (organicos, rastreabilidade)\n' +
      '- Facilities (produtos biodegradaveis, gestao de residuos)\n' +
      '- Transporte (frotas eletricias/hibridas)\n\n' +
      '**Dica:** A sustentabilidade nao e mais diferencial — e requisito. Invista em certificacoes ambientais e prepare sua empresa para comprovar praticas sustentaveis na cadeia produtiva.',
    legalBasis:
      'Lei 14.133/2021, arts. 5, 11 (IV); Decreto 7.746/2012',
    relatedTerms: ['licitacao', 'edital', 'termo-referencia'],
    relatedSectors: ['meio-ambiente', 'energia'],
    relatedArticles: [],
    metaDescription:
      'Entenda o que e licitacao sustentavel, quais criterios verdes sao exigidos e como preparar sua empresa (Lei 14.133).',
  },
  {
    slug: 'portal-compras-estadual-diferenca-federal',
    title:
      'Qual a diferenca entre portais de compras estaduais e federal?',
    category: 'tecnologia-sistemas',
    answer:
      'O ecossistema de compras publicas no Brasil e fragmentado entre plataformas federais, estaduais e municipais, cada uma com regras, cadastros e interfaces proprias. Entender essas diferencas e essencial para empresas que desejam atuar em multiplas esferas.\n\n' +
      '**Portal federal — ComprasGov (comprasgov.br):**\n' +
      '- Ambito: Todos os orgaos do Executivo Federal\n' +
      '- Cadastro: SICAF (unificado)\n' +
      '- Catalogo: CATMAT (materiais) e CATSER (servicos)\n' +
      '- Certificado digital: Obrigatorio (ICP-Brasil)\n' +
      '- Volume: ~200 mil processos/ano\n\n' +
      '**Principais portais estaduais:**\n\n' +
      '| Estado | Portal | Cadastro |\n' +
      '|--------|--------|----------|\n' +
      '| SP | BEC/SP (bec.sp.gov.br) | CAUFESP |\n' +
      '| RJ | SIGA (compras.rj.gov.br) | SIGA-RJ |\n' +
      '| MG | Portal de Compras MG | CAGEF |\n' +
      '| RS | CELIC (celic.rs.gov.br) | CFRS |\n' +
      '| PR | DECOM/PR | Cadastro SEAP |\n' +
      '| BA | Comprasnet.BA | SAEB |\n\n' +
      '**Plataformas privadas usadas por estados e municipios:**\n\n' +
      '| Plataforma | Cobertura |\n' +
      '|------------|----------|\n' +
      '| Portal de Compras Publicas | 2.500+ orgaos |\n' +
      '| BLL Compras | 4.000+ orgaos |\n' +
      '| Licitacoes-e (BB) | Federal + estadual + municipal |\n' +
      '| Compras BR | Municipal |\n' +
      '| Licitar Digital | Municipal |\n\n' +
      '**Diferencas praticas para fornecedores:**\n\n' +
      '1. **Cadastro:** Cada plataforma exige cadastro proprio. O SICAF federal nao e automaticamente aceito em portais estaduais.\n' +
      '2. **Interface:** Cada sistema tem interface e fluxo diferentes — familiarize-se antes de participar.\n' +
      '3. **Regras:** Embora a Lei 14.133 seja nacional, regulamentacoes estaduais/municipais podem ter particularidades.\n' +
      '4. **Certificado digital:** Obrigatorio em quase todos, mas alguns portais permitem acesso com login/senha para consulta.\n' +
      '5. **Publicacao:** O PNCP esta centralizando progressivamente, mas nem todos os municipios publicam la.\n\n' +
      '**Estrategia para fornecedores:**\n' +
      '- Cadastre-se nas plataformas dos estados onde deseja atuar\n' +
      '- Mantenha cadastros atualizados em multiplos portais\n' +
      '- Use ferramentas de monitoramento (como SmartLic) que agregam todas as fontes\n' +
      '- Priorize estados com maior volume de compras no seu setor',
    legalBasis: 'Lei 14.133/2021, art. 175',
    relatedTerms: ['pncp', 'sicaf', 'pregao-eletronico'],
    relatedSectors: [],
    relatedArticles: [],
    metaDescription:
      'Compare portais de compras federal (ComprasGov), estaduais (BEC, SIGA, CELIC) e privados: cadastros, regras e como participar.',
  },
  {
    slug: 'inteligencia-artificial-licitacoes',
    title:
      'Como a inteligencia artificial esta transformando licitacoes?',
    category: 'tecnologia-sistemas',
    answer:
      'A inteligencia artificial (IA) esta revolucionando tanto o lado do comprador publico quanto do fornecedor no mercado de licitacoes. Desde a analise automatizada de editais ate a deteccao de fraudes, a IA esta criando novas possibilidades e vantagens competitivas.\n\n' +
      '**IA no lado do governo (comprador):**\n\n' +
      '1. **Pesquisa de precos automatizada:** Algoritmos analisam historico de contratacoes no PNCP para estimar valores de referencia com maior precisao.\n' +
      '2. **Deteccao de fraudes:** Machine learning identifica padroes suspeitos como conluio entre licitantes, direcionamento de editais e sobrepreco.\n' +
      '3. **Chatbots para fornecedores:** Assistentes virtuais respondem duvidas sobre editais e processos em tempo real.\n' +
      '4. **Classificacao automatica:** IA categoriza e rotula contratacoes, facilitando a busca e analise.\n' +
      '5. **Analise de risco de fornecedores:** Modelos preditivos avaliam a probabilidade de inadimplemento.\n\n' +
      '**IA no lado do fornecedor:**\n\n' +
      '1. **Monitoramento inteligente de editais:** Ferramentas como o SmartLic usam IA para classificar licitacoes por relevancia setorial, filtrando o que realmente importa dentre milhares de publicacoes diarias.\n' +
      '2. **Analise de viabilidade:** Algoritmos avaliam automaticamente a viabilidade de participacao com base em modalidade, prazo, valor e localizacao.\n' +
      '3. **Inteligencia de precos:** IA analisa contratos historicos para sugerir faixas de precos competitivos por tipo de servico e regiao.\n' +
      '4. **Geracao de documentos:** LLMs (Large Language Models) auxiliam na elaboracao de propostas tecnicas, recursos e impugnacoes.\n' +
      '5. **Analise concorrencial:** IA mapeia concorrentes por setor, identificando seus historicos de participacao e taxas de sucesso.\n\n' +
      '**Exemplos praticos de IA em licitacoes:**\n\n' +
      '- **TCU:** Utiliza o sistema ALICE (Analise de Licitacoes e Editais) para auditar contratacoes automaticamente.\n' +
      '- **CGU:** Emprega IA para deteccao de sobrepreco em obras publicas.\n' +
      '- **SmartLic:** Classifica setorialmente editais usando GPT-4.1-nano para zero-match classification.\n' +
      '- **Painel de Precos:** Usa algoritmos para calcular precos de referencia a partir de contratos historicos.\n\n' +
      '**O futuro proximo:**\n' +
      '- Editais gerados por IA (rascunhos automatizados)\n' +
      '- Negociacao assistida por IA em dispensas e inexigibilidades\n' +
      '- Gestao de contratos preditiva (alertas de risco antes de problemas)\n' +
      '- Matching automatico entre demandas publicas e capacidades de fornecedores\n\n' +
      '**Para fornecedores:** Adotar ferramentas de IA para monitoramento e analise de licitacoes nao e mais vantagem competitiva — e sobrevivencia. Quem analisa editais manualmente nao consegue competir em escala com quem usa inteligencia artificial.',
    legalBasis: 'Lei 14.133/2021; LGPD (Lei 13.709/2018)',
    relatedTerms: ['pncp', 'licitacao', 'edital'],
    relatedSectors: ['informatica'],
    relatedArticles: [],
    metaDescription:
      'Descubra como a IA esta transformando licitacoes: monitoramento inteligente, analise de precos, deteccao de fraudes e mais.',
  },
];

/* ------------------------------------------------------------------ */
/*  Helper functions                                                   */
/* ------------------------------------------------------------------ */

export function getQuestionBySlug(slug: string): Question | undefined {
  return QUESTIONS.find((q) => q.slug === slug);
}

export function getQuestionsByCategory(
  category: QuestionCategory,
): Question[] {
  return QUESTIONS.filter((q) => q.category === category);
}

export function getAllQuestionSlugs(): string[] {
  return QUESTIONS.map((q) => q.slug);
}

export function getQuestionsForGlossaryTerm(termSlug: string): Question[] {
  return QUESTIONS.filter((q) => q.relatedTerms.includes(termSlug));
}

export function getQuestionsForSector(sectorSlug: string): Question[] {
  return QUESTIONS.filter((q) => q.relatedSectors.includes(sectorSlug));
}
