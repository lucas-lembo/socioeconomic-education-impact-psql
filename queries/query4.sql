WITH media_se_por_escola AS (
    SELECT
        ia."idEscola",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se
    FROM public."IndicadoresAlunos" ia
    JOIN public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY ia."idEscola"
)

SELECT
    esc."idEscola",
    esc."nome" AS nome_escola,
    tr."nomeTipoRede" AS tipo_rede,
    ROUND(ideb."notaIdeb"::numeric, 2) AS nota_ideb,
    ROUND(se.media_se::numeric, 2) AS media_ponderada_se
FROM public."Escola" esc
JOIN public."TipoRede" tr ON esc."idTipoRede" = tr."idTipoRede"
JOIN public."NotaIDEB" ideb ON esc."idEscola" = ideb."idEscola"
LEFT JOIN media_se_por_escola se ON esc."idEscola" = se."idEscola"
WHERE ideb."notaIdeb" IS NOT NULL
ORDER BY tr."nomeTipoRede", nota_ideb DESC;
