WITH escola_localizacao AS (
    SELECT
        e."idEscola",
        m.uf,
        m.nome AS nome_municipio,
        tc.nome AS tipo_capital
    FROM "Escola" e
    JOIN "Municipio" m ON e."idMunicipio" = m."idMunicipio"
    JOIN "TipoCapital" tc ON m."idTipoCapital" = tc."idTipoCapital"
),
socioeconomico_escola AS (
    SELECT 
        ia."idEscola",
        ia."anoMedicao",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se,
        SUM(ia."qtdAlunosInse") AS total_alunos
    FROM "IndicadoresAlunos" ia
    JOIN "PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN "ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY ia."idEscola", ia."anoMedicao"
),
saeb_escola AS (
    SELECT
        ns."idEscola",
        ns."anoMedicao",
        ns."notaMatematica",
        ns."notaLinguaPort",
        ns."notaPadronizada"
    FROM "NotaSAEB" ns
),
base_completa AS (
    SELECT
        sl.uf,
        sl.tipo_capital,
        se."anoMedicao",
        se.media_se,
        se.total_alunos,
        sa.notaMatematica,
        sa.notaLinguaPort,
        sa.notaPadronizada
    FROM socioeconomico_escola se
    JOIN escola_localizacao sl ON se."idEscola" = sl."idEscola"
    JOIN saeb_escola sa ON se."idEscola" = sa."idEscola" AND se."anoMedicao" = sa."anoMedicao"
)
SELECT
    uf,
    tipo_capital,
    anoMedicao,
    ROUND(SUM(media_se * total_alunos) / NULLIF(SUM(total_alunos), 0), 2) AS media_ponderada_se,
    ROUND(SUM(notaMatematica * total_alunos) / NULLIF(SUM(total_alunos), 0), 2) AS media_ponderada_matematica,
    ROUND(SUM(notaLinguaPort * total_alunos) / NULLIF(SUM(total_alunos), 0), 2) AS media_ponderada_lingua,
    ROUND(SUM(notaPadronizada * total_alunos) / NULLIF(SUM(total_alunos), 0), 2) AS media_ponderada_padronizada
FROM base_completa
GROUP BY uf, tipo_capital, anoMedicao
ORDER BY uf, anoMedicao, tipo_capital;
