WITH NSE_Ponderado_Escola AS (
    SELECT
        ia."idEscola",
        ia."anoMedicao",
        SUM(pca."idClassificacaoSE" * pca."porcentagemAlunos") / NULLIF(SUM(pca."porcentagemAlunos"), 0) AS "nivel_socioeconomico_ponderado"
    FROM
        "IndicadoresAlunos" ia
    JOIN
        "PorcentagemClassificacaoAlunos" pca ON pca."idIndicadoresAlunos" = ia."idIndicadoresAlunos"
    GROUP BY
        ia."idEscola", ia."anoMedicao"
)

SELECT
    e."idEscola",
    tr."nomeTipoRede" AS "tipo_rede",
    ni."anoMedicao",
    ROUND(ni."notaIdeb"::numeric, 2) AS "nota_ideb",
    ROUND(nse."nivel_socioeconomico_ponderado"::numeric, 2) AS "nivel_socioeconomico"
FROM
    "NotaIDEB" ni
JOIN
    "Escola" e ON e."idEscola" = ni."idEscola"
JOIN
    "TipoRede" tr ON tr."idTipoRede" = e."idTipoRede"
JOIN
    NSE_Ponderado_Escola nse ON nse."idEscola" = ni."idEscola" AND nse."anoMedicao" = ni."anoMedicao"
ORDER BY
    tr."nomeTipoRede", nse."nivel_socioeconomico_ponderado" DESC;
