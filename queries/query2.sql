WITH base_completa AS (
    SELECT
        esc."idEscola",
        esc."idTipoLocalizacao",
        tl."nomeTipoLocalizacao",
        m.uf,
        est.nome AS nome_estado,
        sa."notaMatematica",
        sa."notaLinguaPort",
        ia."qtdAlunosInse"
    FROM public."Escola" esc
    JOIN public."Municipio" m ON esc."idMunicipio" = m."idMunicipio"
    JOIN public."Estado" est ON m.uf = est.uf
    JOIN public."TipoLocalizacao" tl ON esc."idTipoLocalizacao" = tl."idTipoLocalizacao"
    JOIN public."NotaSAEB" sa ON esc."idEscola" = sa."idEscola"
    JOIN public."IndicadoresAlunos" ia ON esc."idEscola" = ia."idEscola"
),
media_se_por_escola AS (
    SELECT
        ia."idEscola",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se
    FROM public."IndicadoresAlunos" ia
    JOIN public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY ia."idEscola"
)

SELECT
    bc.uf,
    bc.nome_estado,
    bc."nomeTipoLocalizacao" AS tipo_localizacao,
    ROUND(SUM(bc."notaMatematica" * bc."qtdAlunosInse")::numeric / NULLIF(SUM(bc."qtdAlunosInse"), 0), 2) AS media_ponderada_matematica,
    ROUND(SUM(bc."notaLinguaPort" * bc."qtdAlunosInse")::numeric / NULLIF(SUM(bc."qtdAlunosInse"), 0), 2) AS media_ponderada_portugues,
    ROUND(SUM(COALESCE(se.media_se, 0) * bc."qtdAlunosInse")::numeric / NULLIF(SUM(bc."qtdAlunosInse"), 0), 2) AS media_ponderada_se
FROM base_completa bc
LEFT JOIN media_se_por_escola se ON bc."idEscola" = se."idEscola"
GROUP BY
    bc.uf, bc.nome_estado, bc."nomeTipoLocalizacao"
ORDER BY
    bc.nome_estado, tipo_localizacao;
