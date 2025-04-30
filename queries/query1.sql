SELECT 
    e.uf,
    est.nome AS nome_estado,
    AVG(saeb."notaMatematica") AS media_matematica,
    AVG(saeb."notaLinguaPort") AS media_lingua_portuguesa,
    -- AVG(se.media_classificacao_se) AS media_classificacao_socioeconomica
    SUM(se.media_classificacao_se * se."qtdAlunosInse") / SUM(se."qtdAlunosInse") AS media_ponderada_classificacao_socioeconomica
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

SELECT 
    e.uf,
    est.nome AS nome_estado,
    AVG(saeb."notaMatematica") AS media_matematica,
    AVG(saeb."notaLinguaPort") AS media_portugues,
    SUM(se.media_se * se.total_alunos) / SUM(se.total_alunos) AS media_ponderada_se  -- Ponderada pela quantidade de alunos
FROM 
    public."Escola" esc
JOIN 
    public."Municipio" e ON esc."idMunicipio" = e."idMunicipio"
JOIN 
    public."Estado" est ON e.uf = est.uf
JOIN 
    public."NotaSAEB" saeb ON saeb."idEscola" = esc."idEscola"
JOIN (
    -- Subconsulta fudida que calcula a média SE por escola já multiplicando pela quantidade de alunos
    SELECT 
        ia."idEscola",
        SUM(pca."porcentagemAlunos" * cse."idClassificacaoSE") / 100.0 AS media_se,
        SUM(ia."qtdAlunosInse") AS total_alunos  -- Aqui eu somei os alunos pra ponderar depois
    FROM 
        public."IndicadoresAlunos" ia
    JOIN 
        public."PorcentagemClassificacaoAlunos" pca ON ia."idIndicadoresAlunos" = pca."idIndicadoresAlunos"
    JOIN 
        public."ClassificacaoSocioEconomica" cse ON pca."idClassificacaoSE" = cse."idClassificacaoSE"
    GROUP BY 
        ia."idEscola"  -- Só agrupei por escola, o resto tá agregado (SUM)
) se ON se."idEscola" = esc."idEscola"
WHERE 
    esc."idTipoLocalizacao" = (
        SELECT "idTipoLocalizacao" 
        FROM public."TipoLocalizacao" 
        WHERE LOWER("nomeTipoLocalizacao") LIKE '%rural%'
        LIMIT 1
    )
GROUP BY 
    e.uf, est.nome  -- Agrupa por estado
ORDER BY 
    est.nome;  -- Ordena pelo nome do estado