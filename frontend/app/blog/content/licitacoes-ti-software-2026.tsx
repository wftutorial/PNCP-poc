import Link from 'next/link';
import BlogInlineCTA from '../components/BlogInlineCTA';

/**
 * SEO Sector Guide S2: Licitacoes de TI e Software 2026
 *
 * Content cluster: guias setoriais de licitacoes
 * Target: 3,000-3,500 words | Primary KW: licitacoes tecnologia
 */
export default function LicitacoesTISoftware2026() {
  return (
    <>
      {/* FAQPage JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            mainEntity: [
              {
                '@type': 'Question',
                name: 'Qual a modalidade mais usada para licitacoes de TI?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O pregao eletronico e a modalidade dominante, utilizada em mais de 80% dos editais de TI publicados no PNCP. A Lei 14.133/2021 classifica a maioria dos servicos de TI como "servicos comuns" (art. 6o, XIII), o que torna o pregao obrigatorio. Excecoes incluem: desenvolvimento de software sob medida de alta complexidade (que pode usar concorrencia por tecnica e preco) e aquisicao de licencas de software proprietario sem concorrente (que pode ser contratada por inexigibilidade, art. 74, I).',
                },
              },
              {
                '@type': 'Question',
                name: 'Posso participar de licitacao de software sendo startup ou MEI?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim. A Lei Complementar 123/2006 garante tratamento diferenciado para ME e EPP em licitacoes: empate ficto (ate 5% acima do menor preco em pregao), prazo adicional para regularizacao fiscal (5 dias uteis), e licitacoes exclusivas para valores ate R$ 80.000. Para startups constituidas como ME/EPP, esses beneficios se aplicam integralmente. A principal barreira nao e juridica, mas documental: editais de TI frequentemente exigem atestados de capacidade tecnica com quantitativos minimos, o que pode ser desafiador para empresas novas.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quais certificacoes sao exigidas em editais de TI?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'As certificacoes mais frequentes em editais de TI sao: ISO 27001 (seguranca da informacao, exigida em ~15% dos editais de TI), ISO 9001 (gestao da qualidade), CMMI nivel 2 ou 3 (maturidade de processos de software, exigida em ~8% dos editais), e MPS.BR (modelo brasileiro de melhoria de processos). Para profissionais individuais da equipe tecnica, sao comuns: PMP (gerente de projetos), ITIL (gestao de servicos), AWS/Azure/GCP (cloud), e LGPD/DPO (protecao de dados). A exigencia de certificacoes especificas como unico criterio de habilitacao pode ser questionada quando restringe a competitividade.',
                },
              },
              {
                '@type': 'Question',
                name: 'O que e prova de conceito (POC) em licitacoes de software?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A prova de conceito (POC) e um procedimento previsto na Lei 14.133 (art. 17, §3o) que permite ao orgao contratante verificar se a solucao ofertada atende aos requisitos tecnicos do edital antes da adjudicacao. Em editais de TI, a POC normalmente envolve: demonstracao funcional do software em ambiente controlado, validacao de requisitos tecnicos especificos (integracao, performance, seguranca), e execucao de casos de teste predefinidos. O prazo tipico e de 5 a 15 dias uteis. A POC e eliminatoria — se a solucao nao for aprovada, a empresa e desclassificada e o proximo colocado e convocado.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como funciona o modelo de fabrica de software em licitacoes?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O modelo de fabrica de software e a forma predominante de contratacao de desenvolvimento no governo. O orgao contrata um volume de Pontos de Funcao (PF) ou UST (Unidades de Servico Tecnico) por periodo, e demanda entregas conforme necessidade. Valores tipicos: R$ 400 a R$ 900 por Ponto de Funcao, dependendo da complexidade e da regiao. Contratos variam de 5.000 PF/ano (orgaos menores) a 100.000+ PF/ano (grandes ministerios). A metrica de PF segue a metodologia IFPUG/NESMA, e a contagem e frequentemente fonte de disputas contratuais.',
                },
              },
              {
                '@type': 'Question',
                name: 'Quais UFs publicam mais editais de TI?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'O Distrito Federal (DF) lidera com folga, concentrando aproximadamente 25% do valor total de editais de TI, devido a concentracao de orgaos federais em Brasilia. Em seguida: Sao Paulo (SP) com ~18% (governo estadual + prefeituras de grande porte), Rio de Janeiro (RJ) com ~12%, e Minas Gerais (MG) com ~8%. Para o governo federal especificamente, praticamente todos os grandes contratos de TI tem execucao em Brasilia, mesmo quando o orgao tem presenca nacional.',
                },
              },
            ],
          }),
        }}
      />

      {/* HowTo JSON-LD — steps to participate in IT bids */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            name: 'Como participar de licitacoes de TI e software',
            description:
              'Passo a passo para empresas de tecnologia participarem de licitacoes publicas no Brasil, do cadastro a adjudicacao.',
            step: [
              {
                '@type': 'HowToStep',
                name: 'Obter SICAF e certificacoes',
                text: 'Cadastre a empresa no SICAF (Sistema de Cadastramento Unificado de Fornecedores) e obtenha certificacoes relevantes (ISO 27001, ISO 9001, MPS.BR) conforme o perfil de editais pretendido.',
              },
              {
                '@type': 'HowToStep',
                name: 'Montar portfólio de atestados tecnicos',
                text: 'Reuna atestados de capacidade tecnica de clientes anteriores (publicos e privados) que comprovem experiencia em servicos similares aos licitados. Priorize atestados com quantitativos mensuraveis.',
              },
              {
                '@type': 'HowToStep',
                name: 'Monitorar editais no PNCP e portais estaduais',
                text: 'Acompanhe diariamente o PNCP, ComprasGov e portais estaduais de licitacao. Filtre por palavras-chave do setor: desenvolvimento de software, outsourcing de TI, cloud, ciberseguranca.',
              },
              {
                '@type': 'HowToStep',
                name: 'Analisar viabilidade tecnica e comercial',
                text: 'Avalie cada edital nos 4 fatores de viabilidade: modalidade, timeline, valor estimado e geografia. Para TI, verifique tambem: stack tecnologica exigida, metricas de SLA e equipe minima.',
              },
              {
                '@type': 'HowToStep',
                name: 'Elaborar proposta tecnica e de precos',
                text: 'Monte a proposta tecnica (metodologia, equipe, cronograma, ferramentas) e a planilha de precos (por PF, UST ou hora tecnica). Atenda a todos os requisitos do termo de referencia.',
              },
              {
                '@type': 'HowToStep',
                name: 'Participar do pregao e fase de lances',
                text: 'No dia do pregao eletronico, participe da fase de lances com limite de preco previamente calculado. Apos encerramento, esteja preparado para enviar documentacao de habilitacao no prazo (geralmente 2-4 horas).',
              },
              {
                '@type': 'HowToStep',
                name: 'Executar POC se exigida',
                text: 'Se o edital preve prova de conceito, demonstre a solucao conforme os criterios definidos. Prepare ambiente, dados de teste e equipe tecnica com antecedencia.',
              },
            ],
          }),
        }}
      />

      {/* Opening paragraph */}
      <p className="text-base sm:text-xl leading-relaxed text-ink">
        O governo brasileiro e o maior comprador de tecnologia do pais. Em
        2025, o PNCP registrou mais de 62.000 publicacoes relacionadas a{' '}
        <strong>tecnologia da informacao, software e servicos digitais</strong>,
        com valor estimado agregado superior a R$ 45 bilhoes. A transformacao
        digital do setor publico -- impulsionada pela Estrategia Nacional de
        Governo Digital, pela LGPD e pela obrigatoriedade do PNCP -- gerou um
        crescimento de 22% no volume de editais de TI entre 2023 e 2025. Para
        empresas de tecnologia, o mercado B2G representa uma oportunidade
        concreta e recorrente, mas exige compreensao das regras especificas de{' '}
        <strong>licitacoes de tecnologia</strong>. Este guia cobre modalidades,
        tipos de objeto, faixas de valor, requisitos e estrategias para o
        setor.
      </p>

      {/* Section 1 */}
      <h2>Panorama do setor de TI em licitacoes 2026</h2>

      <p>
        Tres forcas estruturais estao expandindo o mercado de TI governamental
        em 2026. A primeira e a continuidade da Estrategia Nacional de Governo
        Digital (Decreto 10.332/2020, atualizado em 2024), que determina a
        digitalizacao de 100% dos servicos publicos federais ate 2026 e
        impulsiona contratacoes de plataformas digitais, cloud e integracao
        de sistemas.
      </p>

      <p>
        A segunda e a LGPD (Lei 13.709/2018), cuja fiscalizacao intensificada
        pela ANPD a partir de 2024 forcou orgaos publicos a contratar servicos
        de adequacao, auditoria de dados, implementacao de controles de acesso
        e nomeacao de encarregados (DPOs). Editais com componente LGPD
        cresceram 45% entre 2024 e 2025.
      </p>

      <p>
        A terceira e a migracao para cloud. O governo federal publicou a
        Portaria SGD/ME 778/2019 (atualizada em 2023), que estabelece a
        contratacao de servicos de computacao em nuvem como modelo preferencial.
        Grandes orgaos como Serpro, Dataprev e ministerios estao migrando
        datacenters on-premises para AWS GovCloud, Azure Government e nuvem
        privada, gerando demanda por servicos de migracao, arquitetura cloud
        e operacao (CloudOps/DevOps).
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Numeros do setor -- TI e Software em licitacoes (2025)
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Volume de publicacoes no PNCP:</strong> ~62.000 processos
            relacionados a TI, software e servicos digitais
          </li>
          <li>
            <strong>Valor estimado agregado:</strong> superior a R$ 45 bilhoes
            (todas as esferas)
          </li>
          <li>
            <strong>Crescimento 2023-2025:</strong> +22% em volume de editais,
            +35% em valor agregado
          </li>
          <li>
            <strong>Modalidade predominante:</strong> pregao eletronico (80%+
            dos processos)
          </li>
          <li>
            <strong>UF com maior concentracao:</strong> DF (governo federal),
            seguido de SP, RJ e MG
          </li>
          <li>
            <strong>Segmentos em alta:</strong> cloud migration, ciberseguranca,
            adequacao LGPD, IA/ML, RPA (automacao de processos)
          </li>
        </ul>
      </div>

      <p>
        O monitoramento desses editais no{' '}
        <Link href="/blog/pncp-guia-completo-empresas" className="text-brand-navy dark:text-brand-blue hover:underline">
          PNCP
        </Link>{' '}
        e no ComprasGov e essencial. A classificacao setorial por{' '}
        <Link href="/blog/inteligencia-artificial-licitacoes-como-funciona" className="text-brand-navy dark:text-brand-blue hover:underline">
          inteligencia artificial
        </Link>{' '}
        permite filtrar o volume massivo de publicacoes e identificar apenas
        os editais alinhados ao perfil tecnico da empresa.
      </p>

      {/* Section 2 */}
      <h2>Modalidades mais comuns em licitacoes de TI</h2>

      <h3>
        <Link href="/glossario#pregao-eletronico" className="text-brand-navy dark:text-brand-blue hover:underline">
          Pregao eletronico
        </Link>{' '}
        -- o padrao do setor
      </h3>

      <p>
        O pregao eletronico e utilizado em mais de 80% dos editais de TI. A
        Lei 14.133 classifica servicos de TI como &ldquo;servicos comuns&rdquo;
        quando os padroes de desempenho e qualidade podem ser objetivamente
        definidos no edital. Na pratica, isso abrange: outsourcing de TI,
        licenciamento de software padrao, servicos de infraestrutura (hosting,
        cloud), suporte tecnico, help desk e desenvolvimento de software com
        especificacao funcional detalhada.
      </p>

      <p>
        O criterio de julgamento e predominantemente menor preco por item ou
        por lote. A fase de lances e competitiva e exige que a empresa tenha
        calculado previamente o preco minimo sustentavel -- preco abaixo do
        custo operacional leva a contratos deficitarios que comprometem a
        qualidade da entrega e a reputacao da empresa.
      </p>

      <h3>
        <Link href="/glossario#ata-de-registro-de-precos" className="text-brand-navy dark:text-brand-blue hover:underline">
          Ata de registro de precos (ARP)
        </Link>
      </h3>

      <p>
        A ARP e uma ferramenta estrategica no setor de TI. O orgao gerenciador
        realiza o pregao, registra precos unitarios (por hora tecnica, por
        ponto de funcao, por licenca), e demanda conforme necessidade ao longo
        de 12 meses (prorrogavel por mais 12). Outros orgaos podem aderir a
        ata mediante autorizacao.
      </p>

      <p>
        Para empresas de TI, a ARP tem vantagens concretas: volume garantido
        (o orgao se compromete com quantidade minima), previsibilidade de
        receita, e possibilidade de atender multiplos orgaos com uma unica
        licitacao vencida. Em contrapartida, o preco registrado deve ser
        competitivo o suficiente para vencer o pregao, mas com margem
        suficiente para sustentar a operacao por 12 a 24 meses sem reajuste.
      </p>

      <h3>
        <Link href="/glossario#inexigibilidade" className="text-brand-navy dark:text-brand-blue hover:underline">
          Inexigibilidade
        </Link>
      </h3>

      <p>
        A inexigibilidade (art. 74, I, Lei 14.133) e aplicavel quando a
        contratacao envolve software proprietario com fornecedor exclusivo.
        Se a empresa desenvolve um produto proprio que nao tem concorrente
        direto para atender a necessidade do orgao, a contratacao pode ser
        direta, sem licitacao. E necessario comprovar a exclusividade por
        meio de declaracao do fabricante ou atestado de entidade representativa.
        Aproximadamente 12% das contratacoes de TI no governo federal utilizam
        inexigibilidade, especialmente para renovacao de licencas e contratos
        de manutencao de sistemas legados.
      </p>

      {/* Section 3 */}
      <h2>Tipos de objeto em licitacoes de TI</h2>

      <p>
        O universo de editais de TI e diverso. Compreender os tipos de objeto
        ajuda a identificar os nichos onde a empresa tem maior competitividade.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Principais tipos de objeto em editais de TI
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Fabrica de software (desenvolvimento):</strong> contratacao
            por Pontos de Funcao (PF) ou UST. Inclui analise, codificacao,
            testes e implantacao. Contratos tipicos: 12-60 meses, R$ 500K a
            R$ 50M+.
          </li>
          <li>
            <strong>Licenciamento de software:</strong> aquisicao de licencas
            (Microsoft, Oracle, SAP, Red Hat, etc.) ou subscricao SaaS.
            Frequentemente via ARP. Valores: R$ 50K a R$ 20M.
          </li>
          <li>
            <strong>Outsourcing / service desk:</strong> alocacao de
            profissionais de TI (desenvolvedores, DBAs, analistas de infra).
            Contratacao por posto de trabalho ou por UST. Mercado de alto
            volume.
          </li>
          <li>
            <strong>Infraestrutura cloud:</strong> migracao para nuvem,
            arquitetura cloud-native, servicos gerenciados (IaaS/PaaS/SaaS).
            Segmento em crescimento acelerado desde 2023.
          </li>
          <li>
            <strong>Ciberseguranca:</strong> SOC (Security Operations Center),
            pentest, analise de vulnerabilidades, gestao de identidades (IAM),
            DLP. Demanda impulsionada por LGPD e ataques a orgaos publicos.
          </li>
          <li>
            <strong>Manutencao e sustentacao:</strong> suporte a sistemas
            legados, correcao de bugs, evolucoes menores. Contratos de 12-24
            meses. Menor margem, porem receita recorrente e estavel.
          </li>
          <li>
            <strong>Consultoria e governanca de TI:</strong> PDTIC (Plano
            Diretor de TI), mapeamento de processos, adequacao LGPD, auditoria.
            Valores menores (R$ 100K-R$ 1M), mas exigem qualificacao tecnica
            especifica.
          </li>
        </ul>
      </div>

      {/* Section 4 */}
      <h2>Faixas de valor em licitacoes de TI</h2>

      <p>
        O setor de TI tem amplitude de valor que vai de contratos de
        R$ 20.000 (dispensa para microsservicos) a contratos de centenas de
        milhoes (outsourcing de grandes ministerios). A segmentacao por faixa
        permite foco estrategico.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Segmentacao por faixa de valor -- TI e Software
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Microsservicos e dispensas (R$ 20K - R$ 200K):</strong>{' '}
            Desenvolvimento de modulos, integracao de APIs, consultoria pontual.
            Baixa barreira de entrada. Ideal para startups e ME/EPP. Volume
            alto, mas valor individual baixo.
          </li>
          <li>
            <strong>Projetos medios (R$ 200K - R$ 2M):</strong>{' '}
            Desenvolvimento de sistemas, implantacao de ERP/CRM, migracao de
            plataforma. Exigem atestados de projetos similares. Concorrencia
            moderada: 6 a 15 empresas por edital.
          </li>
          <li>
            <strong>Grandes contratos (R$ 2M - R$ 20M):</strong>{' '}
            Fabrica de software, outsourcing completo, infraestrutura cloud
            de grande porte. Exigem certificacoes (ISO, CMMI), equipe tecnica
            robusta e capacidade financeira comprovada. Concorrencia: 3 a 8
            empresas.
          </li>
          <li>
            <strong>Megacontratos (acima de R$ 20M):</strong>{' '}
            Outsourcing ministerial, datacenter completo, plataformas
            nacionais. Dominados por grandes integradoras. Frequentemente
            exigem consorcio.
          </li>
        </ul>
      </div>

      {/* Section 5 */}
      <h2>UFs com maior volume de editais de TI</h2>

      <p>
        A geografia dos editais de TI e fortemente concentrada no Distrito
        Federal, reflexo da centralizacao administrativa do governo federal.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Ranking de UFs por volume e valor de editais de TI (dados PNCP 2025)
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>1. Distrito Federal (DF):</strong> ~25% do valor total.
            Ministerios, autarquias, tribunais. Maiores contratos do pais
            (Serpro, Dataprev, STF, TSE). Execucao presencial frequentemente
            exigida em Brasilia.
          </li>
          <li>
            <strong>2. Sao Paulo (SP):</strong> ~18% do valor. Governo
            estadual (Prodesp), prefeitura da capital, municipios de grande
            porte (Campinas, Santos, Guarulhos). Forte demanda por ciberseguranca
            e cloud.
          </li>
          <li>
            <strong>3. Rio de Janeiro (RJ):</strong> ~12% do valor. Petrobras,
            BNDES, Marinha, Fiocruz. Concentracao em grandes orgaos federais
            com sede no RJ.
          </li>
          <li>
            <strong>4. Minas Gerais (MG):</strong> ~8% do valor. Governo
            estadual (Prodemge), universidades federais (UFMG, UFU, UFJF).
            Volume diversificado entre capital e interior.
          </li>
          <li>
            <strong>5. Rio Grande do Sul (RS):</strong> ~5% do valor. Banrisul,
            PROCERGS, universidades. Historico de investimento em TI acima
            da media regional.
          </li>
        </ul>
      </div>

      <p>
        Para empresas fora do DF, uma estrategia valida e comecar por editais
        estaduais e municipais da propria regiao, onde a presenca local e
        vantagem competitiva, e expandir para o governo federal conforme o
        portfólio de atestados cresce.
      </p>

      {/* Section 6 */}
      <h2>Requisitos tecnicos em licitacoes de TI</h2>

      <p>
        A habilitacao tecnica em editais de TI combina exigencias
        institucionais (certificacoes da empresa) com exigencias individuais
        (qualificacao da equipe).
      </p>

      <h3>Atestados de capacidade tecnica</h3>

      <p>
        Atestados sao o principal documento de habilitacao. Devem comprovar
        experiencia em servicos compativeis em natureza e quantidade. Para
        fabrica de software, o edital pode exigir atestado de execucao de,
        por exemplo, 5.000 Pontos de Funcao em 12 meses. Para outsourcing,
        atestado de alocacao de 20+ profissionais de TI simultaneamente.
        O limite legal e de 50% do quantitativo licitado (art. 67, §1o,
        Lei 14.133).
      </p>

      <h3>Certificacoes da empresa</h3>

      <p>
        As certificacoes mais frequentes em editais de TI incluem: ISO 27001
        (seguranca da informacao, exigida em ~15% dos editais), ISO 9001
        (gestao da qualidade, ~12%), CMMI nivel 2 ou 3 (maturidade de
        processos, ~8%), e MPS.BR (modelo brasileiro, aceito como alternativa
        ao CMMI). A obtencao de ISO 27001 leva tipicamente de 6 a 12 meses
        e custa entre R$ 30.000 e R$ 80.000 -- e um investimento que amplia
        significativamente o universo de editais disputaveis.
      </p>

      <h3>Equipe tecnica minima</h3>

      <p>
        Editais de TI frequentemente exigem comprovacao de equipe com perfis
        especificos: gerente de projetos (PMP ou PRINCE2), arquiteto de
        software (experiencia em microsservicos, cloud), DBA (certificacao
        Oracle/PostgreSQL), analista de seguranca (CEH, CISSP, CompTIA
        Security+), especialista LGPD (DPO certificado). O vinculo pode ser
        por CLT, contrato de prestacao de servicos ou declaracao de
        compromisso de contratacao futura.
      </p>

      {/* BlogInlineCTA at ~40% */}
      <BlogInlineCTA
        slug="licitacoes-ti-software-2026"
        campaign="guias"
        ctaHref="/explorar"
        ctaText="Explorar licitacoes gratis"
        ctaMessage="Descubra editais abertos no seu setor -- busca gratuita"
      />

      {/* Section 7 */}
      <h2>Armadilhas comuns em editais de TI</h2>

      <p>
        O setor de TI possui armadilhas especificas que, se nao identificadas
        na analise do edital, podem comprometer a execucao do contrato ou
        inviabilizar a participacao.
      </p>

      <h3>Descricao generica do objeto</h3>

      <p>
        Termos de referencia vagos como &ldquo;contratacao de servicos de
        desenvolvimento de sistemas&rdquo; sem especificacao de tecnologias,
        volumetria, ambiente ou integracao criam risco para o contratado. O
        orgao pode demandar qualquer tipo de desenvolvimento, em qualquer
        linguagem, com qualquer nivel de complexidade, dentro do preco
        contratado. Antes de participar, verifique se o edital detalha: stack
        tecnologica, estimativa de Pontos de Funcao ou UST, ambiente de
        producao (on-premises vs cloud), integracao com sistemas existentes,
        e niveis de servico mensuraveis (SLA).
      </p>

      <h3>Metricas de SLA irreais</h3>

      <p>
        Editais que exigem disponibilidade de 99,99% (4,38 minutos de
        downtime por mes) para sistemas que rodam em infraestrutura on-premises
        do proprio orgao sao tecnicamente impraticaveis. Da mesma forma,
        SLAs de tempo de resposta de 30 minutos para suporte 24x7 em
        municipios remotos geram custo operacional desproporcional. A
        recomendacao e calcular o custo real de atender cada SLA exigido
        antes de formular o preco -- SLAs agressivos frequentemente sao a
        fonte de prejuizo em contratos de TI.
      </p>

      <h3>Exigencia de certificacoes como barreira</h3>

      <p>
        Editais que exigem certificacoes de nicho altamente especificas (por
        exemplo, certificacao de um unico fornecedor para um modulo
        especifico) como criterio eliminatorio de habilitacao podem estar
        direcionados para um concorrente especifico. A Lei 14.133 permite
        impugnacao quando as exigencias de habilitacao restringem
        indevidamente a competitividade (art. 164). Se a empresa identifica
        que uma exigencia de certificacao e desproporcional ao objeto,
        pode apresentar impugnacao fundamentada ate 3 dias uteis antes da
        abertura.
      </p>

      <h3>Lock-in tecnologico nao declarado</h3>

      <p>
        Sistemas legados do orgao em tecnologias proprietarias (Oracle Forms,
        SAP ABAP, plataformas low-code especificas) podem exigir
        conhecimento altamente especializado que nao esta explicito no edital.
        Antes de participar, pesquise o historico de contratacoes do orgao
        no PNCP para identificar quais tecnologias estao em uso e se a
        sua equipe tem capacidade de absorver a curva de aprendizado.
      </p>

      {/* Section 8 */}
      <h2>Atas de registro de preco como porta de entrada</h2>

      <p>
        Para empresas que estao iniciando no mercado B2G de TI, as atas de
        registro de preco (ARP) oferecem uma rota de entrada com risco
        controlado.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Vantagens da ARP para empresas de TI
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Volume sem compromisso imediato:</strong> a ARP registra
            precos, mas a demanda e gradual. A empresa nao precisa mobilizar
            toda a equipe no dia seguinte ao registro -- o orgao faz ordens
            de servico conforme necessidade.
          </li>
          <li>
            <strong>Multiplos orgaos com uma licitacao:</strong> outros orgaos
            podem aderir a ata (carona), multiplicando o potencial de receita
            sem novo processo licitatorio.
          </li>
          <li>
            <strong>Construcao de portfólio:</strong> cada ordem de servico
            executada gera um atestado de capacidade tecnica que pode ser
            usado em futuras licitacoes de maior porte.
          </li>
          <li>
            <strong>Previsibilidade:</strong> precos fixos por 12-24 meses
            permitem planejamento financeiro. O risco e conhecido.
          </li>
          <li>
            <strong>Fato gerador sob demanda:</strong> a empresa so aloca
            recursos quando ha ordem de servico efetiva. Diferente de
            contratos de outsourcing onde a equipe e fixa.
          </li>
        </ul>
      </div>

      <p>
        A estrategia recomendada para empresas em crescimento e: comecar por
        ARPs de menor valor em orgaos municipais ou estaduais, construir
        atestados tecnicos, e progressivamente disputar contratos de maior
        porte. Um ciclo tipico de 18 a 24 meses leva uma empresa de micro
        porte a disputar editais na faixa de R$ 500K a R$ 2M com atestados
        proprios.
      </p>

      {/* Section 9 */}
      <h2>Como analisar viabilidade de um edital de TI</h2>

      <p>
        A{' '}
        <Link href="/blog/analise-viabilidade-editais-guia" className="text-brand-navy dark:text-brand-blue hover:underline">
          analise de viabilidade
        </Link>{' '}
        aplicada ao setor de TI usa os mesmos 4 fatores (modalidade, timeline,
        valor, geografia) com calibracao especifica para as particularidades
        do setor.
      </p>

      <h3>Fator 1: Modalidade (peso 30%)</h3>

      <p>
        Em TI, o pregao eletronico e dominante e favorece empresas ageis em
        lances e documentacao. Concorrencias por tecnica e preco aparecem em
        projetos complexos e favorecem empresas com certificacoes e acervo
        diferenciado. Inexigibilidade beneficia exclusivamente fabricantes de
        software proprietario. A empresa deve identificar em qual modalidade
        sua taxa de adjudicacao historica e maior.
      </p>

      <h3>Fator 2: Timeline (peso 25%)</h3>

      <p>
        Para pregoes eletronicos de TI, o prazo minimo e de 8 dias uteis, mas
        propostas tecnicas de qualidade exigem 15 a 25 dias. O fator critico
        em TI e a disponibilidade de equipe: se o edital exige alocacao de
        profissionais especificos, a empresa precisa confirmar disponibilidade
        antes de participar. Prometer profissionais alocados em outro contrato
        e fonte comum de inadimplencia.
      </p>

      <h3>Fator 3: Valor estimado (peso 25%)</h3>

      <p>
        Valores de referencia em editais de TI frequentemente sao baseados em
        pesquisas de mercado ou em contratos anteriores. Quando o valor de
        referencia esta defasado (preco por PF de 3 anos atras sem reajuste),
        a margem pode ser insuficiente. Verifique se o preco unitario de
        referencia e compativel com o custo operacional da sua empresa
        (incluindo encargos, impostos, overhead e margem minima).
      </p>

      <h3>Fator 4: Geografia (peso 20%)</h3>

      <p>
        Em TI, a geografia tem peso menor que em engenharia, pois muitos
        servicos podem ser executados remotamente. Porem, editais que exigem
        presenca fisica da equipe em Brasilia (governo federal) ou no municipio
        contratante geram custo de deslocamento e alojamento que deve ser
        computado. A pandemia acelerou a aceitacao de trabalho remoto no
        governo, mas muitos editais ainda exigem presencialidade parcial
        (3 dias/semana no orgao).
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Exemplo pratico -- Viabilidade de edital de TI
        </p>
        <p className="text-sm text-ink-secondary mb-3">
          Empresa de software em SP avalia um pregao eletronico para fabrica
          de software de um tribunal em Brasilia, 8.000 PF em 24 meses,
          valor estimado R$ 5,6M, execucao hibrida (60% remoto):
        </p>
        <ul className="space-y-1.5 text-sm text-ink-secondary">
          <li>
            <strong>Modalidade (30%):</strong> Pregao eletronico, empresa
            tem experiencia e agilidade nesta modalidade = 8/10 x 0,30 = 2,40
          </li>
          <li>
            <strong>Timeline (25%):</strong> 15 dias uteis para proposta,
            equipe disponivel para alocacao = 7/10 x 0,25 = 1,75
          </li>
          <li>
            <strong>Valor (25%):</strong> R$ 700/PF, margem compativel com
            custo operacional da empresa = 8/10 x 0,25 = 2,00
          </li>
          <li>
            <strong>Geografia (20%):</strong> Execucao hibrida, 40%
            presencial em Brasilia, empresa tem profissionais no DF =
            7/10 x 0,20 = 1,40
          </li>
          <li className="pt-2 font-semibold">
            Pontuacao total: 7,55/10 -- Viabilidade alta. Recomendado
            prosseguir com analise detalhada do termo de referencia.
          </li>
        </ul>
      </div>

      <p>
        Para outros setores que frequentemente se conectam com TI em editais
        multiservico, consulte os guias de{' '}
        <Link href="/blog/licitacoes-engenharia-2026" className="text-brand-navy dark:text-brand-blue hover:underline">
          licitacoes de engenharia
        </Link>{' '}
        (obras com componente de automacao/TI) e{' '}
        <Link href="/blog/licitacoes-saude-2026" className="text-brand-navy dark:text-brand-blue hover:underline">
          licitacoes de saude
        </Link>{' '}
        (sistemas hospitalares, prontuario eletronico).
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Monitore editais de TI com inteligencia -- 14 dias gratis
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic filtra editais de tecnologia por relevancia e analisa
          viabilidade automaticamente. Pare de ler editais irrelevantes --
          receba apenas os que fazem sentido para o seu perfil.
        </p>
        <Link
          href="/signup?source=blog&article=licitacoes-ti-software-2026&utm_source=blog&utm_medium=cta&utm_content=licitacoes-ti-software-2026&utm_campaign=guias"
          className="inline-block bg-brand-navy hover:bg-brand-blue-hover text-white font-semibold px-5 sm:px-6 py-2.5 sm:py-3 rounded-button text-sm sm:text-base transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          Teste Gratis por 14 Dias
        </Link>
        <p className="text-xs text-ink-secondary mt-3">
          Sem cartao de credito. Veja todas as funcionalidades na{' '}
          <Link href="/features" className="underline hover:text-ink">
            pagina de recursos
          </Link>.
        </p>
      </div>

      {/* FAQ Section */}
      <h2>Perguntas Frequentes</h2>

      <h3>Qual a modalidade mais usada para licitacoes de TI?</h3>
      <p>
        O{' '}
        <Link href="/glossario#pregao-eletronico" className="text-brand-navy dark:text-brand-blue hover:underline">
          pregao eletronico
        </Link>{' '}
        e a modalidade dominante, utilizado em mais de 80% dos editais de TI
        publicados no PNCP. A Lei 14.133/2021 classifica a maioria dos
        servicos de TI como &ldquo;servicos comuns&rdquo; (art. 6o, XIII),
        tornando o pregao obrigatorio. Excecoes incluem: desenvolvimento de
        software de alta complexidade (concorrencia por tecnica e preco) e
        software proprietario sem concorrente (inexigibilidade, art. 74, I).
        Para a maioria das empresas de TI, dominar o processo de pregao
        eletronico e pre-requisito para atuar no mercado B2G.
      </p>

      <h3>Posso participar de licitacao de software sendo startup ou MEI?</h3>
      <p>
        Sim. A Lei Complementar 123/2006 garante tratamento diferenciado para
        ME e EPP: empate ficto (ate 5% acima do menor preco em pregao), prazo
        adicional para regularizacao fiscal (5 dias uteis), e licitacoes
        exclusivas para valores ate R$ 80.000. A principal barreira e
        documental: editais de TI frequentemente exigem atestados com
        quantitativos minimos. A estrategia recomendada para startups e
        comecar por dispensas de licitacao (ate R$ 50.000 para servicos) e
        ARPs de menor porte para construir portfólio de atestados.
      </p>

      <h3>Quais certificacoes sao exigidas em editais de TI?</h3>
      <p>
        As mais frequentes sao: ISO 27001 (seguranca da informacao, ~15% dos
        editais), ISO 9001 (qualidade, ~12%), CMMI nivel 2/3 (~8%), e MPS.BR
        (alternativa brasileira ao CMMI). Para profissionais da equipe: PMP
        (gestao de projetos), ITIL (gestao de servicos), certificacoes cloud
        (AWS, Azure, GCP), e LGPD/DPO. Nem todos os editais exigem todas as
        certificacoes -- a frequencia varia por tipo de objeto e orgao
        contratante. ISO 27001 e o investimento com maior retorno, pois
        abre portas para editais de ciberseguranca e dados sensiveis.
      </p>

      <h3>O que e prova de conceito (POC) em licitacoes de software?</h3>
      <p>
        A POC e um procedimento previsto na Lei 14.133 (art. 17, §3o) que
        permite ao orgao verificar se a solucao ofertada atende aos requisitos
        tecnicos antes da adjudicacao. O licitante melhor classificado e
        convocado a demonstrar a solucao em ambiente controlado, executando
        casos de teste predefinidos no edital. O prazo tipico e de 5 a 15
        dias uteis. A POC e eliminatoria: se nao aprovada, a empresa e
        desclassificada e o proximo colocado e convocado. Para se preparar,
        mantenha um ambiente de demonstracao atualizado e equipe tecnica
        disponivel para configuracao rapida.
      </p>

      <h3>Como funciona o modelo de fabrica de software em licitacoes?</h3>
      <p>
        O modelo de fabrica de software e a forma predominante de contratacao
        de desenvolvimento no governo. O orgao contrata um volume de Pontos
        de Funcao (PF) ou Unidades de Servico Tecnico (UST) por periodo e
        demanda entregas conforme necessidade. Valores tipicos: R$ 400 a
        R$ 900 por Ponto de Funcao, dependendo da complexidade e regiao.
        A metrica segue a metodologia IFPUG/NESMA. Os contratos variam de
        5.000 PF/ano (orgaos menores) a 100.000+ PF/ano (grandes
        ministerios). E fundamental que a empresa domine a contagem de PF,
        pois discrepancias entre a contagem do orgao e a do contratado sao
        a principal fonte de conflitos contratuais.
      </p>

      <h3>Quais UFs publicam mais editais de TI?</h3>
      <p>
        O Distrito Federal (DF) lidera com aproximadamente 25% do valor total
        de editais de TI, devido a concentracao de orgaos federais. Em
        seguida: Sao Paulo (SP) com ~18%, Rio de Janeiro (RJ) com ~12%, e
        Minas Gerais (MG) com ~8%. Para empresas que buscam volume sem se
        deslocar para Brasilia, os governos estaduais de SP e RJ oferecem
        oportunidades significativas com execucao local. Municipios de grande
        porte (acima de 500 mil habitantes) tambem publicam editais de TI com
        frequencia crescente, especialmente para cidades inteligentes e
        digitalizacao de servicos publicos.
      </p>
    </>
  );
}
