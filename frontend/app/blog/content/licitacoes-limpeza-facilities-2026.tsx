import Link from 'next/link';
import BlogInlineCTA from '../components/BlogInlineCTA';

/**
 * SEO GUIA-S4: Licitacoes de Limpeza e Facilities 2026 — Guia Completo
 *
 * Content cluster: guias setoriais
 * Target: 3,000+ words | Primary KW: licitacoes limpeza
 */
export default function LicitacoesLimpezaFacilities2026() {
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
                name: 'Como montar planilha de custos para licitação de limpeza?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A planilha de custos para licitação de limpeza deve incluir: remuneração base conforme a convenção coletiva vigente (CCT), encargos sociais e trabalhistas (INSS, FGTS, 13º, férias — entre 65% e 80% sobre o salário), insumos (produtos de limpeza, EPIs, uniformes), equipamentos (incluindo depreciação), custos indiretos (supervisão, administração) e BDI (Bonificação e Despesas Indiretas, tipicamente entre 15% e 25%). A soma de todos esses componentes, dividida pela produtividade por m², gera o custo por posto de serviço.',
                },
              },
              {
                '@type': 'Question',
                name: 'Qual o peso da convenção coletiva na formação de preço?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A convenção coletiva de trabalho (CCT) é o fator determinante na formação de preço de serviços de limpeza. O salário base definido na CCT da região de execução do contrato representa entre 50% e 60% do custo total do posto. Cada reajuste anual da CCT (dissídio) impacta diretamente o preço — empresas que não consideram o dissídio projetado na formação de preço correm risco de operar com margem negativa após o reajuste.',
                },
              },
              {
                '@type': 'Question',
                name: 'Preciso de quantos atestados de capacidade?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A Lei 14.133/2021 permite que o edital exija atestados que comprovem execução de até 50% do quantitativo licitado (art. 67, §1º). Na prática, editais de limpeza exigem entre 1 e 3 atestados que demonstrem experiência na prestação de serviços similares (limpeza predial, conservação, asseio) com quantitativo mínimo de postos ou área atendida. Atestados de contratos públicos têm maior peso, mas contratos privados também são aceitos quando acompanhados de documentação comprobatória.',
                },
              },
              {
                '@type': 'Question',
                name: 'É possível participar em UFs diferentes da sede?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'Sim, não há restrição legal para participar de licitações em UFs diferentes da sede da empresa. Porém, é necessário considerar que a convenção coletiva aplicável é a do local de execução do contrato (não a da sede), o que pode alterar significativamente o custo. Além disso, muitos editais exigem que a empresa mantenha escritório ou preposto na cidade de execução durante a vigência do contrato.',
                },
              },
              {
                '@type': 'Question',
                name: 'Como funciona a repactuação de contratos de limpeza?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'A repactuação é o mecanismo de reajuste de contratos de serviços contínuos com mão de obra dedicada, prevista no art. 135 da Lei 14.133/2021. Diferente do reajuste por índice, a repactuação se baseia na variação dos custos efetivos — especialmente o novo piso salarial definido pela CCT. O contratado deve solicitar a repactuação apresentando planilha de custos atualizada, demonstrando a variação de cada componente. O prazo mínimo para a primeira repactuação é de 12 meses contados da data do orçamento estimativo.',
                },
              },
              {
                '@type': 'Question',
                name: 'O que é BDI e como calcular para serviços de limpeza?',
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: 'BDI (Bonificação e Despesas Indiretas) é o percentual aplicado sobre os custos diretos para cobrir despesas administrativas, impostos sobre faturamento (ISS, PIS, COFINS, CSLL, IRPJ) e a margem de lucro. Para serviços de limpeza, o BDI típico varia entre 15% e 25%. O cálculo segue a fórmula: BDI = [(1 + AC) × (1 + S) × (1 + R) × (1 + L) / (1 - I)] - 1, onde AC = administração central, S = seguros, R = riscos, L = lucro e I = impostos. O TCU possui referências de BDI aceitáveis em seus acórdãos (Acórdão 2622/2013-TCU-Plenário).',
                },
              },
            ],
          }),
        }}
      />

      {/* HowTo JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'HowTo',
            name: 'Como participar de licitações de limpeza e facilities em 2026',
            description:
              'Passo a passo para empresas de limpeza, conservação e facilities que desejam vender serviços ao governo via licitações públicas.',
            step: [
              {
                '@type': 'HowToStep',
                name: 'Identifique a convenção coletiva da região-alvo',
                text: 'Consulte a CCT do sindicato de asseio e conservação da cidade onde pretende executar o contrato. O piso salarial é a base de toda a planilha de custos.',
              },
              {
                '@type': 'HowToStep',
                name: 'Monte a planilha de custos detalhada',
                text: 'Elabore planilha com salário base (CCT), encargos sociais e trabalhistas, insumos, EPIs, uniformes, equipamentos, custos indiretos e BDI.',
              },
              {
                '@type': 'HowToStep',
                name: 'Reúna atestados de capacidade técnica',
                text: 'Obtenha atestados de contratos anteriores (públicos ou privados) que comprovem experiência em limpeza predial ou serviços similares.',
              },
              {
                '@type': 'HowToStep',
                name: 'Cadastre-se nos portais de compras',
                text: 'Faça cadastro no PNCP, ComprasGov (SICAF) e portais estaduais. Mantenha documentação fiscal e trabalhista sempre atualizada.',
              },
              {
                '@type': 'HowToStep',
                name: 'Analise viabilidade antes de participar',
                text: 'Avalie cada edital considerando valor estimado, CCT aplicável, número de postos, localização e histórico de pagamento do órgão.',
              },
            ],
          }),
        }}
      />

      {/* Opening paragraph */}
      <p className="text-base sm:text-xl leading-relaxed text-ink">
        Servicos de limpeza, conservacao e facilities management representam uma das
        maiores categorias de contratacao publica no Brasil. Em 2024, o governo
        federal sozinho manteve mais de <strong>R$ 12 bilhoes em contratos ativos</strong>{' '}
        de servicos terceirizados de limpeza e conservacao predial, segundo o Painel
        de Compras do Governo Federal. Somando estados e municipios, o mercado
        ultrapassa R$ 40 bilhoes anuais. A demanda e constante, os contratos sao
        de longa duracao (12 a 60 meses) e a renovacao e previsivel. Mas vencer
        nesse segmento exige dominio de planilha de custos, conhecimento profundo
        da convencao coletiva e capacidade operacional comprovada. Este guia
        apresenta tudo o que voce precisa saber para participar com competitividade
        de licitacoes de limpeza e facilities em 2026.
      </p>

      {/* Section 1: Panorama */}
      <h2>Panorama: terceirizacao no setor publico</h2>

      <p>
        A terceirizacao de servicos de limpeza, conservacao, portaria e manutencao
        predial e uma realidade consolidada na administracao publica brasileira.
        Desde o Decreto 9.507/2018, regulamentado agora pela Lei 14.133/2021, o
        governo pode contratar empresas privadas para executar servicos de apoio
        que nao envolvam atividade-fim do orgao. Na pratica, isso significa que
        praticamente todo orgao publico -- de um tribunal federal a uma escola
        municipal -- contrata limpeza e conservacao via licitacao.
      </p>

      <p>
        O PNCP registra entre 5.000 e 9.000 publicacoes mensais relacionadas a
        servicos de limpeza, conservacao e facilities, considerando todas as
        esferas e modalidades. Esse volume faz do segmento a maior categoria de
        servicos continuados terceirizados no setor publico, a frente de
        vigilancia, TI e alimentacao.
      </p>

      <p>
        Uma caracteristica definidora desse mercado e a mao de obra intensiva.
        Em contratos de limpeza, o custo com pessoal (salarios + encargos)
        representa entre 70% e 82% do valor total. Isso torna a convencao
        coletiva de trabalho (CCT) o fator mais critico na formacao de preco
        -- e o principal diferenciador entre uma proposta competitiva e uma
        proposta inexequivel.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Dados de referencia -- Mercado de limpeza e facilities no setor publico
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Volume mensal no PNCP:</strong> 5.000 a 9.000 publicacoes
            (pregoes, dispensas, atas de registro de preco) em todas as esferas.
          </li>
          <li>
            <strong>Contratos federais ativos:</strong> mais de R$ 12 bilhoes em
            servicos de limpeza e conservacao (Painel de Compras, 2024).
          </li>
          <li>
            <strong>Duracao media do contrato:</strong> 12 meses iniciais com
            possibilidade de prorrogacao por ate 10 anos (art. 107 da Lei
            14.133/2021 para servicos continuados).
          </li>
          <li>
            <strong>Percentual de custo com pessoal:</strong> 70% a 82% do valor
            total do contrato (fonte: IN SEGES/ME 5/2017, modelo referencial).
          </li>
          <li>
            <strong>Setores sindicais:</strong> SEAC (Sindicato das Empresas de
            Asseio e Conservacao) presente em todos os 26 estados e DF, com CCTs
            proprias por base territorial.
          </li>
        </ul>
      </div>

      {/* Section 2: Tipos de objeto */}
      <h2>Tipos de objeto: limpeza, jardinagem, portaria, manutencao e copeiragem</h2>

      <p>
        O conceito de &ldquo;facilities management&rdquo; abrange diversos servicos de
        apoio a operacao de edificios e instalacoes. Em licitacoes publicas, os
        objetos mais frequentes sao:
      </p>

      <h3>Limpeza e conservacao predial</h3>

      <p>
        O objeto mais comum e mais volumoso. Inclui varrição, lavagem, aspiração,
        higienizacao de banheiros, recolhimento de residuos, limpeza de vidros e
        fachadas. Os editais definem a produtividade esperada por servente (tipicamente
        600 a 1.200 m2 por jornada de 8 horas, conforme IN SEGES 5/2017) e o
        numero de postos necessarios. A frequencia pode ser diaria, semanal ou
        quinzenal, dependendo do tipo de area (administrativa, hospitalar, laboratorio).
      </p>

      <h3>Jardinagem e paisagismo</h3>

      <p>
        Servicos de manutencao de areas verdes, incluindo poda, irrigacao, adubacao,
        controle de pragas e plantio. Frequentemente licitados em conjunto com
        limpeza predial em editais multiservicos, ou separadamente para orgaos
        com grandes areas externas (universidades, quarteis, hospitais com campus).
      </p>

      <h3>Portaria e recepcao</h3>

      <p>
        Controle de acesso, atendimento ao publico, operacao de interfones e CCTV,
        recepcao de visitantes. Embora nao seja estritamente &ldquo;limpeza&rdquo;,
        muitos editais de facilities agrupam portaria com limpeza e conservacao em
        um unico contrato. O custo por posto de portaria e tipicamente maior que
        limpeza, pois exige jornada 12x36 ou 24 horas com escalas.
      </p>

      <h3>Manutencao predial</h3>

      <p>
        Servicos de manutencao preventiva e corretiva de instalacoes eletricas,
        hidraulicas, de climatizacao e de alvenaria. Requer mao de obra qualificada
        (eletricistas, encanadores, técnicos de refrigeracao) e pode envolver
        fornecimento de materiais. As convencoes coletivas para manutencao sao
        diferentes das de limpeza (SINDMACON ou equivalente), com pisos salariais
        superiores.
      </p>

      <h3>Copeiragem</h3>

      <p>
        Preparacao e distribuicao de cafe, cha, agua e lanches em ambientes
        administrativos. Servico de menor porte, mas presente em praticamente
        todo orgao publico. Frequentemente incluido em editais de limpeza como
        item adicional.
      </p>

      {/* Section 3: Modalidades */}
      <h2>Modalidades: pregao, SRP e contratacao continuada</h2>

      <p>
        Servicos de limpeza sao classificados como servicos comuns (art. 6, XIII da
        Lei 14.133/2021), o que torna o{' '}
        <Link href="/glossario#pregao-eletronico" className="text-brand-navy dark:text-brand-blue hover:underline">
          pregao eletronico
        </Link>{' '}
        a modalidade obrigatoria. Mais de 85% dos editais de limpeza publicados no
        PNCP utilizam pregao eletronico com criterio de menor preco global ou menor
        preco por lote.
      </p>

      <p>
        O Sistema de Registro de Precos (SRP) e utilizado quando o orgao deseja
        flexibilidade no quantitativo -- por exemplo, quando precisa contratar
        servicos de limpeza para multiplas unidades com cronogramas diferentes.
        A ata de registro de precos permite acionar o fornecedor conforme a
        necessidade, sem obrigacao de contratacao integral.
      </p>

      <p>
        A contratacao continuada (art. 106 da Lei 14.133/2021) e a regra para
        servicos de limpeza: o contrato e firmado por 12 meses com possibilidade
        de prorrogacao sucessiva, podendo atingir ate 10 anos de duracao total
        (art. 107). Essa caracteristica e vantajosa para o fornecedor porque
        gera receita recorrente e previsivel -- desde que a empresa consiga manter
        a qualidade do servico e negociar repactuacoes adequadas ao longo do tempo.
      </p>

      {/* Section 4: Planilha de custos */}
      <h2>Planilha de custos e formacao de preco</h2>

      <p>
        A planilha de custos e o documento mais critico em licitacoes de limpeza.
        Diferente de pregoes de bens (onde o preco e simples: custo do produto +
        margem), em servicos de limpeza cada componente de custo deve ser
        discriminado e justificado. A Instrucao Normativa SEGES/ME 5/2017
        (ainda vigente como referencia) estabelece o modelo de planilha, e a
        maioria dos editais adota esse formato.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Estrutura da planilha de custos -- Limpeza predial
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li>
            <strong>Modulo 1 -- Remuneracao:</strong> Salario base (conforme CCT),
            adicional de insalubridade (quando aplicavel, 20% do salario minimo),
            adicional noturno (se houver turno noturno), vale-transporte
            (desconto legal de 6%).
          </li>
          <li>
            <strong>Modulo 2 -- Encargos e beneficios:</strong> INSS patronal
            (20% + RAT/FAP), FGTS (8%), PIS/PASEP (1%), SESC/SESI (1,5%), SENAC/SENAI
            (1%), SEBRAE (0,6%), INCRA (0,2%), salario-educacao (2,5%), ferias + 1/3,
            13o salario, licencas, rescisao provisionada. Total de encargos: 65% a 80%
            sobre o salario.
          </li>
          <li>
            <strong>Modulo 3 -- Insumos:</strong> Produtos de limpeza (detergente,
            desinfetante, cera, limpa-vidro), sacos de lixo, papel higienico, papel
            toalha. Custo medio: R$ 150 a R$ 400 por posto/mes.
          </li>
          <li>
            <strong>Modulo 4 -- Uniformes e EPIs:</strong> 2 jogos de uniforme por
            semestre, calcados, luvas, mascaras, oculos de protecao. Custo medio:
            R$ 80 a R$ 200 por posto/mes (amortizado).
          </li>
          <li>
            <strong>Modulo 5 -- Equipamentos:</strong> Aspiradores, enceradeiras,
            lavadoras, carrinhos funcionais. Custo de depreciacao: R$ 50 a R$ 150
            por posto/mes.
          </li>
          <li>
            <strong>Modulo 6 -- Custos indiretos e BDI:</strong> Administracao
            central (3% a 5%), lucro (5% a 10%), impostos (ISS 2% a 5%, PIS 0,65%
            a 1,65%, COFINS 3% a 7,6%, CSLL 1,08%, IRPJ 1,2%). BDI total: 15% a 25%.
          </li>
        </ul>
      </div>

      <p>
        O erro mais grave na formacao de preco e utilizar valores genericos em vez
        dos valores especificos da convencao coletiva da regiao de execucao. Um
        servente de limpeza em Sao Paulo (piso de R$ 1.870 em 2025) custa
        significativamente mais que em cidades do interior do Nordeste (piso de
        R$ 1.420 a R$ 1.550). Usar o piso errado gera uma proposta inexequivel
        (se usar o piso menor para uma vaga em SP) ou nao competitiva (se usar
        o piso maior para uma vaga no interior).
      </p>

      {/* Section 5: Convencao coletiva */}
      <h2>Convencao coletiva e impacto regional</h2>

      <p>
        A convencao coletiva de trabalho (CCT) e o documento que define o piso
        salarial, beneficios, jornada e condicoes especificas para trabalhadores
        do setor de asseio e conservacao em uma determinada base territorial.
        Cada estado -- e em alguns casos, cada regiao metropolitana -- possui
        sua propria CCT, negociada entre o SEAC (sindicato patronal) e o
        sindicato dos empregados.
      </p>

      <p>
        A variacao entre regioes e significativa. O piso salarial para servente
        de limpeza pode variar em ate 40% entre a capital e o interior do mesmo
        estado, e em ate 60% entre estados diferentes. Beneficios obrigatorios
        (vale-alimentacao, plano odontologico, seguro de vida, cesta basica)
        tambem variam conforme a CCT, impactando diretamente a planilha de
        custos.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-surface-1 border border-[var(--border)] rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Pisos salariais de referencia -- Servente de limpeza (CCTs 2024/2025)
        </p>
        <ul className="space-y-2 text-sm text-ink-secondary">
          <li><strong>Sao Paulo (capital):</strong> R$ 1.870,00</li>
          <li><strong>Rio de Janeiro (capital):</strong> R$ 1.750,00</li>
          <li><strong>Belo Horizonte:</strong> R$ 1.620,00</li>
          <li><strong>Curitiba:</strong> R$ 1.710,00</li>
          <li><strong>Porto Alegre:</strong> R$ 1.680,00</li>
          <li><strong>Salvador:</strong> R$ 1.550,00</li>
          <li><strong>Brasilia (DF):</strong> R$ 1.795,00</li>
          <li><strong>Recife:</strong> R$ 1.480,00</li>
          <li className="pt-2 text-xs">
            Fonte: CCTs registradas no Sistema Mediador (MTE), vigencia 2024/2025.
            Valores aproximados, sujeitos a negociacoes coletivas em andamento.
          </li>
        </ul>
      </div>

      <p>
        O dissidio anual (reajuste definido na nova CCT) e o evento que mais
        impacta a rentabilidade de contratos em andamento. Se a empresa nao
        provisionar o dissidio projetado na formacao de preco original, corre
        risco de operar no prejuizo ate conseguir a repactuacao contratual --
        que pode levar 60 a 120 dias apos a vigencia da nova CCT.
      </p>

      {/* Section 6: UFs com maior demanda */}
      <h2>UFs com maior demanda de servicos de limpeza</h2>

      <p>
        O volume de licitacoes de limpeza segue a concentracao de orgaos publicos
        e a populacao urbana. Os estados com maior numero de publicacoes sao
        aqueles com mais unidades administrativas, hospitais, escolas e tribunais.
      </p>

      <p>
        <strong>Sao Paulo</strong> lidera de forma expressiva, com o maior numero
        de municipios populosos e a maior administracao estadual do pais.{' '}
        <strong>Minas Gerais</strong>, com 853 municipios (o maior numero entre
        todas as UFs), gera volume alto de pregoes municipais. O{' '}
        <strong>Distrito Federal</strong> concentra a administracao federal e
        produz editais de grande valor (ministerios, tribunais superiores,
        autarquias). <strong>Rio de Janeiro</strong> e <strong>Rio Grande do
        Sul</strong> completam o top 5, impulsionados por suas redes estaduais
        de saude e educacao.
      </p>

      <p>
        Para fornecedores que buscam expandir atuacao, estados do Centro-Oeste
        (GO, MT, MS) oferecem oportunidades com menor concorrencia. A desvantagem
        e a necessidade de manter equipe local, pois editais de servicos
        continuados exigem presenca operacional permanente.
      </p>

      {/* Section 7: Requisitos */}
      <h2>Requisitos de habilitacao</h2>

      <p>
        Licitacoes de limpeza exigem documentacao especifica alem dos requisitos
        genericos da Lei 14.133/2021.
      </p>

      <p>
        <strong>CNAE adequado:</strong> O CNPJ deve conter CNAE compativel com o
        objeto. Os mais comuns sao 8121-4/00 (limpeza em predios e em domicilios)
        e 8111-7/00 (servicos combinados para apoio a edificios). Editais multiservicos
        podem exigir CNAEs adicionais (8130-3/00 para paisagismo, 8020-0/01 para
        portaria).
      </p>

      <p>
        <strong>Atestados de capacidade tecnica:</strong> Comprovacao de execucao
        anterior de servicos similares com quantitativo minimo definido no edital
        (tipicamente 50% do numero de postos licitados). Atestados devem ser
        emitidos por orgaos ou empresas contratantes, com descricao detalhada
        do objeto, quantitativos e periodo de execucao. Para entender os
        requisitos legais completos, veja{' '}
        <Link href="/blog/lei-14133-guia-fornecedores" className="text-brand-navy dark:text-brand-blue hover:underline">
          o guia pratico da Lei 14.133 para fornecedores
        </Link>.
      </p>

      <p>
        <strong>Qualificacao economico-financeira:</strong> Balanco patrimonial
        demonstrando indices de liquidez geral (LG), liquidez corrente (LC)
        e solvencia geral (SG) iguais ou superiores a 1. Para contratos de grande
        porte (acima de R$ 5 milhoes anuais), pode ser exigido capital social
        minimo proporcional ao valor da contratacao (tipicamente 10%).
      </p>

      <p>
        <strong>Vistoria tecnica:</strong> Muitos editais exigem vistoria
        presencial nas instalacoes do orgao antes da apresentacao da proposta.
        A vistoria permite avaliar a area total, o tipo de piso, a altura dos
        vidros, o numero de banheiros e outras condicoes que impactam
        diretamente a produtividade e o custo.
      </p>

      {/* CTA at ~40% */}
      <BlogInlineCTA
        slug="licitacoes-limpeza-facilities-2026"
        campaign="guias"
        ctaHref="/explorar"
        ctaText="Explorar licitacoes gratis"
        ctaMessage="Descubra editais abertos no seu setor — busca gratuita"
      />

      {/* Section 8: Erros fatais */}
      <h2>Erros fatais em licitacoes de limpeza</h2>

      <p>
        O setor de limpeza tem armadilhas especificas que eliminam fornecedores
        antes mesmo da fase de lances. Conhecer esses erros e a diferenca entre
        uma empresa que cresce com contratos publicos e uma que acumula prejuizos.
      </p>

      <h3>Erro 1: Nao considerar o dissidio na formacao de preco</h3>

      <p>
        O erro mais comum e mais caro. A empresa formula o preco com base no piso
        salarial vigente sem considerar que, em 6 a 10 meses, o dissidio reajustara
        esse piso em 5% a 12%. Se o contrato nao prever clausula de repactuacao, ou
        se a repactuacao demorar a ser processada, a empresa opera com margem negativa
        durante meses. A pratica recomendada e incluir na proposta uma projecao de
        dissidio baseada no historico da CCT (media dos ultimos 3 reajustes).
      </p>

      <h3>Erro 2: Esquecer uniformes e EPIs no custo</h3>

      <p>
        A NR-6 exige fornecimento gratuito de EPIs (luvas, mascaras, calcados de
        seguranca) ao trabalhador. A CCT tipicamente obriga o fornecimento de 2
        jogos de uniforme por semestre. Empresas que nao incluem esses itens na
        planilha de custos apresentam proposta com valor artificialmente baixo --
        que sera questionada na analise de exequibilidade (art. 59, paragrafo 4
        da Lei 14.133/2021) e pode resultar em desclassificacao.
      </p>

      <h3>Erro 3: Subestimar a supervisao</h3>

      <p>
        Contratos de limpeza com mais de 15 postos tipicamente exigem um
        encarregado (supervisor) dedicado. O custo desse profissional (salario
        30% a 50% superior ao do servente, conforme CCT) deve ser incluido na
        planilha. Muitas empresas omitem o encarregado para reduzir o preco,
        mas a ausencia de supervisao resulta em queda de qualidade, notificacoes
        e, eventualmente, rescisao contratual.
      </p>

      <h3>Erro 4: Usar a CCT errada</h3>

      <p>
        A CCT aplicavel e a do local de execucao do contrato, nao a da sede da
        empresa. Uma empresa sediada em Recife que vence um pregao em Brasilia
        deve aplicar a CCT de Brasilia -- cujo piso e significativamente superior.
        Usar o piso de Recife na proposta gera inexequibilidade e desclassificacao.
        Para um panorama de como outros setores lidam com formacao de preco, veja{' '}
        <Link href="/blog/licitacoes-alimentacao-2026" className="text-brand-navy dark:text-brand-blue hover:underline">
          o guia de licitacoes de alimentacao 2026
        </Link>.
      </p>

      <h3>Erro 5: Nao provisionar rescisoes trabalhistas</h3>

      <p>
        Contratos de limpeza tem rotatividade alta (turnover de 15% a 30% ao ano).
        Cada desligamento gera custos (aviso previo, multa FGTS 40%, ferias
        proporcionais). Empresas que nao provisionam esses custos na planilha
        (tipicamente 3% a 5% sobre o custo de pessoal) enfrentam problemas de
        fluxo de caixa ao longo do contrato.
      </p>

      {/* Section 9: Como vencer */}
      <h2>Como vencer em licitacoes de limpeza: o preco e 80% do criterio</h2>

      <p>
        Em pregoes eletronicos de limpeza, o criterio de julgamento e quase sempre
        menor preco. Isso significa que a capacidade de formular o preco mais baixo
        viavel -- sem ser inexequivel -- e o fator decisivo. A margem de diferenca
        entre propostas vencedoras e classificadas em segundo lugar costuma ser
        inferior a 3%.
      </p>

      <p>
        As empresas que consistentemente vencem licitacoes de limpeza compartilham
        tres caracteristicas:
      </p>

      <p>
        <strong>Dominio da planilha:</strong> Conhecem profundamente cada componente
        de custo e conseguem otimizar sem cortar itens obrigatorios. A diferenca
        entre propostas nao esta no salario (definido pela CCT) nem nos encargos
        (definidos por lei), mas nos custos de insumos, equipamentos e
        administracao central -- onde ha espaco para eficiencia.
      </p>

      <p>
        <strong>Escala operacional:</strong> Empresas com mais contratos conseguem
        diluir custos de administracao central, comprar insumos com desconto de
        volume e manter equipe de supervisao compartilhada entre contratos
        proximos geograficamente.
      </p>

      <p>
        <strong>Gestao de pessoal eficiente:</strong> O maior custo e pessoal.
        Empresas que conseguem reduzir turnover (via beneficios, treinamento,
        boas condicoes de trabalho) economizam nos custos de rescisao e
        recrutamento, permitindo precos mais competitivos. Para uma abordagem
        estruturada sobre como analisar a viabilidade de cada edital antes de
        investir na proposta, consulte{' '}
        <Link href="/blog/analise-viabilidade-editais-guia" className="text-brand-navy dark:text-brand-blue hover:underline">
          o guia de analise de viabilidade de editais
        </Link>.
      </p>

      <div className="not-prose my-6 sm:my-8 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 sm:p-6">
        <p className="text-sm font-semibold text-ink mb-3">
          Exemplo pratico -- Formacao de preco por posto de limpeza em SP
        </p>
        <ul className="space-y-1.5 text-sm text-ink-secondary">
          <li>
            <strong>Salario base (CCT SP 2024/25):</strong> R$ 1.870,00
          </li>
          <li>
            <strong>Encargos sociais e trabalhistas (72%):</strong> R$ 1.346,40
          </li>
          <li>
            <strong>Beneficios CCT (VT, VA, plano odontologico):</strong> R$ 520,00
          </li>
          <li>
            <strong>Insumos de limpeza:</strong> R$ 280,00
          </li>
          <li>
            <strong>Uniformes e EPIs (amortizado):</strong> R$ 120,00
          </li>
          <li>
            <strong>Equipamentos (depreciacao):</strong> R$ 85,00
          </li>
          <li>
            <strong>Supervisao (proporcional):</strong> R$ 190,00
          </li>
          <li>
            <strong>Subtotal custo direto:</strong> R$ 4.411,40
          </li>
          <li>
            <strong>BDI (20%):</strong> R$ 882,28
          </li>
          <li className="pt-2 font-semibold">
            Preco por posto/mes: R$ 5.293,68
          </li>
        </ul>
      </div>

      {/* Section 10: Repactuacao */}
      <h2>Repactuacao: como manter a rentabilidade ao longo do contrato</h2>

      <p>
        A repactuacao e o mecanismo que permite reequilibrar o contrato apos
        mudancas nos custos de mao de obra (dissidio) e insumos. Diferente do
        reajuste por indice (que aplica um unico percentual), a repactuacao
        exige demonstracao item a item da variacao de custos, com base na
        nova CCT e nos precos de mercado.
      </p>

      <p>
        O art. 135 da Lei 14.133/2021 preve a repactuacao para contratos de servicos
        continuados com mao de obra dedicada. O processo funciona assim: apos a
        vigencia da nova CCT (que define o novo piso salarial), a empresa solicita
        a repactuacao ao orgao contratante, apresentando planilha de custos
        atualizada. O orgao analisa, negocia e, se os valores estiverem adequados,
        formaliza o aditivo contratual com efeitos retroativos a data da nova CCT.
      </p>

      <p>
        Na pratica, o processo pode levar de 60 a 120 dias entre a solicitacao e o
        pagamento do retroativo. Nesse periodo, a empresa absorve a diferenca de
        custo. Por isso, e essencial manter reserva de capital de giro proporcional
        ao numero de contratos ativos e ao impacto esperado do dissidio.
      </p>

      {/* CTA Section */}
      <div className="not-prose mt-8 sm:mt-12 bg-brand-blue-subtle dark:bg-brand-navy/20 rounded-xl p-5 sm:p-8 text-center border border-brand-blue/20">
        <p className="text-lg sm:text-xl font-bold text-ink mb-2">
          Encontre editais de limpeza e facilities com o SmartLic -- 14 dias gratis
        </p>
        <p className="text-sm sm:text-base text-ink-secondary mb-4 sm:mb-6 max-w-lg mx-auto">
          O SmartLic monitora o PNCP e classifica editais por setor usando IA.
          Receba licitacoes de limpeza, conservacao e facilities compativeis com
          seu perfil -- filtradas por UF, valor e modalidade.
        </p>
        <Link
          href="/signup?source=blog&article=licitacoes-limpeza-facilities-2026&utm_source=blog&utm_medium=cta&utm_content=licitacoes-limpeza-facilities-2026&utm_campaign=guias"
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

      <h3>Como montar planilha de custos para licitacao de limpeza?</h3>
      <p>
        A planilha deve incluir remuneracao base conforme a CCT vigente do local
        de execucao, encargos sociais e trabalhistas (65% a 80% sobre o salario),
        insumos de limpeza, EPIs e uniformes, equipamentos (depreciacao), custos
        indiretos (supervisao, administracao central) e BDI (15% a 25%). A soma
        de todos os componentes gera o custo por posto de servico. Siga o modelo
        da IN SEGES/ME 5/2017 como referencia e adapte aos termos especificos
        do edital. Cada item deve ser justificado com base em convencao coletiva,
        pesquisa de mercado ou norma regulatoria.
      </p>

      <h3>Qual o peso da convencao coletiva na formacao de preco?</h3>
      <p>
        A CCT e o fator determinante. O salario base definido pela convencao
        representa entre 50% e 60% do custo total do posto, e os encargos
        incidentes sobre o salario elevam esse percentual para 70% a 82%.
        Cada reajuste anual (dissidio) impacta diretamente o preco. Empresas
        que nao projetam o dissidio na formacao de preco correm risco de operar
        com margem negativa apos o reajuste.{' '}
        <Link href="/glossario#valor-estimado" className="text-brand-navy dark:text-brand-blue hover:underline">
          Entender o valor estimado
        </Link>{' '}
        do edital em relacao a CCT e fundamental.
      </p>

      <h3>Preciso de quantos atestados de capacidade?</h3>
      <p>
        A Lei 14.133/2021 permite exigencia de atestados que comprovem ate 50%
        do quantitativo licitado (art. 67, paragrafo 1). Na pratica, editais de
        limpeza exigem entre 1 e 3 atestados demonstrando experiencia com servicos
        similares, indicando numero de postos ou area atendida, periodo de execucao
        e qualidade do servico. Atestados de contratos publicos tem maior peso,
        mas contratos privados sao aceitos quando acompanhados de notas fiscais e
        contrato.
      </p>

      <h3>E possivel participar em UFs diferentes da sede?</h3>
      <p>
        Sim, nao ha restricao legal. Porem, e essencial considerar que a CCT
        aplicavel e a do local de execucao (nao a da sede), o que altera
        significativamente os custos. Muitos editais exigem escritorio ou preposto
        na cidade de execucao durante a vigencia. Alem disso, a logistica de
        supervisao, recrutamento e fornecimento de insumos deve ser planejada
        para a localidade de destino, nao para a origem.
      </p>

      <h3>Como funciona a repactuacao de contratos de limpeza?</h3>
      <p>
        A repactuacao (art. 135 da Lei 14.133/2021) e o reajuste de contratos de
        servicos continuados baseado na variacao de custos efetivos. Apos a vigencia
        da nova CCT, o contratado solicita repactuacao apresentando planilha
        atualizada. O orgao analisa e formaliza aditivo com efeitos retroativos.
        O prazo minimo para a primeira repactuacao e 12 meses da data do orcamento.
        Na pratica, o processo leva 60 a 120 dias entre solicitacao e pagamento,
        exigindo capital de giro da empresa para absorver o custo no interim. Consulte
        tambem{' '}
        <Link href="/glossario#habilitacao" className="text-brand-navy dark:text-brand-blue hover:underline">
          os requisitos de habilitacao
        </Link>{' '}
        para garantir conformidade durante todo o contrato.
      </p>

      <h3>O que e BDI e como calcular para servicos de limpeza?</h3>
      <p>
        BDI (Bonificacao e Despesas Indiretas) e o percentual aplicado sobre os
        custos diretos para cobrir administracao central, seguros, riscos, impostos
        sobre faturamento (ISS, PIS, COFINS, CSLL, IRPJ) e margem de lucro. Para
        servicos de limpeza, o BDI tipico varia entre 15% e 25%. O calculo segue a
        formula do TCU (Acordao 2622/2013-Plenario). Na pratica, BDI abaixo de 15%
        levanta suspeita de inexequibilidade, e acima de 30% pode ser questionado
        na analise de aceitabilidade. O regime tributario da empresa (Simples Nacional,
        Lucro Presumido ou Real) impacta diretamente o componente de impostos dentro
        do BDI.
      </p>
    </>
  );
}
