WITH media_se_por_escola AS (
    SELECT
        ia."idEscola",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se
    FROM public."IndicadoresAlunos" ia
    JOIN public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY ia."idEscola"
),
base_escolas AS (
    SELECT
        esc."idEscola",
        tr."nomeTipoRede" AS tipo_rede,
        ideb."notaIdeb" AS nota_ideb,
        se.media_se
    FROM public."Escola" esc
    JOIN public."TipoRede" tr ON esc."idTipoRede" = tr."idTipoRede"
    JOIN public."NotaIDEB" ideb ON esc."idEscola" = ideb."idEscola"
    LEFT JOIN media_se_por_escola se ON esc."idEscola" = se."idEscola"
    WHERE ideb."notaIdeb" IS NOT NULL
)

SELECT
    tipo_rede,
    ROUND(AVG(nota_ideb)::numeric, 2) AS media_ideb,
    ROUND(AVG(media_se)::numeric, 2) AS media_se
FROM base_escolas
GROUP BY tipo_rede
ORDER BY tipo_rede;
