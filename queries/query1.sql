SELECT 
    e.uf,
    est.nome AS nome_estado,
    AVG(saeb."notaMatematica") AS media_matematica,
    AVG(saeb."notaLinguaPort") AS media_lingua_portuguesa,
    -- AVG(se.media_classificacao_se) AS media_classificacao_socioeconomica
    SUM(se.media_classificacao_se * se.qtdAlunosInse) / SUM(se.qtdAlunosInse) AS media_ponderada_classificacao_socioeconomica
FROM public."Escola" esc
JOIN public."Municipio" e ON esc."idMunicipio" = e."idMunicipio"
JOIN public."Estado" est ON e.uf = est.uf
JOIN public."NotaSAEB" saeb ON saeb."idEscola" = esc."idEscola"
JOIN (
    -- Subconsulta: calcula a média socioeconômica ponderada por escola
    SELECT 
        ia."idEscola",
        ia."qtdAlunosInse",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_classificacao_se
    FROM public."IndicadoresAlunos" ia
    JOIN public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY ia."idEscola"
) se ON se."idEscola" = esc."idEscola"
WHERE esc."idTipoLocalizacao" = (
    SELECT "idTipoLocalizacao" 
    FROM public."TipoLocalizacao" 
    WHERE LOWER("nomeTipoLocalizacao") LIKE '%rural%'
    LIMIT 1
)
GROUP BY e.uf
ORDER BY est.nome;
